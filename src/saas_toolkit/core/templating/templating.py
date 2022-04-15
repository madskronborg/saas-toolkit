from __future__ import annotations
from . import generics


class TemplateVariable(generics.BaseTemplateVariable):
    pass


class TemplateItem(generics.BaseTemplateItem["Template"]):
    pass


class Template(
    generics.BaseTemplate["TemplateGroup", "Template", TemplateItem, TemplateVariable]
):
    pass


class TemplateGroup(
    generics.BaseTemplateGroup["TemplateGroup", Template, TemplateVariable]
):
    pass


class TemplateStructure(
    generics.BaseTemplateStructure[Template, TemplateItem, TemplateVariable]
):
    pass


class TemplateBuild(generics.BaseTemplateBuild[list[dict]]):
    pass


class TemplateBuilder(
    generics.BaseTemplateBuilder[
        TemplateGroup,
        Template,
        TemplateItem,
        TemplateVariable,
        TemplateStructure,
        TemplateBuild,
    ]
):
    class Config:
        template_structure_model = TemplateStructure
        template_build_model = TemplateBuild
