#!/usr/bin/env python3
"""
CatAPI Vote Generator

This script generates a specified number of votes for random images using the CatAPI.
It can be used to set up test scenarios with specific vote counts.

Usage:
  python cat_vote_generator.py --votes 10 --api-key YOUR_API_KEY
"""

import os
import time
import random
import string
import argparse
from typing import Dict, Any
import json

from C6_Analysis.S18_Get_To_The_Point.Result.cat_api_client import CatApiClient



def generate_random_sub_id() -> str:
    """Generate a random sub_id for voting"""
    # Using a UUID and timestamp to ensure uniqueness
    timestamp = str(int(time.time()))
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test-user-{timestamp}-{random_str}"


def generate_votes(api_client: CatApiClient, num_votes: int,
                   use_multiple_images: bool = True,
                   save_results: bool = True) -> Dict[str, Any]:
    """
    Generate a specified number of votes using random data

    Args:
        api_client: The Cat API client
        num_votes: Number of votes to generate
        use_multiple_images: Whether to use multiple images or just one
        save_results: Whether to save results to a JSON file

    Returns:
        Dictionary with vote generation results
    """
    results = {
        "total_votes": num_votes,
        "images": [],
        "votes": []
    }

    print(f"\n=== Generating {num_votes} votes ===")

    # If using multiple images, decide how many
    num_images = random.randint(1, min(5, num_votes)) if use_multiple_images else 1

    # Collect image IDs
    image_ids = []
    for _ in range(num_images):
        image_data = api_client.find_random_image()
        image_ids.append(image_data["id"])
        results["images"].append({
            "id": image_data["id"],
            "url": image_data["url"]
        })

    print(f"Using {len(image_ids)} images for voting")

    # Generate votes
    for i in range(num_votes):
        # Select an image
        image_id = random.choice(image_ids)

        # Generate a unique sub_id
        sub_id = generate_random_sub_id()

        # Randomly choose a vote value (mostly upvotes, but some downvotes)
        value = 1 if random.random() < 0.8 else 0

        # Add the vote
        try:
            vote_result = api_client.add_vote(image_id, sub_id, value)
            print(f"Vote {i + 1}/{num_votes} created: ID {vote_result.get('id')}")

            # Add to results
            results["votes"].append({
                "id": vote_result.get("id"),
                "image_id": image_id,
                "sub_id": sub_id,
                "value": value
            })

        except Exception as e:
            print(f"Error creating vote {i + 1}: {str(e)}")

    # Verify the votes
    print("\n=== Verifying votes ===")
    for img_id in image_ids:
        votes = api_client.get_votes_for_image(img_id)
        print(f"Image {img_id}: {len(votes)} votes recorded")

        # Add to results
        for img in results["images"]:
            if img["id"] == img_id:
                img["verified_vote_count"] = len(votes)
                break

    # Save results to file if requested
    if save_results:
        filename = f"catapi_votes_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {filename}")

    return results


def main():
    """Main function to parse arguments and run the vote generator"""
    parser = argparse.ArgumentParser(description="Generate votes for the Cat API")

    parser.add_argument("--votes", type=int, required=True,
                        help="Number of votes to generate")

    parser.add_argument("--api-key", type=str, default=os.environ.get("CAT_API_KEY"),
                        help="Your Cat API key (can also set CAT_API_KEY env var)")

    parser.add_argument("--single-image", action="store_true",
                        help="Use only one image for all votes")

    parser.add_argument("--no-save", action="store_true",
                        help="Don't save results to a file")

    args = parser.parse_args()

    # Validate required arguments
    if not args.api_key:
        parser.error("API key is required. Provide it with --api-key or set CAT_API_KEY env var")

    if args.votes < 1:
        parser.error("Number of votes must be at least 1")

    # Initialize the client
    api_client = CatApiClient(args.api_key)

    # Generate votes
    results = generate_votes(
        api_client,
        args.votes,
        use_multiple_images=not args.single_image,
        save_results=not args.no_save
    )

    # Print summary
    print("\n=== Summary ===")
    print(f"Total votes created: {len(results['votes'])}")
    print(f"Using {len(results['images'])} images")

    for img in results["images"]:
        verified_count = img.get("verified_vote_count", "unknown")
        print(f"Image {img['id']}: {verified_count} verified votes")

    print("\nDone!")


if __name__ == "__main__":
    main()