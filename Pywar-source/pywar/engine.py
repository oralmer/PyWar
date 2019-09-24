"""pyWar"""

from collections import defaultdict
import itertools
import random
import uuid

import commands
from common_types import Coordinates
from constants import *  # TODO: Consider not importing wildcard.

# Piece role in battles

# The piece is attacking in this battle.
ATTACKER_ROLE = 1
# The piece is defending in this battle.
DEFENDER_ROLE = 2
# The piece is passive in this battle.
PASSIVE_ROLE = 3

# Visibility levels of Tiles

# The country does not know anything about the tile, except for its owning country.
# This visibility level is applied if the Tile is not owned by the country, and the country
# has no pieces on the tile, or on evey neighbor of it in distance 1.
NO_VISIBILITY = 0
# The country can see the pieces on the tile, but not the money on it.
# This visibility level is applied if the Tile is within
# SATELILTE_SIGHTING_RANGE distance of a satelite of my country.
SATELITE_VISIBILITY = 1
# The country can see the pieces and money on the tile, but not the spies and
# satalites on it.
# This visibility level is applied if any of the following is satisfied:
# * The tile is owned by the country.
# * The country has a piece on the Tile, or on any neighbor in distance 1 of the tile.
# * The country has a tower in a neighbor of distance TOWER_SIGHTING_RANGE.
PARTIAL_VISIBILITY = 2
# The country can see all pieces and money on the tile, including spies of other countries.
# This visibility level is applied if the country has a spy on this tile.
FULL_VISIBILITY = 3

class Game(object):
  def __init__(self, width, height):
    self.countries = set()
    self.battles_in_queue = defaultdict(list)  # dict: tile -> attackers
    self.tiles = [[LandTile(self, Coordinates(x=x, y=y)) for y in range(height)] for x in range(width)]
    self.width = width
    self.height = height
    self.pieces = {}  # dict: piece ID -> piece
    self.turns = 0

  def add_country(self, *args, **kwargs):
    country = Country(self, *args, **kwargs)
    self.countries.add(country)
    return country
  
  def get_country(self, name):
    for country in self.countries:
      if country.name == name:
        return country
    return None

  def get_new_id(self):
    return str(uuid.uuid4())

  def to_dict(self):
    return {
      'countries': [country.name for country in self.countries],
      'tiles': [[tile.to_dict() for tile in tile_row] for tile_row in self.tiles],
      'width': self.width,
      'height': self.height,
    }

  def to_dict_as_seen_by(self, country):
    return {
      'tiles': [tile.to_dict_as_seen_by(country) for tile in itertools.chain.from_iterable(self.tiles)],
      'country': country.name,
      'all_countries': [c.name for c in self.countries],
      'width': self.width,
      'height': self.height,
    }

  def apply_turn(self, commands_by_country):
    self.turns += 1
    commanded_pieces = set()
    for country, command_dicts in commands_by_country.items():
      try:
        for command_dict in command_dicts:
          command = commands.command_from_dict(command_dict)
          if command.piece_id in commanded_pieces:
            raise ValueError('A piece cannot make have two commands in one turn')
          commanded_pieces.add(command.piece_id)
          if self.pieces[command.piece_id].country != country:
            raise KeyError('Wrong piece')
          command.apply(self)
      except:
        print('Country has an exception, skipping commands')
    self.perform_battles()
    country_to_satelite_visible_tiles = defaultdict(set)
    country_to_visible_tiles = defaultdict(set)
    country_to_tiles_with_its_own_spies = defaultdict(set)
    for piece in self.pieces.values():
      piece.turn_done()
      if isinstance(piece, Satelite):
        country_to_satelite_visible_tiles[piece.country].update(piece.tile.neighbors(SATELITE_SIGHTING_RANGE))
        continue
      country_to_visible_tiles[piece.country].add(piece.tile)
      country_to_visible_tiles[piece.country].update(piece.tile.neighbors())
      if isinstance(piece, Spy):
        country_to_tiles_with_its_own_spies[piece.country].add(piece.tile)
      elif isinstance(piece, Tower):
        country_to_visible_tiles[piece.country].update(piece.tile.neighbors(TOWER_SIGHTING_RANGE))

    # Set visibility level for each tile per country.
    for tile in itertools.chain.from_iterable(self.tiles):
      tile.visibility_level_per_country = {
        country : FULL_VISIBILITY if tile in country_to_tiles_with_its_own_spies[country] else
              PARTIAL_VISIBILITY if tile.country is country or tile in country_to_visible_tiles[country] else NO_VISIBILITY
        for country in self.countries}

  def perform_battles(self):
    all_battles = []
    for tile, attackers in self.battles_in_queue.items():
      defenders = tile.get_defenders()
      passives = tile.pieces.difference(attackers).difference(defenders)
      tile_participants = list(itertools.chain(
          ((piece, ATTACKER_ROLE) for piece in attackers),
          ((piece, DEFENDER_ROLE) for piece in defenders),
          ((piece, PASSIVE_ROLE) for piece in passives if not isinstance(piece, (Spy, Satelite, Builder)))))
      random.shuffle(tile_participants)
      all_battles.append((tile, tile_participants))
    self.battles_in_queue = defaultdict(list)
    random.shuffle(all_battles)
    for tile, participants in all_battles:
      perform_battle_in_tile(tile, participants)

def perform_battle_in_tile(tile, participants):
  participants_per_country = defaultdict(list)
  for participant in participants:
    participants_per_country[participant[0].country].append(participant)
  for duel_participants in itertools.zip_longest(*participants_per_country.values(), fillvalue=(None, None)):
    # Note that a duel may consist of more or less than 2 parties
    pieces_to_kill = set()
    conquering_pieces = []
    for piece, role in duel_participants:
      if piece is None:
        continue
      if piece.should_die_in_battle(role, tile, duel_participants):
        pieces_to_kill.add(piece)
      if piece.should_conquer(role, duel_participants):
        conquering_pieces.append(piece)
    assert(len(conquering_pieces) <= 1), 'Too many conquering pieces found!'
    if conquering_pieces:
      country = conquering_pieces[0].country
      tile.country = country
      for piece in tile.pieces:
        if isinstance(piece, (Artillery, Bunker, Builder, Tower)):
          piece.country = country
        elif isinstance(piece, (Airplane, Helicopter)) and not piece.in_air:
          piece.country = country
        elif isinstance(piece, (Antitank, IronDome, Spy)):
          pieces_to_kill.add(piece)
    for piece in pieces_to_kill:
      piece.kill()

class Country(object):
  def __init__(self, game, name):
    self.game = game
    self.name = name
    self.tiles = set()
    self.pieces = set()

def distance(a, b):
  if not isinstance(a, Coordinates):
    a = a.coordinates
  if not isinstance(b, Coordinates):
    b = b.coordinates
  return abs(a.x - b.x) + abs(a.y - b.y)

class LandTile(object):
  def __init__(self, game, coordinates, money=0):
    self.game = game
    self._coordinates = coordinates
    self._coordinates_dict = coordinates._asdict()
    self.money = money
    self._country = None
    self.pieces = set()
    self.visibility_level_per_country = {}

  def __repr__(self):
    return '<Tile at {}{}>'.format(self.coordinates, ' owned by {}'.format(self.country.name) if self.country is not None else '')

  @property
  def coordinates(self):
    return self._coordinates

  @property
  def coordinates_dict(self):
    return self._coordinates_dict

  @property
  def country(self):
    return self._country

  @country.setter
  def country(self, value):
    if self._country is not None:
      self._country.tiles.remove(self)
    self._country = value
    if value is not None:
      value.tiles.add(self)

  def neighbors(self, dist=1):
    result = []
    for x in range(max(0, self.coordinates.x - dist), min(self.game.width, self.coordinates.x + dist + 1)):
      for y in range(max(0, self.coordinates.y - dist), min(self.game.height, self.coordinates.y + dist + 1)):
        tile = self.game.tiles[x][y]
        if distance(self, tile) > dist:
          continue
        yield tile

  def get_defenders(self):
    defenders = []
    for tile in self.neighbors(MAX_DEFENDER_RANGE):
      for piece in tile.pieces:
        if piece.can_defend(self):
          if isinstance(piece, Bunker):
            defenders.extend([piece] * (BUNKER_DEFEND_MULTIPLIER - 1))
          defenders.append(piece)
    return defenders

  def to_dict(self):
    return {
      'coordinate': self.coordinates_dict,
      'money': self.money,
      'country': self.country.name if self.country else None,
      'pieces': [piece.to_dict() for piece in self.pieces]
    }

  def to_dict_as_seen_by(self, country):
    visibility = self.visibility_level_per_country.get(country, NO_VISIBILITY)
    if visibility == FULL_VISIBILITY:
      pieces_to_return = [piece.to_dict() for piece in self.pieces]
    elif visibility == PARTIAL_VISIBILITY:
      pieces_to_return = [piece.to_dict() for piece in self.pieces if piece.country == country or not isinstance(piece, (Spy, Satelite))]
    else:
      pieces_to_return = []
    return {
      'coordinate': self.coordinates_dict,
      'money': self.money if visibility >= PARTIAL_VISIBILITY else None,
      'country': self.country.name if self.country else None,
      'pieces': pieces_to_return
    }

class BasePiece(object):
  def __init__(self, game, tile, country, max_speed, piece_type):
    self.game = game
    self._id = game.get_new_id()
    self._tile = tile
    self._country = country
    self.max_speed = max_speed
    self.piece_type = piece_type
    self.dict = {'id': self.id, 'type': self.piece_type, 'country': self.country.name}
    game.pieces[self._id] = self
    tile.pieces.add(self)
    country.pieces.add(self)

  @property
  def id(self):
    return self._id

  @property
  def tile(self):
    return self._tile

  @tile.setter
  def tile(self, value):
    if distance(self._tile, value) > self.max_speed:
      raise ValueError('Cannot move piece to requested tile')
    self._tile.pieces.remove(self)
    self._tile = value
    value.pieces.add(self)

  @property
  def country(self):
    return self._country

  @country.setter
  def country(self, value):
    self._country.pieces.remove(self)
    self._country = value
    self._country.pieces.add(self)
    self.dict['country'] = value.name

  def turn_done(self):
    """Method for deriving classes to override if cleanup is needed when a turn is done."""
    pass

  def can_defend(self, tile):
    """Returns True iff this piece can defend the given tile."""
    return False

  def kill(self):
    del self.game.pieces[self._id]
    self.tile.pieces.remove(self)
    self.country.pieces.remove(self)

  def should_die_in_battle(self, role, tile, participants):
    """Returns True iff this piece should die in the given battle.

    The battle is performed on the given tile, and the direct enemies are given
    in the participants list, that contains tuples of a piece and its role. The
    role of the current piece is passed as role.
    """
    raise NotImplementedError()

  def should_conquer(self, role, participants):
    """Returns True iff this piece should conquer the tile in the given battle."""
    return False

  def to_dict(self):
    """Returns a JSON-like dictionary representing this piece."""
    return self.dict

  def additional_load_from_dict(self, piece_dict):
    """Method for deriving class to override if it could load additional state from the piece dict."""
    pass

class FlyingPiece(BasePiece):
  def __init__(self, max_time_in_air, *args, **kwargs):
    super(FlyingPiece, self).__init__(*args, **kwargs)
    self.in_air = self.dict['inAir'] = False
    self.time_in_air = -1
    self.max_time_in_air = max_time_in_air
    self.theoretical_max_speed = self.max_speed
    self.max_speed = 0

  def take_off(self):
    self.in_air = self.dict['inAir'] = True
    self.time_in_air = self.dict['timeInAir'] = max(0, self.time_in_air)
    self.max_speed = self.theoretical_max_speed

  def land(self):
    if not self.in_air:
      return
    if self.tile.country is not None and self.country != self.tile.country:
      self.country = self.tile.country
    self.in_air = self.dict['inAir'] = False
    self.time_in_air = -1
    del self.dict['timeInAir']
    self.max_speed = 0

  def turn_done(self):
    if self.in_air:
      self.time_in_air += 1
      self.dict['timeInAir'] += 1
      if self.time_in_air > self.max_time_in_air:
        self.land()

  def additional_load_from_dict(self, piece_dict):
    super(FlyingPiece, self).additional_load_from_dict(piece_dict)
    self.in_air = self.dict['inAir'] = piece_dict['inAir']
    if 'timeInAir' in piece_dict:
      self.time_in_air = self.dict['timeInAir'] = piece_dict['timeInAir']
    else:
      self.time_in_air = -1
      if 'timeInAir' in self.dict:
        del self.dict['timeInAir']

class Tank(BasePiece):
  PRICE = TANK_PRICE

  def __init__(self, *args, **kwargs):
    super(Tank, self).__init__(max_speed=TANK_SPEED, piece_type='tank', *args, **kwargs)
    self.is_attacking = False

  def attack(self):
    assert(not self.is_attacking), 'Tank cannot attack twice in a turn'
    self.game.battles_in_queue[self.tile].append(self)
    self.is_attacking = True

  def turn_done(self):
    self.is_attacking = False

  def can_defend(self, tile):
    return tile == self.tile and not self.is_attacking

  def should_die_in_battle(self, role, tile, participants):
    assert(role != PASSIVE_ROLE), 'A tank cannot be passive!'
    for participant, other_role in participants:
      if participant is self:
        continue
      if isinstance(participant, (Tank, Airplane, Helicopter, Artillery)) and other_role == ATTACKER_ROLE:
        return True
      if isinstance(participant, Antitank):
        return True
      if role == ATTACKER_ROLE:
        if isinstance(participant, Tank):
          return True
        if isinstance(participant, Artillery) and other_role == DEFENDER_ROLE:
          return True
    return False

  def should_conquer(self, role, participants):
    return role == ATTACKER_ROLE and len(participants) == 1

class Airplane(FlyingPiece):
  PRICE = AIRPLANE_PRICE

  def __init__(self, *args, **kwargs):
    super(Airplane, self).__init__(AIRPLANE_MAX_TIME_IN_AIR, max_speed=AIRPLANE_SPEED, piece_type='airplane', *args, **kwargs)
    self.is_attacking = False

  def attack(self):
    assert(not self.is_attacking), 'Airplane cannot attack twice in a turn'
    assert(self.in_air), 'Airplane must not be on ground while attacking'
    self.is_attacking = True
    self.game.battles_in_queue[self.tile].append(self)

  def turn_done(self):
    super(Airplane, self).turn_done()
    self.is_attacking = False

  def should_die_in_battle(self, role, tile, participants):
    assert(role != DEFENDER_ROLE), 'An airplane cannot be a defender!'
    if role == ATTACKER_ROLE:
      assert(self.in_air), 'An airplane cannot attack on land!'
    for participant, other_role in participants:
      if participant is self:
        continue
      if isinstance(participant, IronDome) and other_role == DEFENDER_ROLE and self.in_air:
        return True
      if isinstance(participant, (Airplane, Helicopter, Artillery)) and other_role == ATTACKER_ROLE:
        return True
      if role == PASSIVE_ROLE and isinstance(participant, Tank) and other_role == ATTACKER_ROLE and not self.in_air:
          return True
      if role == ATTACKER_ROLE and other_role != PASSIVE_ROLE and isinstance(participant, Artillery):
          return True
    return False

class Artillery(BasePiece):
  PRICE = ARTILLERY_PRICE

  def __init__(self, *args, **kwargs):
    super(Artillery, self).__init__(max_speed=ARTILLERY_SPEED, piece_type='artillery', *args, **kwargs)
    self.is_attacking = False

  def attack(self, destination):
    assert(not self.is_attacking), 'Artillery cannot attack twice in a turn'
    if distance(self.tile, destination) > ARTILLERY_ATTACK_RANGE:
      raise ValueError('Artillery cannot get that far')
    self.game.battles_in_queue[self.game.tiles[destination.x][destination.y]].append(self)
    self.is_attacking = True

  def turn_done(self):
    self.is_attacking = False

  def can_defend(self, tile):
    return distance(tile, self.tile) <= ARTILLERY_DEFEND_RANGE and self.tile != tile and not self.is_attacking

  def should_die_in_battle(self, role, tile, participants):
    if tile != self.tile:
      assert(role != PASSIVE_ROLE), 'Artillery cannot be passive outsite its own tile!'
    for participant, other_role in participants:
      if participant is self:
        continue
      if role == PASSIVE_ROLE and other_role == ATTACKER_ROLE and isinstance(participant, (Tank, Airplane, Artillery)):
        return True
      if other_role == ATTACKER_ROLE and isinstance(participant, Helicopter):
        return True
    return False

class Helicopter(FlyingPiece):
  PRICE = HELICOPTER_PRICE

  def __init__(self, *args, **kwargs):
    super(Helicopter, self).__init__(HELICOPTER_MAX_TIME_IN_AIR, max_speed=HELICOPTER_SPEED, piece_type='helicopter', *args, **kwargs)
    self.is_attacking = False

  def attack(self, destination):
    assert(not self.is_attacking), 'Helicopter cannot attack twice in a turn'
    assert(self.in_air), 'Helicopter must not be on ground while attacking'
    if distance(self.tile, destination) > HELICOPTER_ATTACK_RANGE:
      raise ValueError('Helicopter cannot attack that far')
    self.game.battles_in_queue[self.tile].append(self)
    self.is_attacking = True

  def turn_done(self):
    super(Helicopter, self).turn_done()
    self.is_attacking = False

  def should_die_in_battle(self, role, tile, participants):
    assert(role != DEFENDER_ROLE), 'A helicopter cannot be a defender!'
    if role == ATTACKER_ROLE:
      assert(self.in_air), 'A helicopter cannot attack on land!'
    for participant, other_role in participants:
      if participant is self:
        continue
      if isinstance(participant, IronDome) and other_role == DEFENDER_ROLE and self.in_air:
        return True
      if isinstance(participant, (Airplane, Helicopter)) and other_role == ATTACKER_ROLE:
        return True
      if role == PASSIVE_ROLE and isinstance(participant, Tank) and other_role == ATTACKER_ROLE and not self.in_air:
        return True
      if self.in_air and other_role == DEFENDER_ROLE and isinstance(participant, IronDome):
        return True
      if role == PASSIVE_ROLE and other_role == ATTACKER_ROLE and isinstance(participant, Artillery):
        return True
    return False

class Antitank(BasePiece):
  PRICE = ANTITANK_PRICE

  def __init__(self, *args, **kwargs):
    super(Antitank, self).__init__(max_speed=ANTITANK_SPEED, piece_type='antitank', *args, **kwargs)

  def can_defend(self, tile):
    return tile == self.tile

  def should_die_in_battle(self, role, tile, participants):
    assert(role == DEFENDER_ROLE), 'An antitank must be a defender!'
    for participant, other_role in participants:
      if other_role == ATTACKER_ROLE and isinstance(participant, (Airplane, Helicopter)):
        return True
    return False

class IronDome(BasePiece):
  PRICE = IRONDOME_PRICE

  def __init__(self, *args, **kwargs):
    super(IronDome, self).__init__(max_speed=IRONDOME_SPEED, piece_type='irondome', *args, **kwargs)
    self.is_defending = self.dict['isDefending'] = False

  def turn_on(self):
    self.is_defending = self.dict['isDefending'] = True
    self.max_speed = 0

  def turn_off(self):
    self.is_defending = self.dict['isDefending'] = False
    self.max_speed = IRONDOME_SPEED

  def can_defend(self, tile):
    return self.is_defending and distance(tile, self.tile) <= IRONDOME_DEFEND_RANGE

  def should_die_in_battle(self, role, tile, participants):
    assert(role != ATTACKER_ROLE), 'Iron dome cannot attack!'
    if role == PASSIVE_ROLE:
      assert(tile == self.tile), 'Iron dome cannot be passive in other tiles!'
    for participant, other_role in participants:
      if role == DEFENDER_ROLE:
        if other_role == ATTACKER_ROLE and isinstance(participant, Tank) and participant.tile == self.tile:
          return True
        continue
      # role == PASSIVE_ROLE
      if other_role == ATTACKER_ROLE and isinstance(participant, (Tank, Airplane, Helicopter, Artillery)):
        return True
    return False

  def additional_load_from_dict(self, piece_dict):
    super(IronDome, self).additional_load_from_dict(piece_dict)
    self.is_defending = self.dict['isDefending'] = piece_dict['isDefending']

class Bunker(BasePiece):
  PRICE = BUNKER_PRICE

  def __init__(self, *args, **kwargs):
    super(Bunker, self).__init__(max_speed=0, piece_type='bunker', *args, **kwargs)
    self.hits = 0

  def turn_done(self):
    self.hits = 0

  def can_defend(self, tile):
    return self.tile == tile

  def should_die_in_battle(self, role, tile, participants):
    assert(role == DEFENDER_ROLE), 'A bunker must be a defender!'
    for participant, other_role in participants:
      if other_role == ATTACKER_ROLE and isinstance(participant, (Tank, Airplane, Helicopter, Artillery)):
        self.hits += 1
    return self.hits > BUNKER_DEFEND_MULTIPLIER

class Spy(BasePiece):
  PRICE = SPY_PRICE

  def __init__(self, *args, **kwargs):
    super(Spy, self).__init__(max_speed=SPY_SPEED, piece_type='spy', *args, **kwargs)

class Tower(BasePiece):
  PRICE = TOWER_PRICE

  def __init__(self, *args, **kwargs):
    super(Tower, self).__init__(max_speed=0, piece_type='tower', *args, **kwargs)

class Satelite(BasePiece):
  PRICE = SATELITE_PRICE

  def __init__(self, *args, **kwargs):
    super(Satelite, self).__init__(max_speed=SATELITE_SPEED, piece_type='satelite', *args, **kwargs)

class Builder(BasePiece):
  PRICE = BUILDER_PRICE

  def __init__(self, *args, **kwargs):
    super(Builder, self).__init__(max_speed=BUILDER_SPEED, piece_type='builder', *args, **kwargs)
    self.dict['money'] = 0

  @property
  def money(self):
    return self.dict['money']

  @money.setter
  def money(self, value):
    self.dict['money'] = value

  def collect_money(self, amount):
    if amount < 0:
      raise ValueError('Cannot collect a negative amount of money')
    if amount > BUILDER_MAX_COLLECTION_IN_TURN:
      raise ValueError('Cannot collect more than {} money'.format(BUILDER_MAX_COLLECTION_IN_TURN))
    assert(self.tile.country == self.country), 'Builder can collect money only from its own country'
    if self.tile.money < amount:
      raise ValueError('Not enough money on tile')
    if self.money + amount > BUILDER_MAX_MONEY:
      raise ValueError('Builder cannot have more than {} money'.format(BUILDER_MAX_MONEY))
    self.money += amount
    self.tile.money -= amount

  def throw_money(self, amount):
    if amount < 0:
      raise ValueError('Cannot throw a negative amount of money')
    if self.money < amount:
      raise ValueError('Not enough money to throw')
    self.money -= amount
    self.tile.money += amount

  def build(self, piece_type):
    piece_class = TYPE_TO_CLASS.get(piece_type)
    if piece_class is None:
      raise ValueError('Unknown piece type %s to build' % piece_type)
    if self.money < piece_class.PRICE:
      raise ValueError('Not enough money to build')
    self.money -= piece_class.PRICE
    return piece_class(game=self.game, tile=self.tile, country=self.country)

  def additional_load_from_dict(self, piece_dict):
    super(Builder, self).additional_load_from_dict(piece_dict)
    self.dict['money'] = piece_dict['money']

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

def piece_from_dict(game, tile, country, piece_dict):
  piece_class = TYPE_TO_CLASS.get(piece_dict['type'])
  result = piece_class(game=game, tile=tile, country=country)
  result.additional_load_from_dict(piece_dict)
  return result

def game_from_dict(game_dict):
  game = Game(game_dict['width'], game_dict['height'])
  game.countries = {Country(game, country_name) for country_name in game_dict['countries']}
  country_by_name = {country.name: country for country in game.countries}
  for tile_row, dicts_tile_row in zip(game.tiles, game_dict['tiles']):
    for tile, tile_dict in zip(tile_row, dicts_tile_row):
      tile.money = tile_dict['money']
      tile.country = country_by_name[tile_dict['country']] if tile_dict['country'] is not None else None
      for piece_dict in tile_dict['pieces']:
        piece_from_dict(game, tile, country_by_name[piece_dict['country']], piece_dict)
  return game

