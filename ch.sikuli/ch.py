import time
import json
import base64
import sys

HIGHLIGHTS = False
SAVEPATH = "d:\\cygwin\\home\\sic\\ch\\"
LOGFILEPATH = "d:\\cygwin\\home\\sic\\ch\\ch.log"
LEVELSKIP = 10
SAVEGAME = True
EXITASCEND = False
MAXLEVELTIME = 4

SAMURAI = 3200
MAXZONE = 2010

###############

heroes = ["Cid", "Treebeast", "Ivan", "Brittany", "Fisherman", "Betty", "Samurai", "Leon", "Seer", "Alexa",
    "Natalia", "Mercedes", "Bobby", "Broyle", "George", "Midas", "ReferiJerator", "Abaddon","MaZhu",
    "Amenhotep","Beastlord","Athena","Aphrodite","Shinatobe","Grant","Frostleaf","DreadKnight","Atlas",
    "Terra","Phthalo","Orntchya","Lilin","Cadmia","Alabaster","Astraea"]

heroidx = dict(map(lambda x: (heroes[x], x+1), range(len(heroes))))
heroname = dict(map(lambda x: (x+1, heroes[x]), range(len(heroes))))

state = {}

def resetstate():
    global state
    state = {
        'ascendNow': False,
        'ascendSoon': False,
        'besthero': False,
        'level': 0,
        'hired': 0,
        'starttime': time.time(),
        'wait': False,
        'primalSouls': 0,
        'primalSoulsStart': 0,
        'samurai': 0,
        'gold': 0,
        'maxgildidx': 0,
        'gild1level': 0,
        'gild2level': 0,

        'highestFinishedZone': 0, 
        'rubies': 0, 
        'totalHeroSouls': 0, 
        'currentZoneHeight': 0,
        'gold': 0
    }

def timediff(start, end=None):
    if not end:
        end = time.time()
    diff = end - start
    return ("%02d:%02d:%02d.%04d" % (diff / 3600, (diff % 3600 / 60), diff % 60, (diff % 60 - int(diff % 60)) * 10000), diff)

def clickleft(n):
    for x in range(n):
        mouseDown(Button.LEFT)
        mouseUp()

def clickn(what=None, n=1, mod=0):
    if what:
        hover(what)
    else:
        hover(getLastMatch())
    clickleft(n)

def zclick(thing, count):
    hover(thing)
    keyDown('z')
    wait(0.05)
    clickleft(count)
    wait(0.05)
    keyUp('z')
    wait(0.1)
    return True

# find fish
def fish():
    if exists(Pattern("1439028358739.png").similar(0.85),0):
        if not state["ascendSoon"]:
            click()
            Debug.user("fish")
        else:
            Debug.user("ascending soon, saving fish")
        return True
    return False

def rest(delay=0.1):
    fish()
    if exists("1439022623124.png"):
        hover("1439022623124.png")
    wait(delay)

def decodeSave(dat):
    ANTI_CHEAT_CODE = "Fe12NAfA3R6z4k0z"

    first,rest = dat.split(ANTI_CHEAT_CODE,1)

    txt=""
    for i in range(0, len(first), 2):
      txt += first[i]

    base64.b64decode(txt)

    savegame = json.loads(base64.b64decode(txt))
    return json.loads(base64.b64decode(txt))

def checkrelics(save):
    found = False
    equip = {}
    minprimal = 99

    for x in save['items']['slots'].keys():
        equip[save['items']['slots'][x]] = int(x)

    for k,v in save['items']['items'].items():
        for x in range(1,5):
            if equip[int(k)] <= save['items']['equipmentSlots']:
                bt = 'bonusType%d'%(x)
                bv = 'bonus%dLevel'%(x)
                if v[bt] == 17:
                    if v[bv] < minprimal:
                        minprimal = v[bv]

    for k,v in save['items']['items'].items():
        if equip[int(k)] > save['items']['equipmentSlots']:
            Debug.user("relic: %s %s minprimal %d" % (k, v, minprimal))
            for x in range(1,5):
                bt = 'bonusType%d'%(x)
                bv = 'bonus%dLevel'%(x)
                if v[bt] == 17:
                    if v[bv] >= minprimal:
                        found = True

    return found

def updateFromSave():
    savedata = saveGame(savefile=False)
    save = decodeSave(savedata)

    state["samurai"] = save["heroCollection"]["heroes"][unicode(heroidx["Samurai"])]["level"]


    maxGildIdx = 0
    maxGild = 0
    hired = 0

    for idx, hero in save["heroCollection"]["heroes"].items():
        if hero["level"] > 0:
            hired += 1
        if hero["epicLevel"] > maxGild:
            maxGild = hero["epicLevel"]
            maxGildIdx = hero["id"]

    state["hired"] = hired
    state["maxgildidx"] = maxGildIdx

    state["gild1level"] = save["heroCollection"]["heroes"][unicode(maxGildIdx)]["level"]
    state["gild2level"] = save["heroCollection"]["heroes"][unicode(maxGildIdx - 1)]["level"]

    Debug.user("maxGild: %d %d %s %d" %(maxGild, maxGildIdx, heroname[maxGildIdx], state["gild1level"]))

    for k in ["primalSouls", "highestFinishedZone", "rubies", "totalHeroSouls", "currentZoneHeight",
        "gold"]:
        state[k] = save[k]
        Debug.user("%s: %s"%(k, save[k]))

    return save

def saveGame(savefile=True):
    if not SAVEGAME:
        savefile = False

    if exists(Pattern("1439437506317.png").similar(0.90)):
        click()
        if exists(Pattern("1439437547153.png").similar(0.80)):
            click()
            wait(0.5)
            if savefile:
                timestr = time.strftime("%Y_%m_%d_%H_%M_%S")
                type(SAVEPATH + timestr)
                wait(0.5)
                keyDown(Key.ENTER)
                wait(0.05)
                keyUp(Key.ENTER)
                wait(1)
            else:
                keyDown(Key.ESC)
                wait(0.05)
                keyUp(Key.ESC)
                wait(1)

            if exists(Pattern("1439437994711.png").similar(0.80), 1):
                click()

    return Env.getClipboard()

def findDown(thing, func, args=[]):
    while not exists(thing, 0.1):
        # find scrollbar
        if exists(Pattern("1439062815605.png").similar(0.86), 0):
            # scroll down
            clickn(Pattern("1439062815605.png").similar(0.77).targetOffset(0,2), 4)

        if buyUpgrades():
            break

        rest()

    if exists(thing, 0.1):
        return func(thing, *args)
    else:
        return False

# scroll to bottom of hero list
# check for target
# if it exists, call func against it
def findUp(thing, func, args=[]):
    scrollBottom()

    while not exists(thing, 0):
        # scroll up button
        if exists(Pattern("1439036427073.png").similar(0.83),0):
            clickn(Pattern("1439036427073.png").similar(0.83), 4)

        # scrolled to top
        if exists(Pattern("1439025863027.png").similar(0.83),0):
            break

    if exists(thing, 0):
        return func(thing, *args)
    else:
        return False

def progressMode():
    if exists(Pattern("1439085105926.png").similar(0.89),0):
        click()
        Debug.user("enable progress mode")
        return True
    return False

def buyUpgrades():
    if exists(Pattern("1439025589326.png").similar(0.85),0):
        click()
        return True
    return False

def scrollBottom():
    # Buy All Upgrades
    while not exists(Pattern("1439025589326.png").similar(0.85), 0):
        rest(0.05)
        # scroll up once to avoid getting stuck immediately after a new hero is available
        if exists(Pattern("1439036427073.png").similar(0.83), 0):
            click()
        # find scrollbar
        if exists(Pattern("1439436060095.png").similar(0.90).targetOffset(0,-13), 0):
            # scroll down
            clickn(Pattern("1439436060095.png").similar(0.90).targetOffset(0,-13), 4)

    wait(0.20)

def scrollTop():
    # find scroll bar at the top
#    while not exists(Pattern("1439025863027.png").similar(0.80),0):

    # click crossed swords
    if exists(Pattern("1439025078984.png").similar(0.90)):
        Debug.user("click crossed swords")
        click()
    else:
        Debug.user("failed to scroll to the top, didn't find crossed swords")

def ascend():
    Debug.user("ascending now")
    savedata = saveGame()
    save = decodeSave(savedata)

    collectedsouls = save["primalSouls"] - state["primalSoulsStart"]

    for k in ["primalSouls", "highestFinishedZone", "rubies", "totalHeroSouls", "currentZoneHeight"]:
        Debug.user("%s: %s"%(k, save[k]))

    if checkrelics(save):
        # found a better relic than current, don't trash it, abort instead
        Debug.user("found better relic, not ascending")
        return

    # Relics
    if exists(Pattern("1439100490944.png").similar(0.80),1):
        click()
        wait(0.5)
        # Salvage
        if exists("1439155381793.png",1):
            click()
            wait(0.5)
            # Yes
            if exists(Pattern("1439100607949.png").similar(0.90),1):
                click()

    scrollTop()

    # Amenhotep
    findDown(Pattern("1439072160611.png").similar(0.75).targetOffset(-74,57), click, [])
    # Yes
    if exists(Pattern("1439072311108.png").similar(0.91)):
        click()

    diffstr, diff = timediff(state["starttime"])

    rate = 0
    if diff > 0:
        rate = collectedsouls / diff

    Debug.user("Time for this run: %s rate: %f" % (diffstr, rate))
    updateFromSave()

    if EXITASCEND:
        exit()

# find available dark ritual with energize etc
def darkRitual():
    if exists(Pattern("1439478702484.png").similar(0.90)):
        if exists(Pattern("1439368983011.png").similar(0.80),0):
            Debug.user("activate dark ritual")
            keyDown('8')
            wait(0.1)
            keyUp('8')
            wait(0.1)

            keyDown('6')
            wait(0.1)
            keyUp('6')
            wait(0.1)

            keyDown('9')
            wait(0.1)
            keyUp('9')
            wait(0.1)

###############

def levelchange(event):
    state['level'] += 1
    event.stopObserver()

def checklevel(duration=MAXLEVELTIME):
    before = state['level']
    levelregion = None
    starttime = time.time()
    if exists(Pattern("1439022522525.png").similar(0.85)):
        r = getLastMatch()

        r.setX(r.getX() - 100)
        r.setY(r.getY() - 510)
        r.setH(30)
        r.setW(300)

        levelregion = Region(r.getX(), r.getY(), r.getW(), r.getH())
        if HIGHLIGHTS:
            levelregion.highlight()

        levelregion.onChange(50, levelchange)
        levelregion.observe(duration)

    diffstr, diff = timediff(starttime)
    Debug.user("checklevel time %s" %(diffstr))

    return before != state['level']

###############

def exithotkey(event):
    exit()

def ascendhotkey(event):
    state["ascendNow"] = True

def waithotkey(event):
    if "wait" in state:
        state["wait"] = not state["wait"]

###############

Env.addHotkey(Key.F1, KeyModifier.CTRL, exithotkey)
Env.addHotkey(Key.F2, KeyModifier.CTRL, ascendhotkey)
Env.addHotkey(Key.F3, KeyModifier.CTRL, waithotkey)

setShowActions(True)
Settings.UserLogs = True
Settings.UserLogPrefix = "user"
Settings.UserLogTime = True
Settings.ObserveScanRate = 3
Settings.MoveMouseDelay = 0.1

if LOGFILEPATH:
    Debug.on(2)
    Debug.setLogFile(LOGFILEPATH)

# click the X
if exists(Pattern("1439437994711.png").similar(0.80)):
    click()

# find top crossed swords to make the window active
if exists(Pattern("1439025078984.png").similar(0.90)):
    click()
    r = getLastMatch()
    r.setX(r.getX() - 30)
    r.setY(r.getY() - 100)
    r.setH(r.getH() + 650)
    r.setW(r.getW() + 1100)
    setROI(r.getX(), r.getY(), r.getW(), r.getH())
    roi = Region(r.getX(), r.getY(), r.getW(), r.getH())
    Debug.user("screenshot: %s" % SCREEN.capture(roi))

resetstate()
save = updateFromSave()
state["primalSoulsStart"] = state["primalSouls"]

Debug.user("")
Debug.user("Start")

while True:

    Debug.user("Loop start: %s" %state)

    if (state["ascendSoon"] and fish()) or state["ascendNow"]:
        Debug.user("Ascend Now")
        ascend()
        rest(2)

    if state["wait"]:
        pos = Env.getMouseLocation()
        Debug.user("Wait a while %s"%(pos))
        checklevel()
        wait(1)
        continue

    save = updateFromSave()

    # 0 DPS
    if state["hired"] == 0:
#    if exists(Pattern("1439111492693.png").similar(0.93),1):
        Debug.user("found 0 dps")

        wait(1)
        resetstate()
        state["primalSoulsStart"] = state["primalSouls"]

        if fish():
            Debug.user("Found fish, waiting..")
            wait(5)
            Debug.user("findDown samurai")
            findDown(Pattern("1439802146629.png").targetOffset(-230,15), zclick, [100])
        else:
            first = True

            for x in range(LEVELSKIP):
                # skip levels, next level arrow
                clickn(Pattern("1439078366733.png"), 18)
                rest()
                # space next to next level arrow
                clickn(Pattern("1439078366733.png").targetOffset(-60,0), 1)

                # click next to shop
                if first:
                    if exists(Pattern("1439022522525.png").similar(0.85).targetOffset(-60,0)):
                        clickn(getLastMatch(), 25)
                        first = False

                Debug.user("findDown samurai")
                findDown(Pattern("1439802146629.png").targetOffset(-230,15), zclick, [20])

                # necessary to wait a bit at each step in order to collect enough gold to progress
                wait(2)

        progressMode()

    fish()
    darkRitual()

    if state['samurai'] < SAMURAI:
        scrollTop()

        Debug.user("findDown samurai")
        findDown(Pattern("1439802146629.png").targetOffset(-230,15), zclick, [20])

        scrollBottom()
        buyUpgrades()
        scrollTop()

        progressMode()

        if state['samurai'] > SAMURAI / 2:
            Debug.user("findDown hire: %s" %(state['hired']))
            hired = state['hired']
            while hired < 26 and \
                    findDown(Pattern("1439151880109.png").similar(0.90), zclick, [8]):
                rest(0.01)

                hired += 1

            Debug.user("findDown hire done: %s"% hired)

    else:
        # gilded
        Debug.user("look for gilded heroes")
        if findUp(Pattern("1439148729231.png").similar(0.93).targetOffset(46,33), zclick, [10]):
            if not state["besthero"]:
                r = getLastMatch()

                r.setX(r.getX() + 40)
                r.setY(r.getY() + 140)
                r.setH(30)
                r.setW(100)

                wait(0.5)
                hirebutton = Region(r.getX(), r.getY(), r.getW(), r.getH())

                if HIGHLIGHTS:
                    hirebutton.highlight()
                    wait(2)
                    hirebutton.highlight()

                rest()

                try:
                    hirebutton.find(Pattern("1439492761474.png").similar(0.90))
                    Debug.user("failed to level best hero")
                    if exists(Pattern("1439031334204.png").similar(0.85).targetOffset(16,11)):
                        zclick(getLastMatch(), 10)
                        Debug.user("leveled secondary gilded hero")
                except:
                    Debug.user("found hired best hero")
                    state['besthero'] = True
                    pass

        else:
            findUp(Pattern("1439031334204.png").similar(0.85).targetOffset(16,11), zclick, [10])
            Debug.user("leveled secondary hero, didn't find primary")

        scrollBottom()
        buyUpgrades()

        Debug.user("done with gild level up")

        # find inactive progression mode
        if progressMode() or state["highestFinishedZone"] > MAXZONE:
            state["ascendSoon"] = True
            Debug.user("Ascend Soon")

    Debug.user("Loop done: %s" %(state))
