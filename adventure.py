from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any, Callable, Dict, Generator, Iterable, List, Tuple


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

    def __init__(self, engine, **kwargs):
        super().__init__(engine, **kwargs)

    def go(self, direction: str = "") -> Tuple[str, bool]:
        if not direction:
            return "Sorry, you need to 'go' somewhere.", False

        exits: dict = self.engine.get_current_room().get("exits")
        if direction not in exits:
            return f"There's no way to go {direction}", False

        id_room_to_go: int = exits.get(direction)
        room_to_go: dict = self.engine.rooms[id_room_to_go]
        if "locked" in room_to_go:
            return f'Locked. Requiring {room_to_go.get("locked")}', False

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

    def unlock(self, direction: str = "") -> Tuple[str, bool]:
        id_room_to_unlock: int = (
            self.engine.get_current_room().get("exits").get(direction)
        )
        if not id_room_to_unlock:
            return f"No room on {direction}", False

        room_to_unlock: dict = self.engine.rooms[id_room_to_unlock]
        requirings = room_to_unlock.get("locked", [])
        if not requirings:
            return f"The room on {direction} is not locked", False

        requirings_cnt = Counter(requirings)

        my_inventory: list = self.engine.my_inventory
        lacking = ""
        for requring in requirings_cnt:
            diff = requirings_cnt.get(requring) - my_inventory.count(requring)
            if diff > 0:
                lacking += f"{requring}: {diff};"
        if lacking:
            return f"Lacking: {lacking}", False

        consumed = ""
        for requring in requirings_cnt:
            for _ in range(requirings_cnt.get(requring)):
                my_inventory.remove(requring)
            consumed += f"{requring}: {requirings_cnt.get(requring)}"

        room_to_unlock.pop("locked")
        return f"Consumed: {consumed}", True

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


class GameEngine:
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

    def __init__(self, mapfile: str) -> None:
        self.command_set = CommandSet(engine=self)
        self.rooms = self.load_map(mapfile)
        self.current_room: int = 0
        self.my_inventory: list = None
        self.over: bool = True

    @property
    def command_set(self) -> CommandSet:
        return self.__command_set

    @command_set.setter
    def command_set(self, command_set: CommandSet = None) -> None:
        self.__command_set = command_set

    @property
    def rooms(self) -> List[Dict]:
        return self.__rooms

    @rooms.setter
    def rooms(self, rooms: List[Dict]) -> None:
        self.__rooms = rooms

    @property
    def current_room(self) -> dict:
        return self.__current_room

    @current_room.setter
    def current_room(self, room: dict) -> None:
        self.__current_room = room

    @property
    def my_inventory(self) -> list:
        return self.__my_inventory

    @my_inventory.setter
    def my_inventory(self, inventory: list) -> None:
        self.__my_inventory = inventory

    @property
    def over(self) -> bool:
        return self.__over

    @over.setter
    def over(self, over: bool) -> None:
        self.__over = over

    def load_map(self, filename: str) -> list:
        with open(filename, "r") as file:
            return json.load(file)

    def get_current_room(self) -> dict:
        return self.rooms[self.current_room]

    def go(self, direction: str) -> None:
        message, _ = self.command_set.go(direction)
        print(message)
        self.look()

    def look(self) -> None:
        for info in self.command_set.look():
            print(info)

    def get(self, item: str) -> None:
        message, _ = self.command_set.get(item)
        print(message)

    def inventory(self):
        message, ok, my_inventory = self.command_set.inventory()
        print(message)

        if ok:
            for item in my_inventory:
                print(f"  {item}")

    def quit(self) -> None:
        message, _ = self.command_set.quit()
        print(message)

    def help(self) -> None:
        print("You can run the following commands:")
        for verb in self.command_set.help():
            print(f"  {verb}")

    def drop(self, item: str = "") -> None:
        message, _ = self.command_set.drop(item)
        print(message)

    def unlock(self, direction: str = "") -> None:
        message, ok = self.command_set(direction)
        print(message)

    def __resolve_abbreviation(
        self, raw_input: str, *options: Iterable
    ) -> Tuple[str, bool, Tuple[str, Tuple[str]]]:
        keywords = raw_input.split()
        completion = ""

        if not keywords:
            return completion, False, ("", ("",))
        while keywords:
            keyword = keywords.pop(0)
            candidates = set()
            for option in options:
                if isinstance(option, dict):
                    if keyword in option:
                        completion += f"{option[keyword]} "
                        break
                    candidates |= {
                        option.get(key)
                        for key in option
                        if isinstance(key, str) and key.startswith(keyword)
                    }
                else:
                    if keyword in option:
                        completion += f"{keyword} "
                        break
                    candidates |= set(
                        filter(
                            lambda x: isinstance(x, str) and x.startswith(keyword),
                            option,
                        )
                    )

            if len(candidates) >= 1:
                return completion.strip(), False, (keyword, tuple(candidates))
            if len(candidates) == 1:
                completion += f"{candidates.pop()} "

        completion=completion.strip()
        if not completion:
            return completion,False,(keyword,tuple(candidates))

        return completion.strip(), True, (keyword, tuple(candidates))

    def __parse(self, raw_input: str):
        if "\x04" in raw_input:
            print("\nUse 'quit' to exit.")
            return

        completion, ok, prefix_candidates = self.__resolve_abbreviation(
            raw_input,
            GameEngine.DIRECTIONS,
            tuple(
                self.command_set.help(),
            ),
            {
                "ne": "northeast",
                "nw": "northwest",
                "se": "southeast",
                "sw": "southwest",
            },
        )

        if not ok:
            _, candidates = prefix_candidates
            if not candidates:
                print("Invalid command.")
                return

            candidates_str = f'{", ".join(candidates[:-1])} ' + f"or {candidates[-1]}"
            if (
                all(candidate in GameEngine.DIRECTIONS for candidate in candidates)
                and completion.strip() == ""
            ):
                print(f"Did you want to go {candidates_str}?")

            else:
                print(f"Did you want to {completion} {candidates_str}")
            return

        verb, *rest = completion.split()
        if not (verb := getattr(self, verb)):
            print("Invalid command.")
            return
        verb(*rest)

    def start(self) -> None:
        self.over = False
        self.look()
        while not self.over:
            try:
                raw_input = input("What would you like to do? ").lower()
                self.__parse(raw_input)
            except EOFError:
                print("Use 'quit' to exit.")
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                print(e)
            continue

        sys.exit(0)


def direction_ext():
    for direction in GameEngine.DIRECTIONS:
        # Define a new method for the direction
        def m1(self, direction=direction):
            return self.go(direction)

        def m2(self, direction=direction):
            return self.go(direction)

        setattr(CommandSet, direction, m1)
        setattr(GameEngine, direction, m2)


if __name__ == "__main__":
    direction_ext()
    if len(sys.argv) < 2:
        print("Usage: python adventure.py [map filename]")
        sys.exit(1)

    game_engine = GameEngine(mapfile=sys.argv[1])
    # game_engine = GameEngine(mapfile="ambig.map.json")
    game_engine.start()
