import requests
import time


def setup_cat_image_with_three_votes():
    """
    Sets up a test scenario with a cat image that has received 3 votes.

    This function:
    1. Uploads a cat image to The Cat API
    2. Casts 3 votes for the image from different sub_ids
    3. Returns the image_id and other relevant information

    Returns:
        dict: A dictionary containing test data including the image_id and vote information
    """
    # API configuration
    BASE_URL = "https://api.thecatapi.com/v1"
    # You should replace this with your actual API key
    API_KEY = "your_cat_api_key_here"

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    test_data = {}

    # Step 1: Upload a cat image to the API
    # For this example, we'll use the search API to find an existing image
    # rather than uploading a new one, as uploading requires multipart/form-data

    print("Searching for a cat image...")
    search_params = {
        "limit": 1,
        "size": "small"  # Getting small image for simplicity
    }

    response = requests.get(f"{BASE_URL}/images/search", params=search_params, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to search for images: {response.status_code}, {response.text}")

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

        vote_response = requests.post(f"{BASE_URL}/votes", json=vote_data, headers=headers)

        if vote_response.status_code not in [200, 201]:
            raise Exception(f"Failed to cast vote: {vote_response.status_code}, {vote_response.text}")

        vote_result = vote_response.json()
        test_data["votes"].append(vote_result)

        # Adding a small delay between API calls to avoid rate limiting
        time.sleep(0.5)

    # Step 3: Verify the votes were recorded by getting the votes for this image
    print("Verifying votes...")
    votes_response = requests.get(f"{BASE_URL}/votes", params={"image_id": image_id}, headers=headers)

    if votes_response.status_code != 200:
        raise Exception(f"Failed to get votes: {votes_response.status_code}, {votes_response.text}")

    votes_data = votes_response.json()
    test_data["votes_verification"] = votes_data

    # Check if we have 3 votes for this image
    image_votes = [v for v in votes_data if v["image_id"] == image_id]
    print(f"Found {len(image_votes)} votes for image {image_id}")

    if len(image_votes) < 3:
        print("Warning: Not all votes may have been recorded. Check the API response.")

    print("Setup complete!")
    return test_data


def cleanup_test_data(test_data=None, cleanup_all=False):
    """
    Cleans up test data by removing votes, favorites, and uploaded images.

    Args:
        test_data (dict, optional): The test data returned by setup_cat_image_with_three_votes().
                                   If None and cleanup_all is True, will attempt to clean all user data.
        cleanup_all (bool, optional): If True, will attempt to clean all user data regardless of test_data.
                                     Default is False.

    Returns:
        dict: A summary of cleanup operations performed
    """
    # API configuration
    BASE_URL = "https://api.thecatapi.com/v1"
    # You should replace this with your actual API key
    API_KEY = "your_cat_api_key_here"

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

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
            votes_response = requests.get(f"{BASE_URL}/votes", headers=headers)
        elif test_data and "image_id" in test_data:
            votes_response = requests.get(
                f"{BASE_URL}/votes",
                params={"image_id": test_data["image_id"]},
                headers=headers
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
                    delete_response = requests.delete(f"{BASE_URL}/votes/{vote_id}", headers=headers)

                    if delete_response.status_code in [200, 204]:
                        cleanup_summary["votes_removed"] += 1
                    else:
                        error_msg = f"Failed to delete vote {vote_id}: {delete_response.status_code}"
                        print(error_msg)
                        cleanup_summary["errors"].append(error_msg)

                    # Adding a small delay between API calls to avoid rate limiting
                    time.sleep(0.5)

        # Step 2: Clean up favorites (if applicable)
        print("Cleaning up favorites...")

        # Get all favorites if cleanup_all is True, otherwise skip if no test_data
        if cleanup_all or (test_data and "image_id" in test_data):
            favorites_params = {}
            if test_data and "image_id" in test_data:
                favorites_params["image_id"] = test_data["image_id"]

            favorites_response = requests.get(f"{BASE_URL}/favourites", params=favorites_params, headers=headers)

            if favorites_response.status_code == 200:
                favorites = favorites_response.json()

                for favorite in favorites:
                    favorite_id = favorite.get("id")
                    if favorite_id:
                        print(f"Deleting favorite with ID: {favorite_id}")
                        delete_response = requests.delete(f"{BASE_URL}/favourites/{favorite_id}", headers=headers)

                        if delete_response.status_code in [200, 204]:
                            cleanup_summary["favorites_removed"] += 1
                        else:
                            error_msg = f"Failed to delete favorite {favorite_id}: {delete_response.status_code}"
                            print(error_msg)
                            cleanup_summary["errors"].append(error_msg)

                        # Adding a small delay between API calls to avoid rate limiting
                        time.sleep(0.5)

        # Step 3: Clean up uploaded images (if applicable)
        # Note: This only works for images that were uploaded by the user, not for images from the search endpoint
        print("Cleaning up uploaded images...")

        images_response = requests.get(f"{BASE_URL}/images", headers=headers)

        if images_response.status_code == 200:
            images = images_response.json()

            for image in images:
                image_id = image.get("id")
                if image_id:
                    print(f"Deleting image with ID: {image_id}")
                    delete_response = requests.delete(f"{BASE_URL}/images/{image_id}", headers=headers)

                    if delete_response.status_code in [200, 204]:
                        cleanup_summary["images_removed"] += 1
                    else:
                        error_msg = f"Failed to delete image {image_id}: {delete_response.status_code}"
                        print(error_msg)
                        cleanup_summary["errors"].append(error_msg)

                    # Adding a small delay between API calls to avoid rate limiting
                    time.sleep(0.5)

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
    try:
        # Run the setup function
        test_data = setup_cat_image_with_three_votes()
        print(f"Successfully set up test scenario with image ID: {test_data['image_id']}")
        print(f"This image now has 3 votes from different users.")

        # Example of using the test data for additional tests
        # ... perform your tests here ...

        # Clean up after tests
        print("\nCleaning up test data...")
        cleanup_summary = cleanup_test_data(test_data)
        print(f"Cleanup summary: {cleanup_summary}")

    except Exception as e:
        print(f"Error during test: {str(e)}")