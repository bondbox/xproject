# coding:utf-8

from errno import ENOENT
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest import main
from unittest import mock

from xproject_python import projector

TEMPLATES = (root := Path(__file__).parent.parent.parent) / "templates"
TEMPLATES_PROJECT: Path = TEMPLATES / "project"
TEMPLATES_PACKAGE: Path = TEMPLATES / "package"
TEMPLATES_MODULE: Path = TEMPLATES / "module"


class TestModule(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.module_config = projector.ModuleConfig()
        cls.package_config = projector.PackageConfig(
            modules={"module": cls.module_config}
        )

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.module = projector.Module("module", self.package_config)

    def tearDown(self):
        pass

    def test_name(self):
        self.assertEqual(self.module.name, "module")


class TestPackage(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.module_config = projector.ModuleConfig()
        cls.package_config = projector.PackageConfig(
            modules={"module": cls.module_config}
        )

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @mock.patch.object(projector.Module, "TEMPLATES_MODULE", TEMPLATES_MODULE)  # noqa:E501
    @mock.patch.object(projector.Package, "TEMPLATES_PACKAGE", TEMPLATES_PACKAGE)  # noqa:E501
    def test_attribute_module_more_than_one(self):
        module1_config = projector.ModuleConfig(
            templates={projector.Module.ATTRIBUTE: True}
        )
        module2_config = projector.ModuleConfig(
            templates={projector.Module.ATTRIBUTE: False}
        )
        package_config = projector.PackageConfig(
            modules={"module1": module1_config, "module2": module2_config}
        )
        project_config = projector.ProjectConfig(
            packages={"package": package_config}
        )
        package = projector.Package("package", project_config)
        self.assertRaises(ValueError, package.dump, base=".")

    @mock.patch.object(projector.Package, "TEMPLATES_PACKAGE", TEMPLATES_PACKAGE)  # noqa:E501
    def test_attribute_module_less_than_one(self):
        package_config = projector.PackageConfig()
        project_config = projector.ProjectConfig(
            packages={"package": package_config}
        )
        package = projector.Package("package", project_config)
        self.assertRaises(ValueError, package.dump, base=".")


class TestProject(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = root.parent
        cls.configs = Path(__file__).parent / "configs"

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generate_no_such_file(self):
        self.assertEqual(projector.main([str(self.root)]), ENOENT)

    @mock.patch.object(projector.Module, "TEMPLATES_MODULE", TEMPLATES_MODULE)  # noqa:E501
    @mock.patch.object(projector.Package, "TEMPLATES_PACKAGE", TEMPLATES_PACKAGE)  # noqa:E501
    @mock.patch.object(projector.Project, "TEMPLATES_PROJECT", TEMPLATES_PROJECT)  # noqa:E501
    def test_generate(self):
        for config in self.configs.rglob("*.toml"):
            with TemporaryDirectory() as root:
                self.assertEqual(projector.main([root, f"--config={config}"]), 0)  # noqa:E501


if __name__ == "__main__":
    main()
