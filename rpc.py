from watcher import Watcher
from pypresence.presence import Presence
import time
import glob
import json
from config import LOGS_PATH, CLIENT_ID, DISPLAYED_RANK, RANKS


def get_latest_log():
    files = {filename: filename.split(
        '.')[1] for filename in glob.glob(LOGS_PATH + '/Journal.*.log')}
    return max(files, key=lambda key: files[key])


class RPClient:
    def __init__(self):
        self.commander = ''
        self.ship = 'none'
        self.system = 'none'
        self.body = 'none'
        self.docked = ''
        self.fsd_destination = ''
        self.near_planet = False
        self.landed = False
        self.srv = False
        self.rank = 0
        self.shutdown = False

        self.RPC = Presence(CLIENT_ID, pipe=0)
        self.RPC.connect()

    def parse(self, line):
        data = json.loads(line)
        event = data['event']

        if event == 'LoadGame':
            self.commander = data['Commander']
            self.ship = data['Ship_Localised']
        if event == 'Location':
            self.system = data['StarSystem']
        if event == 'Docked':
            self.docked = data['StationName']
        if event == 'Undocked':
            self.docked = ''
        if event == 'FSDJump':
            self.system = data['StarSystem']
            self.body = data['Body']
            self.fsd_destination = ''
        if event == 'SupercruiseExit':
            self.body = data['Body']
        if event == 'Rank':
            self.rank = data[DISPLAYED_RANK.title()]
        if event == 'StartJump' and data['JumpType'] == 'Hyperspace':
            self.fsd_destination = data['StarSystem']
        if event == 'ApproachBody':
            self.near_planet = True
            self.body = data['Body']
        if event == 'Touchdown':
            self.landed = True
        if event == 'LaunchSRV':
            self.srv = True
        if event == 'DockSRV':
            self.srv = False
        if event == 'Liftoff':
            self.landed = False
        if event == 'LeaveBody':
            self.near_planet = False
        if event == 'Shutdown':
            self.shutdown

    def parse_all(self):
        file = open(get_latest_log(), 'r', encoding='utf8')
        lines = file.readlines()

        for line in lines:
            self.parse(line)

    def start(self):
        self.parse_all()

        print('Your presence is working!')

        def change():
            self.parse_all()
            state = 'In ' + self.ship

            if self.docked != '':
                details = "Docked at " + self.docked
            elif self.fsd_destination != '':
                details = 'Jumping to ' + self.fsd_destination
            elif self.srv:
                details = 'In SRV on ' + self.body
            elif self.landed:
                details = 'Landed on ' + self.body
            elif self.near_planet:
                details = 'Near ' + self.body
            else:
                details = "Exploring " + self.system

            large_image = self.ship.lower().replace(' ', '-')
            large_text = 'Commander ' + self.commander
            small_image = DISPLAYED_RANK.lower() + '-' + str(self.rank)
            small_text = RANKS[DISPLAYED_RANK.lower()][self.rank]
            self.RPC.update(state=state, details=details, large_image=large_image,
                            large_text=large_text, small_image=small_image, small_text=small_text)

        watcher = Watcher(get_latest_log(), change)
        watcher.watch()

        while True:
            if (self.shutdown == True):
                break
            time.sleep(1)
