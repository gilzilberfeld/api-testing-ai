# 1. Create a new vote (upvote a cat image)
POST https://api.thecatapi.com/v1/votes
Headers:
  x-api-key: YOUR_API_KEY
  Content-Type: application/json
Body:
{
  "image_id": "9ccXTANkb",
  "value": 1,
  "sub_id": "user-123"
}

# 2. Get all votes from your account
GET https://api.thecatapi.com/v1/votes
Headers:
  x-api-key: YOUR_API_KEY

# 3. Get a specific vote by ID (using the ID returned from the create operation)
GET https://api.thecatapi.com/v1/votes/{vote_id}
Headers:
  x-api-key: YOUR_API_KEY

# 4. Create another vote (downvote a different cat image)
POST https://api.thecatapi.com/v1/votes
Headers:
  x-api-key: YOUR_API_KEY
  Content-Type: application/json
Body:
{
  "image_id": "MTYzNjA5OQ",
  "value": -1,
  "sub_id": "user-123"
}

# 5. Get votes filtered by sub_id
GET https://api.thecatapi.com/v1/votes?sub_id=user-123
Headers:
  x-api-key: YOUR_API_KEY

# 6. Delete a vote by ID
DELETE https://api.thecatapi.com/v1/votes/{vote_id}
Headers:
  x-api-key: YOUR_API_KEY

# 7. Verify deletion by trying to get the deleted vote
GET https://api.thecatapi.com/v1/votes/{vote_id}
Headers:
  x-api-key: YOUR_API_KEY

# 8. Create votes with different sub_ids to test filtering
POST https://api.thecatapi.com/v1/votes
Headers:
  x-api-key: YOUR_API_KEY
  Content-Type: application/json
Body:
{
  "image_id": "bo5BqUB5X",
  "value": 1,
  "sub_id": "user-456"
}

# 9. Get votes with pagination parameters
GET https://api.thecatapi.com/v1/votes?limit=5&page=0
Headers:
  x-api-key: YOUR_API_KEY

# 10. Get votes with combined filtering (sub_id and pagination)
GET https://api.thecatapi.com/v1/votes?sub_id=user-123&limit=10
Headers:
  x-api-key: YOUR_API_KEY