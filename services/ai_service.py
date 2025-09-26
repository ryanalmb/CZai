import logging
from typing import Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service class to handle all Gemini API interactions, migrated to google-genai with fallback.

    - Supports multiple API keys with failover rotation: uses the current key until an API error
      occurs, then advances to the next key. After the last key fails, it loops back to the first.
    - Primary SDK: google-genai. Fallback SDK: google-generativeai.
    - Bilingual optimistic persona (English first, then Simplified Chinese).
    """

    def __init__(self):
        """Initialize the AI service with API keys and SDK selection."""
        self.model_name = settings.gemini_model
        # Multi-key support
        self.gemini_keys = settings.gemini_api_keys if getattr(settings, "gemini_api_keys", []) else [settings.gemini_api_key]
        if not self.gemini_keys:
            raise ValueError("No Gemini API keys configured")
        self.key_index = 0  # current active key index

        self.sdk = None  # "new" or "old"
        self.clients_new = []  # list of google-genai Clients (one per key)
        self.genai_old = None
        self._new_types = {}

        # System prompt template for CZ.AI
        self.system_prompt = (
            "You are CZ.AI — a CZ‑style consultant and assistant (parody). Keep replies short, confident, and optimistic, with clear, builder‑energy aphorisms. "
            "Always respond bilingually: first in English, then in Simplified Chinese (简体中文). "
            "Focus on high‑level, educational information about blockchain/BNB Chain and community culture. Do NOT provide financial, investment, or trading advice. "
            "Never recommend buying/selling/holding, price targets, timing trades, or portfolio allocations. Do not tailor advice to a person’s situation. "
            "If asked for recommendations, politely decline and offer a general educational overview instead. Keep tone warm, respectful, and constructive."
        )

        # Attempt to use the new google-genai SDK first (preferred)
        try:
            import google.genai as genai_new  # type: ignore
            from google.genai.types import GenerateContentConfig, Tool, GoogleSearch  # type: ignore

            self.sdk = "new"
            self.genai_new = genai_new
            self._new_types = {
                "GenerateContentConfig": GenerateContentConfig,
                "Tool": Tool,
                "GoogleSearch": GoogleSearch,
            }
            # Create a client per key
            for k in self.gemini_keys:
                self.clients_new.append(genai_new.Client(api_key=k))
            logger.info("Using google-genai SDK with %d key(s)", len(self.clients_new))
        except Exception as e:  # noqa: BLE001
            logger.info("google-genai not available or failed to initialize, falling back to google-generativeai: %s", e)
            # Fallback to legacy SDK (configure per request with the active key)
            import google.generativeai as genai_old  # type: ignore
            self.sdk = "old"
            self.genai_old = genai_old
            logger.info("Using google-generativeai SDK (legacy) with %d key(s)", len(self.gemini_keys))

    def needs_grounding(self, query: str) -> bool:
        """Determine if a query needs web grounding based on keywords."""
        grounding_keywords = [
            "news", "price", "BNB news", "hack", "regulation",
            "today", "yesterday", "latest", "update", "recent",
            "announcement", "market", "change", "now", "current"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in grounding_keywords)

    def is_greeting(self, query: str) -> bool:
        """Detect if the user input is a simple greeting/salutation to trigger a cheerful welcome."""
        q = (query or "").strip().lower()
        if not q:
            return False
        # Common greeting tokens and very short messages
        greetings = {
            "hi", "hello", "hey", "yo", "sup", "gm", "gn", "good morning",
            "good night", "good evening", "good afternoon", "hiya", "hola", "bonjour",
        }
        # Exact match or startswith
        if q in greetings:
            return True
        # Handle punctuation and short variations like "hi!", "hey!!", "hello :)"
        for g in greetings:
            if q.startswith(g + " ") or q.startswith(g + "!") or q == g + "!" or q == g + "!!":
                return True
        # Very short inputs (1-2 words) that are common salutes
        if len(q.split()) <= 2 and any(g in q for g in greetings):
            return True
        return False

    def _extract_text_from_response(self, response) -> str:
        """Attempt to extract text from both new and old SDK response shapes."""
        # 1) New SDK common helpers
        for attr in ("output_text", "text"):
            if hasattr(response, attr) and getattr(response, attr):
                return str(getattr(response, attr))

        # 2) Candidates -> parts.text path (works for both in many cases)
        candidates = getattr(response, "candidates", None)
        if candidates:
            cand = candidates[0]
            # Try a direct text field
            if hasattr(cand, "text") and cand.text:
                return str(cand.text)
            # Try parts
            content = getattr(cand, "content", None)
            if content and hasattr(content, "parts") and content.parts:
                parts_text = []
                for part in content.parts:
                    if hasattr(part, "text") and part.text:
                        parts_text.append(part.text)
                if parts_text:
                    return " ".join(parts_text)

        return ""

    def _is_blocked_candidate(self, response) -> bool:
        """Heuristics to detect blocked responses across SDKs."""
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return False
        cand = candidates[0]
        # finish_reason may be an int code or a string; common blocked indicators
        fr = getattr(cand, "finish_reason", None)
        # Treat MAX_TOKENS as not a policy block
        if fr in ("MAX_TOKENS",):
            return False
        if fr in (2, "SAFETY", "BLOCKED", "OTHER", "FINISH_REASON_UNSPECIFIED"):
            return True
        # No parts and zero tokens is also a strong indicator
        token_count = getattr(cand, "token_count", None)
        content = getattr(cand, "content", None)
        parts = getattr(content, "parts", None) if content else None
        if (parts is None or len(parts) == 0) and (token_count in (0, None)):
            return True
        return False

    def _handle_response(self, response, user_query) -> str:
        """Unified response handler for both grounded and non-grounded queries."""
        try:
            # If a blocked candidate is detected, return a policy-safe message
            if self._is_blocked_candidate(response):
                logger.warning("Blocked response for query '%s'. Raw: %s", user_query, response)
                return (
                    "All good! I can’t provide investment or trading recommendations — but I’d love to share upbeat, high‑level insights to light the way!\n"
                    "没问题！我不能提供投资或交易建议——但我很乐意用积极、乐观的方式分享高层次的学习信息，给你启发！"
                )

            text_response = self._extract_text_from_response(response)
            if not text_response:
                # If we hit max tokens without parts, suggest retrying shorter
                candidates = getattr(response, "candidates", None)
                fr = getattr(candidates[0], "finish_reason", None) if candidates else None
                if fr == "MAX_TOKENS":
                    return (
                        "Whoa, too much sunshine for one message! Try a shorter question or ask me to summarize.\n"
                        "内容有点长啦！可以试试更简短的问题，或者让我来个要点总结～"
                    )
                # Check prompt-level feedback if available (legacy SDK)
                pf = getattr(response, "prompt_feedback", None)
                br = getattr(pf, "block_reason", None) if pf else None
                if br:
                    logger.warning("Prompt blocked for query '%s': %s", user_query, br)
                    return (
                        "I keep things educational and safe, so I can’t answer that directly — want a high‑level overview instead?\n"
                        "为了安全与合规，我不能直接回答这个问题——要不要来个高层次的背景讲解？"
                    )
                logger.warning("No valid text extracted for query '%s'. Raw: %s", user_query, response)
                return (
                        "No worries — I didn’t catch that, but I’m ready to help! Try rephrasing or asking for a quick overview.\n"
                        "别担心——我没完全理解，但我一定能帮上忙！可以换个说法，或让我先给你一个快速概览。"
                    )

            # Extract lightweight citations if available (legacy grounding metadata)
            citations = []
            candidates = getattr(response, "candidates", None)
            if candidates:
                cand = candidates[0]
                gm = getattr(cand, "grounding_metadata", None)
                if gm:
                    chunks = getattr(gm, "grounding_chunks", [])
                    for chunk in chunks[:2]:
                        web = getattr(chunk, "web", None)
                        url = getattr(web, "url", None) if web else None
                        if url:
                            citations.append(url)

            if citations:
                return f"{text_response} (" + ", ".join(citations) + ")"
            return text_response
        except Exception as e:  # noqa: BLE001
            logger.error("Error processing response for user query '%s': %s. Raw: %s", user_query, e, response)
            return (
            "Oops, the optimism engine hiccuped — give it another go!\n"
            "哎呀，乐观引擎打了个喷嚏——再试一次就好！"
        )

    def generate_response(self, user_query: str) -> str:
        """Generate a response using Gemini with optional grounding and key failover."""
        # Instant sunshine mode for greetings — no LLM needed
        if self.is_greeting(user_query):
            return (
                "Hey hey! 🌞✨ Amazing to see you, fren! Energy’s high, optimism’s higher — let’s make today legendary! How can I help you shine?\n"
                "嘿嘿！🌞✨ 很高兴见到你，朋友！能量满格，乐观加倍——今天一起创造传奇吧！我可以怎样帮助你闪耀？"
            )

        # Build user prompt with safe behavior baked in
        user_prompt = (
            f"User question: {user_query}\n"
            "Instructions: Respond in both English and Simplified Chinese (简体中文). Use a very optimistic, upbeat, high‑energy tone. "
            "Provide general, educational information only. Do not provide financial, investment, or trading advice or recommendations (no buy/sell/hold, price targets, timing, or allocations). "
            "If asked for recommendations, politely decline and pivot to educational context."
        )

        use_grounding = (
            settings.use_gemini_search and
            not settings.context7_disabled and
            self.needs_grounding(user_query)
        )

        num_keys = len(self.gemini_keys)
        # Try with the current key; on API error, advance to the next and retry, looping over all keys once.
        for attempt in range(num_keys):
            idx = self.key_index
            try:
                if self.sdk == "new":
                    GenerateContentConfig = self._new_types["GenerateContentConfig"]
                    Tool = self._new_types["Tool"]
                    GoogleSearch = self._new_types["GoogleSearch"]

                    config = GenerateContentConfig(
                        temperature=0.9,
                        max_output_tokens=1024,
                        system_instruction=self.system_prompt,
                    )
                    client = self.clients_new[idx]
                    if use_grounding:
                        response = client.models.generate_content(
                            model=self.model_name,
                            contents=user_prompt,
                            config=config,
                            tools=[Tool(google_search=GoogleSearch())],
                        )
                    else:
                        response = client.models.generate_content(
                            model=self.model_name,
                            contents=user_prompt,
                            config=config,
                        )
                else:
                    # Legacy SDK path: configure per-request with the active key
                    genai_old = self.genai_old
                    genai_old.configure(api_key=self.gemini_keys[idx])
                    model = genai_old.GenerativeModel(
                        model_name=self.model_name,
                        system_instruction=self.system_prompt,
                    )
                    generation_config = genai_old.GenerationConfig(
                        temperature=0.9,
                        max_output_tokens=1024,
                    )
                    if use_grounding:
                        chat = model.start_chat()
                        response = chat.send_message(
                            user_prompt,
                            generation_config=generation_config,
                            tools=[genai_old.protos.Tool(google_search=genai_old.protos.GoogleSearch())],
                        )
                    else:
                        response = model.generate_content(
                            user_prompt,
                            generation_config=generation_config,
                        )

                # If we reached here, call succeeded; keep using this key
                return self._handle_response(response, user_query)

            except Exception as e:  # noqa: BLE001
                # On any API exception, advance to the next key and try again
                logger.warning(
                    "Gemini API error with key index %d: %s. Switching to next key (attempt %d/%d).",
                    idx, e, attempt + 1, num_keys
                )
                self.key_index = (self.key_index + 1) % num_keys
                continue

        # If all keys failed in this cycle
        logger.error("All configured Gemini API keys failed for this request.")
        return (
            "We’ve run into a temporary connection issue, but the sun will rise again — please try once more!\n"
            "我们遇到了一点临时连接问题，但太阳依然会升起——请再试一次！"
        )
