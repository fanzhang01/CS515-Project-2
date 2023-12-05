# Group members

- Fan Zhang
  - fzhang32@stevens.edu
- Wai Hou Cheang
  - wcheang@stevens.edu

# The URL of your public GitHub repo

https://github.com/fanzhang01/CS515-Project-2.git

# An estimate of how many hours you spent on the project

24 hrs

# A description of how you tested your code

Running the program and do the logging when necessary. Set Breakpoints and debug when the error was not that visible

# Any bugs or issues you could not resolve

N/A

# An example of a difficult issue or bug and how you resolved

# A list of the extensions you’ve chosen to implement, with appropriate detail on them for the CAs to evaluate them (i.e., what are the new verbs/features, how do you exercise them, where are they in the map)

# Extensions

1. **Abbreviations for verbs, directions, and items**

   - **Features**: Allows players to use abbreviated forms of commands, items, and directions.
   - **Usage**: Players can type shorter versions of commands like `i` for `inventory`, `n` for `north`, or `g` for `get`. For ambiguous abbreviations, the game will ask for clarification.
   - **Example**: Typing `g b` in a room with a `banana` and a `bandana` will prompt the game to ask whether the player meant `banana` or `bandana`.
   - **Implementation**: Prefix-based matching is used for commands and exits, while substring matching is used for items.

2. **Help Verb**

   - **Features**: Offers guidance on available commands.
   - **Usage**: Typing `help` displays a list of valid verbs, with an ellipsis (...) indicating commands that expect a target.
   - **Dynamics**: The help text is dynamically generated from the defined verbs in the game.
   - **Example**:
     ```
     > help
     You can run the following commands:
       go ...
       get ...
       look
       inventory
       quit
       help
     ```

3. **Directions Become Verbs**

   - **Features**: Allows using directions as standalone commands.
   - **Usage**: Players can simply type `east` or `e` instead of `go east`.
   - **Special Handling**: The game differentiates between similar commands like `eat` and `east`, ensuring no interference.
   - **Abbreviations**: Supports abbreviations for uncommon exits (e.g., `nw` for `northwest`).

4. **Drop Verb**

   - **Features**: Opposite of `get`, letting players remove items from their inventory and place them in the current room.
   - **Restriction**: Only items in the player's inventory can be dropped.
   - **Usage**: Typing `drop [item]` will remove that item from the inventory if the player has it.
   - **Example**:
     ```
     > drop rose
     You drop the rose.
     ```

5. **Locked Doors**
   - **Features**: Some doors or paths can be locked, requiring specific items to unlock.
   - **Configuration**: Whether a door is locked or unlocked is defined in the game's asset, not in the engine.
   - **Implementation Choices**: You can choose to have players just need the item, or you could add `lock` and `unlock` verbs.
   - **Example**: A door might be locked and require a `key` to open. The player must have the `key` in their inventory to proceed.
