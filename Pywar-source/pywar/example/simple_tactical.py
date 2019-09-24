import random

import common_types
import strategic_api

tank_to_coordinate_to_attack = {}


def move_tank_to_destination(tank, dest):
    """Returns True if the tank's mission is complete."""
    if dest is None:
        return
    tank_coordinate = tank.tile.coordinates
    if dest.x < tank_coordinate.x:
        new_coordinate = common_types.Coordinates(tank_coordinate.x - 1, tank_coordinate.y)
    elif dest.x > tank_coordinate.x:
        new_coordinate = common_types.Coordinates(tank_coordinate.x + 1, tank_coordinate.y)
    elif dest.y < tank_coordinate.y:
        new_coordinate = common_types.Coordinates(tank_coordinate.x, tank_coordinate.y - 1)
    elif dest.y > tank_coordinate.y:
        new_coordinate = common_types.Coordinates(tank_coordinate.x, tank_coordinate.y + 1)
    else:
        tank.attack()
        return True
    tank.move(new_coordinate)
    return False


class MyStrategicApi(strategic_api.StrategicApi):
    def __init__(self, *args, **kwargs):
        super(MyStrategicApi, self).__init__(*args, **kwargs)
        to_remove = set()
        for tank_id, destination in tank_to_coordinate_to_attack.items():
            tank = self.context.my_pieces.get(tank_id)
            if tank is None:
                to_remove.add(tank_id)
                continue
            if move_tank_to_destination(tank, destination):
                to_remove.add(tank_id)
        for tank_id in to_remove:
            del tank_to_coordinate_to_attack[tank_id]

    def get_my_country(self):
        return self.context.my_country

    def list_all_countries(self):
        return self.context.all_countries

    def conquer_using_tanks_tile_of(self, countries):
        tank = self._get_available_tank()
        if tank is None:
            return
        tile = self._get_destination_tile(countries)
        if tile is None:
            return
        tank_to_coordinate_to_attack[tank.id] = tile.coordinates
        if move_tank_to_destination(tank, tile.coordinates):
            del tank_to_coordinate_to_attack[tank.id]

    def _get_available_tank(self):
        """Returns a tank that has no assigned destination."""
        items = list(self.context.my_pieces.items())
        random.shuffle(items)
        for piece_id, piece in items:
            if piece.type != 'tank':
                continue
            if piece_id in tank_to_coordinate_to_attack:
                continue
            if len(self.context.get_commands_of_piece(piece_id)) > 0:
                continue
            return piece
        # No available tank
        return None

    def _get_destination_tile(self, countries):
        """Returns a tile that is owned by one of the given countries.

        Only a tile that has no tank heading to will be returned.
        """
        tiles = list(self.context.tiles.values())
        random.shuffle(tiles)
        for tile in tiles:
            if tile.country not in countries:
                continue
            if tile.coordinates not in tank_to_coordinate_to_attack.values():
                return tile
        # No available tile
        return None


def get_strategic_implementation(context):
    return MyStrategicApi(context)
