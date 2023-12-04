from typing import Generator, Tuple

from BaseCommandSet import BaseCommandSet

# from draft import GameEngine


class CommandSet(BaseCommandSet):
    DIRECTIONS = (
        "north",
        "south",
        "east",
        "west",
        "northeast",
        "southeast",
        "southwest",
        "northwest",
    )

    def __init__(self, engine=None, **kwargs):
        super().__init__(engine, **kwargs)

    def go(self, direction: str = "") -> Tuple[str, bool]:
        if not direction:
            return "Sorry, you need to 'go' somewhere.", False

        exits: dict = self.engine.get_current_room().get("exits")
        if direction not in exits:
            return f"There's no way to go {direction}", False

        self.engine.current_room = exits.get(direction)
        return f"You go {direction}", True

    def look(self) -> Generator[str, None, None]:
        current_room: dict = self.engine.get_current_room()
        yield f'> {current_room.get("name")}\n'
        yield f'{current_room.get("desc")}\n'

        if "items" in current_room:
            items = ", ".join(current_room.get("items"))
            yield f"Items: {items}\n"

        exits = " ".join(current_room.get("exits"))
        yield f"Exits: {exits}\n"

    def get(self, item: str = "") -> Tuple[str, bool]:
        if not item:
            return "Sorry, you need to 'get' something.", False

        items: list = self.engine.get_current_room().get("items")
        if not items:
            return "There are no items to get in this room.", False
        if item not in items:
            return f"There's no {item} to get.", False

        self.engine.my_inventory.append(item)
        items.remove(item)
        return f"You pick up the {item}", True

    def inventory(self) -> Tuple[str, bool, list]:
        if not (my_inventory := self.engine.my_inventory):
            return "You're not carrying anything.", False, None
        return "Inventory:", True, my_inventory

    def quit(self):
        self.engine.over = True
        return "Goodbye!", True

    def help(self) -> Generator[str, None, None]:
        return self.__get_help()

    def __get_help(self) -> Generator[str, None, None]:
        import inspect

        base_attr = set(dir(self.__class__.__base__))
        sub_attr = set(dir(self))
        for attr in sub_attr - base_attr:
            if not attr.startswith("_") and callable(getattr(self, attr)):
                if len(inspect.signature(getattr(self, attr)).parameters.keys()) > 1:
                    yield f"{attr} ..."
                yield attr

    def drop(self, item: str = "") -> Tuple[str, bool]:
        if not item:
            return "Sorry, you need to 'go' somewhere.", False

        my_inventory: list = self.engine.inventory
        if item not in my_inventory:
            return f"There's no {item} to drop.", False

        my_inventory.remove(item)
        items: list = self.engine.get_current_room().get("items")
        items.append(item)
        return f"You drop {item}.", True


def direction_ext():
    for direction in CommandSet.DIRECTIONS:
        # Define a new method for the direction
        def method(self, direction=direction):
            return self.go(direction)

        setattr(CommandSet, direction, method)


direction_ext()

if __name__ == "__main__":
    for help in CommandSet().help():
        print(help)
