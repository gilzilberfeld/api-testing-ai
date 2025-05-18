import random
import string
import time


class UserIdStrategy:
    """Strategy for generating user IDs (sub_ids)"""

    @staticmethod
    def random_id(prefix: str = "test-user") -> str:
        """Generate a random user ID with prefix"""
        timestamp = str(int(time.time()))
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{prefix}-{timestamp}-{random_str}"

    @staticmethod
    def sequential_id(index: int, prefix: str = "test-user") -> str:
        """Generate a sequential user ID with prefix and index"""
        return f"{prefix}-{index:04d}"

    @staticmethod
    def fixed_id(user_id: str) -> str:
        """Use a fixed user ID for all votes"""
        return user_id
