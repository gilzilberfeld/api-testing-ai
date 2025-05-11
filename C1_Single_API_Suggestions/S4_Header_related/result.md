# Test Cases for Cat API Involving Non-Default Header Fields

## POST /images/upload Endpoint Cases

### Authentication Headers
- Upload with authentication token in Authorization header (Bearer token)
- Upload with API key in x-api-key header
- Testing various auth header formats (OAuth, Basic Auth if supported)

### Content-Related Headers
- Upload with specific Content-Type header (multipart/form-data)
- Upload with Content-Type header for specific image formats
- Upload with Content-Length header to specify file size
- Upload with Transfer-Encoding: chunked for large file uploads

### Custom/API-Specific Headers
- Testing with Accept header to specify preferred response format (application/json)
- Upload with x-sub-id header (if API supports custom headers for metadata)
- Upload with Cache-Control headers to control caching behavior
- Upload with If-None-Match or ETag headers for conditional requests

### Security-Related Headers
- Upload with CORS headers (Origin, Access-Control-Request-Method)
- Testing with Content-Security-Policy headers
- Upload with X-Forwarded-For or similar proxy headers

### Rate Limiting and Usage Headers
- Testing responses to X-RateLimit headers
- Upload with custom quota or usage tracking headers (if supported)

## Other API Endpoints with Non-Default Headers

### For Votes Endpoints
- Sending votes with Content-Type: application/json
- Using If-Modified-Since headers when retrieving votes
- Using Range headers to retrieve partial sets of votes
- Using Accept-Language headers if API supports localization

### General API Headers
- Testing with User-Agent variations
- Testing with Accept-Encoding for compression options
- Using Idempotency-Key headers for retrying operations safely (if supported)
- Using custom tracking headers like X-Request-ID

Many of these test cases will depend on what specific headers the Cat API actually supports beyond the standard Authorization and Content-Type headers. Without the specific API documentation, these represent common headers that might be relevant for testing a RESTful API with upload functionality.