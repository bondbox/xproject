# coding:utf-8

from asyncio import run
from errno import ECANCELED
from pathlib import Path
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.layout.containers import HSplit
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.shortcuts import clear
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import TextArea
from xkits_command.actuator import Command
from xkits_command.actuator import CommandArgument
from xkits_command.actuator import CommandExecutor
from xkits_command.parser import ArgParser

from xproject_python.attribute import __project_desc__ as project_description
from xproject_python.attribute import __project_home__ as project_home
from xproject_python.attribute import __version__ as version
from xproject_python.configure import DEFAULT_CONFIG_FILE
from xproject_python.configure import ModuleConfig
from xproject_python.configure import PackageConfig
from xproject_python.configure import ProjectConfig


class Actuator():

    def __init__(self, label: str) -> None:
        self.__label: str = label

    @property
    def label(self) -> str:
        return self.__label

    async def action(self) -> None:
        raise NotImplementedError


class SelectExecuteDialog:

    def __init__(self, items: Sequence[Actuator], title: str = "Please select") -> None:  # noqa:E501
        self.__items: List[Actuator] = list(items)
        self.__title: str = title
        self.__index: int = 0

    @property
    def title(self) -> str:
        return self.__title

    @property
    def selected(self) -> Actuator:
        return self.__items[self.__index]

    def __prev(self, event: KeyPressEvent) -> None:  # pylint: disable=unused-argument # noqa:E501
        self.__index = max(0, self.__index - 1)

    def __next(self, event: KeyPressEvent) -> None:  # pylint: disable=unused-argument # noqa:E501
        self.__index = min(len(self.__items) - 1, self.__index + 1)

    async def __execute(self, event: KeyPressEvent) -> None:
        event.app.exit(result=await self.selected.action())

    def __get_menu(self) -> List[Tuple[str, str]]:
        result = [("class:title", f"{self.title}\n\n")]

        selected_item: Actuator = self.selected

        for item in self.__items:
            if item is selected_item:
                result.append(("class:selected", f"> {item.label}\n"))
            else:
                result.append(("class:unselected", f"  {item.label}\n"))

        return result

    async def run_async(self) -> None:
        layout = Layout(
            HSplit([
                Window(
                    content=FormattedTextControl(self.__get_menu, show_cursor=False),  # noqa:E501
                ),
            ])
        )

        style = Style.from_dict({
            "title": "bold ansiblue",
            "selected": "ansigreen bold",
            "unselected": "",
        })

        bindings = KeyBindings()
        bindings.add("up")(lambda event: self.__prev(event))
        bindings.add("down")(lambda event: self.__next(event))
        bindings.add("enter")(lambda event: self.__execute(event))

        return await Application(
            layout=layout,
            style=style,
            key_bindings=bindings,
            full_screen=True,
        ).run_async()


class TextInputDialog:

    def __init__(self, title: str = "Input") -> None:
        self.__title: str = title
        self.__text: str = ""

        self.__input_area: TextArea = TextArea(
            text=self.__text,
            multiline=False,
            style="bg:#222222 #ffffff",
        )

    @property
    def title(self) -> str:
        return self.__title

    def __accept(self, event: KeyPressEvent) -> None:
        event.app.exit(result=self.__input_area.text or None)

    def __cancel(self, event: KeyPressEvent) -> None:
        event.app.exit(result=None)

    async def run_async(self) -> Optional[str]:
        layout = Layout(
            HSplit([
                Window(
                    content=FormattedTextControl(lambda: [("class:title", f" {self.title} ")]),  # noqa:E501
                    height=1,
                    style="bg:ansiblue ansigreen",
                ),
                Window(height=1, char="\n"),
                self.__input_area,
                Window(height=1, char="\n"),
                Window(
                    content=FormattedTextControl(
                        lambda: [
                            ("class:button", " [Enter] Create "),
                            ("class:button", " [Esc] Cancel ")
                        ]
                    ),
                    height=1,
                    style="bg:ansiwhite ansiblack",
                ),
            ])
        )

        style = Style.from_dict({
            "title": "bold ansiblue",
            "button": "ansiyellow bold",
        })

        bindings = KeyBindings()
        bindings.add("enter")(lambda event: self.__accept(event))
        bindings.add("escape")(lambda event: self.__cancel(event))

        return await Application(
            layout=layout,
            style=style,
            key_bindings=bindings,
            full_screen=False,
        ).run_async()


class ModuleDialog(Actuator):

    class Back(Actuator):
        def __init__(self, parent: "ModuleDialog") -> None:
            super().__init__(label="Back package")
            self.__parent: ModuleDialog = parent

        @property
        def parent(self) -> "ModuleDialog":
            return self.__parent

        async def action(self) -> None:
            self.parent.exit()

    class Delete(Actuator):
        def __init__(self, parent: "ModuleDialog") -> None:
            super().__init__(label="Delete module")
            self.__parent: ModuleDialog = parent

        @property
        def parent(self) -> "ModuleDialog":
            return self.__parent

        async def action(self) -> None:
            module: ModuleDialog = self.parent
            package: PackageDialog = module.parent
            package.del_module(module_name=module.name)
            module.exit()

    def __init__(self, module_name: str, parent: "PackageDialog") -> None:
        super().__init__(label=f"Module: {module_name}")
        self.__parent: PackageDialog = parent
        self.__name: str = module_name
        self.__exit: bool = False

    def __iter__(self) -> Iterator[Actuator]:
        yield ModuleDialog.Back(self)
        yield ModuleDialog.Delete(self)

    @property
    def parent(self) -> "PackageDialog":
        return self.__parent

    @property
    def name(self) -> str:
        return self.__name

    def exit(self) -> bool:
        self.__exit = True
        return self.__exit

    async def action(self) -> None:
        self.__exit = False
        while not self.__exit:
            title: str = f"Module {self.name}"
            items: List[Actuator] = list(iter(self))
            await SelectExecuteDialog(items=items, title=title).run_async()  # noqa:E501


class PackageDialog(Actuator):

    class New(Actuator):
        def __init__(self, parent: "PackageDialog") -> None:
            super().__init__(label="Add new module")
            self.__parent: PackageDialog = parent

        @property
        def parent(self) -> "PackageDialog":
            return self.__parent

        async def action(self) -> None:
            if isinstance(result := await TextInputDialog(title=self.label).run_async(), str):  # noqa:E501
                await self.parent.add_module(result).action()

    class Back(Actuator):
        def __init__(self, parent: "PackageDialog") -> None:
            super().__init__(label="Back project")
            self.__parent: PackageDialog = parent

        @property
        def parent(self) -> "PackageDialog":
            return self.__parent

        async def action(self) -> None:
            self.parent.exit()

    class Delete(Actuator):
        def __init__(self, parent: "PackageDialog") -> None:
            super().__init__(label="Delete package")
            self.__parent: PackageDialog = parent

        @property
        def parent(self) -> "PackageDialog":
            return self.__parent

        async def action(self) -> None:
            package: PackageDialog = self.parent
            project: ProjectDialog = package.parent
            project.del_package(package_name=package.name)
            package.exit()

    def __init__(self, package_name: str, parent: "ProjectDialog") -> None:
        super().__init__(label=f"Package: {package_name}")
        self.__modules: Dict[str, ModuleDialog] = {}
        self.__parent: ProjectDialog = parent
        self.__name: str = package_name
        self.__exit: bool = False

    def __iter__(self) -> Iterator[Actuator]:
        yield PackageDialog.Back(self)
        yield PackageDialog.New(self)
        yield from self.__modules.values()
        yield PackageDialog.Delete(self)

    @property
    def parent(self) -> "ProjectDialog":
        return self.__parent

    @property
    def name(self) -> str:
        return self.__name

    def exit(self) -> bool:
        self.__exit = True
        return self.__exit

    @property
    def modules(self) -> Iterator[ModuleDialog]:
        yield from self.__modules.values()

    def add_module(self, module_name: str) -> ModuleDialog:
        if (module := self.__modules.get(module_name)) is None:
            module = ModuleDialog(module_name=module_name, parent=self)
            self.__modules[module.name] = module
        return module

    def del_module(self, module_name: str) -> Optional[ModuleDialog]:
        return self.__modules.pop(module_name, None)

    async def action(self) -> None:
        self.__exit = False
        while not self.__exit:
            title: str = f"Package {self.name}"
            items: List[Actuator] = list(iter(self))
            await SelectExecuteDialog(items=items, title=title).run_async()  # noqa:E501


class ProjectDialog():

    class New(Actuator):
        def __init__(self, parent: "ProjectDialog") -> None:
            super().__init__(label="Add new package")
            self.__parent: ProjectDialog = parent

        @property
        def parent(self) -> "ProjectDialog":
            return self.__parent

        async def action(self) -> None:
            if isinstance(result := await TextInputDialog(title=self.label).run_async(), str):  # noqa:E501
                await self.parent.add_package(result).action()

    class Create(Actuator):
        def __init__(self, parent: "ProjectDialog") -> None:
            super().__init__(label="Create project")
            self.__parent: ProjectDialog = parent

        @property
        def parent(self) -> "ProjectDialog":
            return self.__parent

        async def action(self) -> None:
            self.parent.exit(cancel=False)

    class Cancel(Actuator):
        def __init__(self, parent: "ProjectDialog") -> None:
            self.__parent: ProjectDialog = parent
            super().__init__(label="Cancel")

        @property
        def parent(self) -> "ProjectDialog":
            return self.__parent

        async def action(self) -> None:
            self.parent.exit(cancel=True)

    def __init__(self, project_name: str) -> None:
        self.__packages: Dict[str, PackageDialog] = {}
        self.__name: str = project_name
        self.__exit: bool = False
        super().__init__()

    def __iter__(self) -> Iterator[Actuator]:
        yield ProjectDialog.Create(self)
        yield ProjectDialog.New(self)
        yield from self.__packages.values()
        yield ProjectDialog.Cancel(self)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def cancel(self) -> bool:
        return self.__cancel

    def exit(self, cancel: bool) -> bool:
        self.__cancel = cancel
        self.__exit = True
        return self.__exit

    @property
    def packages(self) -> Iterator[PackageDialog]:
        yield from self.__packages.values()

    def add_package(self, package_name: str) -> PackageDialog:
        if (package := self.__packages.get(package_name)) is None:
            package = PackageDialog(package_name=package_name, parent=self)
            self.__packages[package.name] = package
        return package

    def del_package(self, package_name: str) -> Optional[PackageDialog]:
        return self.__packages.pop(package_name, None)

    async def run_async(self) -> None:
        while not self.__exit:
            title: str = f"Project {self.name}"
            items: List[Actuator] = list(iter(self))
            await SelectExecuteDialog(items=items, title=title).run_async()
            clear()


@CommandArgument("dialog", help="Start Python project configuration dialogue")
def add_cmd_dialog(_arg: ArgParser):
    _arg.add_pos("project_name", type=str, nargs="?", metavar="PROJECT")


@CommandExecutor(add_cmd_dialog)
def run_cmd_dialog(cmds: Command) -> int:
    project_name: str = cmds.args.project_name or Path.cwd().name
    project_dialog = ProjectDialog(project_name=project_name)
    run(project_dialog.run_async())

    if project_dialog.cancel:
        return ECANCELED

    package_dialogs: List[PackageDialog] = list(project_dialog.packages)
    multiple: bool = True if len(package_dialogs) > 1 else False

    packages: Dict[str, PackageConfig] = {}
    for package_dialog in package_dialogs:
        modules: Dict[str, ModuleConfig] = {
            module_dialog.name: ModuleConfig(base=module_dialog.name)
            for module_dialog in package_dialog.modules
        }

        packages[package_dialog.name] = PackageConfig(
            base=package_dialog.name if multiple else ".",
            version="0.1.alpha.1",
            modules=modules,
        )

    ProjectConfig.load(
        project={
            'name': project_dialog.name,
            'home': project_home,
            'description': project_description,
        },
        packages=packages,
    ).dumpf(DEFAULT_CONFIG_FILE)

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = version
    return cmds.run(root=add_cmd_dialog, argv=argv, epilog=f"For more, please visit {project_home}.")  # noqa:E501


if __name__ == "__main__":
    run(ProjectDialog("demo").run_async())
