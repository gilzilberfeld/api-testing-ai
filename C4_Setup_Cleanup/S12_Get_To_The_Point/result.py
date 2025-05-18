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


if __name__ == "__main__":
    try:
        # Run the setup function
        test_data = setup_cat_image_with_three_votes()
        print(f"Successfully set up test scenario with image ID: {test_data['image_id']}")
        print(f"This image now has 3 votes from different users.")

        # You can use test_data for further testing
        # For example:
        # image_id = test_data["image_id"]
        # - Test getting votes for this image
        # - Test adding more votes
        # - Test adding/removing from favorites
        # etc.

    except Exception as e:
        print(f"Error setting up test: {str(e)}")