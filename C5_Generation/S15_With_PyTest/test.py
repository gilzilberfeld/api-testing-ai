import requests
import pytest
import time


class TestCatAPIVotes:
    """Test suite for Cat API vote functionality using pytest framework."""

    BASE_URL = "https://api.thecatapi.com/v1"
    API_KEY = "your_cat_api_key_here"  # Replace with your actual API key

    @pytest.fixture
    def headers(self):
        """Fixture providing API headers."""
        return {
            "x-api-key": self.API_KEY,
            "Content-Type": "application/json"
        }

    @pytest.fixture
    def test_image_with_votes(self, headers):
        """
        Fixture that sets up a test image with exactly 3 votes.
        This runs before each test and cleans up after the test completes.
        """
        print("\n=== Setting up test image with 3 votes ===")

        # Step 1: Find a cat image to use for testing
        search_params = {
            "limit": 1,
            "size": "small"
        }

        response = requests.get(f"{self.BASE_URL}/images/search", params=search_params, headers=headers)
        assert response.status_code == 200, f"Failed to search for images: {response.text}"

        image_data = response.json()[0]
        image_id = image_data["id"]
        image_url = image_data["url"]

        print(f"Found cat image with ID: {image_id}")

        # Step 2: Cast 3 votes for this image from different sub_ids
        vote_sub_ids = ["test-user-1", "test-user-2", "test-user-3"]
        votes = []

        for i, sub_id in enumerate(vote_sub_ids):
            print(f"Casting vote {i + 1} from sub_id: {sub_id}...")

            vote_data = {
                "image_id": image_id,
                "value": 1,  # Upvote
                "sub_id": sub_id
            }

            vote_response = requests.post(f"{self.BASE_URL}/votes", json=vote_data, headers=headers)
            assert vote_response.status_code in [200,
                                                 201], f"Failed to cast vote: {vote_response.status_code}, {vote_response.text}"

            votes.append(vote_response.json())
            time.sleep(0.5)  # Small delay to avoid rate limiting

        # Step 3: Verify the votes were recorded
        print("Verifying votes...")
        votes_response = requests.get(f"{self.BASE_URL}/votes", params={"image_id": image_id}, headers=headers)
        assert votes_response.status_code == 200, f"Failed to get votes: {votes_response.text}"

        votes_data = votes_response.json()
        image_votes = [v for v in votes_data if v["image_id"] == image_id]
        vote_count = len(image_votes)

        print(f"Found {vote_count} votes for image {image_id}")

        if vote_count < 3:
            print("Warning: Not all votes may have been recorded. Check the API response.")

        # Create and yield the test data for the test to use
        test_data = {
            "image_id": image_id,
            "image_url": image_url,
            "vote_sub_ids": vote_sub_ids,
            "votes": votes,
            "vote_count": vote_count,
            "additional_votes": []  # Will store any new votes created during tests
        }

        print("Setup complete!")

        # Yield the test data to the test
        yield test_data

        # Cleanup after the test is done
        print("\n=== Cleaning up test data ===")
        self.cleanup_test_data(test_data, headers)

    def cleanup_test_data(self, test_data, headers):
        """
        Helper method to clean up all test data (votes, favorites, etc.)

        Args:
            test_data: Dictionary containing test data
            headers: API headers
        """
        cleanup_summary = {
            "votes_removed": 0,
            "favorites_removed": 0,
            "images_removed": 0,
            "errors": []
        }

        try:
            # Step 1: Clean up votes for the test image
            print(f"Cleaning up votes for image {test_data['image_id']}...")

            votes_response = requests.get(
                f"{self.BASE_URL}/votes",
                params={"image_id": test_data["image_id"]},
                headers=headers
            )

            if votes_response.status_code == 200:
                votes = votes_response.json()

                for vote in votes:
                    vote_id = vote.get("id")
                    if vote_id:
                        print(f"Deleting vote with ID: {vote_id}")
                        delete_response = requests.delete(f"{self.BASE_URL}/votes/{vote_id}", headers=headers)

                        if delete_response.status_code in [200, 204]:
                            cleanup_summary["votes_removed"] += 1
                        else:
                            error_msg = f"Failed to delete vote {vote_id}: {delete_response.status_code}"
                            print(error_msg)
                            cleanup_summary["errors"].append(error_msg)

                        time.sleep(0.2)  # Small delay to avoid rate limiting

            # Step 2: Clean up any additional votes added during testing
            if "additional_votes" in test_data:
                for vote in test_data["additional_votes"]:
                    vote_id = vote.get("id")
                    if vote_id:
                        print(f"Deleting additional vote with ID: {vote_id}")
                        delete_response = requests.delete(f"{self.BASE_URL}/votes/{vote_id}", headers=headers)

                        if delete_response.status_code in [200, 204]:
                            cleanup_summary["votes_removed"] += 1
                        else:
                            error_msg = f"Failed to delete additional vote {vote_id}: {delete_response.status_code}"
                            print(error_msg)
                            cleanup_summary["errors"].append(error_msg)

                        time.sleep(0.2)

            # Step 3: Clean up any favorites created during testing
            print("Checking for favorites to clean up...")
            favorites_response = requests.get(
                f"{self.BASE_URL}/favourites",
                params={"image_id": test_data["image_id"]},
                headers=headers
            )

            if favorites_response.status_code == 200:
                favorites = favorites_response.json()

                for favorite in favorites:
                    favorite_id = favorite.get("id")
                    if favorite_id:
                        print(f"Deleting favorite with ID: {favorite_id}")
                        delete_response = requests.delete(f"{self.BASE_URL}/favourites/{favorite_id}", headers=headers)

                        if delete_response.status_code in [200, 204]:
                            cleanup_summary["favorites_removed"] += 1
                        else:
                            error_msg = f"Failed to delete favorite {favorite_id}: {delete_response.status_code}"
                            print(error_msg)
                            cleanup_summary["errors"].append(error_msg)

                        time.sleep(0.2)

            print("Cleanup complete!")
            print(
                f"Removed {cleanup_summary['votes_removed']} votes and {cleanup_summary['favorites_removed']} favorites.")

            if cleanup_summary["errors"]:
                print(f"Encountered {len(cleanup_summary['errors'])} errors during cleanup.")

        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            print(error_msg)
            cleanup_summary["errors"].append(error_msg)

    def test_vote_count_increases(self, headers, test_image_with_votes):
        """
        Test that adding a vote increases the vote count for an image.

        Args:
            headers: Fixture providing API headers
            test_image_with_votes: Fixture providing test image with votes
        """
        print("\n=== Running test: Adding a vote should increase vote count ===")

        # Get test data from fixture
        image_id = test_image_with_votes["image_id"]
        initial_vote_count = test_image_with_votes["vote_count"]

        print(f"Initial vote count: {initial_vote_count}")

        # Step 1: Add a new vote from a different sub_id
        new_sub_id = "test-user-new"
        vote_data = {
            "image_id": image_id,
            "value": 1,  # Upvote
            "sub_id": new_sub_id
        }

        print(f"Adding new vote from sub_id: {new_sub_id}...")
        vote_response = requests.post(f"{self.BASE_URL}/votes", json=vote_data, headers=headers)

        assert vote_response.status_code in [200,
                                             201], f"Failed to add vote: {vote_response.status_code}, {vote_response.text}"

        # Save the new vote for cleanup
        new_vote = vote_response.json()
        test_image_with_votes["additional_votes"].append(new_vote)

        # Add a small delay to allow the API to process the vote
        time.sleep(1)

        # Step 2: Get the updated vote count
        updated_votes_response = requests.get(
            f"{self.BASE_URL}/votes",
            params={"image_id": image_id},
            headers=headers
        )

        assert updated_votes_response.status_code == 200, "Failed to get updated votes"

        updated_votes = updated_votes_response.json()
        updated_vote_count = len([v for v in updated_votes if v["image_id"] == image_id])

        print(f"Updated vote count after adding new vote: {updated_vote_count}")

        # Step 3: Assert that the vote count increased by 1
        assert updated_vote_count == initial_vote_count + 1, "Vote count did not increase after adding a new vote"
        print("Test passed: Vote count increased as expected")


if __name__ == "__main__":
    # This allows running with pytest command or directly executing this file
    pytest.main(["-v", __file__])