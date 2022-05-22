from kitman.db.models import BaseModel, BaseMeta, ormar
from typing import TYPE_CHECKING, ForwardRef, TypeVar
from ormar.relations.querysetproxy import QuerysetProxy

## Types
TTemplateVariable = TypeVar("TTemplateVariable", bound="BaseTemplateVariable")
TTemplateItem = TypeVar("TTemplateItem", bound="BaseTemplateItem")

## Refs
TemplateVariableRef = ForwardRef("TemplateVariable")
TemplateItemRef = ForwardRef("TemplateItemRef")
TemplateRef = ForwardRef("Template")
TemplateGroupRef = ForwardRef("TemplateGroup")


class BaseTemplateVariable(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)
    description: str = ormar.Text(nullable=True)
    value: str = ormar.String(max_length=1024, nullable=True)
    required: bool = ormar.Boolean(default=False)


class BaseTemplateItem(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)
    description: str = ormar.Text(nullable=True)
    value: dict = ormar.JSON()


class BaseTemplate(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)
    description: str = ormar.Text(nullable=True)
    category: str = ormar.String(max_length=255)
    items: list[BaseTemplateItem] | QuerysetProxy[BaseTemplateItem] = ormar.ManyToMany(
        TemplateItemRef, related_name="templates"
    )
    variables: list[BaseTemplateVariable] | QuerysetProxy[
        BaseTemplateVariable
    ] = ormar.ManyToMany(TemplateVariableRef, related_name="templates")
    unique_keys: list[str] = ormar.JSON(default=list)
    parent: TemplateRef | None = ormar.ForeignKey(
        TemplateRef, nullable=True, ondelete="SET NULL"
    )


class BaseTemplateGroup(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)
    description: str = ormar.Text(nullable=True)

    templates: list[TemplateRef] | QuerysetProxy[TemplateRef] = ormar.ManyToMany(
        TemplateRef, related_name="groups"
    )
    variables: list[TemplateVariableRef] | QuerysetProxy[
        TemplateVariableRef
    ] = ormar.ManyToMany(TemplateVariableRef, related_name="groups")
