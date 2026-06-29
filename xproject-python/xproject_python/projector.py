# coding:utf-8

from errno import ENOENT
from json import dumps
from pathlib import Path
from sys import version_info
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from packaging.specifiers import SpecifierSet
from tomli import load
from tomli_w import dump
from xkits_command.actuator import Command
from xkits_command.actuator import CommandArgument
from xkits_command.actuator import CommandExecutor
from xkits_command.parser import ArgParser
from xkits_file.template import TemplateManagerPath
from xkits_file.template import Variable

from xproject_python.attribute import __project_home__ as project_home
from xproject_python.attribute import __version__ as version
from xproject_python.configure import AuthorConfig
from xproject_python.configure import DEFAULT_CONFIG_FILE
from xproject_python.configure import ModuleConfig
from xproject_python.configure import PackageConfig
from xproject_python.configure import ProjectConfig
from xproject_python.utilities import CoverageRC
from xproject_python.utilities import Flake8
from xproject_python.utilities import PylintRC
from xproject_python.utilities import Requirements

TEMPLATES: Path = Path(__file__).parent / "templates"


class Module:
    TEMPLATES_MODULE: Path = TEMPLATES / "module"
    ATTRIBUTE: str = "attribute.py"
    DOT: str = "."

    def __init__(self, name: str, config: PackageConfig, variable: Optional[Variable] = None):  # noqa:E501
        option: ModuleConfig = config.modules[name]

        variables: Variable = variable.duplicate() if isinstance(variable, Variable) else Variable()  # noqa:E501
        variables.set_default("module_name", module_name := self.normalize(name))  # noqa:E501

        module_base: str = option.base or self.DOT

        self.__name: str = module_name
        self.__base: str = module_base
        self.__option: ModuleConfig = option
        self.__variable: Variable = variables

    @property
    def name(self) -> str:
        return self.__name

    @property
    def base(self) -> str:
        return self.__base

    @property
    def option(self) -> ModuleConfig:
        return self.__option

    @property
    def variable(self) -> Variable:
        return self.__variable

    @property
    def include_data(self) -> Iterator[Tuple[str, str]]:
        if (data := self.option.data) is not None:
            for src, dst in data.include.items():
                yield src, self.path_join(dst)

    @property
    def exclude(self) -> Iterator[str]:
        for path in self.option.exclude:
            yield self.path_join(path)

    @property
    def package(self) -> Iterator[str]:
        if self.option.package is not None:
            for path in self.option.package:
                yield self.path_join(path)
        else:
            yield self.base

    @property
    def omitted(self) -> Iterator[str]:
        for path in self.option.omitted:
            yield self.path_join(path)

    @property
    def scripts(self) -> Iterator[Tuple[str, str]]:
        for name, entry in self.option.scripts.items():
            point: str = (parts := entry.rsplit(":", maxsplit=1)).pop()
            yield name, ":".join([self.dot_join(*parts), point])

    def prepend(self, *parts: str) -> Tuple[str, ...]:
        return (base, *parts) if (base := self.base) != self.DOT else parts  # noqa:E501

    def dot_join(self, *parts: str) -> str:
        return self.DOT.join(self.prepend(*parts))

    def path_join(self, *parts: str) -> str:
        return Path(*self.prepend(*parts)).as_posix()

    @classmethod
    def normalize(cls, name: str) -> str:
        return Requirements.normalize(requirement=name).name.replace("-", "_")

    def dump(self, base: Union[str, Path], writable: bool = False) -> None:
        root: Path = base if isinstance(base, Path) else Path(base)

        files: List[str] = [
            name for name, edit in self.option.templates.items()
            if not (root / name).exists() or edit
        ]

        templates: TemplateManagerPath = TemplateManagerPath(self.variable)
        templates.load(base=self.TEMPLATES_MODULE, include=files)
        templates.dump(base=root, writable=writable)


class Pyproject:  # pylint: disable=too-many-public-methods
    FILENAME: str = "pyproject.toml"

    def __init__(self, coder: Dict[str, Any]):
        self.__coder: Dict[str, Any] = coder

    @property
    def coder(self) -> Dict[str, Any]:
        return self.__coder

    @property
    def project(self) -> Dict[str, Any]:
        return self.coder["project"]

    @property
    def project_authors(self) -> List[Dict[str, str]]:
        return self.project["authors"]

    @property
    def project_keywords(self) -> List[str]:
        return self.project["keywords"]

    @property
    def project_scripts(self) -> Dict[str, Any]:
        return self.project["scripts"]

    @property
    def project_urls(self) -> Dict[str, str]:
        return self.project["urls"]

    @property
    def tool(self) -> Dict[str, Any]:
        return self.coder["tool"]

    @property
    def tool_hatch(self) -> Dict[str, Any]:
        return self.tool["hatch"]

    @property
    def tool_hatch_build(self) -> Dict[str, Any]:
        return self.tool_hatch["build"]

    @property
    def tool_hatch_build_targets(self) -> Dict[str, Any]:
        return self.tool_hatch_build["targets"]

    @property
    def tool_hatch_build_targets_sdist(self) -> Dict[str, Any]:
        return self.tool_hatch_build_targets["sdist"]

    @property
    def tool_hatch_build_targets_sdist_force_include(self) -> Dict[str, Any]:
        return self.tool_hatch_build_targets_sdist["force-include"]

    @property
    def tool_hatch_build_targets_sdist_exclude(self) -> List[str]:
        return self.tool_hatch_build_targets_sdist["exclude"]

    @property
    def tool_hatch_build_targets_sdist_packages(self) -> List[str]:
        return self.tool_hatch_build_targets_sdist["packages"]

    @property
    def tool_hatch_build_targets_wheel(self) -> Dict[str, Any]:
        return self.tool_hatch_build_targets["wheel"]

    @property
    def tool_hatch_build_targets_wheel_force_include(self) -> Dict[str, Any]:
        return self.tool_hatch_build_targets_wheel["force-include"]

    @property
    def tool_hatch_build_targets_wheel_exclude(self) -> List[str]:
        return self.tool_hatch_build_targets_wheel["exclude"]

    @property
    def tool_hatch_build_targets_wheel_packages(self) -> List[str]:
        return self.tool_hatch_build_targets_wheel["packages"]

    @property
    def tool_hatch_metadata(self) -> Dict[str, Any]:
        return self.tool_hatch["metadata"]

    @property
    def tool_hatch_metadata_hooks(self) -> Dict[str, Any]:
        return self.tool_hatch_metadata["hooks"]

    @property
    def tool_hatch_metadata_hooks_requirements_txt(self) -> Dict[str, Any]:
        return self.tool_hatch_metadata_hooks["requirements_txt"]

    @property
    def tool_hatch_metadata_hooks_requirements_txt_files(self) -> List[str]:
        return self.tool_hatch_metadata_hooks_requirements_txt["files"]

    @property
    def tool_hatch_version(self) -> Dict[str, str]:
        return self.tool_hatch["version"]

    def dump(self, filepath: Union[str, Path], writable: bool = False):
        if isinstance(filepath, str):
            filepath = Path(filepath)  # pragma: no cover

        if not filepath.exists() or writable:
            with filepath.open("wb") as whdl:
                dump(self.coder, whdl)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "Pyproject":
        if isinstance(filepath, str):
            filepath = Path(filepath)  # pragma: no cover

        with filepath.open("rb") as rhdl:
            return cls(coder=load(rhdl))


class Package:  # pylint: disable=too-many-instance-attributes
    TEMPLATES_PACKAGE: Path = TEMPLATES / "package"
    FILES: List[str] = ["Makefile"]

    def __init__(self, name: str, config: ProjectConfig, variable: Optional[Variable] = None):  # pylint: disable=too-many-locals # noqa:E501
        option: PackageConfig = config.packages[name]

        variables: Variable = variable.duplicate() if isinstance(variable, Variable) else Variable()  # noqa:E501
        variables.set_default("package_name", package_name := Requirements.normalize(requirement=name).name)  # noqa:E501
        variables.set_default("package_description", package_description := option.description or config.description)  # noqa:E501
        variables.set_default("package_version", package_version := option.version or config.version)  # noqa:E501

        authors: List[AuthorConfig] = [config.authors[index] for index in option.authors]  # noqa:E501
        variables.set_default("authors", dumps(authors, indent=4, default=lambda i: i.__dict__))  # noqa:E501

        coverage: CoverageRC = CoverageRC.load(self.TEMPLATES_PACKAGE / CoverageRC.FILENAME)  # noqa:E501
        flake8: Flake8 = Flake8.load(self.TEMPLATES_PACKAGE / Flake8.FILENAME)
        pylint: PylintRC = PylintRC.load(self.TEMPLATES_PACKAGE / PylintRC.FILENAME)  # noqa:E501

        python_version: str = option.requires_python or f">={version_info.major}.{version_info.minor}"  # noqa:E501
        pyproject: Pyproject = Pyproject.load(self.TEMPLATES_PACKAGE / Pyproject.FILENAME)  # noqa:E501
        pyproject.project["name"] = package_name
        pyproject.project["description"] = package_description
        pyproject.project["requires-python"] = python_version
        pyproject.project_authors.extend(author.__dict__ for author in authors)
        pyproject.project_keywords.extend(config.keywords)
        pyproject.project_keywords.extend(option.keywords)
        pyproject.project_urls["Homepage"] = config.home

        requirements: Requirements = Requirements()
        for requirement in option.requirements:
            requirements.add(requirement)

        package_base: str = option.base or (package_name if len(config.packages) > 1 else Module.DOT)  # noqa:E501

        self.__name: str = package_name
        self.__base: str = package_base
        self.__version: str = package_version
        self.__option: PackageConfig = option
        self.__variable: Variable = variables
        self.__coverage: CoverageRC = coverage
        self.__flake8: Flake8 = flake8
        self.__pylint: PylintRC = pylint
        self.__pyproject: Pyproject = pyproject
        self.__requirements: Requirements = requirements

    def __iter__(self) -> Iterator[Module]:
        for name in self.option.modules:
            yield Module(name=name, config=self.option, variable=self.variable)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def base(self) -> str:
        return self.__base

    @property
    def version(self) -> str:
        return self.__version

    @property
    def option(self) -> PackageConfig:
        return self.__option

    @property
    def variable(self) -> Variable:
        return self.__variable

    @property
    def coverage(self) -> CoverageRC:
        return self.__coverage

    @property
    def flake8(self) -> Flake8:
        return self.__flake8

    @property
    def pylint(self) -> PylintRC:
        return self.__pylint

    @property
    def pyproject(self) -> Pyproject:
        return self.__pyproject

    @property
    def requirements(self) -> Requirements:
        return self.__requirements

    def dump(self, base: Union[str, Path], writable: bool = False) -> None:  # pylint: disable=too-many-locals # noqa:E501
        root: Path = base if isinstance(base, Path) else Path(base)
        modules: List[Module] = list(iter(self))

        attribute_modules: List[Module] = []
        coverage_omit: str = ""
        coverage_source: str = ""
        flake8_exclude: str = ""
        flake8_modules: List[str] = []
        pylint_files: List[str] = []

        for module in sorted(modules, key=lambda m: m.base):
            for src, dst in module.include_data:
                self.pyproject.tool_hatch_build_targets_sdist_force_include[src] = dst  # noqa:E501
                self.pyproject.tool_hatch_build_targets_wheel_force_include[src] = dst  # noqa:E501

            for exclude in module.exclude:
                self.pyproject.tool_hatch_build_targets_sdist_exclude.append(exclude)  # noqa:E501
                self.pyproject.tool_hatch_build_targets_wheel_exclude.append(exclude)  # noqa:E501
                flake8_exclude += f"\n{exclude}"

            for package in module.package:
                self.pyproject.tool_hatch_build_targets_sdist_packages.append(package)  # noqa:E501
                self.pyproject.tool_hatch_build_targets_wheel_packages.append(package)  # noqa:E501
                coverage_source += f"\n{package.removesuffix('.py')}"
                flake8_modules.append(package)

            pylint_files.append(f"{module.base}/*.py")

            for omitted in module.omitted:
                coverage_omit += f"\n{omitted}"

            for script_name, script_entry in module.scripts:
                self.pyproject.project_scripts[script_name] = script_entry

            if Module.ATTRIBUTE in module.option.templates:
                attribute_modules.append(module)

        if (attribute_module_number := len(attribute_modules)) > 1:
            raise ValueError(f"Package {self.name} has more than one attribute module: {', '.join(m.name for m in attribute_modules)}")  # noqa:E501
        if attribute_module_number < 1:
            raise ValueError(f"Package {self.name} has no attribute module")

        self.coverage.parser["run"]["omit"] = coverage_omit
        self.coverage.parser["run"]["source"] = coverage_source
        self.flake8.parser["flake8"]["exclude"] = flake8_exclude
        self.flake8.parser["flake8"]["max-complexity"] = str(self.option.max_complexity)  # noqa:E501
        self.flake8.parser["flake8"]["max-line-length"] = str(self.option.max_line_length)  # noqa:E501

        variables: Variable = self.variable
        variables.set_default("attribute_module", attribute_modules[0].dot_join(Path(Module.ATTRIBUTE).stem))  # noqa:E501
        variables.set_default("flake8_modules", " ".join(flake8_modules))
        variables.set_default("pylint_files", " ".join(pylint_files))

        templates: TemplateManagerPath = TemplateManagerPath(variables)
        templates.load(base=self.TEMPLATES_PACKAGE, include=self.FILES)
        templates.dump(base=root, writable=writable)

        self.requirements.dumpf(filepath=root / Requirements.FILENAME, writable=writable)  # noqa:E501
        self.pyproject.tool_hatch_metadata_hooks_requirements_txt_files.append(Requirements.FILENAME)  # noqa:E501
        self.pyproject.tool_hatch_version["path"] = attribute_modules[0].path_join(Module.ATTRIBUTE)  # noqa:E501
        self.pyproject.dump(filepath=root / Pyproject.FILENAME, writable=writable)  # noqa:E501

        self.coverage.dump(filepath=root / CoverageRC.FILENAME, writable=writable)  # noqa:E501
        self.flake8.dump(filepath=root / Flake8.FILENAME, writable=writable)  # noqa:E501
        self.pylint.dump(filepath=root / PylintRC.FILENAME, writable=writable)  # noqa:E501

        for module in modules:
            module.dump(base=root / module.base, writable=writable)


class Project:
    TEMPLATES_PROJECT: Path = TEMPLATES / "project"

    def __init__(self, config: ProjectConfig):
        project_name: str = Requirements.normalize(requirement=config.name).name  # noqa:E501

        variables: Variable = Variable(
            project_name=project_name,
            project_home=config.home,
            project_description=config.description,
        )

        self.__name: str = project_name
        self.__option: ProjectConfig = config
        self.__variable: Variable = variables

    def __iter__(self) -> Iterator[Package]:
        for name in self.option.packages:
            yield Package(name=name, config=self.option, variable=self.variable)  # noqa:E501

    @property
    def name(self) -> str:
        return self.__name

    @property
    def option(self) -> ProjectConfig:
        return self.__option

    @property
    def variable(self) -> Variable:
        return self.__variable

    def dump(self, base: Union[str, Path], writable: bool = False) -> None:
        root: Path = base if isinstance(base, Path) else Path(base)

        templates: TemplateManagerPath = TemplateManagerPath(self.variable)
        templates.load(base=self.TEMPLATES_PROJECT, include=None)
        templates.dump(base=root, writable=writable)

        packages: Dict[str, Package] = {package.name: package for package in iter(self)}  # noqa:E501

        for package in packages.values():
            dest: Path = root / package.base

            for requirement in package.requirements:
                if dependence := packages.get(requirement.name):
                    requirement.specifier = SpecifierSet(f">={dependence.version}")  # noqa:E501

            package.dump(base=dest, writable=writable)

            if dest != root:
                if not (readme_link := dest / "readme.md").exists():
                    readme_link.symlink_to("../readme.md")


@CommandArgument("generate", help="Create or update Python project files")
def add_cmd_generate(_arg: ArgParser):
    _arg.add_opt_on("--change", help="allow changes to existing files")
    _arg.add_opt("--config", dest="config", type=str, nargs=None,
                 metavar="FILE", default=DEFAULT_CONFIG_FILE,
                 help="Specify configuration file")
    _arg.add_pos("root", type=str, nargs="?", metavar="PATH", default=".",
                 help="Project root directory")


@CommandExecutor(add_cmd_generate)
def run_cmd_generate(cmds: Command) -> int:
    try:
        config: ProjectConfig = ProjectConfig.loadf(cmds.args.config)
    except FileNotFoundError:
        cmds.stderr_red(f"Configuration file {cmds.args.config} not found")
        return ENOENT

    root: Path = Path(cmds.args.root).resolve()
    cmds.stderr_yellow(f"Generate to root directory: {root}")

    project: Project = Project(config=config)
    project.dump(base=root, writable=cmds.args.change)
    cmds.stderr_green(f"Project {project.name} generated")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = version
    return cmds.run(root=add_cmd_generate, argv=argv, epilog=f"For more, please visit {project_home}.")  # noqa:E501
