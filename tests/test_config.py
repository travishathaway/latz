"""
Configuration related tests.
"""
from click.testing import CliRunner

from latz.cli import cli


def test_bad_backend(runner_with_bad_backend: CliRunner):
    """
    Test to make sure the correct error is displayed when we configure a non-existent backend.
    """
    result = runner_with_bad_backend.invoke(cli, ["search", "search_term"])

    assert result.exit_code == 1
    assert "search_backends:" in result.stdout
    assert (
        "'does_not_exist' is not a valid choice for a search backend" in result.stdout
    )


def test_non_existent_config_file(
    runner_with_non_existent_config_file: CliRunner, mocker
):
    """
    If no configuration files exists, everything thing should still work and the default
    backend, "unsplash" will be chosen and run.
    """
    mock_client_get = mocker.patch("latz.plugins.image.unsplash._get", return_value={})
    result = runner_with_non_existent_config_file.invoke(cli, ["search", "ladder"])

    assert "ImageSearchResultSet" in result.stdout
    assert "total_number_results=0" in result.stdout
    assert result.exit_code == 0
    assert len(mock_client_get.mock_calls) == 1


def test_bad_config_parameters(runner_with_bad_config_parameters: CliRunner):
    """
    If a bad configuration file is found, application should raise an error and exit.
    """
    result = runner_with_bad_config_parameters.invoke(cli, ["search", "ladder"])

    assert "Unable to parse configuration file:" in result.stdout
    assert "does_not_exist:" in result.stdout
    assert "extra fields not permitted" in result.stdout
    assert result.exit_code == 1


def test_multiple_config_files(runner_with_multiple_config_files: CliRunner, mocker):
    """
    If multiple configuration files are found, they should all be parsed and the command
    should be run.
    """
    mocker.patch("latz.plugins.image.unsplash._get", return_value={})
    result = runner_with_multiple_config_files.invoke(cli, ["search", "ladder"])

    assert result.exit_code == 0
    assert "https://placekitten.com/200/300" in result.stdout
    assert "https://placekitten.com/600/500" in result.stdout
    assert "https://placekitten.com/1000/800" in result.stdout
