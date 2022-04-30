from typing import Generic, List, Literal, TypeVar

from pydantic import BaseModel, Field, root_validator, validator
from pydantic.generics import GenericModel

from kitman.core import dynamic

TTemplateVariable = TypeVar("TTemplateVariable", bound="BaseTemplateVariable")
TTemplateItem = TypeVar("TTemplateItem", bound="BaseTemplateItem")
TTemplate = TypeVar("TTemplate", bound="BaseTemplate")
TTemplateGroup = TypeVar("TTemplateGroup", bound="BaseTemplateGroup")
TTemplateStructureItem = TypeVar(
    "TTemplateStructureItem", bound="BaseTemplateStructureItem"
)
TTemplateStructure = TypeVar("TTemplateStructure", bound="BaseTemplateStructure")
TTemplateBuild = TypeVar("TTemplateBuild", bound="BaseTemplateBuild")
TTemplateBuildData = TypeVar("TTemplateBuildData", bound=list)

# Simple types for self-reference


class BaseTemplateVariable(BaseModel):

    name: str | int
    value: str | int | None = None
    required: bool = False
    depends_on: set[str] | None = None
    template: str | int | None = None
    group: str | int | None = None

    @validator("depends_on", pre=True)
    def validate_depends_on(cls, value: set[str] | None, values: dict, **kwargs):

        depends_on = set()

        variable_value = values.get("value", None)

        if variable_value:

            if isinstance(variable_value, str):
                placeholders = dynamic.get_placeholders_from_str(variable_value)

                if placeholders:
                    for placeholder in placeholders:
                        depends_on.add(placeholder)

        return depends_on


class BaseTemplateItem(GenericModel, Generic[TTemplate]):

    name: str | int | None = None
    value: dict
    depends_on: set[str] | None = None
    template: str | int | None = None

    @validator("depends_on", pre=True)
    def validate_depends_on(cls, value: set[str] | None, values: dict, **kwargs):

        depends_on = set()

        item_value = values["value"]

        if item_value:
            for key, val in item_value:

                if isinstance(key, str):
                    key_placeholders = dynamic.get_placeholders_from_str(key)

                    for key_placeholder in key_placeholders:
                        depends_on.add(key_placeholder)

                if isinstance(val, str):
                    val_placeholders = dynamic.get_placeholders_from_str(val)

                    for val_placeholder in val_placeholders:
                        depends_on.add(val_placeholder)

        return depends_on


class BaseTemplate(GenericModel, Generic[TTemplate, TTemplateItem, TTemplateVariable]):

    name: str | int
    category: str = "default"
    items: list[TTemplateItem] = []
    variables: list[TTemplateVariable] = []
    unique_keys: set[str] | None = Field(
        None,
        description="A list of keys from the items' value dictionary that should be unique in the final build.",
    )
    children: List[TTemplate] | None = None

    # Internal context variables
    group: str | int | None = None
    extends: TTemplate | None = None

    @validator("variables", "items", each_item=True)
    def add_template_to_variables_and_items(
        cls, v: TTemplateItem | TTemplateVariable, values: dict
    ):

        name = values.get("name", None)

        v.template = name

        return v


class BaseTemplateGroup(
    GenericModel, Generic[TTemplateGroup, TTemplate, TTemplateVariable]
):

    name: str | int
    templates: list[TTemplate]
    variables: list[TTemplateVariable] = []
    children: List[TTemplateGroup] = []

    # Internal context variables
    extends: TTemplateGroup | None = None

    @validator("templates", each_item=True)
    def add_group_to_templates(cls, v: TTemplate, values: dict):

        name = values.get("name", None)

        v.group = name

        return v


class BaseTemplateStructure(
    GenericModel, Generic[TTemplate, TTemplateItem, TTemplateVariable]
):
    """
    TemplateStructure

    The first item in each list is of lowest importance and can be overwritten by items later on in the list.
    """

    templates: list[TTemplate]
    items: list[TTemplateItem]
    variables: list[TTemplateVariable]


class BaseTemplateBuild(Generic[TTemplateBuildData, TTemplateStructure]):

    data: TTemplateBuildData
    structure: TTemplateStructure

    def inspect(self) -> dict:
        """
        inspect

        Inspect build.

        Discover which templates, variables etc. resulted in creating which parts of the build result.

        Returns:
            dict: _description_
        """
        pass

    def merge(self, other: TTemplateBuildData) -> TTemplateBuildData:

        pass

    def get_difference(self, other: TTemplateBuildData) -> dict:
        pass
