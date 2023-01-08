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
        "backend": "placeholder",
        "backend_settings": {
            "placeholder": {
                "type": "kitten",
            }
        },
    }

    with runner.isolated_filesystem(temp_dir=tmp_path):
        with open(config_file, "w") as fp:
            json.dump(config, fp)

        return runner, config_file


@pytest.fixture
def runner_with_bad_backend(tmp_path, mocker):
    """Configures a test CLI runner using a bad backend"""
    runner = CliRunner()
    config_file = tmp_path / CONFIG_FILE_NAME
    mocker.patch("latz.cli.CONFIG_FILES", (config_file,))

    config = {
        "backend": "does_not_exist",
    }

    with runner.isolated_filesystem(tmp_path):
        with open(config_file, "w") as fp:
            json.dump(config, fp)

        yield runner


@pytest.fixture
def runner_with_non_existent_config_file(tmp_path, mocker):
    """Configures a test CLI runner using non-existent config files"""
    runner = CliRunner()

    mocker.patch("latz.cli.CONFIG_FILES", (tmp_path / CONFIG_FILE_NAME,))

    with runner.isolated_filesystem(tmp_path):
        yield runner


@pytest.fixture
def runner_with_bad_config_parameters(tmp_path, mocker):
    """Configures a test CLI runner using a bad backend"""
    runner = CliRunner()

    mocker.patch("latz.cli.CONFIG_FILES", (tmp_path / CONFIG_FILE_NAME,))

    config = {
        "does_not_exist": "does_not_exist",
    }

    with runner.isolated_filesystem(tmp_path):
        with open(tmp_path / CONFIG_FILE_NAME, "w") as fp:
            json.dump(config, fp)

        yield runner


@pytest.fixture
def runner_with_multiple_config_files(tmp_path, mocker):
    """Configures a test CLI runner using a bad backend"""
    runner = CliRunner()

    config_one = tmp_path / f"{CONFIG_FILE_NAME}.one"
    config_two = tmp_path / f"{CONFIG_FILE_NAME}.two"

    mocker.patch(
        "latz.cli.CONFIG_FILES",
        (
            config_one,
            config_two,
        ),
    )

    config_one_data = {
        "backend": "unsplash",
    }

    config_two_data = {
        "backend": "placeholder",
    }

    with runner.isolated_filesystem(tmp_path):
        with open(config_one, "w") as fp:
            json.dump(config_one_data, fp)

        with open(config_two, "w") as fp:
            json.dump(config_two_data, fp)

        yield runner
