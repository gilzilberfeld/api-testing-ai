#!/usr/bin/env python3
"""
CatAPI Vote Generator using Builder Pattern

This script generates votes for random images using the CatAPI, implementing
the builder pattern for flexible configuration.

Usage:
  python cat_vote_generator.py --votes 10 --api-key YOUR_API_KEY
"""

import os
import argparse
from typing import Dict, List, Any, Optional

from C6_Analysis.S19_Refactor_Builder.Result.builder import VoteGeneratorBuilder
from C6_Analysis.S19_Refactor_Builder.Result.cat_api_client import CatApiClient
from C6_Analysis.S19_Refactor_Builder.Result.vote_generation_result import VoteGenerationResult


class VoteGenerator:
    """Generates votes for cat images based on configured strategies"""

    def __init__(self, api_client: CatApiClient, num_votes: int,
                 image_distribution: Dict[str, float],
                 vote_value_strategy: callable,
                 user_id_strategy: callable,
                 specific_image_ids: List[str],
                 verify_votes: bool,
                 save_results: bool,
                 result_filename: Optional[str]):
        """
        Initialize the vote generator
        Args:
            api_client: The Cat API client
            num_votes: Number of votes to generate
            image_distribution: Distribution strategy for votes across images
            vote_value_strategy: Strategy for determining vote values
            user_id_strategy: Strategy for generating user IDs
            specific_image_ids: List of specific image IDs to use
            verify_votes: Whether to verify votes after creating them
            save_results: Whether to save results to a file
            result_filename: Name of the file to save results to
        """
        self.api_client = api_client
        self.num_votes = num_votes
        self.image_distribution = image_distribution
        self.vote_value_strategy = vote_value_strategy
        self.user_id_strategy = user_id_strategy
        self.specific_image_ids = specific_image_ids
        self.verify_votes = verify_votes
        self.save_results = save_results
        self.result_filename = result_filename

    def _get_images(self) -> List[Dict[str, Any]]:
        """Get images to use for voting"""
        required_images = len(self.image_distribution)

        # If specific images were provided, use them
        if self.specific_image_ids:
            images = []
            for img_id in self.specific_image_ids[:required_images]:
                try:
                    image = self.api_client.get_image(img_id)
                    images.append(image)
                except Exception as e:
                    print(f"Error fetching image {img_id}: {str(e)}")

            # If we don't have enough images, fetch random ones
            while len(images) < required_images:
                images.append(self.api_client.find_random_image())

            return images

        # Otherwise, fetch random images
        images = []
        for _ in range(required_images):
            images.append(self.api_client.find_random_image())

        return images

    def _calculate_votes_per_image(self, images: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate how many votes each image should get"""
        votes_per_image = {}
        remaining_votes = self.num_votes

        # Match distribution keys to actual images
        distribution_keys = list(self.image_distribution.keys())
        for i, image in enumerate(images):
            if i < len(distribution_keys):
                key = distribution_keys[i]
                votes = int(self.num_votes * self.image_distribution[key])
                votes_per_image[image["id"]] = votes
                remaining_votes -= votes

        # Distribute any remaining votes due to rounding
        for image_id in votes_per_image.keys():
            if remaining_votes > 0:
                votes_per_image[image_id] += 1
                remaining_votes -= 1
            elif remaining_votes < 0:
                votes_per_image[image_id] = max(0, votes_per_image[image_id] - 1)
                remaining_votes += 1

            if remaining_votes == 0:
                break

        return votes_per_image

    def generate(self) -> VoteGenerationResult:
        """Generate votes according to the configured strategies"""
        result = VoteGenerationResult()

        print(f"\n=== Generating {self.num_votes} votes ===")

        # Get images
        images = self._get_images()
        for image in images:
            result.add_image(image)

        print(f"Using {len(images)} images for voting")

        # Calculate votes per image
        votes_per_image = self._calculate_votes_per_image(images)

        # Generate votes
        votes_created = 0
        for image in images:
            image_id = image["id"]
            votes_for_this_image = votes_per_image.get(image_id, 0)

            for _ in range(votes_for_this_image):
                # Generate a unique sub_id
                sub_id = self.user_id_strategy()

                # Determine vote value
                value = self.vote_value_strategy()

                # Add the vote
                try:
                    vote_result = self.api_client.add_vote(image_id, sub_id, value)
                    print(f"Vote {votes_created + 1}/{self.num_votes} created: ID {vote_result.get('id')}")

                    # Add to results
                    result.add_vote({
                        "id": vote_result.get("id"),
                        "image_id": image_id,
                        "sub_id": sub_id,
                        "value": value
                    })

                    votes_created += 1

                except Exception as e:
                    error_message = str(e)
                    print(f"Error creating vote: {error_message}")
                    result.add_error(error_message)

        # Verify the votes
        if self.verify_votes:
            print("\n=== Verifying votes ===")
            for image in images:
                image_id = image["id"]
                votes = self.api_client.get_votes_for_image(image_id)
                print(f"Image {image_id}: {len(votes)} votes recorded")

                # Update results
                result.update_image_vote_count(image_id, len(votes))

        # Finalize Result
        result.finalize()

        # Save results to file if requested
        if self.save_results:
            filename = result.save_to_file(self.result_filename)
            print(f"\nResults saved to {filename}")

        return result


def main():
    """Main function to parse arguments and run the vote generator"""
    parser = argparse.ArgumentParser(description="Generate votes for the Cat API")

    parser.add_argument("--votes", type=int, required=True,
                        help="Number of votes to generate")

    parser.add_argument("--api-key", type=str, default=os.environ.get("CAT_API_KEY"),
                        help="Your Cat API key (can also set CAT_API_KEY env var)")

    parser.add_argument("--image-strategy", type=str, choices=["single", "multiple", "primary"],
                        default="single", help="Image distribution strategy")

    parser.add_argument("--num-images", type=int, default=3,
                        help="Number of images to use when using multiple images")

    parser.add_argument("--primary-weight", type=float, default=0.6,
                        help="Weight of the primary image (between 0 and 1)")

    parser.add_argument("--vote-strategy", type=str,
                        choices=["all-up", "all-down", "random", "alternating"],
                        default="random", help="Vote value strategy")

    parser.add_argument("--user-id-strategy", type=str,
                        choices=["random", "sequential", "fixed"],
                        default="random", help="User ID generation strategy")

    parser.add_argument("--user-id-prefix", type=str, default="test-user",
                        help="Prefix for generated user IDs")

    parser.add_argument("--fixed-user-id", type=str, default=None,
                        help="Fixed user ID to use when --user-id-strategy=fixed")

    parser.add_argument("--image-id", type=str, action="append", default=[],
                        help="Specific image ID to use (can be specified multiple times)")

    parser.add_argument("--no-verify", action="store_true",
                        help="Skip verification step")

    parser.add_argument("--no-save", action="store_true",
                        help="Don't save results to a file")

    parser.add_argument("--output-file", type=str, default=None,
                        help="Name of the file to save results to")

    args = parser.parse_args()

    # Validate required arguments
    if not args.api_key:
        parser.error("API key is required. Provide it with --api-key or set CAT_API_KEY env var")

    if args.votes < 1:
        parser.error("Number of votes must be at least 1")

    if args.user_id_strategy == "fixed" and not args.fixed_user_id:
        parser.error("--fixed-user-id is required when --user-id-strategy=fixed")

    # Initialize the client
    api_client = CatApiClient(args.api_key)

    # Create the generator builder
    builder = VoteGeneratorBuilder(api_client)

    # Configure vote count
    builder.with_vote_count(args.votes)

    # Configure image distribution
    if args.image_strategy == "single":
        builder.with_single_image()
    elif args.image_strategy == "multiple":
        builder.with_even_distribution(args.num_images)
    elif args.image_strategy == "primary":
        builder.with_primary_image(args.primary_weight, args.num_images - 1)

    # Use specific images if provided
    if args.image_id:
        builder.with_specific_images(args.image_id)

    # Configure vote value strategy
    if args.vote_strategy == "all-up":
        builder.with_all_upvotes()
    elif args.vote_strategy == "all-down":
        builder.with_all_downvotes()
    elif args.vote_strategy == "random":
        builder.with_random_votes()
    elif args.vote_strategy == "alternating":
        builder.with_alternating_votes()

    # Configure user ID strategy
    if args.user_id_strategy == "random":
        builder.with_random_user_ids(args.user_id_prefix)
    elif args.user_id_strategy == "sequential":
        builder.with_sequential_user_ids(args.user_id_prefix)
    elif args.user_id_strategy == "fixed":
        builder.with_fixed_user_id(args.fixed_user_id)

    # Configure verification and Result saving
    builder.with_verification(not args.no_verify)
    builder.with_result_saving(not args.no_save, args.output_file)

    # Build and run the generator
    generator = builder.build()
    result = generator.generate()

    # Print summary
    print("\n=== Summary ===")
    print(f"Total votes created: {len(result.votes)}")
    print(f"Using {len(result.images)} images")

    for img in result.images:
        verified_count = img.get("verified_vote_count", "unknown")
        print(f"Image {img['id']}: {verified_count} verified votes")

    if result.errors:
        print(f"\nErrors encountered: {len(result.errors)}")

    print("\nDone!")


if __name__ == "__main__":
    main()