from collections import namedtuple

Coordinates = namedtuple('Coordinates', ['x', 'y'])

def distance(a, b):
  return abs(a.x - b.x) + abs(a.y - b.y)

