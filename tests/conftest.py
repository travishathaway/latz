import json

import pytest
from click.testing import CliRunner

from latz.constants import CONFIG_FILE_NAME


@pytest.fixture()
def runner(mocker, tmp_path):
    """Configures a test CLI runner using our "dummy" backend"""
    runner = CliRunner()

    config_file = tmp_path / CONFIG_FILE_NAME
    mocker.patch("latz.cli.CONFIG_FILES", (config_file,))

    config = {
        "backend": "dummy",
        "dummy_config": {
            "placeholder_type": "kitten",
        },
    }

    with runner.isolated_filesystem(tmp_path):
        with open(config_file, "w") as fp:
            json.dump(config, fp)

        return runner
