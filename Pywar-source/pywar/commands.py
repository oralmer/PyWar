from common_types import Coordinates

class CommandBase(object):
  def __init__(self, name, piece_id):
    self.name = name
    self.piece_id = piece_id

  def to_dict(self):
    rv = {'name': self.name, 'pieceId': self.piece_id}
    rv.update(self.to_dict_specific())
    return rv

  def to_dict_specific(self):
    return {}

  def apply(self, game):
    raise UnimplementedError()

def no_arguments_command(command_name, apply_function):
  """apply_function takes the piece as its only argument."""
  class CommandInternal(CommandBase):
    def __init__(self, piece_id):
      super(CommandInternal, self).__init__(command_name, piece_id)

    def apply(self, game):
      apply_function(game.pieces[self.piece_id])

    @staticmethod
    def from_dict(d):
      return CommandInternal(d['pieceId'])
  return CommandInternal

MeleeAttackCommand = no_arguments_command('meleeAttack', lambda piece: piece.attack())
TakeOffCommand = no_arguments_command('takeOff', lambda piece: piece.take_off())
LandCommand = no_arguments_command('land', lambda piece: piece.land())
TurnOnProtection = no_arguments_command('turnOnProtection', lambda piece: piece.turn_on())
TurnOffProtection = no_arguments_command('turnOffProtection', lambda piece: piece.turn_off())

class MoveCommand(CommandBase):
  def __init__(self, piece_id, new_location):
    super(MoveCommand, self).__init__('move', piece_id)
    self.new_location = new_location

  def to_dict_specific(self):
    return {'newLocation': self.new_location._asdict()}

  def apply(self, game):
    piece = game.pieces[self.piece_id]
    piece.tile = game.tiles[self.new_location.x][self.new_location.y]

  @staticmethod
  def from_dict(d):
    return MoveCommand(d['pieceId'], Coordinates(**d['newLocation']))

class RemoteAttackCommand(CommandBase):
  def __init__(self, piece_id, attack_destination):
    super(RemoteAttackCommand, self).__init__('remoteAttack', piece_id)
    self.attack_destination = attack_destination

  def to_dict_specific(self):
    return {'destination': self.attack_destination._asdict()}

  def apply(self, game):
    game.pieces[self.piece_id].attack(self.attack_destination)

  @staticmethod
  def from_dict(d):
    return RemoteAttackCommand(d['pieceId'], Coordinates(**d['destination'])) 

class TakeMoneyCommand(CommandBase):
  def __init__(self, piece_id, amount):
    super(TakeMoneyCommand, self).__init__('takeMoney', piece_id)
    self.amount = amount

  def to_dict_specific(self):
    return {'amount': self.amount}

  def apply(self, game):
    game.pieces[self.piece_id].collect_money(self.amount)

  @staticmethod
  def from_dict(d):
    return TakeMoneyCommand(d['pieceId'], d['amount'])

class ThrowMoneyCommand(CommandBase):
  def __init__(self, piece_id, amount):
    super(ThrowMoneyCommand, self).__init__('throwMoney', piece_id)
    self.amount = amount

  def to_dict_specific(self):
    return {'amount': self.amount}

  def apply(self, game):
    game.pieces[self.piece_id].throw_money(self.amount)

  @staticmethod
  def from_dict(d):
    return ThrowMoneyCommand(d['pieceId'], d['amount'])

class BuildPieceCommand(CommandBase):
  def __init__(self, piece_id, new_piece_type):
    super(BuildPieceCommand, self).__init__('build', piece_id)
    self.new_piece_type = new_piece_type

  def to_dict_specific(self):
    return {'newPieceType': self.new_piece_type}

  def apply(self, game):
    game.pieces[self.piece_id].build(self.new_piece_type)

  @staticmethod
  def from_dict(d):
    return BuildPieceCommand(d['pieceId'], d['newPieceType'])

COMMAND_NAME_TO_CLASS = {
  'meleeAttack': MeleeAttackCommand,
  'takeOff': TakeOffCommand,
  'land': LandCommand,
  'turnOnProtection': TurnOnProtection,
  'turnOffProtection': TurnOffProtection,
  'move': MoveCommand,
  'remoteAttack': RemoteAttackCommand,
  'takeMoney': TakeMoneyCommand,
  'throwMoney': ThrowMoneyCommand,
  'build': BuildPieceCommand,
}

def command_from_dict(d):
  return COMMAND_NAME_TO_CLASS[d['name']].from_dict(d)

