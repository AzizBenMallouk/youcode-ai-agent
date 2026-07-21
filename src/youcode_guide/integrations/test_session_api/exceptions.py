class TestSessionApiError(Exception):
    pass


class TestSessionApiUnavailable(
    TestSessionApiError
):
    pass


class InvalidTestSessionResponse(
    TestSessionApiError
):
    pass