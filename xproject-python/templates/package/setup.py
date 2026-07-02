# coding=utf-8

from setuptools import setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    """Customized setuptools install command"""

    def run(self):
        super().run()  # Run the standard installation


setup(
    cmdclass={
        "install": CustomInstallCommand,
    }
)
