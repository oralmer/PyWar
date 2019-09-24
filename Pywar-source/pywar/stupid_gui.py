import json
import tarfile
import time
import sys

import engine

RESET_COLOR = '\x1b[0m'
BLUE = 123
DARK_BLUE = 68
RED = 210
DARK_RED = 1
COUNTRY_COLORS = [
  (BLUE, DARK_BLUE),
  (RED, DARK_RED),
]

PIECE_TYPE_TO_CHAR = {
  'tank': 'T',
  'airplane': 'A',
  'artillery': 'a',
  'helicopter': 'H',
  'antitank': 't',
  'irondome': 'i',
  'bunker': 'b',
  'spy': 's',
  'tower': 'o',
  'satelite': 'S',
  'builder': 'B',
}

def set_bg_to_color(color):
  return '\x1b[48;5;{}m'.format(color)

def set_fg_to_color(color):
  return '\x1b[38;5;{}m'.format(color)

def print_piece(piece):
  return set_fg_to_color(piece.country.foreground) + PIECE_TYPE_TO_CHAR[piece.dict['type']]

def print_tile(tile):
  pieces = [print_piece(piece) for piece in tile.pieces][:4]
  while len(pieces) < 4:
    pieces.append('*')
  if tile.country is None:
    bg = ''
  else:
    bg = set_bg_to_color(tile.country.background)
  return bg + ''.join(pieces) + RESET_COLOR

def load_game(json_file):
  game = engine.game_from_dict(json.load(json_file)['state'])
  sorted_countries = sorted(game.countries, key=lambda x: x.name)
  for i, country in enumerate(sorted_countries):
    country.foreground, country.background = COUNTRY_COLORS[i]
  return game

def print_legend(game):
  for country in sorted(game.countries, key=lambda x: x.name):
    print_string = '{}: {} tiles, {} pieces'.format(country.name, len(country.tiles), len(country.pieces))
    print(set_bg_to_color(country.background) + print_string + RESET_COLOR)

def print_game(game):
  print_legend(game)
  for x in range(game.width):
    row = [print_tile(game.tiles[x][y]) for y in range(game.height)]
    print(''.join(row))

def print_gameplay(file_path):
  with tarfile.open(file_path, 'r:gz') as tar:
    turns = sorted(filter(lambda name: name.startswith('turn'), tar.getnames()))
    for turn in turns:
      print(turn)
      with tar.extractfile(turn) as turn_json:
        game = load_game(turn_json)
        print_game(game)
        time.sleep(0.1)
        print('\n\n')

print_gameplay(sys.argv[1])

