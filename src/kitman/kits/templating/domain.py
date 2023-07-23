from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field, root_validator, validator

from kitman.core import dynamic

import orjson

TTemplateVariable = TypeVar("TTemplateVariable", bound="BaseTemplateVariable")
TTemplateItem = TypeVar("TTemplateItem", bound="BaseTemplateItem")
TTemplate = TypeVar("TTemplate", bound="BaseTemplate")
TTemplateGroup = TypeVar("TTemplateGroup", bound="BaseTemplateGroup")
TTemplateStructure = TypeVar("TTemplateStructure", bound="BaseTemplateStructure")
TTemplateBuild = TypeVar("TTemplateBuild", bound="BaseTemplateBuild")

# Simple types for self-reference


class BaseTemplateVariable(BaseModel):

    name: str | int
    description: str | None = None
    value: str | int | None = None
    required: bool = False
    depends_on: set[str] | None = None
    template: str | int | None = None
    group: str | int | None = None

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("depends_on", pre=True, always=True)
    def validate_depends_on(cls, v: set[str] | None, values: dict, **kwargs):

        depends_on = set()

        variable_value = values.get("value", None)

        if variable_value:

            if isinstance(variable_value, str):
                placeholders = dynamic.get_placeholders_from_str(variable_value)

                if placeholders:
                    for placeholder in placeholders:
                        depends_on.add(placeholder)

        return depends_on


class BaseTemplateItem(BaseModel, Generic[TTemplate]):

    name: str | int | None = None
    description: str | None = None
    value: dict
    depends_on: set[str] | None = None
    template: str | int | None = None

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("depends_on", pre=True, always=True)
    def validate_depends_on(cls, v: set[str] | None, values: dict, **kwargs):

        depends_on = set()

        item_value: dict = values["value"]

        if item_value:
            for key, val in item_value.items():

                if isinstance(key, str):
                    key_placeholders = dynamic.get_placeholders_from_str(key)

                    for key_placeholder in key_placeholders:
                        print("Key variable is:", key_placeholder)
                        depends_on.add(key_placeholder)

                if isinstance(val, str):
                    val_placeholders = dynamic.get_placeholders_from_str(val)

                    for val_placeholder in val_placeholders:
                        print("Value variable is:", val_placeholder)
                        depends_on.add(val_placeholder)

        return depends_on


class BaseTemplate(BaseModel, Generic[TTemplate, TTemplateItem, TTemplateVariable]):

    name: str | int
    description: str | None = None
    category: str = "default"
    items: list[TTemplateItem] = []
    variables: list[TTemplateVariable] = []
    unique_keys: set[str] | None = Field(
        None,
        description="A list of keys from the items' value dictionary that should be unique in the final build.",
    )
    children: list[TTemplate] | None = None

    # Internal context variables
    group: str | int | None = None
    extends: TTemplate | None = None

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("variables", "items", each_item=True)
    def add_template_to_variables_and_items(
        cls, v: TTemplateItem | TTemplateVariable, values: dict
    ):

        name = values.get("name", None)

        v.template = name

        return v


class BaseTemplateGroup(
    BaseModel, Generic[TTemplateGroup, TTemplate, TTemplateVariable]
):

    name: str | int
    description: str | None = None
    templates: list[TTemplate]
    variables: list[TTemplateVariable] = []
    children: list[TTemplateGroup] = []

    # Internal context variables
    extends: TTemplateGroup | None = None

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("templates", each_item=True)
    def add_group_to_templates(cls, v: TTemplate, values: dict):

        name = values.get("name", None)

        v.group = name

        return v


class BaseTemplateStructure(
    BaseModel, Generic[TTemplate, TTemplateItem, TTemplateVariable]
):
    """
    TemplateStructure

    The first item in each list is of lowest importance and can be overwritten by items later on in the list.
    """

    templates: list[TTemplate]
    items: list[TTemplateItem]
    variables: list[TTemplateVariable]


class BaseTemplateBuild(Generic[TTemplateItem, TTemplateStructure]):

    data: list[TTemplateItem]
    structure: TTemplateStructure

    def __init__(self, data: list[TTemplateItem], structure: TTemplateStructure):

        self.data = data
        self.structure = structure

    def json(self, *args, **kwargs) -> str:

        prepared_data = self.dict(*args, **kwargs)

        return orjson.dumps(prepared_data).decode()

    def dict(self, *args, **kwargs) -> list[dict]:

        prepared_data: list[dict] = []

        for item in self.data:
            prepared_data.append(item.dict(*args, **kwargs))

        return prepared_data

    def inspect(self) -> dict:
        """
        inspect

        Inspect build.

        Discover which templates, variables etc. resulted in creating which parts of the build result.

        Returns:
            dict: _description_
        """
        pass

    def merge(self, other: list[TTemplateItem]) -> list[TTemplateItem]:

        pass

    def get_difference(self, other: list[TTemplateItem]) -> dict:
        pass
