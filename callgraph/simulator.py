
import json
import networkx as nx
import random
import re
import sys
import traceback


class Simulator:

    K_CONSUMPTION_TIME = "consumption-time"
    K_CONSUMED_TIME = "consumed-time"
    K_FORKS = "forks"
    K_FORKED = "forked"
    K_JOINS = "joins"
    K_JOINED = "joined"
    K_COMPLETED = "completed"
    K_START_TIME = "start-time"
    K_END_TIME = "end-time"

    def __init__(self):
        pass

    def test(self, args):
        pass

    def is_workflow_finished(self):
        pass

    def simulate_main(self, time, dt, args):
        pass

    def simulate(self, args):
        pass

    def process_started(self, fp, t):
        pass

    def process_progress(self, fp, t):
        pass

    def process_finished(self, fp, t):
        pass

    def node_process_started(self, n, fp, t):
        pass

    def node_process_progress(self, n, fp, t):
        pass

    def node_process_finished(self, n, fp, t):
        pass

    def edge_process_started(self, n, fp, t):
        pass

    def edge_process_progress(self, n, fp, t):
        pass

    def edge_process_finished(self, n, fp, t):
        pass


class SimulatorController:

    def __init__(self, simulator):
        self.simulator = simulator
        pass

    def test(self, args):
        pass

    def run(self, args):
        pass

    
class RandomGenerator:

    K_UNIFORM = "uniform"
    K_NORMAL = "normal"

    K_RANDOM_TIME_MAX = sys.float_info.max
    K_RANDOM_TIME_MIN = 0
    K_FLOAT_MAX = sys.float_info.max
    K_FLOAT_MIN = sys.float_info.min
    K_RANDOM_TIME_MAX = sys.float_info.max
    K_RANDOM_TIME_MIN = 0

    def __init__(self, _min=None, _max=None):
        self.min = self.K_FLOAT_MIN if _min is None else _min
        self.max = self.K_FLOAT_MAX if _max is None else _max
        pass

    def seed(self, ini):
        random.seed(ini)

    def random(self, _type, _mean, _min=None, _max=None, _variance=None):
        if _min is None:
            _min = self.K_FLOAT_MIN
        if _max is None:
            _max = self.K_FLOAT_MAX
        if _type == self.K_UNIFORM:
            r = random.uniform(_min, _max)
        elif _type == self.K_NORMAL:
            if _variance is None:
                _variance = 1
            while True:
                r = random.gauss(_mean, _variance)
                if _min <= r and r <= _max:
                    return r
        else:
            sys.stderr.write("Error: invalid random type:{}\n".format(_type))
            sys.stderr.flush()
            return None
