import datetime
from typing import TYPE_CHECKING, Generic
from ordered_set import TypeVar
from pydantic import EmailStr
from kitman.db.models import BaseModel, BaseMeta, ormar, QuerysetProxy

from kitman.conf import settings

## Types
TUserModel = TypeVar("TUserModel", bound="BaseUser")
TCustomerModel = TypeVar("TCustomerModel", bound="BaseCustomer")
TMembershipModel = TypeVar("TMembershipModel", bound="BaseMembership")
TInvitationModel = TypeVar("TInvitationModel", bound="BaseInvitation")

User = settings.apps.iam.models.user.model
Customer = settings.apps.iam.models.customer.model
Membership = settings.apps.iam.models.membership.model
Invitation = settings.apps.iam.models.invitation.model


class BaseUser(BaseModel, Generic[TCustomerModel, TMembershipModel]):
    class Meta(BaseMeta):
        abstract = True

    username: str = ormar.String(max_length=255, unique=True)
    email: EmailStr = ormar.String(
        max_length=255,
        unique=True,
        nullable=False,
        overwrite_pydantic_type=EmailStr,
    )
    first_name: str = ormar.String(max_length=255, default=str)
    last_name: str = ormar.String(max_length=255, default=str)

    if TYPE_CHECKING:
        ownerships: list[TCustomerModel] | QuerysetProxy[TCustomerModel]
        memberships: list[TMembershipModel] | QuerysetProxy[TMembershipModel]


class BaseInvitation(BaseModel, Generic[TUserModel, TCustomerModel, TMembershipModel]):
    class Meta(BaseMeta):
        abstract = True

    user: TUserModel = ormar.ForeignKey(
        User, related_name="memberships", ondelete="CASCADE"
    )
    customer: TCustomerModel = ormar.ForeignKey(
        Customer, related_name=False, ondelete="CASCADE"
    )
    invited_by: TMembershipModel | None = ormar.ForeignKey(
        Membership, related_name=False, nullable=True, ondelete="SET NULL"
    )


class BaseMembership(BaseModel, Generic[TUserModel, TCustomerModel, TInvitationModel]):
    class Meta(BaseMeta):
        abstract = True

    user: TUserModel = ormar.ForeignKey(
        User, related_name="memberships", ondelete="CASCADE"
    )
    customer: TCustomerModel = ormar.ForeignKey(
        Customer, related_name=False, ondelete="CASCADE"
    )
    Invitation: TInvitationModel | None = ormar.ForeignKey(
        Invitation, related_name=False, nullable=True, ondelete="CASCADE"
    )


class BaseCustomer(BaseModel, Generic[TMembershipModel]):
    class Meta(BaseMeta):
        abstract = True

    name: str = ormar.String(max_length=255)

    owner: User = ormar.ForeignKey(User, related_name="ownerships")

    members: list[TMembershipModel] | QuerysetProxy[
        TMembershipModel
    ] = ormar.ManyToMany(
        User,
        through=Membership,
        through_relation_name="customer",
        through_reverse_relation_name="user",
    )
