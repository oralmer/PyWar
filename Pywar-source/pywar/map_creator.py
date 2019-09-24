from engine import *
from commands import *
import json
import gzip
import time

game = Game(10, 10)
uk = game.add_country('UK')
usa = game.add_country('USA')
botland = game.add_country('Botland')
for x in range(10):
  for y in range(10):
    game.tiles[x][y].money = 10

for x in range(5):
	for y in range(5):
		game.tiles[x][y].country = uk
for x in range(5, 10):
	for y in range(5, 10):
		game.tiles[x][y].country = usa
for x in range(5, 10):
	for y in range(5):
		game.tiles[x][y].country = botland
Builder(game, game.tiles[0][0], uk)
Builder(game, game.tiles[9][9], usa)
Builder(game, game.tiles[9][0], botland)

game_dict = game.to_dict()
with open('game-map.json', 'w') as game_file:
  json.dump(game_dict, game_file)

