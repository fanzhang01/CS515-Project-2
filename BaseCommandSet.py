from typing import Callable, Tuple


class BaseCommandSet:
    def __init__(self, engine=None, **kwargs) -> None:
        self.engine = engine
        self.engine_api = kwargs

    def __setattr__(self, key, value) -> None:
        if "_initialized" in self.__dict__ and key in dir(self):
            raise AttributeError(f"{key} already exists")

        super.__setattr__(self, key, value)

    def __delattr__(self, item):
        object.__delattr__(self, item)

    @property
    def engine(self):
        return self.__direction_mapping

    @engine.setter
    def engine(self, mapping) -> None:
        self.__direction_mapping = mapping

    def add_commands(self, name: str, command: Callable) -> Tuple[str, bool]:
        try:
            assert type(name, str)
            assert type(command, Callable)
            self.__setattr__(name, command)
            setattr(self.engine, name, command)
        except (AssertionError, AttributeError) as e:
            return e, False

        return f"{name} added", True

    def del_methods(self, item: str) -> Tuple[str, bool]:
        if item not in dir(self):
            return f"{item} does not exist", False


if __name__ == "__main__":
    pass
