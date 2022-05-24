from kitman.core import services
from typing import Generic, TypeVar

from uuid import UUID

from . import errors

TSubject = str | UUID | dict
TObj = str | UUID
TRelation = str
TNamespace = str | None

TCheckResponse = TypeVar("TCheckResponse")
TGrantResponse = TypeVar("TGrantResponse")
TRevokeResponse = TypeVar("TRevokeResponse")
TInspectResponse = TypeVar("TInspectResponse")


class BaseAccessService(
    Generic[TCheckResponse, TGrantResponse, TRevokeResponse, TInspectResponse]
):

    namespace: str | None = None

    def get_namespace(self, namespace: str | None) -> str:
        """
        get_namespace

        Utility for getting a namespace.

        Args:
            namespace (str | None): An authorization namespace

        Raises:
            errors.NoNamespaceError: If there is no namespace set

        Returns:
            str: A namespace
        """

        if namespace:
            return namespace

        if self.namespace:
            return namespace

        raise errors.NoNamespaceError(
            f"No namespace found for class f{self.__class__.__name__}",
            code=500,
            status_code=500,
        )

    async def check(
        self,
        subject: TSubject,
        obj: TObj,
        relation: TRelation,
        namespace: TNamespace = None,
    ) -> TCheckResponse:
        pass

    async def grant(
        self,
        subject: TSubject,
        obj: TObj,
        relation: TRelation,
        namespace: TNamespace = None,
    ) -> TGrantResponse:
        pass

    async def revoke(
        self,
        subject: TSubject,
        obj: TObj,
        relation: TRelation,
        namespace: TNamespace = None,
    ) -> TRevokeResponse:
        pass

    async def inspect(
        self,
        subject: TSubject,
        obj: TObj,
        relation: TRelation,
        namespace: TNamespace = None,
    ) -> TInspectResponse:
        pass
