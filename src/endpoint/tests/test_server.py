from endpoint import server
import pytest


@pytest.mark.skip(reason="no teardown")
def test_main():
    server.main()
    raise NotImplementedError
