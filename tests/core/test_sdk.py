from saas_toolkit.core import sdk


class TodoResponse(sdk.Response):
    userId: int
    id: int
    title: str
    completed: bool


class TodoItemExtension(sdk.AsyncClientExtension):
    async def get_todo_item(self, id: int) -> TodoResponse:
        response = await self.client.get(f"todos/{id}")
        return TodoResponse(**response.json())


class TodoExtension(sdk.AsyncClientExtension):

    items: TodoItemExtension

    async def get_todo(self, id: int) -> TodoResponse:
        response = await self.client.get(f"todos/{id}")
        return TodoResponse(**response.json())


class MyClient(sdk.AsyncClient):

    base_url = "https://jsonplaceholder.typicode.com/todos/1"

    todos: TodoExtension


def test_client_construction():

    client = MyClient()

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

    assert client.todos.items.parent == client.todos, "Nested extension parent not set"

    assert client.todos.client == client, "Nested extension client not set"
