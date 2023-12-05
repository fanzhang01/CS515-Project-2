import json
import sys


def load_map(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def display_room(rooms, current_room):
    room = rooms[current_room]
    print(f"> {room['name']}\n")
    print(f"{room['desc']}\n")
    if 'items' in room:
        items = ", ".join(room['items'])
        print(f"Items: {items}\n")
    exits = " ".join(room['exits'].keys())
    print(f"Exits: {exits}\n")


def resolve_abbreviation(input, options, verb):
    if input in options:
        return input, False  # False indicates no ambiguity

    # If no exact match, check for prefix matches
    matches = [option for option in options if option.startswith(input)]
    if len(matches) == 1:
        return matches[0], False  # Single match, no ambiguity
    elif len(matches) > 1:
        formatted_matches = ' or '.join(matches)
        print(f"Did you want to {verb} {formatted_matches}?")
        return matches, True  # Multiple matches, ambiguity present
    else:
        return None, False  # No matches


def go_direction(command, rooms, current_room):
    parts = command.split(maxsplit=1)
    if len(parts) == 1:
        print("Sorry, you need to 'go' somewhere.")
        return current_room

    direction = parts[1]
    resolved_direction, ambiguous = resolve_abbreviation(direction, rooms[current_room]['exits'], "go")

    if not ambiguous and resolved_direction:
        current_room = rooms[current_room]['exits'][resolved_direction]
        print(f"You go {resolved_direction}.\n")
        display_room(rooms, current_room)  # Display new room details
    elif resolved_direction is None:
        print(f"There's no way to go {direction}.")

    return current_room


def get_item(command, rooms, current_room, inventory):
    parts = command.split(maxsplit=1)
    if len(parts) == 1:
        print("Sorry, you need to 'get' something.")
        return current_room, inventory

    item = parts[1]
    if 'items' in rooms[current_room]:
        resolved_item, ambiguous = resolve_abbreviation(item, rooms[current_room]['items'], "get")
        if not ambiguous and resolved_item:
            inventory.append(resolved_item)
            rooms[current_room]['items'].remove(resolved_item)
            print(f"You pick up the {resolved_item}.")
        elif resolved_item is None:
            print(f"There's no {item} to get.")
    else:
        print("There are no items to get in this room.")

    return current_room, inventory


def drop_item(command, current_room, inventory):
    # Implement drop_item functionality
    pass


def inventory_items(current_room, inventory):
    show_inventory(inventory)


def quit_game():
    print("Goodbye!")
    sys.exit(0)


def help_command():
    # Implement help_command functionality
    pass


def show_inventory(inventory):
    if inventory:
        print("Inventory:\n  " + "\n  ".join(inventory))
    else:
        print("You're not carrying anything.")


if len(sys.argv) < 2:
    print("Usage: python adventure.py [map filename]")
    sys.exit(1)

mapfile = sys.argv[1]
rooms = load_map(mapfile)
current_room = 0
inventory = []

display_room(rooms, current_room)

valid_commands = ["go", "get", "drop", "look", "inventory", "quit", "help"]
directions = ["north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest"]
direction_abbreviations = {
    'n': 'north',
    's': 'south',
    'e': 'east',
    'w': 'west',
    'ne': 'northeast',
    'nw': 'northwest',
    'se': 'southeast',
    'sw': 'southwest'
}

while True:
    try:
        raw_input = input('What would you like to do? ').lower()
    except EOFError:
        print()
        print("Use 'quit' to exit.")
        continue

    parts = raw_input.split(maxsplit=1)
    command_verb = parts[0]
    rest_of_command = parts[1] if len(parts) > 1 else ""

    # Check for direction abbreviations
    if command_verb in direction_abbreviations:
        command_verb = direction_abbreviations[command_verb]

    if command_verb in directions:  # Check if it's a direction
        current_room = go_direction(f"go {command_verb}", rooms, current_room)
    else:
        resolved_verb, ambiguous = resolve_abbreviation(command_verb, valid_commands, "do")
        if ambiguous or resolved_verb is None:
            continue  # Skip the loop if command is ambiguous or invalid

        if resolved_verb == 'look':
            display_room(rooms, current_room)
        elif resolved_verb == 'go':
            current_room = go_direction(f"{resolved_verb} {rest_of_command}", rooms, current_room)
        elif resolved_verb == 'get':
            current_room, inventory = get_item(f"{resolved_verb} {rest_of_command}", rooms, current_room, inventory)
        elif resolved_verb == 'drop':
            current_room, inventory = drop_item(f"{resolved_verb} {rest_of_command}", current_room, inventory)
        elif resolved_verb == 'inventory':
            inventory_items(current_room, inventory)
        elif resolved_verb == 'quit':
            quit_game()
        elif resolved_verb == 'help':
            help_command()
        else:
            print("Invalid command.")
