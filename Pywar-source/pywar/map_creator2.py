from engine import *
from commands import *
import json
import gzip
import time

game = Game(10, 10)
cobrastan = game.add_country('cobrastan')
absurdistan = game.add_country('absurdistan')
for x in range(10):
  for y in range(10):
    game.tiles[x][y].money = 5

game.tiles[9][0].money = 60
game.tiles[0][9].money = 60
game.tiles[5][4].money = 30
game.tiles[4][5].money = 30

for x in range(5):
	for y in range(5):
		game.tiles[x][y].country = cobrastan
for x in range(5, 10):
	for y in range(5, 10):
		game.tiles[x][y].country = absurdistan
Builder(game, game.tiles[0][0], cobrastan)
Builder(game, game.tiles[9][9], absurdistan)
Tank(game, game.tiles[0][4], cobrastan)
Tank(game, game.tiles[4][0], cobrastan)
Tank(game, game.tiles[5][9], absurdistan)
Tank(game, game.tiles[9][5], absurdistan)
Antitank(game, game.tiles[5][5], absurdistan)
Antitank(game, game.tiles[4][4], cobrastan)
Spy(game, game.tiles[0][0], cobrastan)
Spy(game, game.tiles[9][9], absurdistan)
#Tank(game, game.tiles[2][2], absurdistan)


#		builder = Builder(game, game.tiles[x][y], cobrastan)
#		builder.money = 7000
#		builder.build('tank')
#		builder.build('tank')
#		builder.build('airplane')
#		builder.build('airplane')
#		builder.build('artillery')
#		builder.build('artillery')
#		builder.build('spy')
#		builder.build('spy')


#		builder = Builder(game, game.tiles[x][y], absurdistan)
#		builder.money = 7000
#		builder.build('tank')
#		builder.build('tank')
#		builder.build('airplane')
#		builder.build('airplane')
#		builder.build('artillery')
#		builder.build('artillery')
#		builder.build('spy')
#		builder.build('spy')

#absurdistan_builder = Builder(game, game.tiles[15][14], absurdistan)
#absurdistan_builder.money = 70000
#absurdistan_tank = absurdistan_builder.build('tank')
#cobrastan_builder = Builder(game, game.tiles[15][16], cobrastan)
#cobrastan_builder.money = 70000
#cobrastan_tank = cobrastan_builder.build('tank')
#cobrastan_tank2 = cobrastan_builder.build('airplane')

game_dict = game.to_dict()
with open('game.json', 'w') as game_file:
  json.dump(game_dict, game_file)

exit()

turn1 = {
	absurdistan: [MoveCommand(absurdistan_tank.id, Coordinates(15, 15))],
	cobrastan: [
		MoveCommand(cobrastan_tank.id, Coordinates(15, 15)),
		MoveCommand(cobrastan_tank2.id, Coordinates(15, 15)),
	],
}
# absurdistan_tank.tile = game.tiles[15][15]
# cobrastan_tank.tile = game.tiles[15][15]
# cobrastan_tank2.tile = game.tiles[15][15]
game.apply_turn(turn1)

turn2 = {
	absurdistan: [MeleeAttackCommand(absurdistan_tank.id)],
	cobrastan: [MeleeAttackCommand(cobrastan_tank2.id)],
}
# absurdistan_tank.attack()
# cobrastan_tank2.attack()
# game.perform_battles()
game.apply_turn(turn2)

print(game.tiles[15][15].to_dict())

x = time.time()
d = game.to_dict()
y = time.time()

print('It took {} seconds to create dict'.format(y - x))

x = time.time()
json_string = json.dumps(d)
y = time.time()
# print(len(json_string))
print('It took {} seconds to create json'.format(y - x))
x = time.time()
compressed = gzip.compress(json_string.encode('utf8'))
y = time.time()
# print(len(compressed))
# print('It took {} seconds to compress'.format(y - x))

# print(json_string)

def time_per_country(country):
	x = time.time()
	d = game.to_dict_as_seen_by(country)
	y = time.time()
	print('It took {} seconds to create dict for {}'.format(y - x, country.name))

	x = time.time()
	json_string = json.dumps(d)
	y = time.time()
	print('It took {} seconds to create json for {}'.format(y - x, country.name))

	x = time.time()
	d2 = json.loads(json_string)
	y = time.time()
	print('It took {} seconds to parse json for {}'.format(y - x, country.name))

time_per_country(absurdistan)
time_per_country(cobrastan)
