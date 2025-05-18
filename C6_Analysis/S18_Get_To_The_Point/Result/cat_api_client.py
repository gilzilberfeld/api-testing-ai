import time
from typing import Dict, Any, Optional, List

import requests

BASE_URL = "https://api.thecatapi.com/v1"
DEFAULT_DELAY = 0.5  # Delay between API calls to avoid rate limiting

class CatApiClient:
    """Wrapper client for interacting with The Cat API"""

    def __init__(self, api_key: str, base_url: str = BASE_URL):
        """
        Initialize the Cat API client
        Args:
            api_key: Your Cat API key
            base_url: The base URL for the Cat API (default: API v1 endpoint)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def find_random_image(self, limit: int = 1) -> Dict[str, Any]:
        """
        Find a random cat image
        Args:
            limit: Number of images to retrieve (default: 1)
        Returns:
            Dict containing image data including 'id' and 'url' keys
        """
        print("Fetching random cat image...")
        params = {
            "limit": limit,
            "size": "small"  # Use small images to reduce data usage
        }
        response = requests.get(
            f"{self.base_url}/images/search",
            params=params,
            headers=self.headers
        )
        assert response.status_code == 200, \
            f"Failed to get images: {response.status_code}, {response.text}"
        images = response.json()
        assert len(images) > 0, "No images found"
        time.sleep(DEFAULT_DELAY)  # Small delay to avoid rate limiting
        return images[0]

    def add_vote(self, image_id: str, sub_id: str, value: int = 1) -> Dict[str, Any]:
        """
        Add a vote for an image
        Args:
            image_id: ID of the image to vote for
            sub_id: ID of the voter (user)
            value: Vote value (1 for up, 0 for down)
        Returns:
            Dict containing vote data including 'id' key
        """
        print(f"Adding vote from sub_id: {sub_id} for image: {image_id}")
        vote_data = {
            "image_id": image_id,
            "value": value,
            "sub_id": sub_id
        }
        response = requests.post(
            f"{self.base_url}/votes",
            json=vote_data,
            headers=self.headers
        )

        # Verify status code
        assert response.status_code in [200, 201], \
            f"Failed to add vote: {response.status_code}, {response.text}"

        # Verify response is valid JSON
        try:
            vote_result = response.json()
        except ValueError:
            assert False, f"Response is not valid JSON: {response.text}"

        # Verify response has the required fields
        assert "id" in vote_result, f"Response missing 'id' field: {vote_result}"

        time.sleep(DEFAULT_DELAY)  # Small delay to avoid rate limiting
        return vote_result

    def get_votes(self, sub_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all votes, optionally filtered by sub_id
        Args:
            sub_id: Optional ID of the voter to filter by
        Returns:
            List of vote data dictionaries
        """
        params = {}
        if sub_id:
            params["sub_id"] = sub_id

        response = requests.get(
            f"{self.base_url}/votes",
            params=params,
            headers=self.headers
        )
        assert response.status_code == 200, \
            f"Failed to get votes: {response.status_code}, {response.text}"
        votes = response.json()
        time.sleep(DEFAULT_DELAY)  # Small delay to avoid rate limiting
        return votes

    def get_votes_for_image(self, image_id: str) -> List[Dict[str, Any]]:
        """
        Get all votes for a specific image
        Args:
            image_id: ID of the image to get votes for
        Returns:
            List of vote data dictionaries
        """
        print(f"Getting votes for image: {image_id}")
        all_votes = self.get_votes()
        image_votes = [vote for vote in all_votes if vote.get("image_id") == image_id]
        return image_votes

    def delete_vote(self, vote_id: int) -> bool:
        """
        Delete a vote by ID
        Args:
            vote_id: ID of the vote to delete
        Returns:
            True if deletion was successful
        """
        print(f"Deleting vote: {vote_id}")
        response = requests.delete(
            f"{self.base_url}/votes/{vote_id}",
            headers=self.headers
        )
        success = response.status_code == 200
        if not success:
            print(f"Warning: Failed to delete vote {vote_id}: {response.status_code}, {response.text}")
        time.sleep(DEFAULT_DELAY)  # Small delay to avoid rate limiting
        return success

    def delete_all_votes(self) -> int:
        """
        Delete all votes created by this client
        Returns:
            Number of votes deleted
        """
        print("Deleting all votes...")
        votes = self.get_votes()
        deleted_count = 0

        for vote in votes:
            vote_id = vote.get("id")
            if vote_id and self.delete_vote(vote_id):
                deleted_count += 1

        print(f"Deleted {deleted_count} votes")
        return deleted_count
