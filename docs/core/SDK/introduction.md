# Introduction

The SDK module makes it easier than ever to create expressive and easy-to-use clients with complete type support. <br>
Everything from data and query to responses can be automatically validated based on standard types or custom `Pydantic` models.

It also manages interoperability between `HTTPX` (Our client) and `Pydantic` (Our data validator), in the following ways:

- Inspects return type on your client methods and transforms HTTP response into the format (or a validation error is raised)
- Inspects arguments and kwargs of your method(s) and validates user input before even calling the method. Can be any type or a Pydantic model
- Automatically converts Pydantic models into dictionaries when calling `HTTPX` http methods like `get` or `post`

Of course, you can handle all of this manually if you wish to.

When building an SDK, there are _4_ major topics to consider:

- Client -> The client manages global information about the SDK e.g. `base_url` for the server and `authentication` if working with a protected api.
- Client extensions -> Client extensions implements logic for specific endpoint groups.
- Request data and query params -> Validates request data/body and query params used before sending the request.
- Responses -> Custom error handling for specific status_codes + support for validating and optionally transforming response data into Pydantic models.
