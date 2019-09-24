import unittest

from common_types import Coordinates
import commands
import constants
import engine

class TestPiece(engine.BasePiece):
  MAX_SPEED = 2
  PIECE_TYPE = 'test'

  def __init__(self, game, tile, country):
    super(TestPiece, self).__init__(game, tile, country, TestPiece.MAX_SPEED, TestPiece.PIECE_TYPE)

class TestFlyingPiece(engine.FlyingPiece):
  MAX_SPEED = 2
  PIECE_TYPE = 'test'
  MAX_TIME_IN_AIR = 10

  def __init__(self, game, tile, country):
    super(TestFlyingPiece, self).__init__(
      TestFlyingPiece.MAX_TIME_IN_AIR,
      game,
      tile,
      country,
      TestFlyingPiece.MAX_SPEED,
      TestFlyingPiece.PIECE_TYPE)

class TestGameGeneral(unittest.TestCase):
  def setUp(self):
    self.game = engine.Game(10, 10)

  def set_up_for_battle(self):
    self.country1 = self.game.add_country('country 1')
    self.country2 = self.game.add_country('country 2')
    self.tile = self.game.tiles[2][4]
    self.other_tile = self.game.tiles[3][4]

  def test_constructor(self):
    self.assertEqual(self.game.width, 10)
    self.assertEqual(self.game.height, 10)
    self.assertEqual(len(self.game.tiles), 10)
    for x, tile_row in enumerate(self.game.tiles):
      self.assertEqual(len(tile_row), 10)
      for y, tile in enumerate(tile_row):
        self.assertEqual(tile.game, self.game)
        self.assertEqual(tile.coordinates, Coordinates(x, y))
        self.assertEqual(tile.country, None)
        self.assertEqual(tile.pieces, set())
    self.assertEqual(self.game.countries, set())
    self.assertEqual(self.game.pieces, {})
    self.assertEqual(self.game.turns, 0)

  def test_country(self):
    self.assertEqual(self.game.get_country('Israel'), None)
    country = self.game.add_country('Israel')
    self.assertEqual(country.game, self.game)
    self.assertEqual(country.name, 'Israel')
    self.assertEqual(country.tiles, set())
    self.assertEqual(country.pieces, set())
    self.assertEqual(self.game.countries, {country})
    self.assertEqual(self.game.get_country('Israel'), country)
    self.assertEqual(self.game.get_country('Iran'), None)

  def test_assign_tile_to_country(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][2]
    tile.country = country
    self.assertIn(tile, country.tiles)
    self.assertIs(tile.country, country)

  def test_tile_distance(self):
    self.assertEqual(engine.distance(self.game.tiles[1][1], self.game.tiles[2][2]), 2)
    self.assertEqual(engine.distance(self.game.tiles[2][4], self.game.tiles[3][4]), 1)
    self.assertEqual(engine.distance(self.game.tiles[2][4], self.game.tiles[2][5]), 1)

  def test_tile_neighbors(self):
    tile = self.game.tiles[2][4]
    neighbors = set(tile.neighbors())
    expected_neighbors = {
      self.game.tiles[1][4],
      self.game.tiles[2][3],
      self.game.tiles[2][4],
      self.game.tiles[2][5],
      self.game.tiles[3][4],
    }
    self.assertEqual(neighbors, expected_neighbors)

  def test_tile_neighbors_edge_x_min(self):
    tile = self.game.tiles[0][4]
    neighbors = set(tile.neighbors())
    expected_neighbors = {
      self.game.tiles[0][3],
      self.game.tiles[0][4],
      self.game.tiles[0][5],
      self.game.tiles[1][4],
    }
    self.assertEqual(neighbors, expected_neighbors)

  def test_tile_neighbors_edge_x_max(self):
    tile = self.game.tiles[9][4]
    neighbors = set(tile.neighbors())
    expected_neighbors = {
      self.game.tiles[8][4],
      self.game.tiles[9][3],
      self.game.tiles[9][4],
      self.game.tiles[9][5],
    }
    self.assertEqual(neighbors, expected_neighbors)

  def test_tile_neighbors_edge_y_min(self):
    tile = self.game.tiles[2][0]
    neighbors = set(tile.neighbors())
    expected_neighbors = {
      self.game.tiles[1][0],
      self.game.tiles[2][0],
      self.game.tiles[2][1],
      self.game.tiles[3][0],
    }
    self.assertEqual(neighbors, expected_neighbors)

  def test_tile_neighbors_edge_y_max(self):
    tile = self.game.tiles[2][9]
    neighbors = set(tile.neighbors())
    expected_neighbors = {
      self.game.tiles[1][9],
      self.game.tiles[2][8],
      self.game.tiles[2][9],
      self.game.tiles[3][9],
    }
    self.assertEqual(neighbors, expected_neighbors)

  def test_tile_neighbors_with_distance(self):
    tile = self.game.tiles[2][4]
    neighbors = set(tile.neighbors(3))
    expected_neighbors = {
      self.game.tiles[0][3],
      self.game.tiles[0][4],
      self.game.tiles[0][5],
      self.game.tiles[1][2],
      self.game.tiles[1][3],
      self.game.tiles[1][4],
      self.game.tiles[1][5],
      self.game.tiles[1][6],
      self.game.tiles[2][1],
      self.game.tiles[2][2],
      self.game.tiles[2][3],
      self.game.tiles[2][4],
      self.game.tiles[2][5],
      self.game.tiles[2][6],
      self.game.tiles[2][7],
      self.game.tiles[3][2],
      self.game.tiles[3][3],
      self.game.tiles[3][4],
      self.game.tiles[3][5],
      self.game.tiles[3][6],
      self.game.tiles[4][3],
      self.game.tiles[4][4],
      self.game.tiles[4][5],
      self.game.tiles[5][4],
    }
    self.assertEqual(neighbors, expected_neighbors)

  def test_tile_to_dict_empty_tile(self):
    tile = self.game.tiles[2][4]
    expected_dict = {
      'coordinate': {'x': 2, 'y': 4},
      'money': 0,
      'country': None,
      'pieces': [],
    }
    self.assertEqual(tile.to_dict(), expected_dict)

  def test_tile_to_dict_with_country(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tile.country = country
    expected_dict = {
      'coordinate': {'x': 2, 'y': 4},
      'money': 0,
      'country': 'Israel',
      'pieces': [],
    }
    self.assertEqual(tile.to_dict(), expected_dict)

  def test_tile_to_dict_with_money(self):
    tile = self.game.tiles[2][4]
    tile.money = 500
    expected_dict = {
      'coordinate': {'x': 2, 'y': 4},
      'money': 500,
      'country': None,
      'pieces': [],
    }
    self.assertEqual(tile.to_dict(), expected_dict)

  def test_tile_to_dict_with_piece(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestPiece(self.game, tile, country)
    expected_dict = {
      'coordinate': {'x': 2, 'y': 4},
      'money': 0,
      'country': None,
      'pieces': [piece.to_dict()],
    }
    self.assertEqual(tile.to_dict(), expected_dict)

  def test_base_piece_basic_containments(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestPiece(self.game, tile, country)
    self.assertIn(piece, country.pieces)
    self.assertIn(piece, tile.pieces)
    self.assertIn(piece.id, self.game.pieces)
    self.assertIs(piece, self.game.pieces[piece.id])

  def test_base_piece_move(self):
    country = self.game.add_country('Israel')
    old_tile = self.game.tiles[2][4]
    new_tile = self.game.tiles[2][3]
    piece = TestPiece(self.game, old_tile, country)
    piece.tile = new_tile
    self.assertIn(piece, new_tile.pieces)
    self.assertNotIn(piece, old_tile.pieces)

  def test_base_piece_move_too_far(self):
    country = self.game.add_country('Israel')
    old_tile = self.game.tiles[2][4]
    new_tile = self.game.tiles[2][0]
    piece = TestPiece(self.game, old_tile, country)
    with self.assertRaises(ValueError):
      piece.tile = new_tile

  def test_base_piece_change_country(self):
    old_country = self.game.add_country('country 1')
    new_country = self.game.add_country('country 2')
    tile = self.game.tiles[2][4]
    piece = TestPiece(self.game, tile, old_country)
    piece.country = new_country
    self.assertIn(piece, new_country.pieces)
    self.assertNotIn(piece, old_country.pieces)

  def test_base_piece_kill(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestPiece(self.game, tile, country)
    piece.kill()
    self.assertNotIn(piece.id, self.game.pieces)
    self.assertNotIn(piece, tile.pieces)
    self.assertNotIn(piece, country.pieces)

  def test_base_piece_to_dict(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestPiece(self.game, tile, country)
    expected_dict = {
      'id': piece.id,
      'type': TestPiece.PIECE_TYPE,
      'country': 'Israel',
    }
    self.assertEqual(piece.to_dict(), expected_dict)

  def test_flying_piece_on_ground_initially(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    self.assertFalse(piece.in_air)

  def test_flying_piece_take_off(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    piece.take_off()
    self.assertTrue(piece.in_air)
    self.assertEqual(piece.time_in_air, 0)

  def test_flying_piece_time_in_air_updates_when_turn_is_done(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    piece.take_off()
    piece.turn_done()
    self.assertTrue(piece.in_air)
    self.assertEqual(piece.time_in_air, 1)

  def test_flying_piece_take_off_already_flying(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    piece.take_off()
    piece.turn_done()
    piece.take_off()
    self.assertTrue(piece.in_air)
    self.assertEqual(piece.time_in_air, 1)

  def test_flying_piece_land_already_on_ground(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    piece.land()
    self.assertFalse(piece.in_air)

  def test_flying_piece_land_on_tile_without_country(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    piece.take_off()
    piece.turn_done()
    piece.land()
    self.assertFalse(piece.in_air)
    self.assertIs(piece.country, country)
    self.assertIn(piece, country.pieces)

  def test_flying_piece_land_on_tile_of_same_country(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tile.country = country
    piece = TestFlyingPiece(self.game, tile, country)
    piece.take_off()
    piece.turn_done()
    piece.land()
    self.assertFalse(piece.in_air)
    self.assertIs(piece.country, country)
    self.assertIn(piece, country.pieces)

  def test_flying_piece_land_on_enemy_country(self):
    country1 = self.game.add_country('Country 1')
    country2 = self.game.add_country('Country 2')
    tile1 = self.game.tiles[2][4]
    tile1.country = country1
    tile2 = self.game.tiles[3][4]
    tile2.country = country2
    piece = TestFlyingPiece(self.game, tile1, country1)
    piece.take_off()
    piece.turn_done()
    piece.tile = tile2
    piece.turn_done()
    self.assertIs(piece.country, country1)
    self.assertIn(piece, country1.pieces)
    piece.land()
    piece.turn_done()
    self.assertIs(piece.country, country2)
    self.assertNotIn(piece, country1.pieces)
    self.assertIn(piece, country2.pieces)

  def test_flying_piece_too_many_time_in_air(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    piece.take_off()
    for i in range(TestFlyingPiece.MAX_TIME_IN_AIR + 1):
      self.assertTrue(piece.in_air)
      self.assertEqual(piece.time_in_air, i)
      piece.turn_done()
    self.assertFalse(piece.in_air)

  def test_flying_piece_can_move_in_air(self):
    country = self.game.add_country('Israel')
    old_tile = self.game.tiles[2][4]
    new_tile = self.game.tiles[3][3]
    piece = TestFlyingPiece(self.game, old_tile, country)
    piece.take_off()
    piece.tile = new_tile
    self.assertIs(piece.tile, new_tile)
    self.assertIn(piece, new_tile.pieces)
    self.assertNotIn(piece, old_tile.pieces)

  def test_flying_piece_cannot_move_while_landed(self):
    country = self.game.add_country('Israel')
    old_tile = self.game.tiles[2][4]
    new_tile = self.game.tiles[3][3]
    piece = TestFlyingPiece(self.game, old_tile, country)
    with self.assertRaises(ValueError):
      piece.tile = new_tile
    self.assertIs(piece.tile, old_tile)
    self.assertIn(piece, old_tile.pieces)
    self.assertNotIn(piece, new_tile.pieces)

  def test_flying_piece_to_dict_on_ground(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    expected_dict = {
      'id': piece.id,
      'type': TestFlyingPiece.PIECE_TYPE,
      'country': 'Israel',
      'inAir': False
    }
    self.assertEqual(piece.to_dict(), expected_dict)

  def test_flying_piece_to_dict_in_air(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    piece = TestFlyingPiece(self.game, tile, country)
    piece.take_off()
    piece.turn_done()
    expected_dict = {
      'id': piece.id,
      'type': TestFlyingPiece.PIECE_TYPE,
      'country': 'Israel',
      'inAir': True,
      'timeInAir': 1
    }
    self.assertEqual(piece.to_dict(), expected_dict)

  def test_tank_max_speed(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tank = engine.Tank(self.game, tile, country)
    self.assertEqual(tank.max_speed, constants.TANK_SPEED)

  def test_tank_attack(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tank = engine.Tank(self.game, tile, country)
    tank.attack()
    self.assertTrue(tank.is_attacking)
    self.assertIn(tile, self.game.battles_in_queue)
    self.assertIn(tank, self.game.battles_in_queue[tile])

  def test_tank_attack_twice(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tank = engine.Tank(self.game, tile, country)
    tank.attack()
    with self.assertRaises(AssertionError):
      tank.attack()

  def test_tank_can_defend_while_not_attacking(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tank = engine.Tank(self.game, tile, country)
    self.assertTrue(tank.can_defend(tile))

  def test_tank_cannot_defend_while_attacking(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tank = engine.Tank(self.game, tile, country)
    tank.attack()
    self.assertFalse(tank.can_defend(tile))

  def test_tank_cannot_defend_other_tile(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tank = engine.Tank(self.game, tile, country)
    self.assertFalse(tank.can_defend(self.game.tiles[2][3]))

  def test_tank_serialization(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    new_tile = self.game.tiles[4][2]
    tank = engine.Tank(self.game, tile, country)
    tank_dict = tank.to_dict()
    new_tank = engine.piece_from_dict(self.game, new_tile, country, tank_dict)
    self.assertIsInstance(new_tank, engine.Tank)

  def test_airplane_constants(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    airplane = engine.Airplane(self.game, tile, country)
    self.assertEqual(airplane.max_speed, 0)
    airplane.take_off()
    self.assertEqual(airplane.max_speed, constants.AIRPLANE_SPEED)
    self.assertEqual(airplane.max_time_in_air, constants.AIRPLANE_MAX_TIME_IN_AIR)

  def test_airplane_attack_on_ground(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    airplane = engine.Airplane(self.game, tile, country)
    with self.assertRaises(AssertionError):
      airplane.attack()
    self.assertFalse(airplane.is_attacking)
    self.assertNotIn(airplane, self.game.battles_in_queue[tile])

  def test_airplane_attack(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    airplane = engine.Airplane(self.game, tile, country)
    airplane.take_off()
    airplane.turn_done()
    airplane.attack()
    self.assertTrue(airplane.is_attacking)
    self.assertIn(tile, self.game.battles_in_queue)
    self.assertIn(airplane, self.game.battles_in_queue[tile])

  def test_airplane_attack_twice(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    airplane = engine.Airplane(self.game, tile, country)
    airplane.take_off()
    airplane.turn_done()
    airplane.attack()
    with self.assertRaises(AssertionError):
      airplane.attack()

  def test_airplane_cannot_defend_on_ground(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    airplane = engine.Airplane(self.game, tile, country)
    self.assertFalse(airplane.can_defend(tile))
    self.assertFalse(airplane.can_defend(self.game.tiles[3][4]))

  def test_airplane_cannot_defend_in_air(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    airplane = engine.Airplane(self.game, tile, country)
    airplane.take_off()
    self.assertFalse(airplane.can_defend(tile))
    self.assertFalse(airplane.can_defend(self.game.tiles[3][4]))

  def test_airplane_serialization(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    new_tile = self.game.tiles[4][2]
    airplane = engine.Airplane(self.game, tile, country)
    airplane_dict = airplane.to_dict()
    new_airplane = engine.piece_from_dict(self.game, new_tile, country, airplane_dict)
    self.assertIsInstance(new_airplane, engine.Airplane)

  def test_artillery_speed(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    artillery = engine.Artillery(self.game, tile, country)
    self.assertEqual(artillery.max_speed, constants.ARTILLERY_SPEED)

  def test_artillery_attack(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[3][3]
    artillery = engine.Artillery(self.game, tile, country)
    artillery.attack(destination.coordinates)
    self.assertTrue(artillery.is_attacking)
    self.assertIn(destination, self.game.battles_in_queue)
    self.assertIn(artillery, self.game.battles_in_queue[destination])

  def test_artillery_attack_distant_tile(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[0][0]
    artillery = engine.Artillery(self.game, tile, country)
    with self.assertRaises(ValueError):
      artillery.attack(destination)

  def test_artillery_attack_twice(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[3][3]
    artillery = engine.Artillery(self.game, tile, country)
    artillery.attack(destination.coordinates)
    with self.assertRaises(AssertionError):
      artillery.attack(destination)

  def test_artillery_can_defend_while_not_attacking(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    artillery = engine.Artillery(self.game, tile, country)
    self.assertTrue(artillery.can_defend(self.game.tiles[2][5]))

  def test_artillery_cannot_defend_while_attacking(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[3][3]
    artillery = engine.Artillery(self.game, tile, country)
    artillery.attack(destination.coordinates)
    self.assertFalse(artillery.can_defend(self.game.tiles[2][5]))

  def test_artillery_cannot_defend_its_tile(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    artillery = engine.Artillery(self.game, tile, country)
    self.assertFalse(artillery.can_defend(tile))

  def test_artillery_cannot_defend_distant_tile(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    artillery = engine.Artillery(self.game, tile, country)
    self.assertFalse(artillery.can_defend(self.game.tiles[0][0]))

  def test_helicopter_constants(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    helicopter = engine.Helicopter(self.game, tile, country)
    self.assertEqual(helicopter.max_speed, 0)
    helicopter.take_off()
    self.assertEqual(helicopter.max_speed, constants.HELICOPTER_SPEED)
    self.assertEqual(helicopter.max_time_in_air, constants.HELICOPTER_MAX_TIME_IN_AIR)

  def test_helicopter_attack_on_ground(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[3][4]
    helicopter = engine.Helicopter(self.game, tile, country)
    with self.assertRaises(AssertionError):
      helicopter.attack(destination)
    self.assertFalse(helicopter.is_attacking)
    self.assertNotIn(helicopter, self.game.battles_in_queue[tile])

  def test_helicopter_attack(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[3][4]
    helicopter = engine.Helicopter(self.game, tile, country)
    helicopter.take_off()
    helicopter.turn_done()
    helicopter.attack(destination)
    self.assertTrue(helicopter.is_attacking)
    self.assertIn(tile, self.game.battles_in_queue)
    self.assertIn(helicopter, self.game.battles_in_queue[tile])

  def test_helicopter_attack_distant_tile(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[0][0]
    helicopter = engine.Helicopter(self.game, tile, country)
    helicopter.take_off()
    helicopter.turn_done()
    with self.assertRaises(ValueError):
      helicopter.attack(destination)

  def test_helicopter_attack_twice(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[3][4]
    helicopter = engine.Helicopter(self.game, tile, country)
    helicopter.take_off()
    helicopter.turn_done()
    helicopter.attack(destination)
    with self.assertRaises(AssertionError):
      helicopter.attack(destination)

  def test_helicopter_cannot_defend_on_ground(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    helicopter = engine.Helicopter(self.game, tile, country)
    self.assertFalse(helicopter.can_defend(tile))
    self.assertFalse(helicopter.can_defend(self.game.tiles[3][4]))

  def test_helicopter_cannot_defend_in_air(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    helicopter = engine.Helicopter(self.game, tile, country)
    helicopter.take_off()
    self.assertFalse(helicopter.can_defend(tile))
    self.assertFalse(helicopter.can_defend(self.game.tiles[3][4]))

  def test_antitank_speed(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    antitank = engine.Antitank(self.game, tile, country)
    self.assertEqual(antitank.max_speed, constants.ANTITANK_SPEED)

  def test_antitank_defends_its_tile(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    antitank = engine.Antitank(self.game, tile, country)
    self.assertTrue(antitank.can_defend(tile))

  def test_antitank_cannot_defend_other_tiles(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    antitank = engine.Antitank(self.game, tile, country)
    self.assertFalse(antitank.can_defend(self.game.tiles[3][4]))

  def test_iron_dome_speed(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    iron_dome = engine.IronDome(self.game, tile, country)
    self.assertEqual(iron_dome.max_speed, constants.IRONDOME_SPEED)

  def test_iron_dome_can_move_before_activated(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[2][3]
    iron_dome = engine.IronDome(self.game, tile, country)
    iron_dome.tile = destination
    self.assertIs(iron_dome.tile, destination)

  def test_iron_dome_cannot_move_when_activates(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[2][3]
    iron_dome = engine.IronDome(self.game, tile, country)
    iron_dome.turn_on()
    with self.assertRaises(ValueError):
      iron_dome.tile = destination

  def test_iron_dome_can_move_after_activated(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    destination = self.game.tiles[2][3]
    iron_dome = engine.IronDome(self.game, tile, country)
    iron_dome.turn_on()
    iron_dome.turn_off()
    iron_dome.tile = destination
    self.assertIs(iron_dome.tile, destination)

  def test_iron_dome_cannot_defend_when_turned_off(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    iron_dome = engine.IronDome(self.game, tile, country)
    self.assertFalse(iron_dome.is_defending)
    self.assertFalse(iron_dome.can_defend(tile))
    self.assertFalse(iron_dome.can_defend(self.game.tiles[3][3]))
    iron_dome.turn_on()
    iron_dome.turn_off()
    self.assertFalse(iron_dome.is_defending)
    self.assertFalse(iron_dome.can_defend(tile))
    self.assertFalse(iron_dome.can_defend(self.game.tiles[3][3]))

  def test_iron_dome_defends_when_turned_on(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    iron_dome = engine.IronDome(self.game, tile, country)
    iron_dome.turn_on()
    self.assertTrue(iron_dome.is_defending)
    self.assertTrue(iron_dome.can_defend(tile))
    self.assertTrue(iron_dome.can_defend(self.game.tiles[3][3]))

  def test_iron_dome_cannot_defend_distant_tile_when_turned_on(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    iron_dome = engine.IronDome(self.game, tile, country)
    iron_dome.turn_on()
    self.assertTrue(iron_dome.is_defending)
    self.assertFalse(iron_dome.can_defend(self.game.tiles[9][9]))

  def test_iron_dome_dict_turned_off(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    iron_dome = engine.IronDome(self.game, tile, country)
    expected_dict = {
      'id': iron_dome.id,
      'type': 'irondome',
      'country': 'Israel',
      'isDefending': False
    }
    self.assertEqual(iron_dome.to_dict(), expected_dict)
    
    iron_dome.turn_on()
    iron_dome.turn_off()
    self.assertEqual(iron_dome.to_dict(), expected_dict)

  def test_iron_dome_dict_turned_on(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    iron_dome = engine.IronDome(self.game, tile, country)
    iron_dome.turn_on()
    expected_dict = {
      'id': iron_dome.id,
      'type': 'irondome',
      'country': 'Israel',
      'isDefending': True
    }
    self.assertEqual(iron_dome.to_dict(), expected_dict)

  def test_bunker_cannot_move(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    bunker = engine.Bunker(self.game, tile, country)
    self.assertEqual(bunker.max_speed, 0)
    with self.assertRaises(ValueError):
      bunker.tile = self.game.tiles[2][5]

  def test_bunker_can_defend_its_tile(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    bunker = engine.Bunker(self.game, tile, country)
    self.assertTrue(bunker.can_defend(tile))

  def test_bunker_cannot_defend_other_tiles(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    bunker = engine.Bunker(self.game, tile, country)
    self.assertFalse(bunker.can_defend(self.game.tiles[2][5]))

  def test_spy_speed(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    spy = engine.Spy(self.game, tile, country)
    self.assertEqual(spy.max_speed, constants.SPY_SPEED)

  def test_spy_cannot_defend(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    spy = engine.Spy(self.game, tile, country)
    self.assertFalse(spy.can_defend(tile))
    self.assertFalse(spy.can_defend(self.game.tiles[0][0]))

  def test_tower_speed(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tower = engine.Tower(self.game, tile, country)
    self.assertEqual(tower.max_speed, 0)

  def test_tower_cannot_defend(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tower = engine.Tower(self.game, tile, country)
    self.assertFalse(tower.can_defend(tile))
    self.assertFalse(tower.can_defend(self.game.tiles[0][0]))

  def test_satelite_speed(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    satelite = engine.Satelite(self.game, tile, country)
    self.assertEqual(satelite.max_speed, constants.SATELITE_SPEED)

  def test_satelite_cannot_defend(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    satelite = engine.Satelite(self.game, tile, country)
    self.assertFalse(satelite.can_defend(tile))
    self.assertFalse(satelite.can_defend(self.game.tiles[0][0]))

  def test_builder_constants(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    self.assertEqual(builder.max_speed, constants.BUILDER_SPEED)
    self.assertEqual(builder.money, 0)

  def test_builder_collect_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tile.country = country
    tile.money = 100
    builder = engine.Builder(self.game, tile, country)
    builder.collect_money(5)
    self.assertEqual(builder.money, 5)
    self.assertEqual(tile.money, 95)

  def test_builder_collect_money_tile_country_mismatch(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tile.money = 100
    builder = engine.Builder(self.game, tile, country)
    with self.assertRaises(AssertionError):
      builder.collect_money(5)
    self.assertEqual(builder.money, 0)
    self.assertEqual(tile.money, 100)

  def test_builder_collect_money_negative(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    with self.assertRaises(ValueError):
      builder.collect_money(-1)

  def test_builder_collect_more_money_than_money_in_tile(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tile.country = country
    tile.money = 1
    builder = engine.Builder(self.game, tile, country)
    with self.assertRaises(ValueError):
      builder.collect_money(5)

  def test_builder_collect_more_moeny_than_collection_limit(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tile.country = country
    tile.money = constants.BUILDER_MAX_COLLECTION_IN_TURN + 1
    builder = engine.Builder(self.game, tile, country)
    with self.assertRaises(ValueError):
      builder.collect_money(constants.BUILDER_MAX_COLLECTION_IN_TURN + 1)

  def test_builder_collect_more_than_builder_money_limit(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tile.country = country
    tile.money = 5
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.BUILDER_MAX_MONEY - 2
    with self.assertRaises(ValueError):
      builder.collect_money(3)

  def test_builder_throw_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    tile.money = 100
    builder = engine.Builder(self.game, tile, country)
    builder.money = 50
    builder.throw_money(20)
    self.assertEqual(tile.money, 120)
    self.assertEqual(builder.money, 30)

  def test_builder_throw_money_negative(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = 50
    with self.assertRaises(ValueError):
      builder.throw_money(-350)

  def test_builder_throw_too_much_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = 50
    with self.assertRaises(ValueError):
      builder.throw_money(350)
    tile.money = 100

  def test_builder_to_dict(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = 50
    expected_dict = {
      'id': builder.id,
      'type': 'builder',
      'country': 'Israel',
      'money': 50
    }
    self.assertEqual(builder.to_dict(), expected_dict)

  def test_builder_build_unknown_piece_type(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    with self.assertRaises(ValueError):
      builder.build('invalid type')

  def test_builder_build_tank(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.TANK_PRICE
    tank = builder.build('tank')
    self.assertIsInstance(tank, engine.Tank)
    self.assertIs(self.game.pieces[tank.id], tank)
    self.assertEqual(country.pieces, {builder, tank})
    self.assertEqual(tile.pieces, {builder, tank})
    self.assertIs(tank.tile, tile)
    self.assertIs(tank.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_tank_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.TANK_PRICE - 1
    with self.assertRaises(ValueError):
      tank = builder.build('tank')

  def test_builder_build_airplane(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.AIRPLANE_PRICE
    airplane = builder.build('airplane')
    self.assertIsInstance(airplane, engine.Airplane)
    self.assertIs(self.game.pieces[airplane.id], airplane)
    self.assertEqual(country.pieces, {builder, airplane})
    self.assertEqual(tile.pieces, {builder, airplane})
    self.assertIs(airplane.tile, tile)
    self.assertIs(airplane.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_airplane_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.AIRPLANE_PRICE - 1
    with self.assertRaises(ValueError):
      airplane = builder.build('airplane')

  def test_builder_build_artillery(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.ARTILLERY_PRICE
    artillery = builder.build('artillery')
    self.assertIsInstance(artillery, engine.Artillery)
    self.assertIs(self.game.pieces[artillery.id], artillery)
    self.assertEqual(country.pieces, {builder, artillery})
    self.assertEqual(tile.pieces, {builder, artillery})
    self.assertIs(artillery.tile, tile)
    self.assertIs(artillery.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_artillery_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.ARTILLERY_PRICE - 1
    with self.assertRaises(ValueError):
      artillery = builder.build('artillery')

  def test_builder_build_helicopter(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.HELICOPTER_PRICE
    helicopter = builder.build('helicopter')
    self.assertIsInstance(helicopter, engine.Helicopter)
    self.assertIs(self.game.pieces[helicopter.id], helicopter)
    self.assertEqual(country.pieces, {builder, helicopter})
    self.assertEqual(tile.pieces, {builder, helicopter})
    self.assertIs(helicopter.tile, tile)
    self.assertIs(helicopter.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_helicopter_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.HELICOPTER_PRICE - 1
    with self.assertRaises(ValueError):
      helicopter = builder.build('helicopter')

  def test_builder_build_antitank(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.ANTITANK_PRICE
    antitank = builder.build('antitank')
    self.assertIsInstance(antitank, engine.Antitank)
    self.assertIs(self.game.pieces[antitank.id], antitank)
    self.assertEqual(country.pieces, {builder, antitank})
    self.assertEqual(tile.pieces, {builder, antitank})
    self.assertIs(antitank.tile, tile)
    self.assertIs(antitank.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_antitank_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.ANTITANK_PRICE - 1
    with self.assertRaises(ValueError):
      antitank = builder.build('antitank')

  def test_builder_build_irondome(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.IRONDOME_PRICE
    irondome = builder.build('irondome')
    self.assertIsInstance(irondome, engine.IronDome)
    self.assertIs(self.game.pieces[irondome.id], irondome)
    self.assertEqual(country.pieces, {builder, irondome})
    self.assertEqual(tile.pieces, {builder, irondome})
    self.assertIs(irondome.tile, tile)
    self.assertIs(irondome.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_irondome_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.IRONDOME_PRICE - 1
    with self.assertRaises(ValueError):
      irondome = builder.build('irondome')

  def test_builder_build_bunker(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.BUNKER_PRICE
    bunker = builder.build('bunker')
    self.assertIsInstance(bunker, engine.Bunker)
    self.assertIs(self.game.pieces[bunker.id], bunker)
    self.assertEqual(country.pieces, {builder, bunker})
    self.assertEqual(tile.pieces, {builder, bunker})
    self.assertIs(bunker.tile, tile)
    self.assertIs(bunker.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_bunker_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.BUNKER_PRICE - 1
    with self.assertRaises(ValueError):
      bunker = builder.build('bunker')

  def test_builder_build_spy(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.SPY_PRICE
    spy = builder.build('spy')
    self.assertIsInstance(spy, engine.Spy)
    self.assertIs(self.game.pieces[spy.id], spy)
    self.assertEqual(country.pieces, {builder, spy})
    self.assertEqual(tile.pieces, {builder, spy})
    self.assertIs(spy.tile, tile)
    self.assertIs(spy.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_spy_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.SPY_PRICE - 1
    with self.assertRaises(ValueError):
      spy = builder.build('spy')

  def test_builder_build_tower(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.TOWER_PRICE
    tower = builder.build('tower')
    self.assertIsInstance(tower, engine.Tower)
    self.assertIs(self.game.pieces[tower.id], tower)
    self.assertEqual(country.pieces, {builder, tower})
    self.assertEqual(tile.pieces, {builder, tower})
    self.assertIs(tower.tile, tile)
    self.assertIs(tower.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_tower_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.TOWER_PRICE - 1
    with self.assertRaises(ValueError):
      tower = builder.build('tower')

  def test_builder_build_satelite(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.SATELITE_PRICE
    satelite = builder.build('satelite')
    self.assertIsInstance(satelite, engine.Satelite)
    self.assertIs(self.game.pieces[satelite.id], satelite)
    self.assertEqual(country.pieces, {builder, satelite})
    self.assertEqual(tile.pieces, {builder, satelite})
    self.assertIs(satelite.tile, tile)
    self.assertIs(satelite.country, country)
    self.assertEqual(builder.money, 0)

  def test_builder_build_satelite_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.SATELITE_PRICE - 1
    with self.assertRaises(ValueError):
      satelite = builder.build('satelite')

  def test_builder_build_builder(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.BUILDER_PRICE
    builder2 = builder.build('builder')
    self.assertIsInstance(builder2, engine.Builder)
    self.assertIs(self.game.pieces[builder2.id], builder2)
    self.assertEqual(country.pieces, {builder, builder2})
    self.assertEqual(tile.pieces, {builder, builder2})
    self.assertIs(builder2.tile, tile)
    self.assertIs(builder2.country, country)
    self.assertEqual(builder2.money, 0)
    self.assertEqual(builder.money, 0)

  def test_builder_build_builder_not_enough_money(self):
    country = self.game.add_country('Israel')
    tile = self.game.tiles[2][4]
    builder = engine.Builder(self.game, tile, country)
    builder.money = constants.BUILDER_PRICE - 1
    with self.assertRaises(ValueError):
      builder = builder.build('builder')

  def test_defender_tank_vs_defender_tank(self):
    self.set_up_for_battle()
    tank1 = engine.Tank(self.game, self.tile, self.country1)
    tank2 = engine.Tank(self.game, self.tile, self.country2)
    participants = [(tank1, engine.DEFENDER_ROLE), (tank2, engine.DEFENDER_ROLE)]
    self.assertFalse(tank1.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(tank2.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_tank_vs_attacker_tank(self):
    self.set_up_for_battle()
    tank1 = engine.Tank(self.game, self.tile, self.country1)
    tank2 = engine.Tank(self.game, self.tile, self.country2)
    participants = [(tank1, engine.ATTACKER_ROLE), (tank2, engine.DEFENDER_ROLE)]
    self.assertTrue(tank1.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(tank2.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_tank_vs_passive_airplane_on_ground(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    airplane = engine.Airplane(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (airplane, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_tank_vs_passive_airplane_in_air(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    airplane = engine.Airplane(self.game, self.tile, self.country2)
    airplane.take_off()
    participants = [(tank, engine.DEFENDER_ROLE), (airplane, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_tank_vs_attacker_airplane_in_air(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    airplane = engine.Airplane(self.game, self.tile, self.country2)
    airplane.take_off()
    participants = [(tank, engine.DEFENDER_ROLE), (airplane, engine.ATTACKER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_defender_tank_vs_passive_helicopter_on_ground(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_tank_vs_passive_helicopter_in_air(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(tank, engine.DEFENDER_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_tank_vs_attacker_helicopter_in_air(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(tank, engine.DEFENDER_ROLE), (helicopter, engine.ATTACKER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_defender_tank_vs_attacker_artillery(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (artillery, engine.ATTACKER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_defender_tank_vs_defender_artillery(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (artillery, engine.DEFENDER_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_tank_vs_passive_artillery(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (artillery, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_tank_vs_antitank(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_tank_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_tank_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_tank_vs_bunker(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(tank, engine.DEFENDER_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_attacker_tank_vs_attacker_tank(self):
    self.set_up_for_battle()
    tank1 = engine.Tank(self.game, self.tile, self.country1)
    tank2 = engine.Tank(self.game, self.tile, self.country2)
    participants = [(tank1, engine.ATTACKER_ROLE), (tank2, engine.ATTACKER_ROLE)]
    self.assertTrue(tank1.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(tank2.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_tank_vs_passive_airplane_on_ground(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    airplane = engine.Airplane(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (airplane, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_tank_vs_passive_airplane_in_air(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    airplane = engine.Airplane(self.game, self.tile, self.country2)
    airplane.take_off()
    participants = [(tank, engine.ATTACKER_ROLE), (airplane, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_tank_vs_attacker_airplane_in_air(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    airplane = engine.Airplane(self.game, self.tile, self.country2)
    airplane.take_off()
    participants = [(tank, engine.ATTACKER_ROLE), (airplane, engine.ATTACKER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_tank_vs_passive_helicopter_on_ground(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_tank_vs_passive_helicopter_in_air(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(tank, engine.ATTACKER_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_tank_vs_attacker_helicopter_in_air(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(tank, engine.ATTACKER_ROLE), (helicopter, engine.ATTACKER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_tank_vs_attacker_artillery(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (artillery, engine.ATTACKER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_tank_vs_defender_artillery(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (artillery, engine.DEFENDER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_tank_vs_passive_artillery(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (artillery, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_tank_vs_antitank(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertTrue(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_tank_vs_defender_iron_dome_in_same_tile(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_tank_vs_defender_iron_dome_in_other_tile(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.other_tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_tank_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_tank_vs_bunker(self):
    self.set_up_for_battle()
    tank = engine.Tank(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(tank, engine.ATTACKER_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(tank.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 1)

  def test_passive_airplane_on_ground_vs_passive_airplane_on_ground(self):
    self.set_up_for_battle()
    airplane1 = engine.Airplane(self.game, self.tile, self.country1)
    airplane2 = engine.Airplane(self.game, self.tile, self.country2)
    participants = [(airplane1, engine.PASSIVE_ROLE), (airplane2, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(airplane2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_passive_airplane_in_air(self):
    self.set_up_for_battle()
    airplane1 = engine.Airplane(self.game, self.tile, self.country1)
    airplane2 = engine.Airplane(self.game, self.tile, self.country2)
    airplane2.take_off()
    participants = [(airplane1, engine.PASSIVE_ROLE), (airplane2, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(airplane2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_attacker_airplane_in_air(self):
    self.set_up_for_battle()
    airplane1 = engine.Airplane(self.game, self.tile, self.country1)
    airplane2 = engine.Airplane(self.game, self.tile, self.country2)
    airplane2.take_off()
    participants = [(airplane1, engine.PASSIVE_ROLE), (airplane2, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(airplane2.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_passive_helicopter_on_ground(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_passive_helicopter_in_air(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(airplane, engine.PASSIVE_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_attacker_helicopter_in_air(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(airplane, engine.PASSIVE_ROLE), (helicopter, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_attacker_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (artillery, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_defender_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (artillery, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_passive_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (artillery, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_antitank(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_on_ground_vs_bunker(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_passive_airplane_in_air_vs_passive_airplane_in_air(self):
    self.set_up_for_battle()
    airplane1 = engine.Airplane(self.game, self.tile, self.country1)
    airplane1.take_off()
    airplane2 = engine.Airplane(self.game, self.tile, self.country2)
    airplane2.take_off()
    participants = [(airplane1, engine.PASSIVE_ROLE), (airplane2, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(airplane2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_attacker_airplane_in_air(self):
    self.set_up_for_battle()
    airplane1 = engine.Airplane(self.game, self.tile, self.country1)
    airplane1.take_off()
    airplane2 = engine.Airplane(self.game, self.tile, self.country2)
    airplane2.take_off()
    participants = [(airplane1, engine.PASSIVE_ROLE), (airplane2, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(airplane2.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_passive_helicopter_on_ground(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_passive_helicopter_in_air(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(airplane, engine.PASSIVE_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_attacker_helicopter_in_air(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(airplane, engine.PASSIVE_ROLE), (helicopter, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_attacker_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (artillery, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_defender_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (artillery, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_passive_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (artillery, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_antitank(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_airplane_in_air_vs_bunker(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(airplane, engine.PASSIVE_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_attacker_airplane_in_air_vs_attacker_airplane_in_air(self):
    self.set_up_for_battle()
    airplane1 = engine.Airplane(self.game, self.tile, self.country1)
    airplane1.take_off()
    airplane2 = engine.Airplane(self.game, self.tile, self.country2)
    airplane2.take_off()
    participants = [(airplane1, engine.ATTACKER_ROLE), (airplane2, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertTrue(airplane2.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_passive_helicopter_on_ground(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    participants = [(airplane, engine.ATTACKER_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_passive_helicopter_in_air(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(airplane, engine.ATTACKER_ROLE), (helicopter, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_attacker_helicopter_in_air(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    helicopter = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter.take_off()
    participants = [(airplane, engine.ATTACKER_ROLE), (helicopter, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_attacker_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.ATTACKER_ROLE), (artillery, engine.ATTACKER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_defender_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.ATTACKER_ROLE), (artillery, engine.DEFENDER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_passive_artillery(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(airplane, engine.ATTACKER_ROLE), (artillery, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_antitank(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(airplane, engine.ATTACKER_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(airplane, engine.ATTACKER_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertTrue(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(airplane, engine.ATTACKER_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_airplane_in_air_vs_bunker(self):
    self.set_up_for_battle()
    airplane = engine.Airplane(self.game, self.tile, self.country1)
    airplane.take_off()
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(airplane, engine.ATTACKER_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(airplane.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 1)

  def test_passive_helicopter_on_ground_vs_passive_helicopter_on_ground(self):
    self.set_up_for_battle()
    helicopter1 = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter2 = engine.Helicopter(self.game, self.tile, self.country2)
    participants = [(helicopter1, engine.PASSIVE_ROLE), (helicopter2, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_passive_helicopter_in_air(self):
    self.set_up_for_battle()
    helicopter1 = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter2 = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter2.take_off()
    participants = [(helicopter1, engine.PASSIVE_ROLE), (helicopter2, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_attacker_helicopter_in_air(self):
    self.set_up_for_battle()
    helicopter1 = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter2 = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter2.take_off()
    participants = [(helicopter1, engine.PASSIVE_ROLE), (helicopter2, engine.ATTACKER_ROLE)]
    self.assertTrue(helicopter1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter2.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_attacker_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (artillery, engine.ATTACKER_ROLE)]
    self.assertTrue(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_defender_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (artillery, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_passive_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (artillery, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_antitank(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_helicopter_on_ground_vs_bunker(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_passive_helicopter_in_air_vs_passive_helicopter_in_air(self):
    self.set_up_for_battle()
    helicopter1 = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter1.take_off()
    helicopter2 = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter2.take_off()
    participants = [(helicopter1, engine.PASSIVE_ROLE), (helicopter2, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_helicopter_in_air_vs_attacker_helicopter_in_air(self):
    self.set_up_for_battle()
    helicopter1 = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter1.take_off()
    helicopter2 = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter2.take_off()
    participants = [(helicopter1, engine.PASSIVE_ROLE), (helicopter2, engine.ATTACKER_ROLE)]
    self.assertTrue(helicopter1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(helicopter2.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_helicopter_in_air_vs_attacker_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (artillery, engine.ATTACKER_ROLE)]
    self.assertTrue(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_passive_helicopter_in_air_vs_defender_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (artillery, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_helicopter_in_air_vs_passive_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (artillery, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_helicopter_in_air_vs_antitank(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_helicopter_in_air_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertTrue(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_helicopter_in_air_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_helicopter_in_air_vs_bunker(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.PASSIVE_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_attacker_helicopter_in_air_vs_attacker_helicopter_in_air(self):
    self.set_up_for_battle()
    helicopter1 = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter1.take_off()
    helicopter2 = engine.Helicopter(self.game, self.tile, self.country2)
    helicopter2.take_off()
    participants = [(helicopter1, engine.ATTACKER_ROLE), (helicopter2, engine.ATTACKER_ROLE)]
    self.assertTrue(helicopter1.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(helicopter2.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_helicopter_in_air_vs_attacker_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.ATTACKER_ROLE), (artillery, engine.ATTACKER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_helicopter_in_air_vs_defender_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.ATTACKER_ROLE), (artillery, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_helicopter_in_air_vs_passive_artillery(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    artillery = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.ATTACKER_ROLE), (artillery, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_helicopter_in_air_vs_antitank(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.ATTACKER_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_helicopter_in_air_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.ATTACKER_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertTrue(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_helicopter_in_air_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.ATTACKER_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_helicopter_in_air_vs_bunker(self):
    self.set_up_for_battle()
    helicopter = engine.Helicopter(self.game, self.tile, self.country1)
    helicopter.take_off()
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(helicopter, engine.ATTACKER_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(helicopter.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 1)

  def test_attacker_artillery_vs_attacker_artillery(self):
    self.set_up_for_battle()
    artillery1 = engine.Artillery(self.game, self.tile, self.country1)
    artillery2 = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(artillery1, engine.ATTACKER_ROLE), (artillery2, engine.ATTACKER_ROLE)]
    self.assertFalse(artillery1.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(artillery2.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))

  def test_attacker_artillery_vs_defender_artillery(self):
    self.set_up_for_battle()
    artillery1 = engine.Artillery(self.game, self.tile, self.country1)
    artillery2 = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(artillery1, engine.ATTACKER_ROLE), (artillery2, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery1.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(artillery2.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_artillery_vs_passive_artillery(self):
    self.set_up_for_battle()
    artillery1 = engine.Artillery(self.game, self.tile, self.country1)
    artillery2 = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(artillery1, engine.ATTACKER_ROLE), (artillery2, engine.PASSIVE_ROLE)]
    self.assertFalse(artillery1.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(artillery2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_artillery_vs_antitank(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(artillery, engine.ATTACKER_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_artillery_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(artillery, engine.ATTACKER_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_attacker_artillery_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(artillery, engine.ATTACKER_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertTrue(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_attacker_artillery_vs_bunker(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(artillery, engine.ATTACKER_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.ATTACKER_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 1)

  def test_defender_artillery_vs_defender_artillery(self):
    self.set_up_for_battle()
    artillery1 = engine.Artillery(self.game, self.tile, self.country1)
    artillery2 = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(artillery1, engine.DEFENDER_ROLE), (artillery2, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery1.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(artillery2.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_artillery_vs_passive_artillery(self):
    self.set_up_for_battle()
    artillery1 = engine.Artillery(self.game, self.tile, self.country1)
    artillery2 = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(artillery1, engine.DEFENDER_ROLE), (artillery2, engine.PASSIVE_ROLE)]
    self.assertFalse(artillery1.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(artillery2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_artillery_vs_antitank(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(artillery, engine.DEFENDER_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_artillery_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(artillery, engine.DEFENDER_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_artillery_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(artillery, engine.DEFENDER_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_artillery_vs_bunker(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(artillery, engine.DEFENDER_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_passive_artillery_vs_passive_artillery(self):
    self.set_up_for_battle()
    artillery1 = engine.Artillery(self.game, self.tile, self.country1)
    artillery2 = engine.Artillery(self.game, self.tile, self.country2)
    participants = [(artillery1, engine.PASSIVE_ROLE), (artillery2, engine.PASSIVE_ROLE)]
    self.assertFalse(artillery1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(artillery2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_artillery_vs_antitank(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    antitank = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(artillery, engine.PASSIVE_ROLE), (antitank, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_artillery_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(artillery, engine.PASSIVE_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_passive_artillery_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(artillery, engine.PASSIVE_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_artillery_vs_bunker(self):
    self.set_up_for_battle()
    artillery = engine.Artillery(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(artillery, engine.PASSIVE_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(artillery.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_antitank_vs_antitank(self):
    self.set_up_for_battle()
    antitank1 = engine.Antitank(self.game, self.tile, self.country1)
    antitank2 = engine.Antitank(self.game, self.tile, self.country2)
    participants = [(antitank1, engine.DEFENDER_ROLE), (antitank2, engine.DEFENDER_ROLE)]
    self.assertFalse(antitank1.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(antitank2.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_antitank_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    antitank = engine.Antitank(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(antitank, engine.DEFENDER_ROLE), (iron_dome, engine.DEFENDER_ROLE)]
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_antitank_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    antitank = engine.Antitank(self.game, self.tile, self.country1)
    iron_dome = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(antitank, engine.DEFENDER_ROLE), (iron_dome, engine.PASSIVE_ROLE)]
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_antitank_vs_bunker(self):
    self.set_up_for_battle()
    antitank = engine.Antitank(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(antitank, engine.DEFENDER_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(antitank.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_defender_iron_dome_vs_defender_iron_dome(self):
    self.set_up_for_battle()
    iron_dome1 = engine.IronDome(self.game, self.tile, self.country1)
    iron_dome2 = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(iron_dome1, engine.DEFENDER_ROLE), (iron_dome2, engine.DEFENDER_ROLE)]
    self.assertFalse(iron_dome1.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome2.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))

  def test_defender_iron_dome_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    iron_dome1 = engine.IronDome(self.game, self.tile, self.country1)
    iron_dome2 = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(iron_dome1, engine.DEFENDER_ROLE), (iron_dome2, engine.PASSIVE_ROLE)]
    self.assertFalse(iron_dome1.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(iron_dome2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_defender_iron_dome_vs_bunker(self):
    self.set_up_for_battle()
    iron_dome = engine.IronDome(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(iron_dome, engine.DEFENDER_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(iron_dome.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_passive_iron_dome_vs_passive_iron_dome(self):
    self.set_up_for_battle()
    iron_dome1 = engine.IronDome(self.game, self.tile, self.country1)
    iron_dome2 = engine.IronDome(self.game, self.tile, self.country2)
    participants = [(iron_dome1, engine.PASSIVE_ROLE), (iron_dome2, engine.PASSIVE_ROLE)]
    self.assertFalse(iron_dome1.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(iron_dome2.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))

  def test_passive_iron_dome_vs_bunker(self):
    self.set_up_for_battle()
    iron_dome = engine.IronDome(self.game, self.tile, self.country1)
    bunker = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(iron_dome, engine.PASSIVE_ROLE), (bunker, engine.DEFENDER_ROLE)]
    self.assertFalse(iron_dome.should_die_in_battle(engine.PASSIVE_ROLE, self.tile, participants))
    self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, 0)

  def test_bunker_vs_bunker(self):
    self.set_up_for_battle()
    bunker1 = engine.Bunker(self.game, self.tile, self.country1)
    bunker2 = engine.Bunker(self.game, self.tile, self.country2)
    participants = [(bunker1, engine.DEFENDER_ROLE), (bunker2, engine.DEFENDER_ROLE)]
    self.assertFalse(bunker1.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker1.hits, 0)
    self.assertFalse(bunker2.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker2.hits, 0)

  def test_bunker_dies_after_many_hits_in_same_turn(self):
    self.set_up_for_battle()
    bunker = engine.Bunker(self.game, self.tile, self.country1)
    tank = engine.Tank(self.game, self.tile, self.country2)
    participants = [(bunker, engine.DEFENDER_ROLE), (tank, engine.ATTACKER_ROLE)]
    for i in range(constants.BUNKER_DEFEND_MULTIPLIER):
      self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
      self.assertEqual(bunker.hits, i + 1)
    self.assertTrue(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
    self.assertEqual(bunker.hits, constants.BUNKER_DEFEND_MULTIPLIER + 1)

  def test_bunker_does_not_die_after_many_hits_in_different_turns(self):
    self.set_up_for_battle()
    bunker = engine.Bunker(self.game, self.tile, self.country1)
    tank = engine.Tank(self.game, self.tile, self.country2)
    participants = [(bunker, engine.DEFENDER_ROLE), (tank, engine.ATTACKER_ROLE)]
    for i in range(constants.BUNKER_DEFEND_MULTIPLIER + 1):
      self.assertFalse(bunker.should_die_in_battle(engine.DEFENDER_ROLE, self.tile, participants))
      self.assertEqual(bunker.hits, 1)
      bunker.turn_done()

# TODO: Test additional_load_from_dict

if __name__ == '__main__':
  unittest.main()
