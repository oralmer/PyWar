from collections import namedtuple

import commands
import constants

Coordinates = namedtuple('Coordinates', ['x', 'y'])

def distance(a, b):
  """Calculates the distance between the coordinates a and b."""
  return abs(a.x - b.x) + abs(a.y - b.y)

class BasePiece(object):
  """Base class for game pieces.

  This class exports the following fields:
  * id: Piece ID, as assigned by the server.
  * tile: The tile object of which this piece has been in, before this turn
          began.
  * type: Piece type (as a string).
  * country: The name of the country of which this piece belongs to.
  """

  def __init__(self, context, tile, piece_dict):
    super(BasePiece, self).__init__()
    self._context = context
    self.tile = tile
    self.id = piece_dict['id']
    self.type = piece_dict['type']
    self.country = piece_dict['country']

  def move(self, destination):
    """Moves this piece to the destination tile.

    destination is expected to have a type of either Coordinates or Tile.
    """
    if isinstance(destination, Tile):
      destination = destination.coordinates
    assert isinstance(destination, Coordinates)
    self._context._commands.append(commands.MoveCommand(self.id, destination))

class FlyingPiece(BasePiece):
  """Base class for flying pieces.

  This class exports the following fields:
  * in_air: A boolean indicating weather this piece is currently flying (True)
            or on the ground (False).
  * time_in_air: An integer counting the amount of turns of which this piece
                 has been flying, or None if this piece is on the ground.

  See BasePiece for more fields.
  """

  def __init__(self, context, tile, piece_dict):
    super(FlyingPiece, self).__init__(context, tile, piece_dict)
    self.in_air = piece_dict['inAir']
    self.time_in_air = piece_dict.get('timeInAir', None)

  def take_off(self):
    """Take off this piece.

    If this piece is already in the air, this is a no-op.
    """
    self._context._commands.append(commands.TakeOffCommand(self.id))

  def land(self):
    """Land this piece.

    If this piece is already on the ground, this is a no-op.
    """
    self._context._commands.append(commands.LandCommand(self.id))

class Tank(BasePiece):
  """Represents a game tank.
  
  The value of its type field is "tank".

  This class does not expose any fields, except those exposed by BasePiece.
  """

  def attack(self):
    """Attacks the current game tile."""
    self._context._commands.append(commands.MeleeAttackCommand(self.id))

class Airplane(FlyingPiece):
  """Represents a game airplane.
  
  The value of its type field is "airplane".

  This class does not expose any fields, except those exposed by BasePiece and
  FlyingPiece.
  """

  def attack(self):
    """Attacks the current game tile."""
    self._context._commands.append(commands.MeleeAttackCommand(self.id))

class Artillery(BasePiece):
  """Represents a game artillery.

  The value of its type field is "artillery".

  This class does not expose any fields, except for those exposed by BasePiece.
  """

  def attack(self, destination):
    """Attacks the destination using this artillery.

    destination is expected to have a type of either Coordinates or Tile.
    """
    if isinstance(destination, Tile):
      destination = destination.coordinates
    assert isinstance(destination, Coordinates)
    self._context._commands.append(commands.RemoteAttackCommand(self.id, destination))

class Helicopter(FlyingPiece):
  """Represents a game helicopter.
  
  The value of its type field is "helicopter".

  This class does not expose any fields, except those exposed by BasePiece and
  FlyingPiece.
  """

  def attack(self, destination):
    """Attacks the destination using this helicopter.

    destination is expected to have a type of either Coordinates or Tile.
    """
    if isinstance(destination, Tile):
      destination = destination.coordinates
    assert isinstance(destination, Coordinates)
    self._context._commands.append(commands.RemoteAttackCommand(self.id, destination))

class Antitank(BasePiece):
  """Represents a game anti-tank.

  The value of its type field is "antitank".

  This class does not expose any fields, except those exposed by BasePiece.
  """
  pass

class IronDome(BasePiece):
  """Represents a game iron dome.

  This class exports the following fields:
  * id_defending: Set to True if and only if the protection of this iron dome
                  has been active before this turn began.

  The value of its type field is "irondome".

  Please refer to BasePiece for information about other exposed fields.
  """
  def __init__(self, context, tile, piece_dict):
    super(IronDome, self).__init__(context, tile, piece_dict)
    self.is_defending = piece_dict['isDefending']

  def turn_on_protection(self):
    """Turns on this iron dome protection."""
    self._context._commands.append(commands.TurnOnProtection(self.id))

  def turn_off_protection(self):
    """Turns off this iron dome protection."""
    self._context._commands.append(commands.TurnOffProtection(self.id))

class Bunker(BasePiece):
  """Represents a game bunker.

  The value of its type field is "bunker".

  This class does not expose any fields, except those exposed by BasePiece.
  """
  pass

class Spy(BasePiece):
  """Represents a game spy.

  The value of its type field is "spy".

  This class does not expose any fields, except those exposed by BasePiece.
  """
  pass

class Tower(BasePiece):
  """Represents a game tower.

  The value of its type field is "tower".

  This class does not expose any fields, except those exposed by BasePiece.
  """
  pass

class Satelite(BasePiece):
  """Represents a game satelite.

  The value of its type field is "spy".

  This class does not expose any fields, except those exposed by BasePiece.
  """
  pass

class Builder(BasePiece):
  """Represents a game builder.

  This class exposes the following fields:
  * money: The amount of money this builder has, before this turn began.

  The value of its type field is "builder".

  Please refer to BasePiece for information about other exposed fields.
  """
  def __init__(self, context, tile, piece_dict):
    super(Builder, self).__init__(context, tile, piece_dict)
    self.money = piece_dict['money']

  def collect_money(self, amount):
    """Collects a certain amount of money from the current Tile."""
    self._context._commands.append(commands.TakeMoneyCommand(self.id, amount))

  def throw_money(self, amount):
    """Throws a certain amount of money to the current Tile."""
    self._context._commands.append(commands.ThrowMoneyCommand(self.id, amount))
  
  def build_tank(self):
    """Builds a new tank piece in the current tile."""
    self._build('tank')

  def build_airplane(self):
    """Builds a new airplane piece in the current tile."""
    self._build('airplane')

  def build_artillery(self):
    """Builds a new artillery piece in the current tile."""
    self._build('artillery')

  def build_helicopter(self):
    """Builds a new helicopter piece in the current tile."""
    self._build('helicopter')

  def build_antitank(self):
    """Builds a new anti-tank piece in the current tile."""
    self._build('antitank')

  def build_iron_dome(self):
    """Builds a new iron dome piece in the current tile."""
    self._build('irondome')

  def build_bunker(self):
    """Builds a new bunker piece in the current tile."""
    self._build('bunker')

  def build_spy(self):
    """Builds a new spy piece in the current tile."""
    self._build('spy')

  def build_tower(self):
    """Builds a new tower piece in the current tile."""
    self._build('tower')

  def build_satelite(self):
    """Builds a new satelite piece in the current tile."""
    self._build('satelite')

  def build_builder(self):
    """Builds a new builder piece in the current tile."""
    self._build('builder')

  def _build(self, piece_type):
    self._context._commands.append(commands.BuildPieceCommand(self.id, piece_type))

TYPE_TO_CLASS = {
  'tank': Tank,
  'airplane': Airplane,
  'artillery': Artillery,
  'helicopter': Helicopter,
  'antitank': Antitank,
  'irondome': IronDome,
  'bunker': Bunker,
  'spy': Spy,
  'tower': Tower,
  'satelite': Satelite,
  'builder': Builder,
}

def _load_piece(context, tile, piece_dict):
  return TYPE_TO_CLASS[piece_dict['type']](context, tile, piece_dict)

class Tile(object):
  """A land unit in the game.

  This class exports the following fields:
  * coordinates: The coordinates of this tile.
  * money: The amount of money in this tile before the turn started, or None if
           this amount is unknown to the current country.
  * country: The name of the country owning this tile, or None if this tile is
             not owned by any country.
  * pieces: A list of pieces on this tile.
  Note that the information here may be incomplete, depending on the visibility
  of the current country on this tile.
  """

  def __init__(self, context, tile_dict):
    super(Tile, self).__init__()
    self.coordinates = Coordinates(**tile_dict['coordinate'])
    self.money = tile_dict['money']
    self.country = tile_dict['country']
    self.pieces = [_load_piece(context, self, piece_dict) for piece_dict in tile_dict['pieces']]

class TurnContext(object):
  """Contains all the context of this turn.

  Some useful fields:
  * tiles: Maps coordinates (int, int) to a Tile object.
  * my_pieces: Maps piece IDs to the actual piece, for pieces owned by our
               country.
  * all_pieces: Same as my_pieces, but for all pieces known by this country.
  * game_width: The width of the game.
  * game_height: The height of the game.
  * my_country: The name of my country.
  * all_countries: The names of all countries in the game.
  """

  def __init__(self, turn_data):
    super(TurnContext, self).__init__()
    self._turn_data = turn_data
    self._commands = []
    self.tiles = {(tile['coordinate']['x'], tile['coordinate']['y']): Tile(self, tile)
                  for tile in turn_data['tiles']}
    self.my_pieces = {}
    self.all_pieces = {}
    self.game_width = turn_data['width']
    self.game_height = turn_data['height']
    self.my_country = turn_data['country']
    self.all_countries = turn_data['all_countries']
    for tile in self.tiles.values():
      for piece in tile.pieces:
        if piece.country == self.my_country:
          self.my_pieces[piece.id] = piece
        self.all_pieces[piece.id] = piece

  def get_tiles_of_country(self, country_name):
    """Returns the set of tile coordinates owned by the given country name.

    If country_name is None, the returned coordinates are of tiles that do not
    belong to any country.
    """
    return {tile.coordinates for tile in self.tiles.values()
            if tile.country == country_name}

  def get_sighings_of_piece(self, piece_id):
    """Returns the sightings of the given piece.

    This method returns a set of sighted pieces and their locations, as seen by
    the given piece.

    Note that the given piece MUST belong to my country in order for this
    method to work.
    """
    piece = self.my_pieces[piece_id]
    if isinstance(piece, Tower):
      sighting_distance = constants.TOWER_SIGHTING_RANGE
    elif isinstance(piece, Satelite):
      sighting_distance = constants.SATELITE_SIGHTING_RANGE
    else:
      sighting_distance = 1
    result = set()
    piece_coordinates = piece.tile.coordinates
    for x in range(piece_coordinates.x - sighting_distance, piece_coordinates.x + sighting_distance):
      for y in range(piece_coordinates.y + sighting_distance, piece_coordinates.y + sighting_distance):
        tile = self.tiles.get((x, y))
        if tile is None or distance(piece_coordinates, tile.coordinates) > sighting_distance:
          continue
        result.update(tile.pieces)
    return result
  
  def get_commands_of_piece(self, piece_id):
    """Returns the list of ordered commands given to the given piece.

    Note that if the piece did not receive any command in this turn, or is not
    owned by my country, or does not exist, an empty list is returned.
    """
    return [command for command in self._commands
            if command.piece_id == piece_id]
  
  def get_result(self):
    return [command.to_dict() for command in self._commands]

