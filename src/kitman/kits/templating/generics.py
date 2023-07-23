from itertools import chain
from typing import Generic, Type, overload
from typing_extensions import Self
from pydantic import ConfigDict, parse_obj_as

from collections import OrderedDict

from .dependency_resolvers import TemplateDependencyResolver

from . import domain


class BaseTemplateBuilder(
    Generic[
        domain.TTemplateGroup,
        domain.TTemplate,
        domain.TTemplateItem,
        domain.TTemplateVariable,
        domain.TTemplateStructure,
        domain.TTemplateBuild,
    ]
):
    model_config = ConfigDict()

    _group: domain.TTemplateGroup | None = None
    _user_templates: dict[str, domain.TTemplate] = {}
    _user_variables: dict[str, domain.TTemplateVariable] = {}

    # Private
    def _get_item_index(
        self,
        search_items: list[domain.TTemplateItem],
        item: domain.TTemplateItem,
        search_keys: set[str] = [],
    ) -> int | None:

        search_params = {}

        for search_key in search_keys:
            search_params[search_key] = item.value[search_key]

        index: int | None = None

        for search_index, search_item in enumerate(search_items):

            search_item_value = search_item.dict(include={"value": search_keys})[
                "value"
            ]

            if search_item_value == search_params:
                index = search_index
                break

        if isinstance(index, int):
            return index

        return None

    @overload
    def _get_tree(self, obj: domain.TTemplate) -> list[domain.TTemplate]:
        ...

    @overload
    def _get_tree(
        self, obj: domain.TTemplate, return_dict=True
    ) -> OrderedDict[str, domain.TTemplate]:
        ...

    @overload
    def _get_tree(self, obj: domain.TTemplateGroup) -> list[domain.TTemplateGroup]:
        ...

    @overload
    def _get_tree(
        self, obj: domain.TTemplateGroup, return_dict=True
    ) -> OrderedDict[str, domain.TTemplateGroup]:
        ...

    def _get_tree(
        self, obj: domain.TTemplateGroup | domain.TTemplate, return_dict: bool = False
    ) -> list[domain.TTemplateGroup | domain.TTemplate] | OrderedDict[
        str, domain.TTemplateGroup | domain.TTemplate
    ]:
        """
        _get_tree.

        Get a tree of all children and the object itself.
        The tree will be in reverse order -> last child is first, obj is last

        Args
            obj (domain.TTemplateGroup | domain.TTemplate): _description_
            return_dict (bool, optional): _description_. Defaults to False.

        Returns
            list[domain.TTemplateGroup | domain.TTemplate] | OrderedDict[ str, domain.TTemplateGroup | domain.TTemplate ]: _description_

        """
        children: list[domain.TTemplateGroup | domain.TTemplate] = []

        if obj.children:
            for child in obj.children:

                children.extend(self._get_tree(child))

        # Add obj to children
        children.append(obj)

        tree: OrderedDict[str, domain.TTemplateGroup | domain.TTemplate] = OrderedDict()

        for child in children:
            tree[child.name] = child

        if return_dict:
            return tree

        return [t for t in tree.values()]

    def _get_structure(self) -> domain.TTemplateStructure:

        # Groups
        groups: list[domain.TTemplateGroup] = self._get_tree(self._group)

        # Templates
        templates: OrderedDict[str, domain.TTemplate] = OrderedDict()

        # Temporary store for group templates
        _group_templates: OrderedDict[str, domain.TTemplate] = OrderedDict()

        for group in groups:

            group_template: domain.TTemplate
            for group_template in group.templates:
                _group_templates[group_template.name] = group_template

        if _group_templates:
            for group_template in _group_templates.values():

                for template in self._get_tree(group_template):
                    templates[template.name] = template

        if self._user_templates:
            for template in self._user_templates.values():
                templates[template.name] = template

        # Items
        items: list[domain.TTemplateItem] = []

        for template in templates.values():

            for item in template.items:
                item_index: int | None = None

                if template.unique_keys:
                    # Check if items is already added - if it is, we have to replace it
                    item_index = self._get_item_index(items, item, template.unique_keys)

                if item_index:
                    items[item_index] = item
                else:
                    items.append(item)

        # Variables
        variables: OrderedDict[str, domain.TTemplateVariable] = OrderedDict()

        for template in templates.values():
            template_variable: domain.TTemplateVariable
            for template_variable in template.variables:
                variables[template_variable.name] = template_variable

        for group in groups:

            group_variable: domain.TTemplateVariable
            for group_variable in group.variables:
                variables[group_variable.name] = group_variable

        if self._user_variables:
            user_variable: domain.TTemplateVariable
            for user_variable in self._user_variables.values():
                variables[user_variable.name] = user_variable

        template_list = [t for t in templates.values()]
        variable_list = [v for v in variables.values()]

        return self.Config.template_structure_model(
            templates=template_list, items=items, variables=variable_list
        )

    def _get_categories(
        self, structure: domain.TTemplateStructure | None = None
    ) -> set[str]:

        if not structure:
            structure = self._get_structure()

        categories: set[str] = set()

        template: domain.TTemplate
        for template in structure.templates:
            categories.add(template.category)

        return categories

    def _get_dependency_resolver(
        self, structure: domain.TTemplateStructure
    ) -> TemplateDependencyResolver[domain.TTemplateItem, domain.TTemplateVariable]:

        return TemplateDependencyResolver[
            domain.TTemplateItem, domain.TTemplateVariable
        ](variables=structure.variables)

    # Public methods

    def set_group(self, group: domain.TTemplateGroup) -> Self:

        self._group = group

        return self

    def add_user_template(self, template: domain.TTemplate) -> Self:

        self._user_templates[template.name] = template

        return self

    def add_user_variable(self, variable: domain.TTemplateVariable) -> Self:

        self._user_variables[variable.name] = variable

        return self

    def build(self) -> domain.TTemplateBuild:

        structure = self._get_structure()
        dependency_resolver = self._get_dependency_resolver(structure)

        data: list[domain.TTemplateItem] = []

        items: list[domain.TTemplateItem] = structure.items

        for item in items:

            resolved_item = dependency_resolver.resolve(item)
            data.append(resolved_item)

        template_build = self.Config.template_build_model(
            data=data, structure=structure
        )

        return template_build
