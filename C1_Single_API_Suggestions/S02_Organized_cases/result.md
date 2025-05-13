# Test Cases for Cat API Votes Endpoints

## Valid Cases

### POST /votes (Create a vote)
- Submit a valid vote with all required fields
- Verify vote is properly associated with the specified image
- Verify vote value is correctly stored (up/down or numeric value)
- Verify successful vote creation returns appropriate vote ID

### GET /votes (Retrieve votes)
- Retrieve all votes for the authenticated user
- Verify pagination works correctly with different page sizes
- Verify votes are returned in expected order (likely chronological)
- Filter votes by image_id

### GET /votes/{vote_id} (Retrieve specific vote)
- Retrieve a specific vote by ID
- Verify all expected vote data is returned

### DELETE /votes/{vote_id} (Delete a vote)
- Delete own vote successfully
- Verify vote is removed from database
- Verify appropriate response code

### GET /images/{image_id}/votes (Get votes for specific image)
- Retrieve all votes for a specific image
- Test pagination for images with many votes
- Filter by vote value (positive/negative)

## Invalid Cases

### POST /votes (Create a vote)
- Submit vote with missing required fields
- Submit vote with invalid image_id
- Submit vote with invalid value (outside allowed range)
- Submit duplicate vote for same user/image combination
- Test rate limiting by submitting many votes quickly
- Test with very large or very small vote values (if numeric)

### GET /votes (Retrieve votes)
- Request with invalid pagination parameters
- Request with non-existent filter values
- Request very large page sizes

### GET /votes/{vote_id} (Retrieve specific vote)
- Request non-existent vote ID
- Request deleted vote ID (if applicable)

### DELETE /votes/{vote_id} (Delete a vote)
- Delete already deleted vote
- Delete non-existent vote
- Delete very old vote (if there are time restrictions)

### GET /images/{image_id}/votes (Get votes for specific image)
- Request votes for image with no votes
- Request votes for non-existent image
- Test with invalid filter parameters

## Authentication/Authorization Cases

### POST /votes (Create a vote)
- Submit vote without authentication token
- Submit vote with expired token
- Submit vote with invalid token
- Test permission levels (if applicable)

### GET /votes (Retrieve votes)
- Request votes without authentication
- Request votes for another user (should be denied or limited based on permissions)

### GET /votes/{vote_id} (Retrieve specific vote)
- Request someone else's vote (permission testing)
- Request with invalid authentication

### DELETE /votes/{vote_id} (Delete a vote)
- Delete vote without authentication
- Delete someone else's vote
- Delete with expired token

### GET /images/{image_id}/votes (Get votes for specific image)
- Test public vs. private image vote visibility
- Test with different user permission levels