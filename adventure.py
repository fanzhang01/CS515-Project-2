
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
        current_exits = self.rooms[self.current_room]['exits']


        if direction in current_exits:
            self.current_room = current_exits[direction]
            print(f"You go {direction}.\n")
            self.display_room()
            return


        matched_exits = [exit for exit in current_exits if exit.startswith(direction)]
        if len(matched_exits) == 1:
            self.current_room = current_exits[matched_exits[0]]
            print(f"You go {matched_exits[0]}.\n")
            self.display_room()
        elif len(matched_exits) > 1:
            print(f"Did you want to go {' or '.join(matched_exits)}?")
        else:
            print(f"There's no way to go {direction}.")


    def take_item(self, item_input):
        room = self.rooms[self.current_room]
        if 'items' in room:

            matched_items = [item for item in room['items'] if item_input in item]

            if len(matched_items) == 1:
                item = matched_items[0]
                self.inventory.append(item)
                room['items'].remove(item)
                print(f"You pick up the {item}.")
            elif len(matched_items) > 1:

                matches_formatted = ', '.join(matched_items[:-1]) + ' or ' + matched_items[-1]
                print(f"Did you want to get the {matches_formatted}?")
            else:
                print(f"There's no {item_input} to get.")
        else:
            print("There are no items to get in this room.")

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

        direction_abbreviations = {
            'nw': 'northwest',
            'ne': 'northeast',
            'sw': 'southwest',
            'se': 'southeast'
        }
        single_letter_directions = {
            'n': 'north',
            's': 'south',
            'e': 'east',
            'w': 'west'
        }

        if verb in direction_abbreviations:
            if direction_abbreviations[verb] in self.rooms[self.current_room]['exits']:
                self.move(direction_abbreviations[verb])
            else:
                print(f"There's no way to go {direction_abbreviations[verb]}.")
            return

        if len(verb) == 1 and verb in single_letter_directions:
            direction = single_letter_directions[verb]
            if direction in self.rooms[self.current_room]['exits']:
                self.move(direction)
            else:
                print(f"There's no way to go {direction}.")
        else:
            if verb == 'go':
                if len(words) > 1:
                    self.move(' '.join(words[1:]))
                else:
                    print("Sorry, you need to 'go' somewhere.")

            elif verb == 'get':
                if len(words) > 1:
                    self.take_item(' '.join(words[1:]))
                else:
                    print("Sorry, you need to 'get' something.")
            elif verb == 'look':
                self.display_room()

            elif verb in ['inventory', 'inv']:
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
    if len(sys.argv) < 2:
        print("Usage: python adventure.py [map filename]")
        sys.exit(1)

    mapfile = sys.argv[1]
    game = Game(mapfile)
    game.play()


if __name__ == "__main__":
    main()
