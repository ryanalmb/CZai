import logging
from typing import Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

class AIService:
    """Service class to handle all Gemini API interactions, migrated to google-genai with fallback.

    This implementation prefers the new `google-genai` SDK, but will fall back to
    the legacy `google-generativeai` SDK if the new one isn't available at runtime.
    """

    def __init__(self):
        """Initialize the AI service with API key and SDK selection."""
        self.model_name = settings.gemini_model
        self.sdk = None  # "new" or "old"
        self.client = None
        self._new_types = {}

        # System prompt template for CZ.AI
        self.system_prompt = (
            "You are CZ.AI, a parody, satirical assistant with a very optimistic, upbeat tone. "
            "Always respond bilingually: first in English, then in Simplified Chinese (简体中文). "
            "Celebrate innovation and progress in crypto, use positive, motivational language, and keep replies concise and high‑energy. "
            "Provide only high-level, educational information about blockchain and crypto markets. Do NOT provide financial, investment, or trading advice. "
            "Never recommend buying/selling/holding, price targets, timing trades, or portfolio allocations. Do not tailor advice to a person’s situation. "
            "If asked for recommendations, politely decline and pivot to general educational context with an optimistic framing. "
            "Keep tone light, satirical, and respectful."
        )

        # Attempt to use the new google-genai SDK first
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
            # New SDK uses a Client instance
            self.client = genai_new.Client(api_key=settings.gemini_api_key)
            logger.info("Using google-genai SDK")
        except Exception as e:  # noqa: BLE001
            logger.info("google-genai not available or failed to initialize, falling back to google-generativeai: %s", e)
            # Fallback to legacy SDK
            import google.generativeai as genai_old  # type: ignore

            self.sdk = "old"
            self.genai_old = genai_old
            genai_old.configure(api_key=settings.gemini_api_key)
            logger.info("Using google-generativeai SDK (legacy)")

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
        """Generate a response using Gemini with optional grounding."""
        try:
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

            if self.sdk == "new":
                GenerateContentConfig = self._new_types["GenerateContentConfig"]
                Tool = self._new_types["Tool"]
                GoogleSearch = self._new_types["GoogleSearch"]

                config = GenerateContentConfig(
                    temperature=0.9,
                    max_output_tokens=1024,
                    system_instruction=self.system_prompt,
                )

                if use_grounding:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=user_prompt,
                        config=config,
                        tools=[Tool(google_search=GoogleSearch())],
                    )
                else:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=user_prompt,
                        config=config,
                    )
            else:
                # Legacy SDK path
                genai_old = self.genai_old
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

            return self._handle_response(response, user_query)

        except Exception as e:  # noqa: BLE001
            logger.error("Error generating response for user query '%s': %s", user_query, e)
            error_msg = str(e).lower()
            if "safety" in error_msg or "block" in error_msg:
                return (
                    "I keep things educational and safe, so I can’t answer that directly — want a high‑level overview instead?\n"
                    "为了安全与合规，我不能直接回答这个问题——要不要来个高层次的背景讲解？"
                )
            return (
                "(No fresh web results; answer may be slightly out of date — but I’ll keep the vibes bright!)\n"
                "（暂时没有最新的网页结果；信息可能略有延迟——不过积极乐观的能量不会断档！）"
            )