import time
import json
import base64
import sys

# for debugging, highlight some areas of interest
HIGHLIGHTS = False

# full path to log file
LOGFILEPATH = "d:\\ch\\ch.log"

# path for savegames
SAVEPATH = "d:\\ch\\"

# write save files
SAVEGAME = True

# number of levels to skip at the start, progressively, levelskip * times 20, for Iris
# how many levels to skip after leveling Natalia, times 20, so 4 means lvl 80
LEVELSKIP = 4

# exit after ascending
EXITASCEND = False

# use this key to activate autoclicker
AUTOCLICKERKEY = Key.F8

# options "Samurai" "Midas" "Frostleaf" "DreadKnight" "Atlas" "Terra" "Phthalo" "Orntchya"
INITIALHERO = "Phthalo"

# level to at least this level:
INITIALLVL = 1000

# stop clicking fish when past this zone
NOFISHZONE = 2400

# start clicking monsters past this zone
DEEPZONE = 2300

# wait for a fish and ascend at this zone
MAXZONE = 2450

# Ascend upon finding relic
RELICASCEND = True

# What combo to repeat when clicking monsters, it just blindly hits this repeatedly,
# so probably a good idea to remove '5' if you're doing a deep run
# it activates DR with '869' periodically (but hopefully only when they're all available
ACTIVECOMBO = '123457'

# How long to wait before trying to level the best hero when clicking monsters
CLICKTIME = 150

###############

heroes = ['Cid', 'Treebeast', 'Ivan', 'Brittany', 'Fisherman', 'Betty', 'Samurai', 'Leon', 'Seer', 'Alexa',
    'Natalia', 'Mercedes', 'Bobby', 'Broyle', 'George', 'Midas', 'ReferiJerator', 'Abaddon','MaZhu',
    'Amenhotep','Beastlord','Athena','Aphrodite','Shinatobe','Grant','Frostleaf','DreadKnight','Atlas',
    'Terra','Phthalo','Orntchya','Lilin','Cadmia','Alabaster','Astraea']

heroidx = { heroes[x]: x+1 for x in range(len(heroes)) }
heroname = { y: x for x,y in heroidx.items() }

state = {}

def resetstate():
    global state
    state = {
        'ascendNow': False,
        'ascendSoon': False,
        'besthero': False,
        'hired': 0,
        'starttime': time.time(),
        'wait': False,
        'primalSouls': 0,
        'primalSoulsStart': 0,
        'initial': 0,
        'gold': 0,
        'maxgildidx': 0,
        'gild1level': 0,
        'gild2level': 0,

        'highestFinishedZone': 0, 
        'rubies': 0, 
        'totalHeroSouls': 0, 
        'currentZoneHeight': 0,
        'maxrate': 0,
        'maxratelvl': 0
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

def zclick(thing, count, key='z'):
    hover(thing)
    keyDown(key)
    wait(0.1)
    clickleft(count)
    wait(0.05)
    keyUp(key)
    wait(0.1)
    return True

def qclick(thing):
    return zclick(thing, 1, 'q')

# find fish
def fish(checkonly=False):
    if exists(Pattern("1439028358739.png").similar(0.85),0):
        if checkonly or state['ascendSoon'] or state['highestFinishedZone'] > NOFISHZONE:
            Debug.user("fish present, not clicking")
        else:
            click()
            Debug.user("fish")
        return True
    return False

def rest(delay=0.1):
    fish()
    if exists("1439022623124.png"):
        hover(getLastMatch())
    if state['highestFinishedZone'] > DEEPZONE or state['highestFinishedZone'] > MAXZONE:
        nearShop(click)
    else:
        nearShop(lambda x: x)

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

def relicfound(save):
    found = len(save['items']['items']) >= 5
    if found:
        Debug.user("Relic found: %d" %(save['items']['_currentUids']['items']))
    return found

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

def dumpHeroInfo(save):
    for idx, hero in sorted(save['heroCollection']['heroes'].items(), key=lambda (x,y): int(x)):
        Debug.user("%s %s level %d" % (idx, heroname[int(idx)], hero['level']))

def updateFromSave():
    savedata = saveGame(savefile=False)
    save = decodeSave(savedata)

    state['initial'] = save['heroCollection']['heroes'][unicode(heroidx[INITIALHERO])]['level']

    maxGildIdx = 0
    maxGild = 0
    hired = 0

    for idx, hero in save['heroCollection']['heroes'].items():
        if hero['level'] > 0:
            hired += 1
        if hero['epicLevel'] > maxGild:
            maxGild = hero['epicLevel']
            maxGildIdx = hero['id']

    state['hired'] = hired
    state['maxgildidx'] = maxGildIdx

    state['gild1level'] = save['heroCollection']['heroes'][unicode(maxGildIdx)]['level']
    state['gild2level'] = save['heroCollection']['heroes'][unicode(maxGildIdx - 1)]['level']

    Debug.user("maxGild: %d %d %s %d" %(maxGild, maxGildIdx, heroname[maxGildIdx], state['gild1level']))

    for k in ['primalSouls', 'highestFinishedZone', 'rubies', 'totalHeroSouls', 'currentZoneHeight', 'gold', 'titanDamage']:
        state[k] = save[k]
        Debug.user("%s: %s"%(k, save[k]))

    return save

def allHired(save):
    idx = heroidx['Frostleaf']
    b = True
    for x in range(1, idx+1):
        b = b and save['heroCollection']['heroes'][unicode(x)]['level'] >= 200
        #Debug.user("idx: %d level: %d" %(x, save['heroCollection']['heroes'][unicode(x)]['level']))

    return b        

def saveGame(savefile=True):
    if not SAVEGAME:
        savefile = False

    # wrench icon
    if exists(Pattern("1439437506317.png").similar(0.90), 1):
        click()
        wait(1)
        # Save button
        if exists(Pattern("1439437547153.png").similar(0.80), 1):
            click()
            wait(1)
            if savefile:
                timestr = time.strftime("%Y_%m_%d_%H_%M_%S")
                type(SAVEPATH + timestr)
                wait(0.5)
                keyDown(Key.ENTER)
                wait(0.05)
                keyUp(Key.ENTER)
                wait(1)
            else:
                wait(0.1)
                keyDown(Key.ESC)
                wait(0.05)
                keyUp(Key.ESC)
                wait(0.1)

            wait(1)
            # X
            while exists(Pattern("1439437994711.png").similar(0.80), 1):
                click()
                wait(0.1)

    rest()

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
        Debug.user("findUp loop")
        # scroll up button
        if exists(Pattern("1439036427073.png").similar(0.83),0):
            clickn(Pattern("1439036427073.png").similar(0.83), 4)

        # scrolled to top
        if exists(Pattern("1439025863027.png").similar(0.83),0):
            break

    rest()

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
    Debug.user("scrollBottom")
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

def locateHero(hero, func, args=[]):
    Debug.user("findUp %s" %(hero))
    heropatterns = {
        "Natalia": Pattern("Natalia.png").similar(0.90).targetOffset(-211,7),
        "Samurai": Pattern("Samurai.png").targetOffset(-230,0),
        "Midas": Pattern("Midas.png").targetOffset(-242,7),
        "Frostleaf": Pattern("Frostleaf.png").targetOffset(-255,7),
        "DreadKnight": Pattern("DreadKnight.png").targetOffset(-235,8),
        "Atlas": Pattern("Atlas.png").targetOffset(-271,8),
        "Terra": Pattern("Terra.png").targetOffset(-269,6),
        "Phthalo": Pattern("Phthalo.png").targetOffset(-262,4),
        "Orntchya": Pattern("Orntchya.png").targetOffset(-184,7)
    }
    return findUp(heropatterns[hero], func, args)

def calcrate():
    collectedsouls = save['primalSouls'] - state['primalSoulsStart']
    diffstr, diff = timediff(state['starttime'])
    rate = 0
    if diff > 0:
        rate = collectedsouls / diff

    if rate > state['maxrate']:
        state['maxrate'] = rate
        state['maxratelvl'] = state['highestFinishedZone']
        
    Debug.user("Time for this run: %s rate: %f zone: %d maxrate %d maxratelvl %d" % (diffstr, rate, 
        state['highestFinishedZone'], state['maxrate'], state['maxratelvl']))

def ascend():
    Debug.user("ascending now")
    savedata = saveGame()
    save = decodeSave(savedata)

    for k in ['primalSouls', 'highestFinishedZone', 'rubies', 'totalHeroSouls', 'currentZoneHeight']:
        Debug.user("%s: %s"%(k, save[k]))

    if checkrelics(save):
        # found a better relic than current, don't trash it, abort instead
        Debug.user("found better relic, not ascending")
        return

    # Relics
    Debug.user("Salvage relics")
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

    Debug.user("find Amenhotep")
    # Amenhotep
    findDown(Pattern("1439072160611.png").similar(0.75).targetOffset(-74,57), click, [])

    Debug.user("click Yes")
    # Yes
    if exists(Pattern("1439072311108.png").similar(0.91)):
        click()

    calcrate()

    if EXITASCEND:
        exit()

def hireHeroes():
    scrollTop()

    hire = 0

    Debug.user("findDown hire: %s" %(state['hired']))
    hired = state['hired']
    while findDown(Pattern("1439151880109.png").similar(0.90), zclick, [2, Key.CTRL]):
        rest(0.01)

        hired += 1
        hire += 1

        if hire > 4:
            break

    Debug.user("findDown hire done: %s"% hired)

# find available dark ritual with energize etc
def darkRitual():
    if exists(Pattern("1439478702484.png").similar(0.90)):
        if exists(Pattern("1439368983011.png").similar(0.80),0):
            Debug.user("activate dark ritual")
            type('869')

def nearShop(f):
    if exists(Pattern("1439022522525.png").similar(0.85).targetOffset(-90,-40)):
        f(getLastMatch())

def clicker(monsterArea, duration):
    endtime = time.time() + duration
    remaining = endtime - time.time()

    hover(monsterArea)
    wait(0.1)
    keyDown(Key.F8)
    wait(0.1)
    keyUp(Key.F8)

    while remaining > 0:
        Debug.user("click monsters remaining time: %d" %(remaining))

        if not state['ascendSoon']:
            if fish(True):
                keyDown(Key.F8)
                wait(0.1)
                keyUp(Key.F8)

                fish()

                keyDown(Key.F8)
                wait(0.1)
                keyUp(Key.F8)

        hover(monsterArea)

        type('12347')
        wait(10)

        remaining = endtime - time.time()

    keyDown(Key.F8)
    wait(0.1)
    keyUp(Key.F8)

    wait(3)

def clickMonsters(duration=150):
    progressMode()
    nearShop(lambda x: clicker(x, duration))

def checkSkillCooldown(save):
    longts = save['unixTimestamp']

    for k in ['skillClickMultiplierEnd', 'skillCriticalClickChanceEnd', 'skillDpsMultiplierEnd', 'skillFreeClicksEnd', 'skillGoldBonusEnd', 'skillWildGoldEnd', 'startTimestamp', 'unixTimestamp']:
        state[k] = save[k]
        Debug.user("%s: %s"%(k, save[k]))

    Debug.user("ts: %d cooldowns: %s" % (longts, save['skillCooldowns']))
    skills = {}
    for skill, cooldown in save['skillCooldowns'].items():
        skills[skill] = longts >= cooldown

    return skills

###############

def exithotkey(event):
    exit()

def ascendhotkey(event):
    state['ascendNow'] = True

def waithotkey(event):
    if "wait" in state:
        state['wait'] = not state['wait']

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

#wait(1)

#keyDown(Key.F8)
#wait(0.1)
#keyUp(Key.F8)

for x in range(2):
    keyDown(Key.ESC)
    wait(0.05)
    keyUp(Key.ESC)
    wait(1)

# click the X
if exists(Pattern("1439437994711.png").similar(0.80)):
    click()

#Debug.user("screenshot: %s" % SCREEN.capture(0,0,1919,1079))

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
    #Debug.user("screenshot: %s" % SCREEN.capture(roi))

resetstate()
save = updateFromSave()
dumpHeroInfo(save)

#Debug.user("skills: %s" % checkSkillCooldown(save))
#sys.exit(1)

state['primalSoulsStart'] = state['primalSouls']

Debug.user("")
Debug.user("Start")

while True:

    Debug.user("Loop start: %s" %state)

    if state['wait']:
        popup("Sikulix paused")
        # toggle wait off
        waithotkey(None)

#        pos = Env.getMouseLocation()
#        Debug.user("Wait a while %s"%(pos))
#        wait(1)
        continue

    if RELICASCEND and relicfound(save):
        state['ascendNow'] = True

    # past ideal zone
    if state['highestFinishedZone'] > NOFISHZONE or (RELICASCEND and relicfound(save)):
        state['ascendSoon'] = True
        Debug.user("Ascend Soon")

    if state['highestFinishedZone'] > DEEPZONE or state['highestFinishedZone'] > MAXZONE:
        clickMonsters(CLICKTIME)

    if (fish(True) and \
            (state['highestFinishedZone'] > MAXZONE or (RELICASCEND and relicfound(save)))) \
        or state['ascendNow']:

        Debug.user("Ascend Now")
        dumpHeroInfo(save)
        ascend()
        rest(2)

    save = updateFromSave()
    calcrate()

    # 0 DPS
    if state['hired'] == 0:
        Debug.user("found 0 dps")

        wait(1)
        resetstate()
        state['primalSoulsStart'] = state['primalSouls']

        if fish():
            Debug.user("Found fish, waiting..")
            wait(5)
        else:
            first = True
            locateHero("Natalia", zclick, [1])

            for x in range(LEVELSKIP):
                # skip levels, next level arrow
                clickn(Pattern("1439078366733.png"), 18)
                rest()
                # space next to next level arrow
                clickn(Pattern("1439078366733.png").targetOffset(-60,0), 1)

                # necessary to wait a bit at each step in order to collect enough gold to progress
                wait(2)

        # Typical Midas start
        locateHero("Midas", zclick, [8])
        progressMode()

        scrollBottom()
        buyUpgrades()
        wait(1)

        type('5')
        clickMonsters(30)
        locateHero(INITIALHERO, qclick)
        clickMonsters(60)

        progressMode()
        locateHero("Natalia", zclick, [8])

    elif state['initial'] < INITIALLVL:
        scrollTop()

        locateHero(INITIALHERO, qclick)
        rest()

        scrollBottom()
        buyUpgrades()
        scrollTop()

        progressMode()

        if not allHired(save):
            hireHeroes()

    else:
        # gilded
        Debug.user("look for gilded heroes")
        if findUp(Pattern("1439148729231.png").similar(0.93).targetOffset(46,33), qclick):
            if not state['besthero']:
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
                        qclick(getLastMatch())
                        Debug.user("leveled secondary gilded hero")
                except:
                    Debug.user("found hired best hero")
                    state['besthero'] = True
                    pass

        else:
            findUp(Pattern("1439031334204.png").similar(0.85).targetOffset(16,11), qclick)
            Debug.user("leveled secondary hero, didn't find primary")

        Debug.user("done with gild level up")

        scrollBottom()
        buyUpgrades()
        scrollTop()

        if not allHired(save):
            hireHeroes()

        # find inactive progression mode
        if progressMode() or state['highestFinishedZone'] > NOFISHZONE or state['highestFinishedZone'] > MAXZONE:
            state['ascendSoon'] = True
            Debug.user("Ascend Soon")

    darkRitual()

    Debug.user("Loop done: %s" %(state))
