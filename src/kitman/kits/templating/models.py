from kitman.db.models import BaseModel, BaseMeta, ormar
from kitman.db.models import TreeMixin
from typing import TypeVar
from ormar.relations.querysetproxy import QuerysetProxy

from kitman.conf import settings

## Types
TTemplateVariable = TypeVar("TTemplateVariable", bound="BaseTemplateVariable")
TTemplateItem = TypeVar("TTemplateItem", bound="BaseTemplateItem")

## User Models
TemplateVariable = settings.kits.templating.models.template_variable.model
TemplateItem = settings.kits.templating.models.template_item.model
Template = settings.kits.templating.models.template.model
TemplateGroup = settings.kits.templating.models.template_group.model
TemplateThroughTemplateVariable = (
    settings.kits.templating.models.template_through_template_variable.model
)
TemplateThroughTemplateItem = (
    settings.kits.templating.models.template_through_template_item.model
)
TemplateGroupThroughTemplate = (
    settings.kits.templating.models.template_group_through_template.model
)
TemplateGroupThroughTemplateVariable = (
    settings.kits.templating.models.template_through_template_variable.model
)


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


class BaseTemplateThroughTemplateVariable(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    template: Template = ormar.ForeignKey(Template, ondelete="CASCADE")
    template_variable: TemplateVariable = ormar.ForeignKey(
        TemplateVariable, ondelete="CASCADE"
    )


class BaseTemplateThroughTemplateItem(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    template: Template = ormar.ForeignKey(Template, ondelete="CASCADE")
    template_item: TemplateVariable = ormar.ForeignKey(
        TemplateVariable, ondelete="CASCADE"
    )


class BaseTemplate(BaseModel, TreeMixin):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)
    description: str = ormar.Text(nullable=True)
    category: str = ormar.String(max_length=255)
    items: list[BaseTemplateItem] | QuerysetProxy[BaseTemplateItem] = ormar.ManyToMany(
        TemplateItem,
        through=TemplateThroughTemplateItem,
        related_name="templates",
        through_relation_name="template",
        through_reverse_relation_name="template_item",
    )
    variables: list[BaseTemplateVariable] | QuerysetProxy[
        BaseTemplateVariable
    ] = ormar.ManyToMany(
        TemplateVariable,
        through=TemplateThroughTemplateVariable,
        related_name="templates",
        through_relation_name="template",
        through_reverse_relation_name="template_variable",
    )

    unique_keys: list[str] = ormar.JSON(default=list)


class BaseTemplateGroupThroughTemplate(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    template_group: TemplateGroup = ormar.ForeignKey(
        TemplateGroup,
        ondelete="CASCADE",
    )
    template: Template = ormar.ForeignKey(Template, ondelete="CASCADE")


class BaseTemplateGroupThroughTemplateVariable(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    template_group: TemplateGroup = ormar.ForeignKey(
        TemplateGroup,
        ondelete="CASCADE",
    )
    template_variable: TemplateVariable = ormar.ForeignKey(
        TemplateVariable, ondelete="CASCADE"
    )


class BaseTemplateGroup(BaseModel):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)
    description: str = ormar.Text(nullable=True)

    templates: list[Template] | QuerysetProxy[Template] = ormar.ManyToMany(
        Template,
        through=TemplateGroupThroughTemplate,
        related_name="groups",
        through_relation_name="template_group",
        through_reverse_relation_name="template",
    )
    variables: list[TemplateVariable] | QuerysetProxy[
        TemplateVariable
    ] = ormar.ManyToMany(
        TemplateVariable,
        through=TemplateGroupThroughTemplateVariable,
        related_name="groups",
        through_relation_name="template_group",
        through_reverse_relation_name="template_variable",
    )
