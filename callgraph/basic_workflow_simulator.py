
from decimal import Decimal, ROUND_HALF_UP
import json
import networkx as nx
import numpy as np
import re
from scipy import stats
from simulator import Simulator, SimulatorController, RandomGenerator
import sys
import traceback


class BasicWorkflowSimulator(Simulator):

    K_GRAPH = "graph"
    K_NODE = "node"
    K_EDGE = "edge"
    K_NAME = "name"
    K_TYPE = "type"
    K_DATAFLOW = "dataflow"
    K_DATA = "data"
    K_CONTROLLER = "controller"
    K_CONTROLFLOW = "controlflow"

    K_CONSUMPTION_TIME = "consumption-time"
    K_CONSUMPTION_TIME_MEAN = "consumption-time-mean"
    K_CONSUMPTION_TIME_MIN = "consumption-time-min"
    K_CONSUMPTION_TIME_MAX = "consumption-time-max"
    K_CONSUMPTION_TIME_VARIANCE = "consumption-time-variance"
    K_CONSUMPTION_TIME_RANDOM = "consumption-time-random"
    K_PROGRESS_FILTER = "pf"
    K_PROGRESS_REPORT = "pr"
    K_PROCESS_STARTED = "process-started"
    K_PROCESS_FINISHED = "process-finished"
    K_PROCESS_PROGRESS = "process-progress"
    K_NODE_PROCESS_STARTED = "node-process-started"
    K_NODE_PROCESS_FINISHED = "node-process-finished"
    K_NODE_PROCESS_PROGRESS = "node-process-progress"
    K_EDGE_PROCESS_STARTED = "edge-process-started"
    K_EDGE_PROCESS_FINISHED = "edge-process-finished"
    K_EDGE_PROCESS_PROGRESS = "edge-process-progress"

    K_STARTED = "started"
    K_PROGRESSING = "progressing"
    K_FINISHED = "finished"


    def __init__(self, G, args=None):
        super().__init__()
        self.G = G
        self.args = {}
        if args is not None:
            for k in args.keys():
                self.args[k] = args[k]
        self.simulator_args = {}
        self.create_nodeid_list()
        self.create_nodeatt_list()
        self.create_edge_matrix()
        self.tested = False

    def get_nodeid_list(self):
        return json.loads(json.dumps(self.nodeid_list))

    def get_nodeatt_list(self):
        return json.loads(json.dumps(self.nodeatt_list))

    def get_edge_matrix(self):
        return json.loads(json.dumps(self.edge_matrix))

    def get_tested(self):
        return self.tested

    def set_tested(self, tested):
        self.tested = tested

    def test_node_attr(self, args):
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        for n in self.G.nodes:
            if self.K_CONSUMPTION_TIME in self.G.nodes[n].keys():
                pass
            elif self.K_CONSUMPTION_TIME_MEAN in self.G.nodes[n].keys():
                if self.K_CONSUMPTION_TIME_RANDOM in self.G.nodes[n].keys():
                    for k in (self.K_CONSUMPTION_TIME_MEAN, self.K_CONSUMPTION_TIME_MIN, self.K_CONSUMPTION_TIME_MAX):
                        if k not in self.G.nodes[n].keys():
                            err += 1
                            fp.write("Error: node {} doesn't has '{}' property.\n".format(n, k))
                            fp.flush()
                    if self.K_CONSUMPTION_TIME_RANDOM in ("uniform","normal"):
                        err += 1
                        fp.write("Error: node {} has invalid value of property '{}':{}.\n".format(n, self.K_CONSUMPTION_TIME_RANDOM),
                                 self.G.nodes[n][self.K_CONSUMPTION_TIME_RANDOM])
                        fp.flush()
                    elif self.K_CONSUMPTION_TIME_RANDOM == "normal":
                        if self.K_CONSUMPTION_TIME_VARIANCE not in self.G.nodes[n].keys():
                            err += 1
                            fp.write("Error: node {} doesn't has '{}' property.\n".format(n, k))
                            fp.flush()
                else:
                    err += 1
                    fp.write("Error: node {} doesn't has '{}' property.\n".format(n, self.K_CONSUMPTION_TIME_RANDOM))
                    fp.flush()
            else:
                err += 1
                fp.write("Error: node {} doesn't has '{}' property.\n".format(n, self.K_CONSUMPTION_TIME_MEAN))
                fp.flush()

            #if self.K_TYPE not in self.G.nodes[n].keys():
            #    err += 1
            #    fp.write("Error: node {} doesn't has '{} property".format(n, self.K_TYPE))
            #    fp.flush()
            #if self.G.nodes[n][self.K_TYPE] not in (self.K_CONTROLLER, self.PROCESSOR):
            #    err += 1
            #    fp.write("Error: {} of node {} is neither '{} nor '{}'\n".format(self.K_TYPE, n, self.K_CONTROLLER, self.K_PROCESSOR))
            #    fp.flush()
            for n in self.G.nodes:
                for k in (self.K_CONSUMPTION_TIME, self.K_CONSUMPTION_TIME_MEAN, self.K_CONSUMPTION_TIME_MIN,
                          self.K_CONSUMPTION_TIME_MAX, self.K_CONSUMPTION_TIME_VARIANCE):
                    if k in self.G.nodes[n].keys():
                        try:
                            v = float(self.G.nodes[n][k])
                            if v < 0:
                                err += 1
                                fp.write("Error: node {} has negative '{}' property:{}.\n".format(n, k))
                                fp.flush()
                        except:
                            err += 1
                            fp.write("Error: node {} has invalid '{}' property.\n".format(n, k))
                            fp.flush()
        return err
    
    def test_edge_attr(self, args):
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        for e in self.G.edges:
            if self.K_CONSUMPTION_TIME in self.G.edges[e[0],e[1]].keys():
                pass
            elif self.K_CONSUMPTION_TIME_MEAN in self.G.edges[e[0],e[1]].keys():
                if self.K_CONSUMPTION_TIME_RANDOM in self.G.edges[e[0],e[1]].keys():
                    for k in (self.K_CONSUMPTION_TIME_MEAN, self.K_CONSUMPTION_TIME_MIN, self.K_CONSUMPTION_TIME_MAX):
                        if k not in self.G.edges[e[0],e[1]].keys():
                            err += 1
                            fp.write("Error: edge {} doesn't has '{}' property.\n".format(str(e), k))
                            fp.flush()
                    if self.K_CONSUMPTION_TIME_RANDOM in ("uniform","normal"):
                        err += 1
                        fp.write("Error: edge {} has invalid value of property '{}':{}.\n".format(str(e), self.K_CONSUMPTION_TIME_RANDOM),
                                 self.G.edges[e[0],e[1]][self.K_CONSUMPTION_TIME_RANDOM])
                        fp.flush()
                    elif self.K_CONSUMPTION_TIME_RANDOM == "normal":
                        if self.K_CONSUMPTION_TIME_VARIANCE not in self.G.edges[e[0],e[1]].keys():
                            err += 1
                            fp.write("Error: edge {} doesn't has '{}' property.\n".format(str(e), k))
                            fp.flush()
                else:
                    err += 1
                    fp.write("Error: edge {} doesn't has '{}' property.\n".format(str(e), self.K_CONSUMPTION_TIME_RANDOM))
                    fp.flush()
            else:
                err += 1
                fp.write("Error: edge {} doesn't has '{}' property.\n".format(str(e), self.K_CONSUMPTION_TIME_MEAN))
                fp.flush()

            for e in self.G.edges:
                for k in (self.K_CONSUMPTION_TIME, self.K_CONSUMPTION_TIME_MEAN, self.K_CONSUMPTION_TIME_MIN,
                          self.K_CONSUMPTION_TIME_MAX, self.K_CONSUMPTION_TIME_VARIANCE):
                    if k in self.G.edges[e[0],e[1]].keys():
                        try:
                            v = float(self.G.edges[e[0],e[1]][k])
                            if v < 0:
                                err += 1
                                fp.write("Error: edge {} has negative '{}' property:{}.\n".format(str(e), k))
                                fp.flush()
                        except:
                            err += 1
                            fp.write("Error: edge {} has invalid '{}' property value:{}.\n".format(str(e), k, str(self.G.edges[e[0],e[1]][k])))
                            fp.flush()

        return err

    def test_connectivities(self, args):
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        return err

    def test(self, args):
        if self.tested:
            return True
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        err += self.test_node_attr(args)
        err += self.test_edge_attr(args)
        err += self.test_connectivities(args)
        if err != 0:
            fp.write("Error: {} problem(s) found\n".format(err))
            fp.flush()
            return False
        return True

    def restore(self, nodeid_list, nodeatt_list, edge_matrix):
        for i,a in zip(range(0, len(nodeatt_list)), nodeatt_list):
            self.nodeatt_list[i].clear()
            for k in a.keys():
                self.nodeatt_list[i][k] = a[k]
        for i in range(0, len(nodeatt_list)):
            for j in range(0, len(nodeatt_list)):
                if self.edge_matrix[i][j] is not None:
                    self.edge_matrix[i][j].clear()
                    for k in edge_matrix[i][j].keys():
                        self.edge_matrix[i][j][k] = edge_matrix[i][j][k]

    def create_nodeid_list(self):
        self.nodeid_list = [_  for _ in self.G.nodes]

    def create_nodeatt_list(self):
        rG = self.G.reverse(copy=True)
        nodeatt_list = [None for _ in self.G.nodes]
        for i,n in zip(range(0, len(self.nodeid_list)), self.nodeid_list):
            nodeatt_list[i] = {
                self.K_FORKS: len(self.G[n].keys()),
                self.K_FORKED: 0,
                self.K_JOINS: len(rG[n].keys()),
                self.K_JOINED: 0,
                self.K_COMPLETED: False,
                self.K_CONSUMED_TIME: 0,
                self.K_START_TIME: None,
                self.K_END_TIME: None,
            }
            for k in (self.K_CONSUMPTION_TIME, self.K_CONSUMPTION_TIME_MEAN, self.K_CONSUMPTION_TIME_MIN,
                      self.K_CONSUMPTION_TIME_MAX, self.K_CONSUMPTION_TIME_RANDOM):
                if k in self.G.nodes[n].keys():
                    nodeatt_list[i][k] = self.G.nodes[n][k]
        self.nodeatt_list = nodeatt_list
    
    def create_edge_matrix(self):
        edge_matrix = []
        for _ in range(0, len(self.nodeid_list)):
            edge_matrix.append([None for _ in range(0, len(self.nodeid_list))])
        for i,n in zip(range(0, len(self.nodeid_list)), self.nodeid_list):
            for j,m in zip(range(0, len(self.nodeid_list)), self.nodeid_list):
                if self.G.has_edge(n, m):
                    edge_matrix[i][j] = {
                        self.K_COMPLETED: False,
                        self.K_CONSUMED_TIME: 0,
                        self.K_START_TIME: None,
                        self.K_END_TIME: None,
                    }
                    for k in (self.K_CONSUMPTION_TIME, self.K_CONSUMPTION_TIME_MEAN, self.K_CONSUMPTION_TIME_MIN,
                              self.K_CONSUMPTION_TIME_MAX, self.K_CONSUMPTION_TIME_RANDOM):
                        if k in self.G.edges[n,m].keys():
                            edge_matrix[i][j][k] = self.G.edges[n,m][k]
        self.edge_matrix = edge_matrix

    def is_workflow_finished(self):
        task_remained = False
        for i,n in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
            if self.nodeatt_list[i] is not None and not self.nodeatt_list[i][self.K_COMPLETED]:
                task_remained = True
                break
        if not task_remained:
            for i,n in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
                for j,m in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
                    if self.edge_matrix[i][j] is not None and not self.edge_matrix[i][j][self.K_COMPLETED]:
                        task_remained = True
                        break
                    if task_remained:
                        break
                if not task_remained:
                    break
        return not task_remained

    def simulate_main(self, time, dt, args):
        self.simulator_args.clear()
        for k in args.keys():
            self.simulator_args[k] = args[k]
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        self.process_started(fp, time)
        edges_to_start = []
        while True:
            for i,n in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
                if self.nodeatt_list[i][self.K_JOINED] == self.nodeatt_list[i][self.K_JOINS]:
                    if self.nodeatt_list[i][self.K_START_TIME] is None:
                        self.nodeatt_list[i][self.K_START_TIME] = time
                        self.nodeatt_list[i][self.K_CONSUMED_TIME] = 0
                        self.node_process_started(n, fp, time)
            edges_to_start_next_time = []
            for i,n in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
                if self.nodeatt_list[i][self.K_START_TIME] is not None and not self.nodeatt_list[i][self.K_COMPLETED]:
                    self.nodeatt_list[i][self.K_CONSUMED_TIME] += dt
                    if self.nodeatt_list[i][self.K_CONSUMED_TIME] >= self.nodeatt_list[i][self.K_CONSUMPTION_TIME]:
                        self.nodeatt_list[i][self.K_END_TIME] = time + dt
                        self.nodeatt_list[i][self.K_COMPLETED] = True
                        for t in self.G[n].keys():
                            edges_to_start_next_time.append((i, self.nodeid_list.index(t)))
                        self.node_process_finished(n, fp, time+dt)
            for i,n in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
                for j,m in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
                    if (i,j) in edges_to_start:
                        if self.edge_matrix[i][j][self.K_START_TIME] is None:
                            self.edge_matrix[i][j][self.K_START_TIME] = time
                            self.edge_matrix[i][j][self.K_CONSUMED_TIME] = 0
                            self.edge_process_started((n,m), fp, time)
            for i,n in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
                for j,m in zip(range(0, len(self.nodeatt_list)), self.nodeid_list):
                    if self.edge_matrix[i][j] is not None:
                        if self.edge_matrix[i][j][self.K_START_TIME] is not None and not self.edge_matrix[i][j][self.K_COMPLETED]:
                            self.edge_matrix[i][j][self.K_CONSUMED_TIME] += dt
                            if self.edge_matrix[i][j][self.K_CONSUMED_TIME] >= self.edge_matrix[i][j][self.K_CONSUMPTION_TIME]:
                                self.edge_matrix[i][j][self.K_END_TIME] = time + dt
                                self.edge_matrix[i][j][self.K_COMPLETED] = True
                                self.nodeatt_list[j][self.K_JOINED] += 1
                                self.edge_process_finished((n,m), fp, time+dt)
            edges_to_start = edges_to_start_next_time
            time += dt
            self.process_progress(fp, time)
            workflow_finished = self.is_workflow_finished()
            if workflow_finished:
                self.process_finished(fp, time)
                return time

    def simulate(self, args):
        if "dt" in args.keys():
            dt = float(args["dt"])
        else:
            dt = 0.1

        # test model
        if not self.test(args):
            return False

        # start simulation
        time = 0
        self.simulate_main(time, dt, args)
        
        return False

    def process_started(self, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_PROCESS_STARTED in self.simulator_args[self.K_PROGRESS_FILTER]):
            self.simulator_args[self.K_PROGRESS_REPORT](self.K_GRAPH, self.G.graph[self.K_NAME], self.K_STARTED, time)

    def process_progress(self, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_PROCESS_STARTED in self.simulator_args[self.K_PROGRESS_FILTER]):
            if time % 10 == 0:
                self.simulator_args[self.K_PROGRESS_REPORT](self.K_GRAPH, self.G.graph[self.K_NAME], self.K_PROGRESSING, time)

    def process_finished(self, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_PROCESS_FINISHED in self.simulator_args[self.K_PROGRESS_FILTER]):
                self.simulator_args[self.K_PROGRESS_REPORT](self.K_GRAPH, self.G.graph[self.K_NAME], self.K_FINISHED, time)

    def node_process_started(self, n, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_NODE_PROCESS_STARTED in self.simulator_args[self.K_PROGRESS_FILTER]):
            self.simulator_args[self.K_PROGRESS_REPORT](self.K_NODE, n, self.K_STARTED, time)

    def node_process_progress(self, n, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_NODE_PROCESS_PROGRESS in self.simulator_args[self.K_PROGRESS_FILTER]):
            self.simulator_args[self.K_PROGRESS_REPORT](n, self.K_PROGRESSING, time)

    def node_process_finished(self, n, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_NODE_PROCESS_FINISHED in self.simulator_args[self.K_PROGRESS_FILTER]):
            self.simulator_args[self.K_PROGRESS_REPORT](self.K_NODE, n, self.K_FINISHED, time)

    def edge_process_started(self, e, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_EDGE_PROCESS_STARTED in self.simulator_args[self.K_PROGRESS_FILTER]):
            self.simulator_args[self.K_PROGRESS_REPORT](self.K_EDGE, e, self.K_STARTED, time)

    def edge_process_progress(self, e, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_EDGE_PROCESS_PROGRESS in self.simulator_args[self.K_PROGRESS_FILTER]):
            if time % 10 == 0:
                self.simulator_args[self.K_PROGRESS_REPORT](self.K_EDGE, e, self.K_PROGRESSING, time)

    def edge_process_finished(self, e, fp, time):
        if self.K_PROGRESS_FILTER not in self.simulator_args.keys() or \
           (self.simulator_args[self.K_PROGRESS_FILTER] is None or \
            self.K_EDGE_PROCESS_FINISHED in self.simulator_args[self.K_PROGRESS_FILTER]):
            self.simulator_args[self.K_PROGRESS_REPORT](self.K_EDGE, e, self.K_FINISHED, time)


class BasicWorkflowSimulatorController(SimulatorController):

    def __init__(self, simulator, args=None):
        super().__init__(simulator)
        self.simulator_args = {}
        pass

    def test(self, args):
        self.simulator.test(args)
        pass

    def dump_progress_report(self, progress_report):
        for s in progress_report:
            s = [str(_) for _ in s]
            sys.stderr.write(", ".join(s) + "\n")

    def describe_stats(self, progress_report):
        if "confidence" in self.simulator_args.keys():
            confidence = simulator_args["confidence"]
        else:
            confidence = 0.9
        samples = []
        for s in progress_report:
            if s[0] == self.simulator.K_GRAPH and s[2] == self.simulator.K_FINISHED:
                samples.append(s[3])
        a = 1.0 * np.array(samples)
        n = len(a)
        m, se = np.mean(a), stats.sem(a)
        h = se * stats.t.ppf((1+confidence)/2.0, n-1)
        sys.stderr.write("Mean time:{}, Confidence time interval for confidence {}:{}-{}\n".format(Decimal(m).quantize(Decimal("0.01"),ROUND_HALF_UP),Decimal(confidence).quantize(Decimal("0.01"),ROUND_HALF_UP),Decimal(m-h).quantize(Decimal("0.01"),ROUND_HALF_UP),Decimal(m+h).quantize(Decimal("0.01"),ROUND_HALF_UP)))

    def run(self, args, once=True):
        # check arguments
        if "t" in args.keys():
            if not self.simulator.test(args):
                return False
        self.simulator_args.clear()
        for k in args.keys():
            self.simulator_args[k] = args[k]
        simulator_args = {}
        if once:
            i = 1
        else:
            if "i" not in args.keys():
                simulator_args["i"] = 100
            else:
                simulator_args["i"] = int(args["i"])
        if "dt" not in args.keys():
            simulator_args["dt"] = 0.1
        else:
            simulator_args["dt"] = float(args["dt"])
        if self.simulator.K_PROGRESS_FILTER not in args.keys():
            report_filter = None
        else:
            pf = args[self.simulator.K_PROGRESS_FILTER]
            if pf is None:
                report_filter = None
            else:
                report_filter = pf.split(",")
        simulator_args[self.simulator.K_PROGRESS_FILTER] = report_filter
        # setup for progress report
        progress_report = []
        output_file = None if "f" not in args.keys() else self.simulator.args["f"]
        def report(*args):
            if output_file is None:
                sys.stdout.write(" ".join([str(_) for _ in args]) + "\n")
                sys.stdout.flush()
            else:
                with open(output_file, "a") as f:
                    f.write(" ".join([str(_) for _ in args]) + "\n")
                    f.flush()
            progress_report.append([_ for _ in args])
            pass
        simulator_args[BasicWorkflowSimulator.K_PROGRESS_REPORT] = report
        if not self.simulator.test(simulator_args):
            return False
        #self.simulator.set_tested(True)
        nodeid_list_org = self.simulator.get_nodeid_list()
        nodeatt_list_org = self.simulator.get_nodeatt_list()
        edge_matrix_org = self.simulator.get_edge_matrix()
        rng = RandomGenerator(simulator_args["dt"],
                              RandomGenerator.K_RANDOM_TIME_MAX)
        # run simulation
        if once:
            nodeid_list = json.loads(json.dumps(nodeid_list_org))
            nodeatt_list = json.loads(json.dumps(nodeatt_list_org))
            edge_matrix = json.loads(json.dumps(edge_matrix_org))
            for n,a in zip(nodeid_list, nodeatt_list):
                if self.simulator.K_CONSUMPTION_TIME not in a.keys():
                    a[self.simulator.K_CONSUMPTION_TIME] = self.random(rng, a)
            for i,n in zip(range(0, len(nodeid_list)), nodeid_list):
                for j,m in zip(range(0, len(nodeid_list)), nodeid_list):
                    if edge_matrix[i][j] is not None:
                        if self.simulator.K_CONSUMPTION_TIME not in edge_matrix[i][j].keys():
                            edge_matrix[i][j][self.simulator.K_CONSUMPTION_TIME] = self.random(rng, a)
            self.simulator.restore(nodeid_list, nodeatt_list, edge_matrix)
            self.simulator.simulate(simulator_args)
            self.dump_progress_report(progress_report)
            return False
        else:
            for i in range(0, simulator_args["i"]):
                nodeid_list = json.loads(json.dumps(nodeid_list_org))
                nodeatt_list = json.loads(json.dumps(nodeatt_list_org))
                edge_matrix = json.loads(json.dumps(edge_matrix_org))
                for n,a in zip(nodeid_list, nodeatt_list):
                    if self.simulator.K_CONSUMPTION_TIME not in a.keys():
                        a[self.simulator.K_CONSUMPTION_TIME] = self.random(rng, a)
                for i,n in zip(range(0, len(nodeid_list)), nodeid_list):
                    for j,m in zip(range(0, len(nodeid_list)), nodeid_list):
                        if edge_matrix[i][j] is not None:
                            if self.simulator.K_CONSUMPTION_TIME not in edge_matrix[i][j].keys():
                                edge_matrix[i][j][self.simulator.K_CONSUMPTION_TIME] = self.random(rng, a)
                self.simulator.restore(nodeid_list, nodeatt_list, edge_matrix)
                self.simulator.simulate(simulator_args)
                pass
            #self.dump_progress_report(progress_report)
            self.describe_stats(progress_report)
            return False

    def random(self, rng, a):
        random_type = a[self.simulator.K_CONSUMPTION_TIME_RANDOM]
        consumption_time_mean = a[self.simulator.K_CONSUMPTION_TIME_MEAN]
        consumption_time_min = a[self.simulator.K_CONSUMPTION_TIME_MIN]
        consumption_time_max = a[self.simulator.K_CONSUMPTION_TIME_MAX]
        if self.simulator.K_CONSUMPTION_TIME_VARIANCE in a.keys():
            consumption_time_variance = a[self.simulator.K_CONSUMPTION_TIME_VARIANCE]
        else:
            consumption_time_variance = 1
        consumption_time = rng.random(random_type,
                                      consumption_time_mean,
                                      consumption_time_min,
                                      consumption_time_max,
                                      consumption_time_variance)
        return consumption_time
