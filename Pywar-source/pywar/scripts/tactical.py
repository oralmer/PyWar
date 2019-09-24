

import random
import sys

import tactical_api
import constants
import strategic_api

piece_to_coordinate_to_attack = {}
builder_to_coordinate_with_money = {}


def move_piece_to_destination(piece, destinations_dict):
    dest = destinations_dict.get(piece.id)
    if dest is None:
        return
    piece_coordinate = piece.tile.coordinates
    if dest.x < piece_coordinate.x:
        new_coordinate = tactical_api.Coordinates(piece_coordinate.x - 1, piece_coordinate.y)
    elif dest.x > piece_coordinate.x:
        new_coordinate = tactical_api.Coordinates(piece_coordinate.x + 1, piece_coordinate.y)
    elif dest.y < piece_coordinate.y:
        new_coordinate = tactical_api.Coordinates(piece_coordinate.x, piece_coordinate.y - 1)
    elif dest.y > piece_coordinate.y:
        new_coordinate = tactical_api.Coordinates(piece_coordinate.x, piece_coordinate.y + 1)
    else:
        del destinations_dict[piece.id]
        return
    piece.move(new_coordinate)


def handle_tank(piece_id, piece, context, not_my_tiles):
    global piece_to_coordinate_to_attack
    if piece.tile.country != context.my_country:
        piece.attack()
        return
    if piece_id not in piece_to_coordinate_to_attack:
        # Randomly select a tile to go to.
        if len(not_my_tiles) == 0:
            return
        piece_to_coordinate_to_attack[piece_id] = random.choice(not_my_tiles)
    move_piece_to_destination(piece, piece_to_coordinate_to_attack)


def handle_builder(piece_id, piece, context):
    global builder_to_coordinate_with_money
    if piece.tile.money > 0 and piece.tile.country == piece.country:
        piece.collect_money(min(piece.tile.money, constants.BUILDER_MAX_COLLECTION_IN_TURN))
    elif piece.money > constants.TANK_PRICE:
        piece.build_tank()
    else:
        if piece_id not in builder_to_coordinate_with_money:
            max_money = -1
            tiles_with_max_money = []
            for tile in context.tiles.values():
                if tile.money is None or tile.money < max_money:
                    continue
                if tile.money == max_money:
                    tiles_with_max_money.append(tile)
                    continue
                max_money = tile.money
                tiles_with_max_money = [tile]
            if len(tiles_with_max_money) == 0:
                return
            builder_to_coordinate_with_money[piece_id] = random.choice(tiles_with_max_money).coordinates
        move_piece_to_destination(piece, builder_to_coordinate_with_money)


class MyStrategicApi(strategic_api.StrategicApi):
    def build_tank(self):
        my_tiles = self.context.get_tiles_of_country(self.context.my_country)
        not_my_tiles = []
        for x in range(self.context.game_width):
            for y in range(self.context.game_height):
                coordinate = tactical_api.Coordinates(x, y)
                if coordinate not in my_tiles:
                    not_my_tiles.append(coordinate)
        for piece_id, piece in self.context.my_pieces.items():
            if piece.type == 'tank':
                pass
                handle_tank(piece_id, piece, self.context, not_my_tiles)
            elif piece.type == 'builder':
                handle_builder(piece_id, piece, self.context)


def get_strategic_implementation(context):
    return MyStrategicApi(context)
