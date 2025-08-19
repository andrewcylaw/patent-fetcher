import pytest


# Full test coverage might also include checking logger calls, patching gzip/datetime, forcing gzip to fail, etc
# If there's a sql output downstream, then those would be tested too
@pytest.mark.skip(reason="LocalOutputClient is only for the demo")
def test_local_output_client_creates_file():
    pass

@pytest.mark.skip(reason="LocalOutputClient is only for the demo")
def test_local_output_client_gzip_error():
    pass

@pytest.mark.skip(reason="SQLite client is only for the demo")
def test_sqlite_output_client_db_write():
    pass

@pytest.mark.skip(reason="SQLite client is only for the demo")
def test_sqlite_output_client_connection_error():
    pass