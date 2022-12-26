from click.testing import CliRunner

from latz.commands.get import command


def test_get_command_happy_path(runner: CliRunner):
    """
    Tests a successful run of the ``get`` command.
    """
    result = runner.invoke(command, ["search_term"])

    assert result.exit_code == 0
    assert result.stdout == "search_term\n"
