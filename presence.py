from watcher import Watcher
from pypresence.presence import Presence
from time import sleep
from glob import glob
from config import LOGS_PATH, CLIENT_ID, DISPLAYED_RANK, RANKS
import json

class PresenceClient:
    def __init__(self):
        self.commander = ''
        self.ship = 'none'
        self.system = 'none'
        self.body = 'none'
        self.docked = ''
        self.docked_station_type = ''
        self.fsd_destination = ''
        self.rank = 0

        self.near_planet = False
        self.landed = False
        self.srv = False
        self.shutdown = False

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
            self.docked_station_type = data['StationType']
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
        if event == 'ShipyardSwap':
            self.ship = data['ShipType_Localised']
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

    def update_state(self):
        large_image = '-'.join(self.ship.lower().split(' '))
        large_text = f'Commander {self.commander}'
        small_image = f'rank-{self.rank}-{DISPLAYED_RANK.lower()}'
        small_text = RANKS[DISPLAYED_RANK.lower()][self.rank]

        state = f'In {self.ship}'

        if self.docked != '':
            details = f'Docked at {self.docked} in {self.system}'
            large_image = self.docked_station_type.lower()
            small_text = f'In {self.ship}'
            small_image = '-'.join(self.ship.lower().split(' '))
        elif self.fsd_destination != '':
            details = f'Jumping to {self.fsd_destination}'
        elif self.srv:
            state = 'In SRV'
            details = f'Exploring {self.body} in {self.system}'
        elif self.landed:
            details = f'Landed on {self.body} in {self.system}' 
        elif self.near_planet:
            details = f'Near {self.body} in {self.system}'
        else:
            details = f'Exploring {self.system}'
        
        self.presence.update(state=state, details=details, large_image=large_image,
                                 large_text=large_text, small_image=small_image, small_text=small_text)

    def parse_all(self):
        file = open(self.get_latest_log(), 'r', encoding='utf8')
        lines = file.readlines()

        for line in lines:
            self.parse(line)

    def start(self):
        print(f'Loading {self.get_latest_log()}')
        print('Your presence is working!')

        def change():
            self.parse_all()
            self.update_state()

        watcher = Watcher(self.get_latest_log(), change)

        while True:
            if (self.shutdown):
                self.presence.close()
                print('Waiting for game to be played..')
                break

            watcher.look()
            sleep(1)
