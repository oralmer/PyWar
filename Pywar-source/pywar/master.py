import argparse
import codecs
import http.client
import io
import json
import os.path
import socket
import subprocess
import sys
import tarfile
import time

import engine

TIMEOUT = 10
REQUEST_HEADERS = {
    'Content-type': 'application/json'
}
COUNTRY_NAMES = [
    'Absurdistan',
    'Berzerkistan',
    'Cobrastan',
    'Derkaderkastan'
]


def parse_args():
    parser = argparse.ArgumentParser(description='PyWar master, running the game engine and triggering the slaves.')
    parser.add_argument('-m', '--map', metavar='FILE', type=str, default='game.json',
                        help='Path to a JSON file containing the initial game map.')
    parser.add_argument('-s', '--slaves', metavar='FILE', type=str, default='slaves.json',
                        help='Path to a JSON file mapping a country name to the slave module path.')
    parser.add_argument('-t', '--turns', metavar='NUM', type=int, default=1024,
                        help='Amount of turns to play in the game.')
    parser.add_argument('-l', '--game-log', metavar='FILE', type=str, default='log/game.tar.gz',
                        help='Gzipped tarball file for dumping game log.')
    parser.add_argument('--slaves-timeout', metavar='TIME', type=float, default=None,
                        help='Timeout for waiting for slaves to be ready.')
    parser.add_argument('--slaves-output', metavar='DIR', type=str, default='log/',
                        help='Directory for storing STDOUT and STDERR files of slave processes.')
    return parser.parse_args()


def ensure_python3():
    if sys.version_info.major != 3:
        raise SystemExit('You must run this with pyhon3.')


def get_open_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def get_slave_file():
    current_dir = os.path.dirname(__file__)
    py_file = os.path.join(current_dir, 'slave.py')
    pyc_file = os.path.join(current_dir, 'slave.pyc')
    if os.path.exists(py_file):
        return py_file
    elif os.path.exists(pyc_file):
        return pyc_file
    else:
        raise FileNotFoundError('Could not find slave script')


class Slave(object):
    def __init__(self, tactical_module_path, strategic_module_path, output_location=None):
        super(Slave, self).__init__()
        self.port = get_open_port()
        if output_location is not None:
            dir_name = os.path.dirname(output_location)
            if not os.path.isdir(dir_name):
                os.makedirs(dir_name)
            self.stdout = open(output_location + '.stdout', 'w')
            self.stderr = open(output_location + '.stderr', 'w')
        else:
            self.stdout = None
            self.stderr = None
        self.subprocess = subprocess.Popen(
            [sys.executable, get_slave_file(), '--port', str(self.port),
             '--tactical-module-path', tactical_module_path,
             '--strategic-module-path', strategic_module_path],
            stdout=self.stdout, stderr=self.stderr)
        self.conn = None

    def is_dead(self):
        return self.subprocess.poll() is not None

    def is_ready(self):
        if self.subprocess.poll() is not None:
            return False
        try:
            conn = http.client.HTTPConnection('localhost', self.port, timeout=0.5)
            conn.request('HEAD', '/isup')
            response = conn.getresponse()
            return response.status == 200
        except:
            return False

    def send_turn_request(self, turn_data):
        assert self.conn is None
        self.conn = http.client.HTTPConnection('localhost', self.port, timeout=TIMEOUT)
        self.conn.request('POST', '/turn', json.dumps(turn_data), REQUEST_HEADERS)

    def get_turn_response(self):
        assert self.conn is not None
        response = self.conn.getresponse()
        self.conn = None
        if response.status != 200:
            raise ValueError(response.reason)
        return json.load(codecs.getreader('utf-8')(response))

    def kill(self):
        self.subprocess.kill()
        self.subprocess.wait()
        if self.stdout is not None:
            self.stdout.close()
            self.stdout = None
        if self.stderr is not None:
            self.stderr.close()
            self.stderr = None


class Master(object):
    def __init__(self, game, slaves, slaves_output_dir=None, game_log=None, expected_turns=0):
        """Initializes the master game.

        slaves is a dict from country name to their code module path.
        """
        super(Master, self).__init__()
        self.game = game
        self.slaves = {game.get_country(country): Slave(module_paths['tactical'], module_paths['strategic'],
                                                        output_location=os.path.join(slaves_output_dir,
                                                                                     country) if slaves_output_dir else None)
                       for country, module_paths in slaves.items()}
        if game_log is None:
            self.game_log = None
        else:
            self.game_log = tarfile.open(game_log, mode='w:gz')
        self._turn_name_padding = len(str(expected_turns))

    def wait_for_ready_slaves(self, timeout=None):
        """Block until all slaves are ready.

        If timeout is not None, this is the time (in seconds) before giving up on
        the slaves.

        If all slaves are ready, True is returned. If we've reached the given
        timeout, False is returned.
        """
        start_time = time.time()
        while timeout is None or time.time() - start_time < timeout:
            for slave in self.slaves.values():
                if slave.is_dead():
                    return False
                if not slave.is_ready():
                    break
            else:
                return True
            print('Slaves are not ready yet, sleeping for 1 second...')
            time.sleep(1)
        return False

    def get_non_ready_slaves(self):
        """Returns the list of country names whose corresponding slaves that are not ready.

        These slaves are considered as automatically losers.
        """
        return [country.name for country, slave in self.slaves.items() if not slave.is_ready()]

    def run_turn(self):
        for country, slave in self.slaves.items():
            turn_data = self.game.to_dict_as_seen_by(country)
            slave.send_turn_request(turn_data)

        turn_commands = {}
        for country, slave in self.slaves.items():
            try:
                commands = slave.get_turn_response()
            except Exception as e:
                print('Failed getting country {} commands: {}'.format(country.name, e))
                turn_commands[country] = []
            else:
                turn_commands[country] = commands

        self.game.apply_turn(turn_commands)
        self.log_turn(turn_commands)

    def countries_in_game(self):
        """Returns the list of countries that still participate in the game.

        A country participates in the game if and only if it has at least one tile,
        or at least one piece.
        """
        return [country for country in self.game.countries if len(country.tiles) > 0 and len(country.pieces) > 0]

    def log_turn(self, turn_commands):
        if self.game_log is None:
            return
        turn_dict = {
            'state': self.game.to_dict(),
            'commands': {country.name: self.add_piece_data(commands) for country, commands in turn_commands.items()},
        }
        turn_data = json.dumps(turn_dict).encode('utf8')
        info = tarfile.TarInfo('turn-{}.json'.format(str(self.game.turns).zfill(self._turn_name_padding)))
        info.size = len(turn_data)
        self.game_log.addfile(info, io.BytesIO(turn_data))

    def add_piece_data(self, commands):
        for command in commands:
            command['type'] = self.game.pieces[command['pieceId']].piece_type
            command['location'] = self.game.pieces[command['pieceId']]._tile._coordinates_dict
        return commands

    def finalize(self):
        for slave in self.slaves.values():
            try:
                slave.kill()
            except:
                pass
        if self.game_log is not None:
            self.game_log.close()
            self.game_log = None


def main(args):
    print('Loading map JSON...')
    with open(args.map, 'r') as map_file:
        game_dict = json.load(map_file)
    print('Loading slaves configuration...')
    with open(args.slaves, 'r') as slaves_file:
        slaves_dict = json.load(slaves_file)
    print('Initializing game...')
    game = engine.game_from_dict(game_dict)
    print('Initializing slaves...')
    master = Master(game, slaves_dict,
                    slaves_output_dir=args.slaves_output,
                    game_log=args.game_log,
                    expected_turns=args.turns)
    try:
        print('Waiting for slaves to be ready...')
        if not master.wait_for_ready_slaves():
            non_ready_slaves = master.get_non_ready_slaves()
            print('Game over automatically for the countries: {}'.format(', '.join(non_ready_slaves)))
            return

        game_start_time = time.time()
        for turn_num in range(args.turns):
            print('Running turn {}...'.format(turn_num))
            master.run_turn()
            countries_in_game = master.countries_in_game()
            if len(countries_in_game) == 1:
                print('{} won the game!'.format(countries_in_game[0].name))
                break
        game_end_time = time.time()
        print('Game completed after {:.3} seconds.'.format(game_end_time - game_start_time))
    finally:
        master.finalize()


if __name__ == '__main__':
    ensure_python3()
    args = parse_args()
    main(args)
