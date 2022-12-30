from pathlib import Path

from click.testing import CliRunner

from latz.cli import cli

COMMAND = "search"


def test_get_command_happy_path(runner: tuple[CliRunner, Path]):
    """
    Tests a successful run of the ``get`` command.
    """
    cmd_runner, _ = runner
    result = cmd_runner.invoke(cli, [COMMAND, "search_term"])

    assert result.exit_code == 0

    assert "https://placekitten.com/200/300" in result.stdout
    assert "https://placekitten.com/600/500" in result.stdout
    assert "https://placekitten.com/1000/800" in result.stdout


def test_get_command_error_on_no_search_term(runner: tuple[CliRunner, Path]):
    """
    Make sure that the application displays help message when no query argument is provided.
    """
    cmd_runner, _ = runner
    result = cmd_runner.invoke(cli, [COMMAND])

    assert result.exit_code == 2
