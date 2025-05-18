import time
from typing import Dict, Any, List

import requests

BASE_URL = "https://api.thecatapi.com/v1"
DEFAULT_DELAY = 0.3  # Default delay between API calls to avoid rate limiting


class CatApiClient:
    """Client for interacting with The Cat API"""


    def __init__(self, api_key: str):
        """
        Initialize the Cat API client

        Args:
            api_key: The API key for authentication
        """
        self.base_url = BASE_URL
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    def find_random_image(self) -> Dict[str, Any]:
        """
        Find a random cat image from the API

        Returns:
            Dict containing image data with 'id' and 'url' keys
        """
        print("Finding a random cat image...")
        search_params = {"limit": 1, "size": "small"}

        response = requests.get(
            f"{self.base_url}/images/search",
            params=search_params,
            headers=self.headers
        )

        assert response.status_code == 200, f"Failed to search for images: {response.text}"

        image_data = response.json()[0]
        print(f"Found cat image with ID: {image_data['id']}")

        return image_data

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

        assert response.status_code in [200, 201], \
            f"Failed to add vote: {response.status_code}, {response.text}"

        vote_result = response.json()
        time.sleep(DEFAULT_DELAY)  # Small delay to avoid rate limiting

        return vote_result

    def get_votes_for_image(self, image_id: str) -> List[Dict[str, Any]]:
        """
        Get all votes for a specific image

        Args:
            image_id: ID of the image to get votes for

        Returns:
            List of vote dictionaries
        """
        response = requests.get(
            f"{self.base_url}/votes",
            params={"image_id": image_id},
            headers=self.headers
        )

        assert response.status_code == 200, f"Failed to get votes: {response.text}"

        votes = response.json()
        return [v for v in votes if v["image_id"] == image_id]

    def delete_vote(self, vote_id: str) -> bool:
        """
        Delete a vote by ID

        Args:
            vote_id: ID of the vote to delete

        Returns:
            bool: True if deletion was successful
        """
        print(f"Deleting vote with ID: {vote_id}")

        response = requests.delete(
            f"{self.base_url}/votes/{vote_id}",
            headers=self.headers
        )

        success = response.status_code in [200, 204]
        time.sleep(DEFAULT_DELAY)  # Small delay to avoid rate limiting

        return success

    def delete_favorite(self, favorite_id: str) -> bool:
        """
        Delete a favorite by ID

        Args:
            favorite_id: ID of the favorite to delete

        Returns:
            bool: True if deletion was successful
        """
        print(f"Deleting favorite with ID: {favorite_id}")

        response = requests.delete(
            f"{self.base_url}/favourites/{favorite_id}",
            headers=self.headers
        )

        success = response.status_code in [200, 204]
        time.sleep(DEFAULT_DELAY)  # Small delay to avoid rate limiting

        return success

    def get_favorites_for_image(self, image_id: str) -> List[Dict[str, Any]]:
        """
        Get all favorites for a specific image

        Args:
            image_id: ID of the image to get favorites for

        Returns:
            List of favorite dictionaries
        """
        response = requests.get(
            f"{self.base_url}/favourites",
            params={"image_id": image_id},
            headers=self.headers
        )

        if response.status_code == 200:
            return response.json()
        return []
