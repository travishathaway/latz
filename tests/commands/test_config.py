from pathlib import Path

from click.testing import CliRunner

from latz.cli import cli


COMMAND = "config"


def test_show_config(runner: tuple[CliRunner, Path]):
    """
    This makes sure that the show command is properly showing our configuration.
    """
    cmd_runner, _ = runner
    result = cmd_runner.invoke(cli, [COMMAND, "show"])

    assert result.exit_code == 0

    assert (
        result.stdout
        == """{
  "backend": "dummy",
  "results_per_page": 10,
  "dummy_config": {
    "placeholder_type": "kitten"
  },
  "unsplash_config": {
    "access_key": "",
    "secret_key": ""
  }
}
"""
    )


def test_set_config_backend(runner: tuple[CliRunner, Path], mocker):
    """
    Makes sure that we can  update the backend via the "config set" subcommand

    TODO: make this test pass!
    """
    cmd_runner, config_file = runner
    mocker.patch("latz.commands.config.commands.CONFIG_FILE_CWD", config_file)
    result = cmd_runner.invoke(cli, [COMMAND, "set", "backend=unsplash"])

    assert result.stdout == ""
    assert result.exit_code == 0

    result = cmd_runner.invoke(cli, [COMMAND, "show"])

    assert result.exit_code == 0
    assert (
        result.stdout
        == """{
  "backend": "unsplash",
  "results_per_page": 10,
  "dummy_config": {
    "placeholder_type": "kitten"
  },
  "unsplash_config": {
    "access_key": "",
    "secret_key": ""
  }
}
"""
    )


def test_set_bad_config_backend(runner: tuple[CliRunner, Path], mocker):
    """
    Test the case when we try to pass in a bad value for "backend".
    """
    cmd_runner, config_file = runner
    mocker.patch("latz.commands.config.commands.CONFIG_FILE_CWD", config_file)
    result = cmd_runner.invoke(cli, [COMMAND, "set", "backend=bad_value"])

    assert result.exit_code == 1


def test_set_config_backend_with_bad_config_file(
    runner: tuple[CliRunner, Path], mocker
):
    """
    Test the case when the config file is not valid JSON and when it's not the right type
    of JSON.

    TODO: This test has a pretty naive approach to its assertions. It would be better
          to have assertions here that don't just rely on the exit code so we can
          tell what error was actually raise.

    TODO: Break this into two tests
    """
    cmd_runner, config_file = runner
    mocker.patch("latz.commands.config.commands.CONFIG_FILE_CWD", config_file)

    with config_file.open("w") as fp:
        fp.write("bad val")

    result = cmd_runner.invoke(cli, [COMMAND, "set", "backend=dummy"])

    assert result.exit_code == 1

    with config_file.open("w") as fp:
        fp.write("[]")

    result = cmd_runner.invoke(cli, [COMMAND, "set", "backend=dummy"])

    assert result.exit_code == 1
