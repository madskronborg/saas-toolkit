from kitman.core import services
from typing import Generic, TypeVar

from uuid import UUID

from . import exceptions, domain


class BaseAccessService(
    Generic[
        domain.TSubject,
        domain.TCheckResponse,
        domain.TGrantResponse,
        domain.TRevokeResponse,
        domain.TInspectResponse,
    ]
):

    namespace: str | None = None

    def get_namespace(self, namespace: str | None) -> str:
        """
        get_namespace

        Utility for getting a namespace.

        Args:
            namespace (str | None): An authorization namespace

        Raises:
            exceptions.NoNamespaceError: If there is no namespace set

        Returns:
            str: A namespace
        """

        if namespace:
            return namespace

        if self.namespace:
            return namespace

        raise exceptions.NoNamespaceError(
            f"No namespace found for class f{self.__class__.__name__}",
            code=500,
            status_code=500,
        )

    async def get_subject(self, subject_id: domain.TSubjectId) -> domain.TSubject:
        pass

    async def check(
        self,
        subject_id: domain.TSubjectId,
        obj: domain.Obj,
        relation: domain.Relation,
        namespace: domain.Namespace = None,
    ) -> domain.TCheckResponse:
        pass

    async def grant(
        self,
        subject_id: domain.TSubjectId,
        obj: domain.Obj,
        relation: domain.Relation,
        namespace: domain.Namespace = None,
    ) -> domain.TGrantResponse:
        pass

    async def revoke(
        self,
        subject_id: domain.TSubjectId,
        obj: domain.Obj,
        relation: domain.Relation,
        namespace: domain.Namespace = None,
    ) -> domain.TRevokeResponse:
        pass

    async def inspect(
        self,
        subject_id: domain.TSubjectId,
        obj: domain.Obj,
        relation: domain.Relation,
        namespace: domain.Namespace = None,
    ) -> domain.TInspectResponse:
        pass
