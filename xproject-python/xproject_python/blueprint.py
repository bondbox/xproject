# coding:utf-8

from typing import Optional
from typing import Sequence

from xkits_command.actuator import Command
from xkits_command.actuator import CommandArgument
from xkits_command.actuator import CommandExecutor
from xkits_command.parser import ArgParser

from xproject_python.attribute import __project_home__ as project_home
from xproject_python.attribute import __version__ as version


@CommandArgument("python", description="Create a Python project")
def add_cmd(_arg: ArgParser):  # pylint: disable=unused-argument
    pass


@CommandExecutor(add_cmd)
def run_cmd(cmds: Command) -> int:  # pylint: disable=unused-argument
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = version
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {project_home}.")  # noqa:E501
