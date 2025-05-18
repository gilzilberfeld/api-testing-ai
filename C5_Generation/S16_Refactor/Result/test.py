import pytest

from C5_Generation.S16_Refactor.Result.cat_api_client import CatApiClient


# Constants
API_KEY = "your_cat_api_key_here"  # Replace with your actual API key


@pytest.fixture
def api_client():
    """
    Fixture providing a configured API client with proper headers.

    Returns:
        C5_Generation.S16_Refactor.result_cat_api_client.CatApiClient: Configured client for making API requests
    """
    return CatApiClient(API_KEY)


@pytest.fixture
def test_image_with_votes(api_client):
    """
    Fixture that sets up a test image with exactly 3 votes.

    Args:
        api_client: The Cat API client fixture

    Yields:
        Dict containing test data including image_id, votes, etc.
    """
    print("\n=== Setting up test image with 3 votes ===")

    # Set up test resources
    image_data = api_client.find_random_image()
    image_id = image_data["id"]

    # Add 3 votes from different users
    vote_sub_ids = ["test-user-1", "test-user-2", "test-user-3"]
    votes = []

    for sub_id in vote_sub_ids:
        vote = api_client.add_vote(image_id, sub_id)
        votes.append(vote)

    # Verify votes were recorded
    actual_votes = api_client.get_votes_for_image(image_id)
    vote_count = len(actual_votes)

    print(f"Found {vote_count} votes for image {image_id}")

    if vote_count < 3:
        print("Warning: Not all votes may have been recorded.")

    # Create test data object
    test_data = {
        "image_id": image_id,
        "image_url": image_data["url"],
        "vote_sub_ids": vote_sub_ids,
        "votes": votes,
        "vote_count": vote_count,
        "additional_votes": []  # Will store any votes created during tests
    }

    print("Setup complete!")

    # Yield the test data to the test
    yield test_data

    # Cleanup after the test is done
    print("\n=== Cleaning up test data ===")
    cleanup_test_data(api_client, test_data)


def cleanup_test_data(api_client, test_data):
    """
    Clean up all test data created during testing

    Args:
        api_client: The Cat API client
        test_data: Dictionary containing test data including image_id, votes, etc.
    """
    cleanup_summary = {
        "votes_removed": 0,
        "favorites_removed": 0,
        "errors": []
    }

    try:
        # Clean up votes for the test image
        image_id = test_data["image_id"]
        print(f"Cleaning up votes for image {image_id}...")

        # Get all votes for this image
        votes = api_client.get_votes_for_image(image_id)

        # Delete each vote
        for vote in votes:
            vote_id = vote.get("id")
            if vote_id and api_client.delete_vote(vote_id):
                cleanup_summary["votes_removed"] += 1
            else:
                cleanup_summary["errors"].append(f"Failed to delete vote {vote_id}")

        # Clean up any favorites created during testing
        print("Checking for favorites to clean up...")
        favorites = api_client.get_favorites_for_image(image_id)

        for favorite in favorites:
            favorite_id = favorite.get("id")
            if favorite_id and api_client.delete_favorite(favorite_id):
                cleanup_summary["favorites_removed"] += 1
            else:
                cleanup_summary["errors"].append(f"Failed to delete favorite {favorite_id}")

        print("Cleanup complete!")
        print(f"Removed {cleanup_summary['votes_removed']} votes and "
              f"{cleanup_summary['favorites_removed']} favorites.")

        if cleanup_summary["errors"]:
            print(f"Encountered {len(cleanup_summary['errors'])} errors during cleanup.")

    except Exception as e:
        print(f"Error during cleanup: {str(e)}")


def test_vote_count_increases(api_client, test_image_with_votes):
    """
    Test that adding a vote increases the vote count for an image.

    Args:
        api_client: The Cat API client fixture
        test_image_with_votes: Fixture providing test image with votes
    """
    print("\n=== Running test: Adding a vote should increase vote count ===")

    # Get test data from fixture
    image_id = test_image_with_votes["image_id"]
    initial_vote_count = test_image_with_votes["vote_count"]

    print(f"Initial vote count: {initial_vote_count}")

    # 1. Add a new vote from a different user
    new_sub_id = "test-user-new"
    new_vote = api_client.add_vote(image_id, new_sub_id)

    # Store the new vote for cleanup
    test_image_with_votes["additional_votes"].append(new_vote)

    # 2. Get the updated vote count
    votes_after = api_client.get_votes_for_image(image_id)
    updated_vote_count = len(votes_after)

    print(f"Updated vote count after adding new vote: {updated_vote_count}")

    # 3. Assert that the vote count increased by 1
    assert updated_vote_count == initial_vote_count + 1, \
        "Vote count did not increase after adding a new vote"

    print("Test passed: Vote count increased as expected")


if __name__ == "__main__":
    pytest.main(["-v", __file__])