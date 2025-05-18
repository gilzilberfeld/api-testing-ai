import random


class VoteValueStrategy:
    """Strategy for determining vote values (up/down)"""

    @staticmethod
    def all_upvotes() -> int:
        """All votes are upvotes (value=1)"""
        return 1

    @staticmethod
    def all_downvotes() -> int:
        """All votes are downvotes (value=0)"""
        return 0

    @staticmethod
    def random_votes(upvote_probability: float = 0.8) -> int:
        """Random mix of up and down votes"""
        return 1 if random.random() < upvote_probability else 0

    @staticmethod
    def alternating_votes() -> int:
        """Alternating pattern of up and down votes"""
        # This needs to be stateful, which doesn't fit well with static methods
        # To be implemented in the builder
        pass
