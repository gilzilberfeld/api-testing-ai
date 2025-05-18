Title: Vote count not incrementing properly when voting for images via CatAPI

Priority: High
Component: CatAPI Voting System
Affects Version: Current API Version
Environment: Test Environment

Description:
When voting for an image using the CatAPI, the vote count does not increase as expected. This issue was detected by our automated test suite (specifically test_vote_count_increases).

Steps to Reproduce:
1. Set up an image that already has 3 votes
2. Cast a new vote for this image
3. Retrieve the vote count for the image
4. Verify that the vote count has increased by 1

Expected Result:
The vote count should increase from 3 to 4 after casting a new vote.

Actual Result:
The vote count remains at 3 or returns an incorrect value after the new vote is cast.

Additional Information:
- Test was executed using the CatApiClient wrapper
- Test environment details: [Environment Information]
- API calls made: 
  * POST to /v1/votes with image_id
  * GET to /v1/votes to retrieve count
  
Impact:
This issue affects the core voting functionality of the application. Users' votes may not be properly counted, which impacts engagement metrics and feature reliability.

Possible Causes:
1. Vote is not being properly saved in the database
2. Vote count calculation logic is incorrect
3. Race condition in the voting process
4. Caching issue where new votes aren't reflected immediately

Attached:
- Test execution logs
- API response details