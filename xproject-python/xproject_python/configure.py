# coding:utf-8

from dataclasses import dataclass
from dataclasses import field
from errno import ENOENT
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence

from xkits_command.actuator import Command
from xkits_command.actuator import CommandArgument
from xkits_command.actuator import CommandExecutor
from xkits_command.parser import ArgParser
from xkits_config import Settings
from xkits_config_toml import ConfigTOML

from xproject_python.attribute import __project_home__ as xproject_home
from xproject_python.attribute import __project_name__ as xproject_name
from xproject_python.attribute import __version__ as version

DEFAULT_CONFIG_FILE: str = f".{xproject_name}_python"


@dataclass
class AuthorConfig(Settings):
    name: str
    email: str


@dataclass
class ModuleConfig(Settings):
    base: Optional[str] = None
    package: Optional[List[str]] = None
    omitted: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    include: Dict[str, str] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)
    templates: Dict[str, bool] = field(default_factory=dict)


@dataclass
class PackageConfig(Settings):  # pylint: disable=too-many-instance-attributes
    base: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    requires_python: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    modules: Dict[str, ModuleConfig] = field(default_factory=dict)
    max_complexity: int = 10
    max_line_length: int = 127


@dataclass
class ProjectConfig(ConfigTOML):
    name: str = xproject_name
    home: str = xproject_home
    description: str = f"Automatically created by [{xproject_name}]({xproject_home})."  # noqa:E501
    authors: Dict[str, AuthorConfig] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    packages: Dict[str, PackageConfig] = field(default_factory=dict)
    version: str = "0.1.alpha.1"


@CommandArgument("update", help="Update Python project configuration")
def add_cmd_config_update(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_config_update)
def run_cmd_config_update(cmds: Command) -> int:
    try:
        ProjectConfig.loadf(cmds.args.file).dumpf(cmds.args.file)
        cmds.stderr_green(f"Configuration file {cmds.args.file} updated")
        return 0
    except FileNotFoundError:
        cmds.stderr_red(f"Configuration file {cmds.args.file} not found")
        return ENOENT


@CommandArgument("config", help="Manage Python project configuration")
def add_cmd_config(_arg: ArgParser):
    _arg.add_argument("--file", dest="file", type=str, nargs=None,
                      metavar="FILE", default=DEFAULT_CONFIG_FILE,
                      help="Specify configuration file")


@CommandExecutor(add_cmd_config, add_cmd_config_update)
def run_cmd_config(cmds: Command) -> int:  # pylint: disable=unused-argument
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = version
    return cmds.run(root=add_cmd_config, argv=argv, epilog=f"For more, please visit {xproject_home}.")  # noqa:E501


if __name__ == "__main__":
    project_name: str = "xproject"
    project_home: str = "https://github.com/bondbox/xproject/"
    project_desc: str = "Initialize project files"

    ProjectConfig(
        name=project_name,
        home=project_home,
        description=project_desc,
        authors={
            "zoumingzhe": AuthorConfig(
                name="Mingzhe Zou",
                email="zoumingzhe@outlook.com",
            ),
        },
        keywords=[
            "project",
        ],
        packages={
            f"{project_name}-python": PackageConfig(
                base=f"{project_name}-python",
                version=None,
                requires_python=">=3.8",
                authors=[
                    "zoumingzhe",
                ],
                keywords=[
                ],
                requirements=[
                    "xkits-command",
                    "xkits-config-toml>=0.5",
                    "xkits-file>=0.9",
                    "prompt-toolkit",
                ],
                modules={
                    f"{project_name}-python": ModuleConfig(
                        base=f"{project_name}_python",
                        package=None,
                        omitted=[
                            "attribute.py",
                            "unittest/*",
                        ],
                        exclude=[
                            "unittest",
                        ],
                        include={
                            "templates": "templates",
                        },
                        scripts={
                            f"{project_name}-python": "blueprint:main",
                        },
                        templates={
                            "__init__.py": False,
                            "attribute.py": True,
                        },
                    ),
                },
                max_complexity=15,
                max_line_length=127,
            ),
        },
        version="0.1.alpha.1",
    ).dumpf(DEFAULT_CONFIG_FILE)
