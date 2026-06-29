# coding:utf-8

from configparser import ConfigParser
from pathlib import Path
from typing import Iterator
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union

from packaging.requirements import Requirement

CFGT = TypeVar("CFGT", bound="Configuration")


class Configuration:

    def __init__(self, parser: Optional[ConfigParser] = None):
        self.__parser: ConfigParser = parser or ConfigParser()

    @property
    def parser(self) -> ConfigParser:
        return self.__parser

    def dump(self, filepath: Union[str, Path], writable: bool = False):
        if isinstance(filepath, str):
            filepath = Path(filepath)  # pragma: no cover

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
            filepath = Path(filepath)  # pragma: no cover

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
