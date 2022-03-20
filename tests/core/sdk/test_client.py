from typing import Optional
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

    limit: int = 100
    offset: int = 0


class TodoExtension(sdk.AsyncClientExtension):

    items: TodoItemExtension

    @sdk.action()
    async def get_all(self, params: Optional[TodoParams] = None) -> list[TodoResponse]:

        return await self.client.get("todos/")

    @sdk.action()
    async def get(self, id: int) -> TodoResponse:
        response = await self.client.get(f"todos/{id}")
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


async def test_action():

    async with TodoClient() as client:

        todo = await client.todos.get(1)

        assert isinstance(
            todo, TodoResponse
        ), "Response is not converted to Pydantic model"

        todos = await client.todos.get_all()

        assert isinstance(todos, list), "Response is not converted to list of models"

        assert isinstance(
            todos[0], TodoResponse
        ), "Response list's items are not of correct type"
