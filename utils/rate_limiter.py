import time
from typing import Dict

class RateLimiter:
    """Simple rate limiter to prevent users from spamming the /CZ command."""
    
    def __init__(self, default_cooldown: int = 30):
        """
        Initialize the rate limiter.
        
        Args:
            default_cooldown: Default cooldown time in seconds
        """
        self.default_cooldown = default_cooldown
        self.user_last_used: Dict[int, float] = {}
    
    def is_allowed(self, user_id: int) -> bool:
        """
        Check if a user is allowed to use the command.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is allowed, False otherwise
        """
        current_time = time.time()
        
        if user_id not in self.user_last_used:
            return True
        
        last_used = self.user_last_used[user_id]
        elapsed_time = current_time - last_used
        
        return elapsed_time >= self.default_cooldown
    
    def update_usage(self, user_id: int):
        """
        Update the last used time for a user.
        
        Args:
            user_id: Telegram user ID
        """
        self.user_last_used[user_id] = time.time()
    
    def get_remaining_time(self, user_id: int) -> int:
        """
        Get the remaining time in seconds before the user can use the command again.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Remaining time in seconds
        """
        if user_id not in self.user_last_used:
            return 0
        
        current_time = time.time()
        last_used = self.user_last_used[user_id]
        elapsed_time = current_time - last_used
        
        remaining = self.default_cooldown - int(elapsed_time)
        return max(0, remaining)