from watcher import Watcher
from pypresence.presence import Presence
from time import sleep
from glob import glob
from config import LOGS_PATH, CLIENT_ID, DISPLAYED_RANK, RANKS
import json

# Yeah, maybe it's shitty code
class PresenceClient:
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
        self.shutdown = False
        self.rank = 0

        self.presence = Presence(CLIENT_ID)
        self.presence.connect()

    def get_latest_log(self):
        files = {filename: filename.split(
            '.')[1] for filename in glob(LOGS_PATH + '/Journal.*.log')}
        return max(files, key=lambda key: files[key])

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
            self.shutdown = True

    def parse_all(self):
        file = open(self.get_latest_log(), 'r', encoding='utf8')
        lines = file.readlines()

        for line in lines:
            self.parse(line)

    def start(self):
        print('Loading {}..'.format(self.get_latest_log()))
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
            self.presence.update(state=state, details=details, large_image=large_image,
                                 large_text=large_text, small_image=small_image, small_text=small_text)

        watcher = Watcher(self.get_latest_log(), change)

        while True:
            if (self.shutdown):
                self.presence.close()
                print('Waiting for game to be played..')
                break

            watcher.look()
            sleep(1)
