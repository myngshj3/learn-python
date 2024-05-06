
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
    K_WORKFLOW = "workflow"
    K_DATAFLOW = "dataflow"
    K_STORAGE = "storage"
    K_CONTROLLER = "controller"
    K_CONTROLFLOW = "controlflow"
    K_CONSUMPTION_TIME = "consumption-time"
    K_CONSUMPTION_TIME_SCHEDULED = "consumption-time-scheduled"
    K_CONSUMPTION_TIME_MEAN = "consumption-time-mean"
    K_CONSUMPTION_TIME_MIN = "consumption-time-min"
    K_CONSUMPTION_TIME_MAX = "consumption-time-max"
    K_CONSUMPTION_TIME_VARIANCE = "consumption-time-variance"
    K_CONSUMPTION_TIME_RANDOM = "consumption-time-random"
    K_START_TIME = Simulator.K_START_TIME
    K_START_TIME_SCHEDULED = "start-time-scheduled"
    K_END_TIME = Simulator.K_END_TIME
    K_END_TIME_SCHEDULED = "end-time-scheduled"
    K_INACTIVE_INTERVALS = "inactive-intervals"
    K_DATAFLOWS = "dataflows"
    K_PARENT = "parent"
    K_CHILDREN = "children"
    K_VELOCITY = "velocity"
    K_VELOCITY_FUNCTION = "velocity-function"
    K_TRANS_COEFFICIENCE = "trans-coefficience"
    K_AMOUNT = "amount"
    K_ACCUMULATED = "accumulated"
    K_INBOUNDS = "inbounds"
    K_OUTBOUNDS = "outbounds"
    K_CLOSED_INBOUNDS = "closed-inbounds"
    K_CLOSED_OUTBOUNDS = "closed-outbounds"
    K_UNIT = "unit"
    K_OPENED = "opened"
    K_CLOSED = "closed"
    K_PROGRESSING = "progressing"
    K_STATE = "state"
    K_PREPARED = "prepared"
    K_ACTIVE = "active"
    K_SUSPENDED = "suspended"
    K_FINISHED = "finished"
    K_UNAVAILABLE = "unavailable"

    K_PROGRESS_FILTER = "pf"
    K_PROGRESS_REPORT = "pr"
    K_CONTROLLER_STARTED = "controller-started"
    K_CONTROLLER_FINISHED = "controller-finished"
    K_CONTROLLER_PROGRESS = "controller-progress"
    K_DATAFLOW_STARTED = "dataflow-started"
    K_DATAFLOW_FINISHED = "dataflow-finished"
    K_DATAFLOW_PROGRESS = "dataflow-progress"
    K_CONTROLFLOW_STARTED = "controlflow-started"
    K_CONTROLFLOW_FINISHED = "controlflow-finished"
    K_CONTROLFLOW_PROGRESS = "controlflow-progress"
    K_STARTED = "started"
    K_FINISHED = "finished"

    K_NORMAL = "normal"
    K_UNIFORM = "uniform"

    def __init__(self, G, args=None):
        super().__init__()
        self.G = None
        self.setup_graph(G)
        self.rG = self.G.reverse(copy=True)
        self.args = {}
        if args is not None:
            for k in args.keys():
                self.args[k] = args[k]
        self.simulator_args = {}
        self.storage_nodes = None
        self.setup_storages()
        self.dataflow_edges = None
        self.setup_dataflows()
        self.controller_nodes = None
        self.setup_controllers()
        self.controlflow_edges = None
        self.setup_controlflows()
        self.tested = False

    def restore(self, G):
        self.setup_graph(G)
        self.rG = self.G.reverse(copy=True)
        self.setup_storages()
        self.setup_dataflows()
        self.setup_controllers()
        self.setup_controlflows()

    def setup_graph(self, G):
        g = nx.DiGraph()
        for k in G.graph.keys():
            g.graph[k] = G.graph[k]
        for n in G.nodes:
            g.add_node(n)
            for k in G.nodes[n].keys():
                g.nodes[n][k] = G.nodes[n][k]
        for e in G.edges:
            g.add_edge(e[0], e[1])
            for k in G.edges[e[0], e[1]].keys():
                g.edges[e[0], e[1]][k] = G.edges[e[0], e[1]][k]
        self.G = g

    def setup_storages(self):
        storage_nodes = []
        for n in self.G.nodes:
            #print(n, self.K_TYPE in self.G.nodes[n].keys())
            if self.G.nodes[n][self.K_TYPE] == self.K_STORAGE:
                storage_nodes.append(n)
                self.G.nodes[n][self.K_INBOUNDS] = len(self.rG[n].keys())
                self.G.nodes[n][self.K_OUTBOUNDS] = len(self.G[n].keys())
        self.storage_nodes = storage_nodes

    def setup_dataflows(self):
        dataflow_edges = []
        for e in self.G.edges:
            if self.G.edges[e[0], e[1]][self.K_TYPE] == self.K_DATAFLOW:
                dataflow_edges.append(e)
        self.dataflow_edges = dataflow_edges

    def setup_controllers(self):
        controller_nodes = []
        for n in self.G.nodes:
            if self.G.nodes[n][self.K_TYPE] == self.K_CONTROLLER:
                controller_nodes.append(n)
        self.controller_nodes = controller_nodes

    def setup_controlflows(self):
        controlflow_edges = []
        for e in self.G.edges:
            if self.G.edges[e[0], e[1]][self.K_TYPE] == self.K_CONTROLFLOW:
                controlflow_edges.append(e)
        self.controlflow_edges = controlflow_edges

    def test(self, args):
        if self.tested:
            return True
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        err += self.test_storage_nodes(args)
        err += self.test_dataflow_edges(args)
        err += self.test_controller_nodes(args)
        err += self.test_controlflow_edges(args)
        if err != 0:
            fp.write("Error: {} problem(s) found\n".format(err))
            fp.flush()
            return False
        return True

    def test_storage_nodes(self, args):
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        for n in self.storage_nodes:
            for k in (self.K_STATE, self.K_INBOUNDS, self.K_OUTBOUNDS, self.K_UNIT):
                if k not in self.G.nodes[n].keys():
                    err += 1
                    fp.write("Error: {} '{}' doesn't has '{}' property.\n".format(self.K_STORAGE, str(n), k))
                    fp.flush()
        return err

    def test_dataflow_edges(self, args):
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        for e in self.dataflow_edges:
            for k in (self.K_STATE, self.K_VELOCITY, self.K_CONSUMED_TIME):
                if k not in self.G.edges[e[0], e[1]].keys():
                    err += 1
                    fp.write("Error: {} '{}' doesn't has '{}' property.\n".format(self.K_DATAFLOW, str(e), k))
                    fp.flush()
        return err

    def test_controller_nodes(self, args):
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        for n in self.controller_nodes:
            for k in (self.K_STATE, self.K_START_TIME, self.K_END_TIME, self.K_DATAFLOWS, self.K_INACTIVE_INTERVALS):
                      #self.K_START_TIME_SCHEDULED, self.K_END_TIME_SCHDULED,
                      #self.K_CONSUMPTION_TIME_SCHDULED, self.INACTIVE_INTERVALS):
                if k not in self.G.nodes[n].keys():
                    err += 1
                    fp.write("Error: {} '{}' doesn't has '{}' property.\n".format(self.K_CONTROLLER, str(n), k))
                    fp.flush()
            if self.K_DATAFLOWS in self.G.nodes[n].keys():
                dataflows = self.G.nodes[n][self.K_DATAFLOWS]
                for df in dataflows:
                    if (df[0], df[1]) not in self.dataflow_edges:
                        err += 1
                        fp.write(
                            "Error: {} {} has invalid dataflow: {}.\n".format(self.K_CONTROLLER, str(n), str((df[0], df[1]))))
                        fp.flush()
        return err

    def test_controlflow_edges(self, args):
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        err = 0
        for e in self.controlflow_edges:
            for k in (self.K_STATE,):
                      #self.K_START_TIME_SCHEDULED, self.K_END_TIME_SCHDULED,
                      #self.K_CONSUMPTION_TIME_SCHDULED, self.INACTIVE_INTERVALS):
                if k not in self.G.edges[e[0], e[1]].keys():
                    err += 1
                    fp.write("Error: {} '{}' doesn't has '{}' property.\n".format(self.K_CONTROLFLOW, str(e), k))
                    fp.flush()
                for s in e:
                    if s not in self.controller_nodes:
                        err += 1
                        fp.write(
                            "Error: {} {} has invalid storage: {}.\n".format(self.K_CONTROLFLOW, str(e), s))
                        fp.flush()
        return err

    def get_graph(self):
        return self.G

    def get_storage_nodes(self):
        return self.storage_nodes

    def get_dataflow_edges(self):
        return self.dataflow_edges

    def get_controller_nodes(self):
        return self.controller_nodes

    def get_tested(self):
        return self.tested

    def set_tested(self, tested):
        self.tested = tested

    def is_workflow_finished(self):
        task_remained = False
        for c in self.controller_nodes:
            if self.G.nodes[c][self.K_STATE] != self.K_FINISHED:
                task_remained = True
        return not task_remained

    def simulate_main(self, time, dt, args):
        self.simulator_args.clear()
        for k in args.keys():
            self.simulator_args[k] = args[k]
        if "fp" in args.keys():
            fp = args["fp"]
        else:
            fp = sys.stderr
        # start workflow
        if time == 0:
            fp.write("{} started at {}.\n".format(self.K_WORKFLOW, time))
        else:
            fp.write("{} resumed at {}.\n".format(self.K_WORKFLOW, time))
        fp.flush()
        while True:
            # collect active controllers
            active_controllers = []
            for c in self.controller_nodes:
                if self.G.nodes[c][self.K_STATE] != self.K_FINISHED:
                    active_controllers.append(c)
                    #print(active_controllers)
            # collect active dataflows
            active_dataflows = []
            for c in active_controllers:
                inactive = False
                for i in self.G.nodes[c][self.K_INACTIVE_INTERVALS]:
                    if i[0] <= time and time <= i[1]:
                        inactive = True
                        break
                if not inactive:
                    for df in self.G.nodes[c][self.K_DATAFLOWS]:
                        active_dataflows.append((df[0], df[1]))
            #print(active_dataflows)
            # drive dataflows
            for s in self.storage_nodes:
                if self.G.nodes[s][self.K_STATE] != self.K_CLOSED:
                    for t in self.G[s].keys():
                        if (s, t) in active_dataflows:
                            #print("drive dataflow", (s, t))
                            if self.G.nodes[t][self.K_STATE] != self.K_CLOSED:
                                # TODO: velocity is needed to be variable
                                velocity = self.G.edges[s, t][self.K_VELOCITY]
                                trans_coefficience = self.G.edges[s, t][self.K_TRANS_COEFFICIENCE]
                                source_amount = self.G.nodes[s][self.K_AMOUNT]
                                if 0.0 < source_amount:
                                    consumed_amount = velocity * dt
                                    if source_amount < consumed_amount:
                                        consumed_amount = source_amount
                                    generated_amount = consumed_amount * trans_coefficience
                                    self.G.nodes[s][self.K_AMOUNT] -= consumed_amount
                                    self.G.nodes[t][self.K_AMOUNT] += generated_amount
                                    self.G.nodes[t][self.K_ACCUMULATED] += generated_amount
                                    source_unit = self.G.nodes[s][self.K_UNIT]
                                    target_unit = self.G.nodes[t][self.K_UNIT]
                                    fp.write("{} {} consumed {}[{}] and generated {}[{}] at {}.\n".format(self.K_DATAFLOW, str((s,t)), consumed_amount, source_unit, generated_amount, target_unit, time+dt))
                                    fp.flush()
                                #else:
                                #    fp.write("{} {} consumed {}[{}] and generated {}[{}] at {}.\n".format(self.K_DATAFLOW, str((s,t)), 0, source_unit, 0, target_unit, time+dt))
                                #    fp.flush()
            # check if strages closed
            for s in self.storage_nodes:
                if self.G.nodes[s][self.K_STATE] != self.K_CLOSED:
                    if self.G.nodes[s][self.K_INBOUNDS] == self.G.nodes[s][self.K_CLOSED_INBOUNDS]:
                        if self.G.nodes[s][self.K_AMOUNT] == 0.0:
                            self.G.nodes[s][self.K_STATE] = self.K_CLOSED
                            fp.write("{} {} closed at {}.\n".format(self.K_STORAGE, s, time+dt))
                            fp.flush()
            # close dataflow sources
            for df in active_dataflows:
                if self.G.nodes[df[0]][self.K_STATE] != self.K_CLOSED:
                    if self.G.nodes[df[0]][self.K_INBOUNDS] == self.G.nodes[df[0]][self.K_CLOSED_INBOUNDS]:
                        if self.G.nodes[df[0]][self.K_AMOUNT] == 0.0:
                            self.G.nodes[df[0]][self.K_STATE] = self.K_CLOSED
            # close dataflow targets
            for df in active_dataflows:
                if self.G.nodes[df[0]][self.K_STATE] == self.K_CLOSED:
                    self.G.nodes[df[1]][self.K_CLOSED_INBOUNDS] += 1
            # check if controllers finished
            for c in self.controller_nodes:
                inactive = False
                if self.G.nodes[c][self.K_STATE] != self.K_FINISHED:
                    for df in self.G.nodes[c][self.K_DATAFLOWS]:
                        if self.G.nodes[df[0]][self.K_STATE] == self.K_CLOSED:
                            self.G.nodes[c][self.K_STATE] = self.K_FINISHED
                            fp.write("{} {} finished at {}.\n".format(self.K_CONTROLLER, c, time+dt))
                            fp.flush()
            # make progress
            time += dt
            self.process_progress(fp, time)
            workflow_finished = self.is_workflow_finished()
            if workflow_finished:
                fp.write("{} {} finished at {}.\n".format(self.K_WORKFLOW, self.G.graph[self.K_NAME], time))
                fp.flush()
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
        graph = self.simulator.get_graph()
        #rng = RandomGenerator(simulator_args["dt"],
        #                      RandomGenerator.K_RANDOM_TIME_MAX)
        # run simulation
        if once:
            self.simulator.restore(graph)
            self.simulator.simulate(simulator_args)
            return False
        else:
            for i in range(0, simulator_args["i"]):
                self.simulator.restore(graph)
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
