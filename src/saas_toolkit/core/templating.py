from __future__ import annotations

from typing import Any, Generic, TypeVar, overload
from typing_extensions import Self
from pydantic import BaseModel, Field

TTemplateVariable = TypeVar("TTemplateVariable", bound="TemplateVariable")
TTemplateItem = TypeVar("TTemplateItem", bound="TemplateItem")
TTemplate = TypeVar("TTemplate", bound="Template")
TTemplateGroup = TypeVar("TTemplateGroup", bound="TemplateGroup")
TBuildResult = TypeVar("TBuildResult", bound=list[dict])


class TemplateVariable(BaseModel):

    name: str
    value: str | int
    required: bool = False
    default: str | int | None = None


class TemplateItem(BaseModel):

    name: str
    value: dict
    template: Template

    unique: bool = Field(True, description="A unique TemplateItem is only represented in the final build. The unique key is the name")


class Template(BaseModel):

    name: str
    items: list[TemplateItem]
    variables: list[TemplateVariable] = []
    group: TemplateGroup | None = None

    extends: Template | None = None


class TemplateGroup(BaseModel):

    name: str
    templates: list[Template]
    variables: list[TemplateVariable] = []

    extends: TemplateGroup | None = None


class TemplateBuilder(
    Generic[TTemplateGroup, TTemplate, TTemplateItem, TTemplateVariable, TBuildResult]
):

    class TemplateStructure(BaseModel):
        """
        TemplateHierarchy 
        
        The first item in each list is of lowest importance and can be overwritten by items later on in the 

        Args:
            BaseModel (_type_): _description_
        """
        templates: list[TTemplate]
        variables: list[TTemplateVariable]


    _group: TTemplateGroup | None = None
    _templates: dict[str, TTemplate] = {}
    _user_variables: dict[str, TTemplateVariable] = {}

    # Private
    @overload
    def _get_children(self, obj: TTemplate) -> list[TTemplate]:
        ...

    @overload
    def _get_children(self, obj: TTemplateGroup) -> list[TTemplateGroup]:
        ...

    def _get_children(self, obj: TTemplateGroup | TTemplate) -> list[TTemplateGroup | TTemplate]:

        children: list[TTemplateGroup | TTemplate] = []

        subject = obj

        # Get children
        while subject.extends is not None:
            children.append(subject)

            if subject.extends:
                subject = subject.extends

        return children.reverse()



    def _get_structure(self) -> TemplateStructure:

        groups = self._get_children(self._group)   if self._group else []


        
        templates: dict[str, TTemplate] = {}

        variables: dict[str, TTemplateVariable] = {}

        for group in groups:

            for group_template in group.templates:

                group_templates = self._get_children(group_template)

                for template in group_templates:

                    templates[template.name] = template

                    for variable in template.variables:
                        variables[variable.name] = variable

            for group_variable in group.variables:
                variables[group_variable.name] = group_variable

        for user_variable in self._user_variables.values():
            variables[user_variable.name] = user_variable

        return self.TemplateStructure(
            templates=templates,
            variables=variables
        )

            

    # Public methods
    def add_group(self, group: TTemplateGroup) -> Self:

        self._groups[group.name] = group

        return self

    def add_template(self, template: TTemplate) -> Self:

        self._templates[template.name] = template

        return self

    def add_user_variable(self, variable: TTemplateVariable) -> Self:

        self._user_variables[variable.name] = variable

        return self

    def build(self) -> TBuildResult:


