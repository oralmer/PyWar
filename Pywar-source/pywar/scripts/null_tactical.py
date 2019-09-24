import random
import sys

import tactical_api
import constants
import strategic_api

class MyStrategicApi(strategic_api.StrategicApi):
  def build_tank(self):
    pass

def get_strategic_implementation(context):
  return MyStrategicApi(context)
