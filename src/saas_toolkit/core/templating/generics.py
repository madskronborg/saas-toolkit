from typing import Any, Generic, TypeVar, overload
from typing_extensions import Self
from pydantic import BaseModel, Field, parse_obj_as, validator
from pydantic.generics import GenericModel
from operator import itemgetter

TTemplateVariable = TypeVar("TTemplateVariable", bound="BaseTemplateVariable")
TTemplateItem = TypeVar("TTemplateItem", bound="BaseTemplateItem")
TTemplate = TypeVar("TTemplate", bound="BaseTemplate")
TTemplateGroup = TypeVar("TTemplateGroup", bound="BaseTemplateGroup")
TTemplateStructure = TypeVar("TTemplateStructure", bound="BaseTemplateStructure")
TTemplateBuild = TypeVar("TTemplateBuild", bound=list[dict])


class BaseTemplateVariable(BaseModel):

    name: str
    value: str | int | None = None
    required: bool = False
    template: TTemplate | None = None
    group: TTemplateGroup | None = None


class BaseTemplateItem(GenericModel, Generic[TTemplate]):

    name: str | int | None = None
    value: dict
    template: TTemplate | None = None


class BaseTemplate(
    GenericModel, Generic[TTemplateGroup, TTemplate, TTemplateItem, TTemplateVariable]
):

    name: str | int | None = None
    category: str = "default"
    items: list[TTemplateItem]
    variables: list[TTemplateVariable] = []
    group: TTemplateGroup | None = None

    extends: TTemplate | None = None

    unique_keys: set[str] | None = Field(
        None,
        description="A list of keys from the items' value dictionary that should be unique in the final build.",
    )


class BaseTemplateGroup(
    GenericModel, Generic[TTemplateGroup, TTemplate, TTemplateVariable]
):

    name: str | int | None = None
    templates: list[TTemplate]
    variables: list[TTemplateVariable] = []

    extends: TTemplateGroup | None = None


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


class BaseTemplateBuild(Generic[TTemplateBuild]):

    data: TTemplateBuild

    def inspect(self) -> dict:
        """
        inspect

        Inspect build.

        Discover which templates, variables etc. resulted in creating which parts of the build result.

        Returns:
            dict: _description_
        """


class BaseTemplateBuilder(
    Generic[
        TTemplateGroup,
        TTemplate,
        TTemplateItem,
        TTemplateVariable,
        TTemplateStructure,
        TTemplateBuild,
    ]
):
    class Config:
        template_structure_model: TTemplateStructure
        template_build_model: TTemplateBuild

    _group: TTemplateGroup | None = None
    _user_templates: dict[str, TTemplate] = {}
    _user_variables: dict[str, TTemplateVariable] = {}

    # Private
    def _get_children(
        self, obj: TTemplateGroup | TTemplate
    ) -> list[TTemplateGroup | TTemplate]:

        children: list[TTemplateGroup | TTemplate] = []

        subject = obj

        # Get children
        while subject.extends is not None:
            children.append(subject)
            subject = subject.extends

        return children.reverse()

    def _get_item_index(
        self,
        items: list[TTemplateItem],
        item: TTemplateItem,
        search_keys: set[str] = [],
    ) -> int | None:

        search_params = {}

        for search_key in search_keys:
            search_params[search_key] = item.value[search_key]

        index: int | None = next(
            (
                index
                for index, item in enumerate(items)
                if item.dict(include={"value": search_keys}) == search_params
            ),
            None,
        )

        if index and index >= 0:
            return index

        return None

    def _get_structure(self) -> TTemplateStructure:

        groups = self._get_children(self._group) if self._group else []

        templates: dict[str, TTemplate] = {}

        items: list[TTemplateItem] = []

        variables: dict[str, TTemplateVariable] = {}

        for group in groups:

            for group_template in group.templates:

                group_templates = self._get_children(group_template)

                for template in group_templates:

                    template.group = group

                    templates[template.name] = template

                    unique_keys = template.unique_keys

                    for item in template.items:
                        item_index: int | None = None

                        if unique_keys:
                            # Check if items is already added - if it is, we have to replace it
                            item_index = self._get_item_index(items, item, unique_keys)

                        if item_index:
                            items[item_index] = item
                        else:
                            items.append(item)

                    for variable in template.variables:
                        variable.template = template

                        variables[variable.name] = variable

            for group_variable in group.variables:
                group_variable.group = group
                variables[group_variable.name] = group_variable

        for user_variable in self._user_variables.values():
            variables[user_variable.name] = user_variable

        return self.Config.template_structure_model(
            templates=templates, variables=variables
        )

    def _get_categories(self, structure: TTemplateStructure | None = None) -> set[str]:

        if not structure:
            structure = self._get_structure()

        categories: set[str] = set()

        for template in structure.templates:
            categories.add(template.category)

        return categories

    # Public methods
    def set_group(self, group: TTemplateGroup) -> Self:

        self._group = group

        return self

    def add_user_template(self, template: TTemplate) -> Self:

        self._user_templates[template.name] = template

        return self

    def add_user_variable(self, variable: TTemplateVariable) -> Self:

        self._user_variables[variable.name] = variable

        return self

    def build(self, group_by_category: bool = True) -> TTemplateBuild:

        build_data = None
        return parse_obj_as(self.Config.template_build_model, build_data)
