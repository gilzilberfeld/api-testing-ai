import random
from typing import Dict, List, Optional

from C6_Analysis.S19_Refactor_Builder.result.main_generator import VoteGenerator
from C6_Analysis.S19_Refactor_Builder.result.userid_strategy import UserIdStrategy
from C6_Analysis.S19_Refactor_Builder.result.vote_value_strategy import VoteValueStrategy
from C6_Analysis.S19_Refactor_Builder.result.image_vote_distribution import ImageVoteDistribution
from C6_Analysis.S19_Refactor_Builder.result.api_client import CatApiClient


class VoteGeneratorBuilder:
    """Builder for configuring and executing vote generation"""

    def __init__(self, api_client: CatApiClient):
        """
        Initialize the vote generator builder
        Args:
            api_client: The Cat API client
        """
        self.api_client = api_client
        self.num_votes = 10
        self.image_distribution = ImageVoteDistribution.single_image()
        self.vote_value_strategy = VoteValueStrategy.random_votes
        self.user_id_strategy = UserIdStrategy.random_id
        self.specific_image_ids = []
        self.verify_votes = True
        self.save_results = True
        self.result_filename = None
        self._alternating_vote_state = True  # For alternating vote values

        # For tracking used IDs to avoid duplicates
        self._used_sub_ids = set()

    def with_vote_count(self, count: int) -> 'VoteGeneratorBuilder':
        """Set the number of votes to generate"""
        assert count > 0, "Vote count must be positive"
        self.num_votes = count
        return self

    def with_single_image(self) -> 'VoteGeneratorBuilder':
        """Use a single image for all votes"""
        self.image_distribution = ImageVoteDistribution.single_image()
        return self

    def with_even_distribution(self, num_images: int) -> 'VoteGeneratorBuilder':
        """Distribute votes evenly across multiple images"""
        assert num_images > 0, "Number of images must be positive"
        self.image_distribution = ImageVoteDistribution.even_distribution(num_images)
        return self

    def with_primary_image(self, primary_weight: float = 0.6, num_others: int = 3) -> 'VoteGeneratorBuilder':
        """One primary image gets most votes, others share the rest"""
        assert 0.0 < primary_weight < 1.0, "Primary weight must be between 0 and 1"
        assert num_others > 0, "Number of other images must be positive"
        self.image_distribution = ImageVoteDistribution.primary_image_distribution(primary_weight, num_others)
        return self

    def with_weighted_distribution(self, weights: Dict[str, float]) -> 'VoteGeneratorBuilder':
        """Custom weighted distribution of votes"""
        assert all(w > 0 for w in weights.values()), "All weights must be positive"
        self.image_distribution = ImageVoteDistribution.weighted_distribution(weights)
        return self

    def with_specific_images(self, image_ids: List[str]) -> 'VoteGeneratorBuilder':
        """Use specific image IDs instead of random ones"""
        assert len(image_ids) > 0, "At least one image ID must be provided"
        self.specific_image_ids = image_ids
        return self

    def with_all_upvotes(self) -> 'VoteGeneratorBuilder':
        """All votes will be upvotes"""
        self.vote_value_strategy = VoteValueStrategy.all_upvotes
        return self

    def with_all_downvotes(self) -> 'VoteGeneratorBuilder':
        """All votes will be downvotes"""
        self.vote_value_strategy = VoteValueStrategy.all_downvotes
        return self

    def with_random_votes(self, upvote_probability: float = 0.8) -> 'VoteGeneratorBuilder':
        """Random mix of up and down votes"""
        assert 0.0 <= upvote_probability <= 1.0, "Probability must be between 0 and 1"

        def random_vote_strategy():
            return 1 if random.random() < upvote_probability else 0

        self.vote_value_strategy = random_vote_strategy
        return self

    def with_alternating_votes(self) -> 'VoteGeneratorBuilder':
        """Alternating pattern of up and down votes"""

        def alternating_vote_strategy():
            self._alternating_vote_state = not self._alternating_vote_state
            return 1 if self._alternating_vote_state else 0

        self.vote_value_strategy = alternating_vote_strategy
        return self

    def with_random_user_ids(self, prefix: str = "test-user") -> 'VoteGeneratorBuilder':
        """Generate random user IDs"""

        def random_id_strategy():
            while True:
                user_id = UserIdStrategy.random_id(prefix)
                if user_id not in self._used_sub_ids:
                    self._used_sub_ids.add(user_id)
                    return user_id

        self.user_id_strategy = random_id_strategy
        return self

    def with_sequential_user_ids(self, prefix: str = "test-user") -> 'VoteGeneratorBuilder':
        """Generate sequential user IDs"""
        counter = [0]  # Using list for mutable closure variable

        def sequential_id_strategy():
            counter[0] += 1
            user_id = UserIdStrategy.sequential_id(counter[0], prefix)
            self._used_sub_ids.add(user_id)
            return user_id

        self.user_id_strategy = sequential_id_strategy
        return self

    def with_fixed_user_id(self, user_id: str) -> 'VoteGeneratorBuilder':
        """Use the same user ID for all votes"""
        self.user_id_strategy = lambda: user_id
        return self

    def with_verification(self, verify: bool = True) -> 'VoteGeneratorBuilder':
        """Whether to verify votes after creating them"""
        self.verify_votes = verify
        return self

    def with_result_saving(self, save: bool = True, filename: Optional[str] = None) -> 'VoteGeneratorBuilder':
        """Whether to save results to a file"""
        self.save_results = save
        self.result_filename = filename
        return self

    def build(self) -> 'VoteGenerator':
        """Build the vote generator with the current configuration"""
        return VoteGenerator(
            api_client=self.api_client,
            num_votes=self.num_votes,
            image_distribution=self.image_distribution,
            vote_value_strategy=self.vote_value_strategy,
            user_id_strategy=self.user_id_strategy,
            specific_image_ids=self.specific_image_ids,
            verify_votes=self.verify_votes,
            save_results=self.save_results,
            result_filename=self.result_filename
        )
