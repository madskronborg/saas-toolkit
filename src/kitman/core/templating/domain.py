from typing import Generic, List, Literal, TypeVar

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

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
    template: str | int | None = None
    group: str | int | None = None


class BaseTemplateItem(GenericModel, Generic[TTemplate]):

    name: str | int | None = None
    value: dict
    template: str | int | None = None


class BaseTemplate(GenericModel, Generic[TTemplate, TTemplateItem, TTemplateVariable]):

    name: str | int = None
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

    name: str | int = None
    templates: list[TTemplate]
    variables: list[TTemplateVariable] = []
    children: List[TTemplateGroup] | None = None

    # Internal context variables
    extends: TTemplateGroup | None = None

    @validator("templates", each_item=True)
    def add_group_to_templates(cls, v: TTemplate, values: dict):

        name = values.get("name", None)

        v.group = name

        return v


class BaseTemplateStructureItem(
    GenericModel, Generic[TTemplate, TTemplateItem, TTemplateVariable]
):

    data: TTemplate | TTemplateItem | TTemplateVariable
    added_by_name: str | int
    added_by_type: Literal["user"] | Literal["group"] | Literal["template"]


class BaseTemplateStructure(GenericModel, Generic[TTemplateStructureItem]):
    """
    TemplateStructure

    The first item in each list is of lowest importance and can be overwritten by items later on in the list.
    """

    templates: list[TTemplateStructureItem]
    items: list[TTemplateStructureItem]
    variables: list[TTemplateStructureItem]


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
