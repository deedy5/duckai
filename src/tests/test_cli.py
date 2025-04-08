from click.testing import CliRunner

from duckai.cli import cli

runner = CliRunner()

def test_chat_command() -> None:
    result = runner.invoke(cli, ["chat"])
    assert "chat" in result.output
