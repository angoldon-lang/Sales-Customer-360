from enum import Enum
from sqlalchemy.orm import Session
from app.models.user import User, Role


class PermissionAction(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class PermissionResource(str, Enum):
    CUSTOMERS = "customers"
    DATA_QUALITY = "data_quality"
    SERVICES = "services"
    OPPORTUNITIES = "opportunities"
    CONTRACTS = "contracts"
    PERMISSIONS = "permissions"


class UserRole(str, Enum):
    SALES = "sales"
    SALES_MANAGER = "sales_manager"
    BU_MANAGER = "bu_manager"
    DIREZIONE = "direzione"
    ADMIN = "admin"
    DATA_STEWARD = "data_steward"


ROLE_PERMISSIONS = {
    UserRole.SALES: {
        PermissionResource.CUSTOMERS: [PermissionAction.READ, PermissionAction.UPDATE],
        PermissionResource.DATA_QUALITY: [PermissionAction.READ, PermissionAction.UPDATE],
        PermissionResource.OPPORTUNITIES: [PermissionAction.READ, PermissionAction.UPDATE],
        PermissionResource.CONTRACTS: [PermissionAction.READ],
    },
    UserRole.SALES_MANAGER: {
        PermissionResource.CUSTOMERS: [PermissionAction.READ, PermissionAction.UPDATE],
        PermissionResource.DATA_QUALITY: [PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.CREATE],
        PermissionResource.OPPORTUNITIES: [PermissionAction.READ, PermissionAction.UPDATE],
        PermissionResource.CONTRACTS: [PermissionAction.READ],
    },
    UserRole.BU_MANAGER: {
        PermissionResource.CUSTOMERS: [PermissionAction.READ],
        PermissionResource.DATA_QUALITY: [PermissionAction.READ],
        PermissionResource.SERVICES: [PermissionAction.READ, PermissionAction.UPDATE, PermissionAction.CREATE],
        PermissionResource.OPPORTUNITIES: [PermissionAction.READ],
        PermissionResource.CONTRACTS: [PermissionAction.READ],
    },
    UserRole.DIREZIONE: {
        PermissionResource.CUSTOMERS: [PermissionAction.READ],
        PermissionResource.DATA_QUALITY: [PermissionAction.READ],
        PermissionResource.SERVICES: [PermissionAction.READ],
        PermissionResource.OPPORTUNITIES: [PermissionAction.READ],
        PermissionResource.CONTRACTS: [PermissionAction.READ],
    },
    UserRole.ADMIN: {
        PermissionResource.CUSTOMERS: [PermissionAction.READ, PermissionAction.CREATE, PermissionAction.UPDATE, PermissionAction.DELETE],
        PermissionResource.DATA_QUALITY: [PermissionAction.READ, PermissionAction.CREATE, PermissionAction.UPDATE, PermissionAction.DELETE],
        PermissionResource.SERVICES: [PermissionAction.READ, PermissionAction.CREATE, PermissionAction.UPDATE, PermissionAction.DELETE],
        PermissionResource.OPPORTUNITIES: [PermissionAction.READ, PermissionAction.CREATE, PermissionAction.UPDATE, PermissionAction.DELETE],
        PermissionResource.CONTRACTS: [PermissionAction.READ, PermissionAction.CREATE, PermissionAction.UPDATE, PermissionAction.DELETE],
        PermissionResource.PERMISSIONS: [PermissionAction.READ, PermissionAction.CREATE, PermissionAction.UPDATE, PermissionAction.DELETE],
    },
    UserRole.DATA_STEWARD: {
        PermissionResource.CUSTOMERS: [PermissionAction.READ, PermissionAction.UPDATE],
        PermissionResource.DATA_QUALITY: [PermissionAction.READ, PermissionAction.UPDATE],
        PermissionResource.CONTRACTS: [PermissionAction.READ],
    },
}


class PermissionChecker:
    """Verifica i permessi dell'utente per risorsa e azione."""

    @staticmethod
    def has_permission(user: User | None, resource: PermissionResource, action: PermissionAction) -> bool:
        """
        Verifica se l'utente ha il permesso per la risorsa e azione.
        """
        if not user:
            return False

        if user.is_admin:
            return True

        role_name = user.role.name if user.role else None
        if not role_name:
            return False

        try:
            role = UserRole(role_name)
        except ValueError:
            return False

        permissions = ROLE_PERMISSIONS.get(role, {})
        allowed_actions = permissions.get(resource, [])

        return action in allowed_actions

    @staticmethod
    def can_view_customer(user: User | None, customer_id: int) -> bool:
        """Verifica se l'utente può vedere il cliente."""
        if not PermissionChecker.has_permission(user, PermissionResource.CUSTOMERS, PermissionAction.READ):
            return False

        if not user or user.is_admin:
            return True

        role_name = user.role.name if user.role else None
        if role_name == UserRole.SALES.value:
            return True
        elif role_name == UserRole.SALES_MANAGER.value:
            return True
        elif role_name == UserRole.DIREZIONE.value:
            return True
        elif role_name == UserRole.DATA_STEWARD.value:
            return True

        return False

    @staticmethod
    def can_edit_data_quality_task(user: User | None, customer_account_owner_id: int | None = None) -> bool:
        """Verifica se l'utente può modificare task di data quality."""
        if not PermissionChecker.has_permission(user, PermissionResource.DATA_QUALITY, PermissionAction.UPDATE):
            return False

        if not user:
            return False

        if user.is_admin:
            return True

        role_name = user.role.name if user.role else None

        if role_name == UserRole.SALES.value:
            return user.id == customer_account_owner_id

        return True

    @staticmethod
    def can_edit_opportunity(user: User | None, account_owner_id: int | None = None) -> bool:
        """Verifica se l'utente può modificare opportunità."""
        if not PermissionChecker.has_permission(user, PermissionResource.OPPORTUNITIES, PermissionAction.UPDATE):
            return False

        if not user:
            return False

        if user.is_admin:
            return True

        role_name = user.role.name if user.role else None

        if role_name == UserRole.SALES.value:
            return user.id == account_owner_id

        return True


class QueryFilter:
    """Filtra le query database in base ai permessi dell'utente."""

    @staticmethod
    def filter_customers_query(query, user: User | None):
        """Filtra i clienti visibili all'utente."""
        if not user:
            return query.filter(False)

        if user.is_admin:
            return query

        role_name = user.role.name if user.role else None

        if role_name == UserRole.SALES.value:
            from app.models.customer import CustomerAccount
            return query.join(CustomerAccount).filter(
                CustomerAccount.account_owner_id == user.id
            ).distinct()
        elif role_name == UserRole.SALES_MANAGER.value:
            from app.models.customer import CustomerAccount
            return query.join(CustomerAccount).filter(
                CustomerAccount.team == user.team
            ).distinct()
        elif role_name in [UserRole.DIREZIONE.value, UserRole.DATA_STEWARD.value]:
            return query

        return query.filter(False)

    @staticmethod
    def filter_opportunities_query(query, user: User | None):
        """Filtra le opportunità visibili all'utente."""
        if not user:
            return query.filter(False)

        if user.is_admin:
            return query

        role_name = user.role.name if user.role else None

        if role_name == UserRole.SALES.value:
            return query.filter(lambda: query.account_owner_id == user.id)
        elif role_name == UserRole.SALES_MANAGER.value:
            return query

        return query

    @staticmethod
    def filter_data_quality_query(query, user: User | None):
        """Filtra i task di data quality visibili all'utente."""
        if not user:
            return query.filter(False)

        if user.is_admin or user.role.name == UserRole.DATA_STEWARD.value:
            return query

        role_name = user.role.name if user.role else None

        if role_name == UserRole.SALES.value:
            return query.filter(lambda: query.account_owner_id == user.id)
        elif role_name == UserRole.SALES_MANAGER.value:
            return query

        return query
