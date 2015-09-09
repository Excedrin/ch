# Clicker Heroes sikulix automation

Generally for a mid/late game, plays hybrid style. Expects 2 adjacent gilded heroes.

It's possible to exit and restart at any point, it'll parse save info to pick up where it left off.

## Hotkeys

    CTRL-F1 exit
    CTRL-F2 ascend now
    CTRL-F3 pause

## Notes

For windows, http://sourceforge.net/projects/fastclicker/ is a good autoclicker

## Automation loop overview:

Make the CH window active (by clicking the crossed swords icon)

Save game, filename based on the date and time.

1. If we're at 0 DPS:

    Level up INITIALHERO, to at least INITIALLVL.

    Level other heroes (thru Frostleaf) to 200.

    Buy upgrades.

2. If INITIALHERO is already lvl INITIALLVL

    Level gilded heroes

3. If zone is past MAXZONE.

    Wait for a fish. Ascend (including salvaging relics)

4. Click on fish.

5. Activate Energized DR and Reload.

## Some editable settings:

    # for debugging, highlight some areas of interest
    HIGHLIGHTS = False

    # full path to log file
    LOGFILEPATH = "d:\\ch\\ch.log"

    # path for savegames
    SAVEPATH = "d:\\ch\\"

    # write save files
    SAVEGAME = True

    # number of levels to skip at the start, progressively, levelskip * times 20, for Iris
    LEVELSKIP = 10

    # exit after ascending
    EXITASCEND = False

    # use this key to activate autoclicker
    AUTOCLICKERKEY = Key.F8

    # options "Samurai" "Midas" "Frostleaf" "DreadKnight" "Atlas" "Terra" "Phthalo" "Orntchya"
    INITIALHERO = "Phthalo"

    # level to at least this level:
    INITIALLVL = 1000

    # stop clicking fish when past this zone
    NOFISHZONE = 2370

    # start clicking monsters past this zone
    DEEPZONE = 2080

    # wait for a fish and ascend at this zone
    MAXZONE = 2520

    # Ascend immediately after finding a relic
    RELICASCEND = False
