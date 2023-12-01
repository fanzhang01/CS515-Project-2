
import json
import sys
import msvcrt

def load_map(filename):
    with open(filename, 'r') as file:
        return json.load(file)


class Game:
    def __init__(self, mapfile):
        self.rooms = load_map(mapfile)
        self.current_room = 0
        self.inventory = []


    def display_room(self):
        room = self.rooms[self.current_room]
        print(f"> {room['name']}\n")
        print(f"{room['desc']}\n")
        if 'items' in room:
            items = ", ".join(room['items'])
            print(f"Items: {items}\n")
        exits = " ".join(room['exits'].keys())
        print(f"Exits: {exits}\n")


    def move(self, direction):
        if direction in self.rooms[self.current_room]['exits']:
            self.current_room = self.rooms[self.current_room]['exits'][direction]
            print(f"You go {direction}.\n")
            self.display_room()
        else:
            print("There's no way to go {}.".format(direction))


    def take_item(self, item):
        room = self.rooms[self.current_room]
        if 'items' in room and item in room['items']:
            self.inventory.append(item)
            room['items'].remove(item)
            print(f"You pick up the {item}.")
        else:
            print(f"There's no {item} anywhere.")


    def show_inventory(self):
        if self.inventory:
            print("Inventory:\n  " + "\n  ".join(self.inventory))
        else:
            print("You're not carrying anything.")


    def resolve_abbreviation(self, abbreviation, options):
        matches = [option for option in options if option.startswith(abbreviation)]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            print(f"Did you mean one of these? {', '.join(matches)}")
            return None
        else:
            print("No matching command found.")
            return None


    def parse_command(self, command):
        words = command.lower().split()
        if not words:
            return
        verb = words[0]

        if verb == 'go':
            if len(words) > 1:
                self.move(words[1])
            else:
                print("Sorry, you need to 'go' somewhere.")
        elif verb == 'look':
            self.display_room()
        elif verb == 'get':
            if len(words) > 1:
                self.take_item(' '.join(words[1:]))
            else:
                print("Sorry, you need to 'get' something.")
        elif verb == 'inventory':
            self.show_inventory()
        elif verb == 'quit':
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid command.")







    def play(self):
        self.display_room()
        while True:
            try:
                print("What would you like to do? ", end='', flush=True)
                command = ""
                while True:
                    if msvcrt.kbhit():
                        char = msvcrt.getch()
                        # Check if it's Ctrl+D (ASCII 4)
                        if char == b'\x04':
                            print("^D")
                            print("Use 'quit' to exit.")
                            break

                        if char in [b'\r', b'\n']:
                            print()
                            break
                        command += char.decode()
            except KeyboardInterrupt:
                raise
            else:
                if command.strip():
                    self.parse_command(command.strip())


def main():
    game = Game("loop.map.json")
    game.play()

if __name__ == "__main__":
    main()
