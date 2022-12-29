"""
Configuration related tests.
"""
from unittest import mock

from click.testing import CliRunner

from latz.cli import cli


def test_bad_backend(runner_with_bad_backend: CliRunner):
    """
    Test to make sure the correct error is displayed when we configure a non-existent backend.
    """
    result = runner_with_bad_backend.invoke(cli, ["search", "search_term"])

    assert result.exit_code == 1
    assert "Backend has been improperly configured" in result.stdout


def test_non_existent_config_file(
    runner_with_non_existent_config_file: CliRunner, mocker
):
    """
    If no configuration files exists, everything thing should still work and the default
    backend, "unsplash" will be chosen and run.
    """
    mock_client = mocker.patch("latz.plugins.image.unsplash.Client")
    result = runner_with_non_existent_config_file.invoke(cli, ["search", "ladder"])

    assert result.stdout == ""
    assert result.exit_code == 0

    expected_mock_call = mock.call().get(
        "https://api.unsplash.com/search/photos", params={"query": "ladder"}
    )
    assert expected_mock_call in mock_client.mock_calls


def test_bad_config_parameters(runner_with_bad_config_parameters: CliRunner):
    """
    If no configuration files exists, everything thing should still work and the default
    backend, "unsplash" will be chosen and run.
    """
    result = runner_with_bad_config_parameters.invoke(cli, ["search", "ladder"])

    assert "Unable to parse configuration file:" in result.stdout
    assert "does_not_exist:" in result.stdout
    assert "extra fields not permitted" in result.stdout
    assert result.exit_code == 1


def test_multiple_config_files(runner_with_multiple_config_files: CliRunner, mocker):
    """
    If no configuration files exists, everything thing should still work and the default
    backend, "unsplash" will be chosen and run.
    """
    mocker.patch("latz.plugins.image.unsplash.Client")
    result = runner_with_multiple_config_files.invoke(cli, ["search", "ladder"])

    assert result.exit_code == 0
    assert "https://placekitten.com/200/300" in result.stdout
    assert "https://placekitten.com/600/500" in result.stdout
    assert "https://placekitten.com/1000/800" in result.stdout
