# flake8: noqa: E402

from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):  # pylint: disable=R0903

    def update(self, metadata: dict) -> None:
        pass
