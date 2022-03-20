# Example

We need to build a SDK for our Todo API.

Firstly, let's look a implementing a way to retrieve and list our current todos and validate + transform responses into our custom Pydantic models.

```py
# Import in all files
from saas_toolkit.core import sdk

# In responses.py
class TodoItemResponse(sdk.Response):

    id: int
    title: str
    text: str

class TodoResponse(sdk.Response):
    id: int
    name: str
    items: list[TodoItemResponse]

# In requests.py

class TodoQuery(sdk.Query):

    created: datetime.datetime


# In client.py
from . import requests, responses

class TodoExtension(sdk.AsyncClientExtension):

    @sdk.action()
    async def get_all(self, params: requests.TodoQuery) -> list[responses.TodoResponse]:

        return self.client.get("todos/", params = query.dict())



class TodoClient(sdk.AsyncClient):

    base_url = "https://my-todos.com/"

    todos: TodoExtension

# We can now run
async with TodoClient() as client:
    todos: list[TodoResponse] = await client.todos.get_all( params = {"created": "2022-02-07T08:00:00Z"}) # Query will be automatically converted to TodoQuery model



```

Let's extend it so we can create new Todo's.

```py

# In requests.py

class TodoCreate(sdk.Response):

    name: str



# In client.py

class TodoExtension(sdk.AsyncClientExtension):

    @sdk.action()
    async def get_all(self, params: requests.TodoQuery) -> list[responses.TodoResponse]:

        return self.client.get("todos/", params = query.dict())


    # TODO: Think in error handling here. Should we add error models? Error handling functions with defaults set in client/parent/extension?
    # TODO: With error models, return signature could be: TodoResponse | TodoErrorResponse

    @sdk_action(responses = {201: TodoResponse})
    async def create(self, data: TodoCreate) -> TodoResponse:

        return self.client.post("todos/", json = data.dict())


# We can now create todos

async with TodoClient() as client:
    new_todo: TodoResponse = await client.todos.create(data = {"name": "Todo Name"}) # Data is automatically validated and coverted to TodoCreate model

```
