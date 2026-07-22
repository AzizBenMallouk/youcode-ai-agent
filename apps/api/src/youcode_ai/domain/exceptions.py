class DomainError(Exception):
    """Erreur métier générale."""


class ConsentNotFoundError(
    DomainError
):
    pass


class ConsentAlreadyRevokedError(
    DomainError
):
    pass

class DuplicateActiveRequestError(
    DomainError
):
    pass

class ExternalServiceError(
    DomainError
):
    pass


class TestSessionNotFoundError(
    DomainError
):
    pass


class NoAvailableTestSessionError(
    DomainError
):
    pass

class VisitorRequestNotFoundError(
    DomainError
):
    pass


class InvalidRequestTypeError(
    DomainError
):
    pass


class InvalidRequestStatusError(
    DomainError
):
    pass


class IncompleteRequestError(
    DomainError
):
    pass