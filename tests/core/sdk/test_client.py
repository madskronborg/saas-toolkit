from typing import Any, Optional
import httpx

import pytest

from saas_toolkit.core import sdk


class TodoResponse(sdk.Response):
    userId: int
    id: int
    title: str
    completed: bool


class TodoItemExtension(sdk.AsyncClientExtension):
    @sdk.action()
    async def get(self, id: int) -> TodoResponse:
        response = await self.client.get(f"todos/{id}")
        return response


class TodoParams(sdk.Params):

    userId: Optional[int] = None


class TodoCreate(sdk.Request):

    userId: int
    title: str
    completed: bool


class TodoExtension(sdk.AsyncClientExtension):

    items: TodoItemExtension

    @sdk.action()
    async def get_all(self, params: Optional[TodoParams] = None) -> list[TodoResponse]:

        return await self.client.get("todos/", params=params)

    @sdk.action()
    async def get_all_as_dict(self) -> list[dict]:
        return await self.client.get("todos/")

    @sdk.action()
    async def get(self, id: int) -> TodoResponse:
        response = await self.client.get(f"todos/{id}")
        return response

    @sdk.action()
    async def get_as_dict(self, id: int) -> dict[str, Any]:
        response = await self.client.get(f"todos/{id}")
        return response

    @sdk.action(response=dict)
    async def get_with_decorated_response(self, id: int) -> TodoResponse:
        response = await self.client.get(f"todos/{id}")
        return response

    @sdk.action(responses={200: dict})
    async def get_with_decorated_responses(self, id: int) -> TodoResponse:
        response = await self.client.get(f"todos/{id}")
        return response

    @sdk.action()
    async def bad_request(
        self,
    ) -> dict:

        response = await self.client.get("idonotexist/")

        return response

    @sdk.action()
    async def create(
        self,
        data: TodoCreate,
    ) -> TodoResponse:

        response = await self.client.post("todos/", json=data)

        return response


class TodoClient(sdk.AsyncClient):

    todos: TodoExtension

    def __init__(
        self, *args, base_url="https://jsonplaceholder.typicode.com/", **kwargs
    ):

        super().__init__(*args, base_url=base_url, **kwargs)


async def test_client_construction():

    async with TodoClient() as client:
        extensions = client._get_extensions()

        assert [ext for ext in extensions.values()] == [
            client.todos.__class__
        ], "Extensions are not loaded"

        # Test level 1
        assert isinstance(client.todos, TodoExtension), "extension not set"

        assert client.todos.parent == client, "Extension does not have client as parent"

        assert client.todos.client == client, "Exntesion does not have client set"

        # Test level 2
        assert isinstance(
            client.todos.items, TodoItemExtension
        ), "Extensions are not nested correctly on other extensions"

        assert (
            client.todos.items.parent == client.todos
        ), "Nested extension parent not set"

        assert client.todos.client == client, "Nested extension client not set"


async def test_get():

    async with TodoClient() as client:

        # Get one (Pydantic)
        todo = await client.todos.get(1)

        assert isinstance(
            todo, TodoResponse
        ), "Response is not converted to Pydantic model"

        # Get one (Dict)
        todo_as_dict: dict[str, Any] = await client.todos.get_as_dict(1)

        assert isinstance(todo_as_dict, dict), "Dict return type not working"

        # Get list

        all_todos = await client.todos.get_all()

        assert isinstance(
            all_todos, list
        ), "Response is not converted to list of models"

        assert isinstance(
            all_todos[0], TodoResponse
        ), "Response list's items are not of correct type"

        # Get list with params
        filtered_todos = await client.todos.get_all(params={"userId": 1})

        assert len(filtered_todos) == 20, "Get with params not working"

        assert isinstance(
            filtered_todos[0], TodoResponse
        ), "Get with params returns wrong type"

        # Get list with list[dict] return type
        all_todos_as_dicts = await client.todos.get_all_as_dict()

        assert isinstance(
            all_todos_as_dicts, list
        ), "Return type of list[dict] does not return a list"
        assert isinstance(
            all_todos_as_dicts[0], dict
        ), "Return type of list[dict] items are not dicts"

        # Get with decorated response
        decorated_response = await client.todos.get_with_decorated_response(1)

        assert isinstance(
            decorated_response, dict
        ), "response type in decorator is not used"

        # Get with decoreated responses
        decorated_responses = await client.todos.get_with_decorated_responses(1)

        assert isinstance(
            decorated_responses, dict
        ), "responses type dictionary is not used"

        # Make bad request
        with pytest.raises(httpx.HTTPStatusError) as exc:

            # Test without debug
            await client.todos.bad_request()

            # Test with debug
            await client.todos.bad_request(debug=True)


async def test_post():

    async with TodoClient() as client:

        # Create with dict
        todo_with_dict = await client.todos.create(
            {"userId": 1, "title": "Some title", "completed": False}
        )

        assert isinstance(
            todo_with_dict, TodoResponse
        ), "Create does not return correct type"

        assert todo_with_dict.userId == 1, "Error in created data"
        assert todo_with_dict.title == "Some title", "Error in created data"
        assert todo_with_dict.completed == False, "Error with created data"
