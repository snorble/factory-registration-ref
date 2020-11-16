import os


def _env(name: str) -> str:
    try:
        return os.environ[name]
    except KeyError:
        raise RuntimeError("Missing required environment variable: {name}")


class class_property(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Settings:
    @class_property  # type: ignore
    @staticmethod
    def FACTORY_NAME() -> str:
        return _env("FACTORY_NAME")

    @class_property  # type: ignore
    @staticmethod
    def DEVICE_GATEWAY_SERVER() -> str:
        return _env("DEVICE_GATEWAY_SERVER")

    @class_property  # type: ignore
    @staticmethod
    def CA_KEY() -> str:
        return _env("CA_KEY")

    @class_property  # type: ignore
    @staticmethod
    def CA_CRT() -> str:
        return _env("CA_CRT")

    @class_property  # type: ignore
    @staticmethod
    def ROOT_CRT() -> str:
        return _env("ROOT_CRT")

    @class_property  # type: ignore
    @staticmethod
    def DEVICES_DIR() -> str:
        return _env("DEVICES_DIR")
