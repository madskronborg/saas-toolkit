import re
from typing import Generic
from . import domain, exceptions

from kitman.core import dynamic

from collections import OrderedDict


class TemplateDependencyResolver(
    Generic[domain.TTemplateItem, domain.TTemplateVariable]
):

    _initial_variables: OrderedDict[str, domain.TTemplateVariable]
    required_variables: OrderedDict[str, domain.TTemplateVariable]
    optional_variables: OrderedDict[str, domain.TTemplateVariable]
    unresolved_variables: OrderedDict[str, domain.TTemplateVariable]
    resolved_variables: OrderedDict[str, domain.TTemplateVariable]

    def __init__(self, variables: list[domain.TTemplateVariable]):

        self._initial_variables = OrderedDict()
        self.required_variables = OrderedDict()
        self.optional_variables = OrderedDict()

        for variable in variables:
            self._initial_variables[variable.name] = variable

            if variable.required:
                self.required_variables[variable.name] = variable

            else:
                self.optional_variables[variable.name] = variable

        self.validate_variables(raise_exception=True)
        self._resolve_variables()

    # Private

    def _set_unresolved_variables(self) -> None:

        unresolved_variables = list(
            filter(
                lambda var: not var.name in self.resolved_variables,
                self._initial_variables.values(),
            )
        )

        for unresolved_variable in unresolved_variables:
            self.unresolved_variables[unresolved_variable.name] = unresolved_variable

    def _resolve_variable(self, variable: domain.TTemplateVariable) -> None:

        if not variable.depends_on:

            self.resolved_variables[variable.name] = variable
            return

        # A dependency is ready if it is resolved or optional
        dependencies_ready = all(
            [
                dependency_name in self.resolved_variables
                or dependency_name in self.optional_variables
                for dependency_name in variable.depends_on
            ]
        )

        if not dependencies_ready:
            return

        dependencies: dict[str, str | int] = {}

        for dependency_name in variable.depends_on:

            dependency = self.resolved_variables.get(dependency_name)

            if not dependency:
                dependency = self.optional_variables.get(dependency_name)

            dependencies[dependency.name] = dependency.value

        # Resolve variable value

        resolved_variable_dict = variable.dict()
        resolved_variable["value"] = resolved_variable_dict["value"].format(
            **dependencies
        )
        resolved_variable = variable.__class__(**resolved_variable_dict)

        if resolved_variable.depends_on:
            # Variables has nested dependencies
            self.unresolved_variables[resolved_variable.name] = resolved_variable

        else:
            self.resolved_variables[variable.name] = resolved_variable

    def _resolve_variables(self) -> None:

        self.unresolved_variables = OrderedDict()
        self.resolved_variables = OrderedDict()

        # Resolve root variables
        for root_variable in filter(
            lambda variable: not variable.depends_on, self._initial_variables.values()
        ):
            self.resolved_variables[root_variable.name] = root_variable

        self._set_unresolved_variables()

        while self.unresolved_variables:

            for unresolved_variable in self.unresolved_variables:

                self._resolve_variable(unresolved_variable)

    # Public
    def validate_variables(self, raise_exception: bool = False) -> bool:
        """
        validate

        Validates variables are valid.

        Args:
            raise_exception (bool, optional): Raise exception if validation fails. Defaults to False.

        Raises:
            exceptions.TemplateDependencyError: if `raise_exception` is `True` and there are unknown variables or invalid required variables

        Returns:
            bool: _description_
        """

        unknown_variables: list[str] = []
        invalid_required_variables: list[str] = []

        for variable in self._initial_variables.values():

            if not variable.depends_on:
                continue

            for dependency_name in variable.depends_on:

                if not dependency_name in self._initial_variables:
                    unknown_variables.append(dependency_name)

                    if variable.required:
                        invalid_required_variables.append(variable.name)

        if not (unknown_variables or invalid_required_variables):

            return True

        if raise_exception:

            error_message: OrderedDict[str, str | list[str]] = OrderedDict()
            error_message["message"] = "Unknown variables or invalid required variables"
            error_message["unknown_variables"] = unknown_variables
            error_message["invalid_required_variables"] = invalid_required_variables

            raise exceptions.TemplateDependencyError(
                message=error_message, status_code=400
            )

        return False

    def validate_item(
        self, item: domain.TTemplateItem, raise_exception: bool = False
    ) -> bool:

        if not item.depends_on:
            return True

        unknown_variables: list[str] = list(
            filter(
                lambda dependency_name: not dependency_name in self.resolved_variables,
                item.depends_on,
            )
        )

        if not unknown_variables:
            return True

        if raise_exception:

            raise exceptions.TemplateDependencyError(
                OrderedDict(
                    message="Item has unknown variables",
                    item=item.dict(),
                    unknown_variables=unknown_variables,
                ),
                code=400,
            )

        return False

    def resolve(self, item: domain.TTemplateItem) -> domain.TTemplateItem:

        if not item.depends_on:
            return item

        self.validate_item(item, raise_exception=True)

        item_dict = item.dict()

        result: dict = {}

        for key, val in item_dict["value"].items():

            key_dependency_names: list[str] = []
            val_dependency_names: list[str] = []

            if isinstance(key, str):
                key_dependency_names = dynamic.get_placeholders_from_str(key)

            if isinstance(val, str):
                val_dependency_names = dynamic.get_placeholders_from_str(val)

            key_dependencies: dict[str, str | int] = {}
            val_dependencies: dict[str, str | int] = {}

            if key_dependency_names:
                for key_dependency_name in key_dependency_names:
                    key_dependencies[key_dependency_name] = self.resolved_variables.get(
                        key_dependency_name
                    ).value

            if val_dependency_names:
                for val_dependency_name in val_dependency_names:
                    val_dependencies[val_dependency_name] = self.resolved_variables.get(
                        val_dependency_name
                    ).value

            resolved_key = key
            resolved_value = val

            if key_dependencies:
                resolved_key = key.format(**key_dependencies)

            if val_dependencies:
                resolved_value = val.format(**val_dependencies)

            result[resolved_key] = resolved_value

        item_dict["value"] = result

        return item.__class__(**item_dict)
