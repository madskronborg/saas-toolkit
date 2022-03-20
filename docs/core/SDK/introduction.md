# Introduction

The SDK module makes it easier than ever to create expressive and easy-to-use clients with complete type support. <br>
Everything from data and query to responses can be automatically validated based on standard types or custom `Pydantic` models.

When building an SDK, there are _4_ major topics to consider:

- Client -> The client manages global information about the SDK e.g. `base_url` for the server and `authentication` if working with a protected api.
- Client extensions -> Client extensions implements logic for specific endpoint groups.
- Request data and query params -> Validates request data/body and query params used before sending the request.
- Responses -> Custom error handling for specific status_codes + support for validating and optionally transforming response data into Pydantic models.
