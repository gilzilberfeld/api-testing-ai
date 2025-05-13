import requests
import unittest
import time


class CatAPIVoteCountTest(unittest.TestCase):
    """Test suite for verifying vote count functionality in The Cat API."""

    BASE_URL = "https://api.thecatapi.com/v1"
    API_KEY = "your_cat_api_key_here"  # Replace with your actual API key

    def setUp(self):
        """Set up the test environment with an image that has 3 votes."""
        self.headers = {
            "x-api-key": self.API_KEY,
            "Content-Type": "application/json"
        }

        # Set up test data with image and 3 votes
        print("\n=== Setting up test data with image and 3 votes ===")
        self.test_data = self.setup_cat_image_with_three_votes()
        self.image_id = self.test_data["image_id"]
        self.initial_vote_count = len(self.test_data["votes"])
        print(f"Initial vote count: {self.initial_vote_count}")

    def tearDown(self):
        """Clean up all test data after the test."""
        print("\n=== Cleaning up test data ===")
        cleanup_summary = self.cleanup_test_data(self.test_data)
        print(f"Cleanup summary: {cleanup_summary}")

    def test_vote_count_increases(self):
        """Test that adding a vote increases the vote count."""
        print("\n=== Running test: Adding a new vote should increase vote count ===")

        # Step 1: Get the current vote count for verification
        votes_response = requests.get(
            f"{self.BASE_URL}/votes",
            params={"image_id": self.image_id},
            headers=self.headers
        )
        self.assertEqual(votes_response.status_code, 200, "Failed to get current votes")

        current_votes = votes_response.json()
        current_vote_count = len([v for v in current_votes if v["image_id"] == self.image_id])
        print(f"Current vote count before adding new vote: {current_vote_count}")

        # Step 2: Add a new vote from a different sub_id
        new_sub_id = "test-user-new"
        vote_data = {
            "image_id": self.image_id,
            "value": 1,  # Upvote
            "sub_id": new_sub_id
        }

        print(f"Adding new vote from sub_id: {new_sub_id}...")
        vote_response = requests.post(f"{self.BASE_URL}/votes", json=vote_data, headers=self.headers)

        self.assertIn(vote_response.status_code, [200, 201],
                      f"Failed to add vote: {vote_response.status_code}, {vote_response.text}")

        # Add a small delay to allow the API to process the vote
        time.sleep(1)

        # Step 3: Get the updated vote count and verify it increased
        updated_votes_response = requests.get(
            f"{self.BASE_URL}/votes",
            params={"image_id": self.image_id},
            headers=self.headers
        )
        self.assertEqual(updated_votes_response.status_code, 200, "Failed to get updated votes")

        updated_votes = updated_votes_response.json()
        updated_vote_count = len([v for v in updated_votes if v["image_id"] == self.image_id])
        print(f"Updated vote count after adding new vote: {updated_vote_count}")

        # Step 4: Assert that the vote count has increased by 1
        self.assertEqual(updated_vote_count, current_vote_count + 1,
                         "Vote count did not increase after adding a new vote")
        print("Test passed: Vote count increased as expected")

        # Optional: Save the new vote_id for cleanup
        new_vote = vote_response.json()
        if new_vote and "id" in new_vote:
            self.test_data.setdefault("additional_votes", []).append(new_vote)

    def setup_cat_image_with_three_votes(self):
        """
        Sets up a test scenario with a cat image that has received 3 votes.

        Returns:
            dict: A dictionary containing test data including the image_id and vote information
        """
        test_data = {}

        # Step 1: Get a cat image from the API
        print("Searching for a cat image...")
        search_params = {
            "limit": 1,
            "size": "small"  # Getting small image for simplicity
        }

        response = requests.get(f"{self.BASE_URL}/images/search", params=search_params, headers=self.headers)

        self.assertEqual(response.status_code, 200, f"Failed to search for images: {response.text}")

        image_data = response.json()[0]
        image_id = image_data["id"]
        test_data["image_id"] = image_id
        test_data["image_url"] = image_data["url"]

        print(f"Found cat image with ID: {image_id}")

        # Step 2: Cast 3 votes for this image from different sub_ids
        vote_sub_ids = ["test-user-1", "test-user-2", "test-user-3"]
        test_data["vote_sub_ids"] = vote_sub_ids
        test_data["votes"] = []

        for i, sub_id in enumerate(vote_sub_ids):
            print(f"Casting vote {i + 1} from sub_id: {sub_id}...")

            vote_data = {
                "image_id": image_id,
                "value": 1,  # Upvote
                "sub_id": sub_id
            }

            vote_response = requests.post(f"{self.BASE_URL}/votes", json=vote_data, headers=self.headers)

            self.assertIn(vote_response.status_code, [200, 201],
                          f"Failed to cast vote: {vote_response.status_code}, {vote_response.text}")

            vote_result = vote_response.json()
            test_data["votes"].append(vote_result)

            # Adding a small delay between API calls to avoid rate limiting
            time.sleep(0.5)

        # Step 3: Verify the votes were recorded by getting the votes for this image
        print("Verifying votes...")
        votes_response = requests.get(f"{self.BASE_URL}/votes", params={"image_id": image_id}, headers=self.headers)

        self.assertEqual(votes_response.status_code, 200, f"Failed to get votes: {votes_response.text}")

        votes_data = votes_response.json()
        test_data["votes_verification"] = votes_data

        # Check if we have 3 votes for this image
        image_votes = [v for v in votes_data if v["image_id"] == image_id]
        print(f"Found {len(image_votes)} votes for image {image_id}")

        if len(image_votes) < 3:
            print("Warning: Not all votes may have been recorded. Check the API response.")

        print("Setup complete!")
        return test_data

    def cleanup_test_data(self, test_data=None, cleanup_all=False):
        """
        Cleans up test data by removing votes, favorites, and uploaded images.

        Args:
            test_data (dict, optional): The test data to clean up.
            cleanup_all (bool, optional): If True, will attempt to clean all user data.

        Returns:
            dict: A summary of cleanup operations performed
        """
        cleanup_summary = {
            "votes_removed": 0,
            "favorites_removed": 0,
            "images_removed": 0,
            "errors": []
        }

        try:
            # Step 1: Clean up votes
            print("Cleaning up votes...")

            # Get all votes if cleanup_all is True, otherwise get only votes for the specific image
            if cleanup_all:
                votes_response = requests.get(f"{self.BASE_URL}/votes", headers=self.headers)
            elif test_data and "image_id" in test_data:
                votes_response = requests.get(
                    f"{self.BASE_URL}/votes",
                    params={"image_id": test_data["image_id"]},
                    headers=self.headers
                )
            else:
                votes_response = None
                cleanup_summary["errors"].append("No test_data or image_id provided for vote cleanup")

            if votes_response and votes_response.status_code == 200:
                votes = votes_response.json()

                for vote in votes:
                    vote_id = vote.get("id")
                    if vote_id:
                        print(f"Deleting vote with ID: {vote_id}")
                        delete_response = requests.delete(f"{self.BASE_URL}/votes/{vote_id}", headers=self.headers)

                        if delete_response.status_code in [200, 204]:
                            cleanup_summary["votes_removed"] += 1
                        else:
                            error_msg = f"Failed to delete vote {vote_id}: {delete_response.status_code}"
                            print(error_msg)
                            cleanup_summary["errors"].append(error_msg)

                        # Adding a small delay between API calls to avoid rate limiting
                        time.sleep(0.2)

            # Step 2: Clean up any additional votes added during testing
            if test_data and "additional_votes" in test_data:
                for vote in test_data["additional_votes"]:
                    vote_id = vote.get("id")
                    if vote_id:
                        print(f"Deleting additional vote with ID: {vote_id}")
                        delete_response = requests.delete(f"{self.BASE_URL}/votes/{vote_id}", headers=self.headers)

                        if delete_response.status_code in [200, 204]:
                            cleanup_summary["votes_removed"] += 1
                        else:
                            error_msg = f"Failed to delete additional vote {vote_id}: {delete_response.status_code}"
                            print(error_msg)
                            cleanup_summary["errors"].append(error_msg)

                        time.sleep(0.2)

            # Step 3: Clean up favorites (if applicable)
            if cleanup_all or (test_data and "image_id" in test_data):
                print("Cleaning up favorites...")
                favorites_params = {}
                if test_data and "image_id" in test_data:
                    favorites_params["image_id"] = test_data["image_id"]

                favorites_response = requests.get(f"{self.BASE_URL}/favourites", params=favorites_params,
                                                  headers=self.headers)

                if favorites_response.status_code == 200:
                    favorites = favorites_response.json()

                    for favorite in favorites:
                        favorite_id = favorite.get("id")
                        if favorite_id:
                            print(f"Deleting favorite with ID: {favorite_id}")
                            delete_response = requests.delete(f"{self.BASE_URL}/favourites/{favorite_id}",
                                                              headers=self.headers)

                            if delete_response.status_code in [200, 204]:
                                cleanup_summary["favorites_removed"] += 1
                            else:
                                error_msg = f"Failed to delete favorite {favorite_id}: {delete_response.status_code}"
                                print(error_msg)
                                cleanup_summary["errors"].append(error_msg)

                            time.sleep(0.2)

            # Step 4: Clean up uploaded images (if applicable)
            # Note: This only works for images that were uploaded by the user
            if cleanup_all:
                print("Cleaning up uploaded images...")
                images_response = requests.get(f"{self.BASE_URL}/images", headers=self.headers)

                if images_response.status_code == 200:
                    images = images_response.json()

                    for image in images:
                        image_id = image.get("id")
                        if image_id:
                            print(f"Deleting image with ID: {image_id}")
                            delete_response = requests.delete(f"{self.BASE_URL}/images/{image_id}",
                                                              headers=self.headers)

                            if delete_response.status_code in [200, 204]:
                                cleanup_summary["images_removed"] += 1
                            else:
                                error_msg = f"Failed to delete image {image_id}: {delete_response.status_code}"
                                print(error_msg)
                                cleanup_summary["errors"].append(error_msg)

                            time.sleep(0.2)

            print("Cleanup complete!")
            print(
                f"Removed {cleanup_summary['votes_removed']} votes, {cleanup_summary['favorites_removed']} favorites, and {cleanup_summary['images_removed']} images.")

            if cleanup_summary["errors"]:
                print(f"Encountered {len(cleanup_summary['errors'])} errors during cleanup.")

            return cleanup_summary

        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            print(error_msg)
            cleanup_summary["errors"].append(error_msg)
            return cleanup_summary


if __name__ == "__main__":
    unittest.main()