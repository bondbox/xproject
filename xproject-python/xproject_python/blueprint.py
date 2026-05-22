# coding:utf-8

from pathlib import Path
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Union

from packaging.requirements import Requirement
from xkits_file.template import TemplateManagerPath
from xkits_file.template import Variable

TEMPLATES: Path = Path(__file__).parent / "templates"


class Requirements:
    """Requirements

    Reference:
        - [PEP 508](https://peps.python.org/pep-0508/)
            Dependency specification for Python Software Packages
    """

    def __init__(self, *requirements: Union[str, Requirement]):
        self.__requirements: List[Requirement] = [self.normalize(requirement) for requirement in requirements]  # noqa:E501

    def __iter__(self) -> Iterator[Requirement]:
        yield from self.__requirements

    def add(self, requirement: Union[str, Requirement]) -> None:
        self.__requirements.append(self.normalize(requirement))

    def dumps(self) -> str:
        return "\n".join(str(requirement) for requirement in self.__requirements)  # noqa:E501

    def dumpf(self, path: Union[str, Path]) -> None:
        with open(path, mode="w", encoding="utf-8") as whdl:
            whdl.write(f"{self.dumps()}\n")

    @classmethod
    def normalize(cls, requirement: Union[str, Requirement]) -> Requirement:  # noqa:E501
        """Normalized Names with PEP 503

        Reference:
            - https://peps.python.org/pep-0426/#name
            - https://peps.python.org/pep-0503/#normalized-names
        """
        from re import sub

        if not isinstance(requirement, Requirement):
            requirement = Requirement(requirement)

        requirement.name = sub(r"[-_.]+", "-", requirement.name).lower()
        return requirement


class Module:
    TEMPLATES_MODULE: Path = TEMPLATES / "module"
    TEMPLATES_PROJECT: Path = TEMPLATES / "project"

    def __init__(self, name: str, variable: Optional[Variable] = None):
        module_name: str = self.normalize(name)

        variables: Variable = variable.duplicate(module_name=module_name) \
            if isinstance(variable, Variable) else Variable(module_name=module_name)  # noqa:E501

        templates: TemplateManagerPath = TemplateManagerPath(variables)
        templates.load(self.TEMPLATES_MODULE)

        self.__name: str = module_name
        self.__templates: TemplateManagerPath = templates
        self.__requirements: Requirements = Requirements()

    @property
    def name(self) -> str:
        return self.__name

    @property
    def templates(self) -> TemplateManagerPath:
        return self.__templates

    @property
    def requirements(self) -> Requirements:
        return self.__requirements

    @classmethod
    def normalize(cls, name: str) -> str:
        return Requirements.normalize(requirement=name).name.replace("-", "_")


class Project:

    def __init__(self, name: str, modules: Optional[Sequence[str]] = None,
                 variable: Optional[Variable] = None,
                 allow_update: bool = False):
        project_name: str = Requirements.normalize(requirement=name).name

        variables: Variable = variable or Variable()
        variables["project_name"] = project_name

        self.__name: str = project_name
        self.__variables: Variable = variables
        # self.__license: str = license
        self.__allow_update: bool = allow_update
        self.__modules: Set[str] = {Module.normalize(module_name) for module_name in modules or [project_name]}  # noqa:E501

    def __iter__(self) -> Iterator[Module]:
        for module_name in self.__modules:
            yield Module(name=module_name, variable=self.variables)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def variables(self) -> Variable:
        return self.__variables

    def create(self) -> None:
        print(f"project name: {self.name}")
        for module in self:
            print(f"module name: {module.name}")
