import pytest
from click.testing import CliRunner


@pytest.fixture()
def runner():
    runner = CliRunner()

    return runner
