# coding:utf-8

from dataclasses import dataclass
from dataclasses import field
from errno import ENOENT
from sys import version_info
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
from xproject_python.utilities import Requirements

DEFAULT_CONFIG_FILE: str = f".{xproject_name}_python"


@dataclass
class AuthorConfig(Settings):
    name: str
    email: str


@dataclass
class DataConfig(Settings):
    include: Dict[str, str] = field(default_factory=dict)
    package: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ModuleConfig(Settings):
    base: Optional[str] = None
    data: Optional[DataConfig] = None
    package: Optional[List[str]] = None
    exclude: List[str] = field(default_factory=list)
    omitted: List[str] = field(default_factory=list)
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
    _arg.add_opt_on("--create", help="Create configuration file if not exists")


@CommandExecutor(add_cmd_config_update)
def run_cmd_config_update(cmds: Command) -> int:
    try:
        project_config: ProjectConfig = ProjectConfig.loadf(cmds.args.file)
    except FileNotFoundError:
        cmds.stderr_red(f"Configuration file {cmds.args.file} not found")
        if not cmds.args.create:
            return ENOENT
        project_config: ProjectConfig = ProjectConfig()

    if len(project_config.packages) < 1:
        project_config.packages[project_config.name] = PackageConfig()
    for package_name, package_config in project_config.packages.items():
        if not package_config.requires_python:
            requires_python: str = f">={version_info.major}.{version_info.minor}"  # noqa:E501
            cmds.stderr_yellow(f"Update package {package_name} requires-python to {requires_python}")  # noqa:E501
            package_config.requires_python = requires_python
        if (modules := len(package_config.modules)) < 1:
            module_name: str = Requirements.normalize(requirement=package_name).name.replace("-", "_")  # noqa:E501
            cmds.stderr_yellow(f"Add module {module_name} to package {package_name}")  # noqa:E501
            package_config.modules[module_name] = ModuleConfig(
                base=module_name,
                omitted=[
                    "attribute.py",
                    "unittest/*",
                ],
                exclude=[
                    "unittest",
                ],
                templates={
                    "attribute.py": True,
                }
            )
        else:
            for module_name, module_config in package_config.modules.items():  # noqa:E501
                if module_config.base is None:
                    cmds.stderr_yellow(f"Update module {package_name}/{module_name} base to {module_name}")  # noqa:E501
                    module_config.base = module_name
                if modules == 1:
                    module_config.templates.setdefault("attribute.py", True)  # noqa:E501
    project_config.dumpf(cmds.args.file)
    cmds.stderr_green(f"Configuration file {cmds.args.file} updated")
    return 0


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
                    "xkits-command>=0.7",
                    "xkits-config-toml>=0.9",
                    "xkits-file>=0.10",
                ],
                modules={
                    f"{project_name}-python": ModuleConfig(
                        base=f"{project_name}_python",
                        data=DataConfig(
                            include={
                                "templates": "templates",
                            },
                        ),
                        package=None,
                        exclude=[
                            "unittest",
                        ],
                        omitted=[
                            "attribute.py",
                            "unittest/*",
                        ],
                        scripts={
                            f"{project_name}-python-config": "configure:main",
                            f"{project_name}-python-generate": "projector:main",  # noqa:E501
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
