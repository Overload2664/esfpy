# Warscape Hotseat Tool
A tool that allows you to create hotseats for total war games.

## Supported Games
- Total War: Shogun II
- Total War: Rome II
- Total War: Attila

I've also enabled support for the titles below (I haven't tested and developed a patch for them as I don't own games):
- Total War: Empire
- Total War: Napoleon

Online battles should be possible for `Total War: Napoleon` and `Total War: Shogun II` with the `drop-in battle` option.

## Run
You can either use the ready Windows version or run the script manually.
To use the ready Windows version, download this [file](https://github.com/Overload2664/esfpy/releases/latest/download/hotseat_tool.zip) and after extracting it, run the file `run.bat`.

To run manually, clone the repo and run the `hotseat_gui.py` script:
```sh
git clone https://github.com/Overload2664/esfpy.git
cd esfpy
python3 src/hotseat_gui.py
```
I recommend using `PyPy` istead of `CPython` as it's noticeably faster. (Done automatically if you use the ready Windows version)

## How to Use
[Video](https://odysee.com/How-to-make-hotseat-for-Total-War-Attila%2C-Rome-II-and-Shogun-II:6)
### Prerequiste
First you have to patch your game to able to save at any given time in campaign, follow this [guide](https://github.com/Overload2664/total_save_patch?tab=readme-ov-file#total-save-patch).

### Initiate
After doing the prerequiste, create a save file in a supported game. Run the program and first choose which game the save file belongs to, then select the desired save file. This could take a bit (in my decent PC it sometimes took about 20 seconds) and consume a fair about of RAM (something like 4 GBs depending on the save file). Press `Mark Humanity` and choose factions you want to be humans. Then press save, head back and press save in the options menu and save the file.

### Going next turn
After a player finishes their turn, make a save file from the game. Open the save file with the program and press `Mark All As Playable` then save the file. Open the save file in the game and press next turn. This should make the game pause on the next player's turn. Now save the game (if it's grayed out then that means you haven't patched the game). Open the new save file with the program again. Press `Mark All As Not Playable` first then press `Mark Playables`. Choose the faction that the next (human) player belongs to (note that after doind this, only one faction should be selected there). Press save and head back. Press `Set Vision` and select the same faction you selected for playables. Press save and head back. Press save in the options menu and make the save file. Now run the new save file in the game. It should be the next (human) player turn!
After finishing each players turn, repeat the same steps to get to the next player's turn.

## Diagnostics
- If the game crashes, then that could be due to either not marking a faction as human or choosing a minor faction (the ones that you normally can't choose).
- If the screen looks weird, you can't control anything and/or the turn order is stuck, then that could be due to choosing different factions for `vision` and `playable` or having more than one faction chosen as `playable`.

## Known Issues
- Fog of War acts up in the first turn. The severity depends on the game.
- Sometimes playing as a minor faction (the ones that you normally can't choose) crashes the game. (Maybe fixable with mods?)
- Can't do diplomacy with other human players if the AI refuses your offers. Possibly fixable with mods, currently I've only found one for Attila though. [Attila Mod](https://steamcommunity.com/workshop/filedetails/?id=596714943).
- Between humans' turns, AIs can make diplomacy with others and instead of you accepting or refusing their offers, an AI makes the decisions for you instead. (Maybe fixable with mods?)
- Camera's zoom level sometimes freezes when you reach a player's turn. Just quick save and reload.
- Program takes considerable time and memory to read or write a save file. Unfortunately this is due to my design choices and the programming language this is written in.

## Bug Report and Contact
If you encounter an issue or want to ask a question, open an issue or join the [Discord server](https://discord.gg/gZuHrSV6Zx).

## Credits
Special thanks to [Tomasz Wegrzanowski](https://github.com/taw) for his awesome [guide](https://t-a-w.blogspot.com/2012/03/esf-empire-total-war-objecthtml), none of this would've been possible without it.
Also credits to [EditSF](https://github.com/Overload2664/esfpy/edit/master/README.md), used the tool immensely.
