# Clicker Heroes sikulix automation

Generally for a mid/late game, plays idle style. Expects 2 adjacent gilded heroes.

It's possible to exit and restart at any point, it'll look for various features to determine what it should be doing.

## Hotkeys

CTRL-F1 exit
CTRL-F2 ascend

## Automation loop overview:

Make the CH window active (by clicking the crossed swords icon)

Save game, filename based on the date and time.

1. If we're at 0 DPS:

    Level up Masked Samurai, to at least 2000.

    Level 25 other heroes to 200.

    Buy upgrades.

2. If Samurai is already 2000:

    Level gilded heroes

3. If levels take longer than MAXLEVELTIME:

    Ascend (including salvaging relics)

4. Click on fish.

5. Activate Energized DR and Reload.

## Some editable settings:

    for debugging, highlight some areas of interest
    HIGHLIGHTS = False
    
    full path to log file
    LOGFILEPATH = ""
    
    number of levels to skip at the start, progressively, levelskip * times 20, for Iris
    LEVELSKIP = 16
    
    save game at start
    SAVEGAME = True
    
    exit after ascending
    EXITASCEND = False
    
    duration to wait for the level to change
    MAXLEVELTIME = 5
