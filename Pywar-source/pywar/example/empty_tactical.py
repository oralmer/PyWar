import random

import tactical_api
import strategic_api


class MyStrategicApi(strategic_api.StrategicApi):
    def __init__(self, *args, **kwargs):
        super(MyStrategicApi, self).__init__(*args, **kwargs)

    def conquer_using_tanks_tile_of(self, countries):
        pass


def get_strategic_implementation(context):
    return MyStrategicApi(context)
