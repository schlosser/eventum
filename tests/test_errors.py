import pytest

from eventum.lib.error import EventumError, _ERROR_DATA


@pytest.yield_fixture(scope="function")
def silent_eventum(eventum):
    """Disable logging for tests. Without this, creating new
    ``EventumError``s would log"""
    eventum.app.logger.disabled = True
    yield eventum
    eventum.app.logger.propagate = False


def test_namespaced_error_is_properly_subclassed(silent_eventum):
    """An error should be a subclass of all of the errors that it is
    namespaced underneath.
    """
    err = EventumError.GCalAPI.NotFound.UpdateFellBackToCreate()

    assert isinstance(err, EventumError)
    assert isinstance(err, EventumError.GCalAPI)
    assert isinstance(err, EventumError.GCalAPI.NotFound)


def test_error_data_is_assigned(silent_eventum):
    """An error should have been assigned an appropriate ``message``,
    ``error_code``, ``http_status_code``.
    """
    err = EventumError.GCalAPI.NotFound.UpdateFellBackToCreate()
    message, error_code, http_status_code, _ = (
        _ERROR_DATA['GCalAPI'][3]['NotFound'][3]['UpdateFellBackToCreate']
    )

    assert err.message == message
    assert err.error_code == error_code
    assert err.http_status_code == http_status_code


@pytest.mark.parametrize(["message", "subs", "output"], [
    ('Error at url `%s`: %s', ('/home', 'Not Found'),
     'Error at url `/home`: Not Found'),
    ('Error at url `%s`: %s', ('/home',), 'Error at url `/home`: '),
    ('Error at url.', ('/home',), 'Error at url.')
])
def test_form_message(silent_eventum, message, subs, output):
    error = EventumError()
    assert error._form_message(message, subs) == output
