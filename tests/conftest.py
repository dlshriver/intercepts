import pytest

import intercepts


@pytest.fixture(autouse=True)
def unregister_intercepts():
    intercepts.unregister_all()
    yield
