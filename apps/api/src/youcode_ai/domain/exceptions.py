class DomainError(Exception):
    """Erreur métier générale."""


class ConsentNotFoundError(DomainError):
    pass


class ConsentAlreadyRevokedError(DomainError):
    pass


class DuplicateActiveRequestError(DomainError):
    pass


class ExternalServiceError(DomainError):
    pass


class TestSessionNotFoundError(DomainError):
    pass


class NoAvailableTestSessionError(DomainError):
    pass


class VisitorRequestNotFoundError(DomainError):
    pass


class InvalidRequestTypeError(DomainError):
    pass


class InvalidRequestStatusError(DomainError):
    pass


class IncompleteRequestError(DomainError):
    pass


# Email
class EmailDeliveryError(DomainError):
    pass


class EmailProviderUnavailableError(DomainError):
    pass


# Auth
class AuthenticationError(DomainError):
    pass


class AuthorizationError(DomainError):
    pass


class AccountLockedError(DomainError):
    pass


class AccountDisabledError(DomainError):
    pass


class DuplicateEmailError(DomainError):
    pass
