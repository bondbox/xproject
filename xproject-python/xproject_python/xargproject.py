# coding:utf-8

from typing import Optional
from typing import Sequence

from xkits_command.actuator import Command
from xkits_command.actuator import CommandArgument
from xkits_command.actuator import CommandExecutor
from xkits_command.parser import ArgParser

from xproject_python.attribute import __urlhome__
from xproject_python.attribute import __version__
from xproject_python.blueprint import Project


@CommandArgument("init", help="Initialize a Python based command-line project")
def add_cmd_init(_arg: ArgParser):
    _arg.add_opt_on("--update", help="allow updating existing files")
    _arg.add_argument("--license", help="select license, default to MIT",
                      type=str, metavar="LICENSE", default="MIT",
                      choices=["MIT", "GPLv2", "GPLv3"])
    _arg.add_pos("project_name", type=str, metavar="PROJECT")


@CommandExecutor(add_cmd_init)
def run_cmd_init(cmds: Command) -> int:
    project: Project = Project(
        name=cmds.args.project_name,
        allow_update=cmds.args.update,
    )
    project.create()
    return 0


@CommandArgument("python", description="Create a Python based command-line project")  # noqa:E501
def add_cmd(_arg: ArgParser):  # pylint: disable=unused-argument
    pass


@CommandExecutor(add_cmd, add_cmd_init)
def run_cmd(cmds: Command) -> int:  # pylint: disable=unused-argument
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {__urlhome__}.")  # noqa:E501
