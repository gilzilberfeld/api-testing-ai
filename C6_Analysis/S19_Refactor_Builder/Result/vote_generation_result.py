import json
import time
from typing import Dict, Any, Optional


class VoteGenerationResult:
    """Class to store and manage the results of vote generation"""

    def __init__(self):
        self.total_votes = 0
        self.images = []
        self.votes = []
        self.errors = []
        self.start_time = time.time()
        self.end_time = None

    def add_image(self, image_data: Dict[str, Any]) -> None:
        """Add an image to the results"""
        self.images.append({
            "id": image_data["id"],
            "url": image_data.get("url", "unknown")
        })

    def add_vote(self, vote_data: Dict[str, Any]) -> None:
        """Add a vote to the results"""
        self.votes.append(vote_data)
        self.total_votes += 1

    def add_error(self, error_message: str) -> None:
        """Add an error to the results"""
        self.errors.append({
            "timestamp": time.time(),
            "message": error_message
        })

    def update_image_vote_count(self, image_id: str, vote_count: int) -> None:
        """Update the verified vote count for an image"""
        for img in self.images:
            if img["id"] == image_id:
                img["verified_vote_count"] = vote_count
                break

    def finalize(self) -> None:
        """Mark the generation as complete"""
        self.end_time = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the results to a dictionary"""
        return {
            "total_votes": self.total_votes,
            "images": self.images,
            "votes": self.votes,
            "errors": self.errors,
            "duration_seconds": round(self.end_time - self.start_time, 2) if self.end_time else None,
            "timestamp": int(self.start_time)
        }

    def save_to_file(self, filename: Optional[str] = None) -> str:
        """Save the results to a JSON file"""
        if not filename:
            filename = f"catapi_votes_{int(self.start_time)}.json"

        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        return filename
