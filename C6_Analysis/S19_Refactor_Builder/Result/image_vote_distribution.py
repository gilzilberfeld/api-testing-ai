from typing import Dict


class ImageVoteDistribution:
    """Represents how votes are distributed across images"""

    @staticmethod
    def single_image() -> Dict[str, float]:
        """All votes go to a single image"""
        return {"single": 1.0}

    @staticmethod
    def even_distribution(num_images: int) -> Dict[str, float]:
        """Votes are evenly distributed across images"""
        return {f"image_{i}": 1.0 / num_images for i in range(num_images)}

    @staticmethod
    def weighted_distribution(weights: Dict[str, float]) -> Dict[str, float]:
        """Custom weighted distribution of votes"""
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}

    @staticmethod
    def primary_image_distribution(primary_weight: float = 0.6, num_others: int = 3) -> Dict[str, float]:
        """One primary image gets most votes, others share the rest"""
        if primary_weight >= 1.0:
            return ImageVoteDistribution.single_image()

        remaining = 1.0 - primary_weight
        secondary_weight = remaining / num_others

        result = {"primary": primary_weight}
        for i in range(num_others):
            result[f"secondary_{i}"] = secondary_weight

        return result
