class ReschedulingError(Exception):
    pass


class ReschedulingRequestNotFound(
    ReschedulingError
):
    pass


class InvalidReschedulingRequest(
    ReschedulingError
):
    pass


class ReschedulingAlreadyProcessed(
    ReschedulingError
):
    pass


class ProposedSessionNotAvailable(
    ReschedulingError
):
    pass