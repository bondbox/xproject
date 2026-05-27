# coding:utf-8

from configparser import ConfigParser
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from packaging.requirements import Requirement
from toml import dump
from toml import load


CFGT = TypeVar("CFGT", bound="Configuration")


class Configuration:

    def __init__(self, parser: Optional[ConfigParser] = None):
        self.__parser: ConfigParser = parser or ConfigParser()

    @property
    def parser(self) -> ConfigParser:
        return self.__parser

    def dump(self, filepath: Union[str, Path], writable: bool = False):
        if isinstance(filepath, str):
            filepath = Path(filepath)

        if not filepath.exists() or writable:
            with filepath.open("w", encoding="utf-8") as whdl:
                self.parser.write(whdl)

    @classmethod
    def load(cls: Type[CFGT], filepath: Union[str, Path]) -> CFGT:
        (parser := ConfigParser()).read(filepath)
        return cls(parser=parser)


class CoverageRC(Configuration):
    FILENAME: str = ".coveragerc"


class Flake8(Configuration):
    FILENAME: str = ".flake8"


class PylintRC(Configuration):
    FILENAME: str = ".pylintrc"


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
    def tool_hatch_version(self) -> List[str]:
        return self.tool_hatch["version"]

    def dump(self, filepath: Union[str, Path], writable: bool = False):
        if isinstance(filepath, str):
            filepath = Path(filepath)

        if not filepath.exists() or writable:
            with filepath.open("w", encoding="utf-8") as whdl:
                dump(self.coder, whdl)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "Pyproject":
        if isinstance(filepath, str):
            filepath = Path(filepath)

        with filepath.open("r", encoding="utf-8") as rhdl:
            return cls(coder=load(rhdl))


class Requirements:
    """Requirements

    Reference:
        - [PEP 508](https://peps.python.org/pep-0508/)
            Dependency specification for Python Software Packages
    """
    FILENAME: str = "requirements.txt"

    def __init__(self, *requirements: Union[str, Requirement]):
        self.__requirements: List[Requirement] = [self.normalize(requirement) for requirement in requirements]  # noqa:E501

    def __iter__(self) -> Iterator[Requirement]:
        yield from self.__requirements

    def add(self, requirement: Union[str, Requirement]) -> None:
        self.__requirements.append(self.normalize(requirement))

    def dumps(self) -> str:
        return "\n".join(str(requirement) for requirement in self.__requirements)  # noqa:E501

    def dumpf(self, filepath: Union[str, Path], writable: bool = False) -> None:  # noqa:E501
        if isinstance(filepath, str):
            filepath = Path(filepath)

        if not filepath.exists() or writable:
            with filepath.open("w", encoding="utf-8") as whdl:
                whdl.write(self.dumps())
                whdl.write("\n")

    @classmethod
    def normalize(cls, requirement: Union[str, Requirement]) -> Requirement:  # noqa:E501
        """Normalized Names with PEP 503

        Reference:
            - https://peps.python.org/pep-0426/#name
            - https://peps.python.org/pep-0503/#normalized-names
        """
        from re import sub  # pylint: disable=import-outside-toplevel

        if not isinstance(requirement, Requirement):
            requirement = Requirement(requirement)

        requirement.name = sub(r"[-_.]+", "-", requirement.name).lower()
        return requirement
