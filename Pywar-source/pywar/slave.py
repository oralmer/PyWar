import argparse
import importlib
import os.path
import sys

from flask import Flask, request, jsonify

from tactical_api import TurnContext

app = Flask(__name__)
tactical_callback = None
strategic_callback = None

def parse_args():
  parser = argparse.ArgumentParser(description='PyWar slave worker, representing a country.')
  parser.add_argument('-p', '--port', metavar='PORT', type=int, required=True,
                      help='Port number to listen on.')
  parser.add_argument('-t', '--tactical-module-path', metavar='FILE', type=str, required=True,
		      help='Path to the module containing the stategic API implementation, exporting a get_strategic_implementation function.')
  parser.add_argument('-s', '--strategic-module-path', metavar='FILE', type=str, required=True,
		      help='Path to the module containing the stategic logic, exporting a do_turn function.')
  return parser.parse_args()

@app.route('/isup')
def is_up():
  return 'Up and running.'

@app.route('/')
def index():
  return 'Hello world from pyWar!'

@app.route('/turn', methods=['POST']  )
def turn():
  turn_context = TurnContext(request.json)
  strategic_api = tactical_callback(turn_context)
  strategic_callback(strategic_api)
  return jsonify(turn_context.get_result())

def load_tactical_callback(module_path):
  global tactical_callback
  sys.path.insert(0, os.path.dirname(module_path))
  module = importlib.import_module(os.path.splitext(os.path.basename(module_path))[0])
  tactical_callback = module.get_strategic_implementation

def load_strategic_callback(module_path):
  global strategic_callback
  sys.path.insert(0, os.path.dirname(module_path))
  module = importlib.import_module(os.path.splitext(os.path.basename(module_path))[0])
  strategic_callback = module.do_turn

def main():
  args = parse_args()
  load_tactical_callback(args.tactical_module_path)
  load_strategic_callback(args.strategic_module_path)
  app.run(host='127.0.0.1', port=args.port)

if __name__ == '__main__':
  main()

