# coding:utf-8

from errno import ENOENT
from pathlib import Path
from unittest import TestCase
from unittest import main

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
        self.assertEqual(configure.main(["update"]), ENOENT)

    def test_update(self):
        for config in self.configs.rglob("*.toml"):
            self.assertEqual(configure.main([f"--file={config}", "update"]), 0)  # noqa:E501


if __name__ == "__main__":
    main()
