# coding:utf-8

from errno import ENOENT
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest import main
from unittest import mock

from xproject_python import configure


class TestConfig(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.configs = Path(__file__).parent / "configs"

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_update_no_such_file(self):
        with TemporaryDirectory() as root:
            config = Path(root) / configure.DEFAULT_CONFIG_FILE
            self.assertEqual(configure.main([f"--file={config}", "update"]), ENOENT)  # noqa:E501
            self.assertEqual(configure.main([f"--file={config}", "update", "--create"]), 0)  # noqa:E501

    @mock.patch.object(configure.ProjectConfig, "dumpf", mock.MagicMock())
    def test_update(self):
        for config in self.configs.rglob("*.toml"):
            self.assertEqual(configure.main([f"--file={config}", "update"]), 0)


if __name__ == "__main__":
    main()
