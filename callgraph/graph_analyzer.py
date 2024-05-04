
import json
import networkx as nx
import re
from basic_workflow_simulator import BasicWorkflowSimulator, BasicWorkflowSimulatorController
#from workflow_time_simulator import WorkflowTimeSimulator, WorkflowTimeSimulatorController
import sys
import traceback


node_pattern = re.compile(r"^([^\{\}]+)({.*\})$")
def split_node(edge):
    m = node_pattern.search(edge)
    if m is None:
        return edge, {}
    else:
        return m.group(1), json.loads(m.group(2))


def do_dump_to_file(dg, f, delim, attr_needed):
    #sys.stderr.write("dump to {}..".format(file))
    n = 0
    for e in dg.edges:
        n += 1
        if attr_needed:
            f.write("{}{}{}{}{}{}{}\n".format(e[0], json.dumps(dg.nodes[e[0]]), delim, e[1], json.dumps(dg.nodes[e[1]]),
                                              delim, json.dumps(dg.edges[e[0],e[1]])))
        else:
            f.write("{}{}{}\n".format(e[0], delim, e[1]))
        #if n % 1000 == 0:
        #    sys.stderr.write("{}..".format(n))
    #sys.stderr.write("{} edges dumped\n".format(n))
    return False


def do_dump(dg, args:dict):
    if "d" in args.keys():
        delim = args["d"]
    else:
        delim = "\t"
    if "a" in args.keys():
        attr_needed = True
    else:
        attr_needed = False
    if "f" in args.keys():
        with open(args["f"], "w", encoding="utf8") as f:
            do_dump_to_file(dg, f, delim, attr_needed)
    else:
        do_dump_to_file(dg, sys.stdout, delim, attr_needed)
    return False


def do_remove_edge_from_file(dg, file, delim):
    with open(file, "r", encoding="utf8") as f:
        while True:
            line = f.readline()
            if line is None or len(line) == 0:
                break
            line = line.strip()
            e = line.split(delim)
            if e is None or type(e) is not list or len(e) not in (2, 3):
                sys.stderr.write("Error: wrong edge data:{}\n", line)
            else:
                s, sa = split_node(e[0])
                t, ta = split_node(e[1])
                if dg.has_edge(s, t):
                    dg.remove_edge(s, t)
    return False


def do_remove_edge(dg, args:dict):
    if "d" in args.keys():
        delim = args["d"]
    else:
        delim = "\t"
    if "f" in args.keys():
        file = args["f"]
        do_remove_edge_from_file(dg, file, delim)
    sl = []
    tl = []
    if "s" in args.keys():
        sl.append(args["s"])
    if "t" in args.keys():
        tl.append(args["t"])
    if "sf" in args.keys():
        with open(args["sf"], "r", encoding="utf8") as f:
            while True:
                line = f.readline()
                if line is None or len(line) == 0:
                    break
                line = line.strip()
                sl.append(line)
    if "tf" in args.keys():
        with open(args["tf"], "r", encoding="utf8") as f:
            while True:
                line = f.readline()
                if line is None or len(line) == 0:
                    break
                line = line.strip()
                tl.append(line)
    for s in sl:
        s, sa = split_node(s)
        for t in tl:
            t, ta = split_node(t)
            if dg.has_edge(s, t):
                dg.remove_edge(s, t)
    return False


def add_edge(dg, edge, att):
    n = []
    a = []
    for _n in edge[0:2]:
        _n, _na = split_node(_n)
        n.append(_n)
        a.append(_na)
    if dg.has_edge(n[0], n[1]):
        dg.remove_edge(n[0], n[1])
    if n[0] == n[1]:
        return False
    dg.add_edge(n[0], n[1])
    for k in att.keys():
        dg.edges[n[0], n[1]][k] = att[k]
    for _n, _a in zip(n, a):
        dg.nodes[_n].clear()
        for k in _a.keys():
            dg.nodes[_n][k] = _a[k]
    return True


def do_add_edge_from_file(dg, file, delim):
    with open(file, "r", encoding="utf8") as f:
        n = 0
        while True:
            line = f.readline()
            if line is None or len(line) == 0:
                break
            line = line.strip()
            e = line.split(delim)
            if e is None or type(e) is not list or len(e) not in (2, 3):
                sys.stderr.write("Error: wrong edge data:{}\n".format(line))
                sys.stderr.flush()
            else:
                if len(e) == 2:
                    att = {}
                else:
                    att = json.loads(e[2])
                if add_edge(dg, e, att):
                    n += 1
                    if n % 1000 == 0:
                        sys.stderr.write("{}..".format(n))
                        sys.stderr.flush()
                else:
                    pass
        sys.stderr.write("{} edges added\n".format(n))
        sys.stderr.flush()
    return False


def do_add_edge(dg, args:dict):
    if "d" in args.keys():
        delim = args["d"]
    else:
        delim = "\t"
    if "f" in args.keys():
        file = args["f"]
        do_add_edge_from_file(dg, file, delim)
    sl = []
    if "s" in args.keys():
        s, sa = split_node(args["s"])
        sl.append([s, sa])
    if "sf" in args.keys():
        with open(args["sf"], "r", encoding="utf8") as f:
            while True:
                line = f.readline()
                if line is None or len(line) == 0:
                    break
                line = line.strip()
                sl.append(line)
    tl = []
    if "t" in args.keys():
        t, ta = split_node(args["t"])
        tl.append([t, ta])
    if "tf" in args.keys():
        with open(args["tf"], "r", encoding="utf8") as f:
            while True:
                line = f.readline()
                if line is None or len(line) == 0:
                    break
                line = line.strip()
                tl.append(line)
    for s in sl:
        for t in tl:
            add_edge(dg, [s, t])
    return False


def do_callgraph(dg, args:dict):
    sl = []
    tl = []
    if "r" in args.keys():
        dg = dg.reverse(copy=True)
    if "a" in args.keys():
        attr_needed = True
    else:
        attr_needed = False
    if "r" in args.keys():
        dg = dg.reverse(copy=True)
    if "rp" in args.keys():
        rp = True
    else:
        rp = False
    if "d" in args.keys():
        delim = args["d"]
    else:
        delim = "\t"
    if "sf" in args.keys():
        with open(args["sf"], "r", encoding="utf8") as f:
            while True:
                line = f.readline()
                if line is None or len(line) == 0:
                    break
                line = line.strip()
                if line in dg.nodes:
                    sl.append(line)
    if "s" in args.keys():
        if args["s"] in dg.nodes and args["s"] not in sl:
            sl.append(args["s"])
    if "tf" in args.keys():
        with open(args["tf"], "r", encoding="utf8") as f:
            while True:
                line = f.readline()
                if line is None or len(line) == 0:
                    break
                line = line.strip()
                if line in dg.nodes:
                    tl.append(line)
    if "t" in args.keys():
        if args["t"] in dg.nodes and args["t"] not in tl:
            tl.append(args["t"])
    if "f" in args.keys():
        with open(args["f"], "w", encoding="utf8") as f:
            i = 0
            for s in sl:
                for t in tl:
                    for p in nx.all_simple_paths(dg, source=s, target=t):
                        i += 1
                        if i % 1000 == 0:
                            sys.stderr.write("{}..".format(i))
                            sys.stderr.flush()
                        if len(p) < 2:
                            continue
                        if rp:
                            p = reversed(p)
                        if attr_needed:
                            p = [_ + json.dumps(dg.nodes[_]) for _ in p]
                        f.write("{}\n".format(delim.join(p)))
                        f.flush()
            sys.stderr.write("{} done\n".format(i))
            sys.stderr.flush()
    else:
        i = 0
        for s in sl:
            for t in tl:
                for p in nx.all_simple_paths(dg, source=s, target=t):
                    i += 1
                    if i % 1000 == 0:
                        sys.stderr.write("{}..".format(i))
                        sys.stderr.flush()
                    if len(p) < 2:
                        continue
                    if rp:
                        p = reversed(p)
                    if attr_needed:
                        p = [_ + json.dumps(dg.nodes[_]) for _ in p]
                    sys.stdout.write("{}\n".format(delim.join(p)))
                    sys.stdout.flush()
        sys.stderr.write("{} done\n".format(i))
        sys.stderr.flush()
    return False


def walker_evaluate(__G__, __e__, __a__):
    __s__ = __e__
    for _ in sorted([_ for _ in __a__.keys()], key=len, reverse=True):
        __s__ = __s__.replace(_, str(__a__[_]))
    return eval(__s__)


def walker_action(G, args):
    fp = args["fp"]
    if "ld" in args.keys():
        ld = args["ld"]
    else:
        ld = 2
    if "hd" in args.keys():
        hd = args["hd"]
    else:
        hd = None
    if "d" in args.keys():
        d = args["d"]
    else:
        d = "\t"
    bp = args["bp"]
    if "rtl" in args.keys():
        rtl = args["rtl"]
    else:
        rtl = None
    if "rp" in args.keys():
        rp = True
    else:
        rp = False
    if "e" in args.keys():
        e = args["e"]
    else:
        e = None

    if len(bp) < ld or (hd is not None and hd < len(bp)):
        dump_needed = False
    elif rtl is None:
        dump_needed = True
    elif bp[len(bp)-1] in rtl:
        dump_needed = True
    else:
        dump_needed = False
    if e is not None:
        try:
            a = {}
            for prop in e["props"].keys():
                a[prop] = sum([G.nodes[_][prop] for _ in bp])
                if len(bp) > 1:
                    a[prop] += sum([G.edges[bp[i],bp[i+1]][prop] for i in range(0, len(bp)-1)])
            if not walker_evaluate(G, e["condition"], a):
                dump_needed = False
        except Exception as e:
            sys.stderr.write("Error: during evaluating condition for path: {}\n".format(bp))
            dump_needed = False

    if dump_needed:
        if "a" in args.keys():
            bp = [_ + json.dumps(G.nodes[_]) for _ in bp]
        if rp:
            bp = reversed(bp)
        fp.write(d.join(bp) + "\n")
        fp.flush()
        return True
    else:
        return False


def walk_naive(G, bpl, action, action_args):
    if "rtl" in action_args.keys():
        rtl = action_args["rtl"]
    else:
        rtl = None
    if "ld" in action_args.keys():
        ld = action_args["ld"]
    else:
        ld = 2
    if "hd" in action_args.keys():
        hd = action_args["hd"]
    else:
        hd = None
    if "e" in action_args.keys():
        equation = action_args["e"]
    else:
        equation = None
    
    for bp in bpl:
        action_args["bp"] = bp
        action(G, action_args)
        if hd is None or len(bp) < hd:
            tl = [_ for _ in G[bp[len(bp)-1]].keys()]
        else:
            tl = []
        w = []
        for t in tl:
            if (hd is None or len(bp) < hd) and t not in bp:
                p = [_ for _ in bp]
                if equation is None:
                    p.append(t)
                    w.append(p)
                else:
                    try:
                        a = {}
                        for prop in equation["props"].keys():
                            a[prop] = sum([G.nodes[_][prop] for _ in p])
                            if len(p) > 1:
                                a[prop] += sum([G.edges[p[i],p[i+1]][prop] for i in range(0, len(p)-1)])
                        #if walker_evaluate(G, equation["condition"], a):
                        p.append(t)
                        w.append(p)
                    except Exception as ex:
                        sys.stderr.write("Error: during evaluating condition for path: {}\n".format(p));
                        sys.stderr.write(traceback.format_exc())
                        sys.stderr.flush()
        walk_naive(G, w, action, action_args)


def do_walk_naive(dg, args:dict):
    sl = []
    walker_args = {}
    if "ld" in args.keys():
        walker_args["ld"] = int(args["ld"])
    else:
        walker_args["ld"] = 2
    if "hd" in args.keys():
        walker_args["hd"] = int(args["hd"])
    else:
        walker_args["hd"] = None
    if "d" in args.keys():
        walker_args["d"] = args["d"]
    else:
        walker_args["d"] = "\t"
    if "w" in args.keys():
        walker_args["w"] = True
    else:
        walker_args["w"] = False
    if "a" in args.keys():
        walker_args["a"] = args["a"]
    if "rp" in args.keys():
        walker_args["rp"] = args["rp"]
    if "e" in args.keys():
        p = re.compile(r"^([^:]+):(.+)$")
        m = p.search(args["e"])
        if m is None:
            sys.stderr.write("Invalid option value for -e:{}".format(args["e"]))
        else:
            att = {"props":{},"condition":m.group(2)}
            for prop in m.group(1).split(","):
                att["props"][prop] = 0
            walker_args["e"] = att
    if "r" in args.keys():
        dg = dg.reverse(copy=True)
    if "sf" in args.keys():
        with open(args["sf"], "r", encoding="utf8") as f:
            while True:
                n = f.readline()
                if n is None or len(n) == 0:
                    break
                n = n.strip()
                if n not in sl and n in dg.nodes:
                    sl.append(n)
    if "s" in args.keys():
        s = args["s"]
        if s not in sl and s in dg.nodes:
            sl.append(s)
    rtl = None
    if "tf" in args.keys():
        rtl = []
        with open(args["tf"], "r", encoding="utf8") as f:
            while True:
                n = f.readline()
                if n is None or len(n) == 0:
                    break
                n = n.strip()
                if n not in rtl and n in dg.nodes:
                    rtl.append(n)
    if "t" in args.keys():
        if rtl is None:
            rtl = []
        if args["t"] not in rtl and args["t"] in dg.nodes:
            rtl.append(args["t"])
    walker_args["rtl"] = rtl
    bpl = []
    for s in sl:
        bpl.append([s])
    if "f" in args.keys():
        with open(args["f"], "w", encoding="utf8") as fp:
            walker_args["fp"] = fp
            walk_naive(dg, bpl, walker_action, walker_args)
            return False
    else:
        walker_args["fp"] = sys.stdout
        walk_naive(dg, bpl, walker_action, walker_args)
        return False


def do_grep_node(dg, args:dict):
    if "f" in args.keys():
        with open(args["f"], "w", encoding="utf8") as f:
            if "n" in args.keys():
                p = re.compile(args["n"])
                for n in dg.nodes:
                    if p.search(n) is not None:
                        f.write("{}\n".format(n))
    else:
        if "n" in args.keys():
            p = re.compile(args["n"])
            for n in dg.nodes:
                if p.search(n) is not None:
                    sys.stdout.write("{}\n".format(n))
    return False


def do_grep_edge(dg, args:dict):
    if "s" in args.keys():
        sp = re.compile(args["s"])
    else:
        sp = re.compile(r".")
    if "t" in args.keys():
        tp = re.compile(args["t"])
    else:
        tp = re.compile(r".")
    if "d" in args.keys():
        delim = args["d"]
    else:
        delim = "\t"
    if "f" in args.keys():
        with open(args["f"], "w", encoding="utf8") as f:
            for e in dg.edges:
                if sp.search(e[0]) is not None and tp.search(e[1]) is not None:
                    f.write("{}{}{}\n".format(e[0], delim, e[1]))
    else:
        for e in dg.edges:
            if sp.search(e[0]) is not None and tp.search(e[1]) is not None:
                sys.stdout.write("{}{}{}\n".format(e[0], delim, e[1]))
    return False


def simulate_workflow(dg, args:dict):
    return simulate_simple_workflow(dg, args)


def simulate_simple_workflow(dg, args:dict):
    rG = dg.reverse(copy=True)
    G = rG.reverse(copy=True)
    if "dt" in args.keys():
        dt = float(args["dt"])
    else:
        dt = 0.1
    err = 0
    for n in G.nodes:
        if "consumption_time" not in G.nodes[n].keys():
            err += 1
            sys.stderr.write("Error: node {} doesn't has 'consumption_time' property".format(n))
            sys.stderr.flush()
        else:
            try:
                _ = float(G.nodes[n]["consumption_time"])
                if _ <= 0:
                    err += 1
                    sys.stderr.write("Error: node {} has negative 'consumption_time' property:{}".format(n, _))
                    sys.stderr.flush()
            except:
                err += 1
                sys.stderr.write("Error: node {} has invalid 'consumption_time' property".format(n))
                sys.stderr.flush()
    for e in G.edges:
        if "consumption_time" not in G.edges[e[0],e[1]].keys():
            err += 1
            sys.stderr.write("Error: edge ({},{}) doesn't has 'consumption_time' property".format(e[0],e[1]))
            sys.stderr.flush()
        else:
            try:
                _ = float(G.edges[e[0],e[1]]["consumption_time"])
                if _ <= 0:
                    err += 1
                    sys.stderr.write("Error: edge ({},{}) has negative 'consumption_time' property:{}".format(e[0],e[1], _))
                    sys.stderr.flush()
            except:
                err += 1
                sys.stderr.write("Error: edge ({},{}) has invalid 'consumption_time' property".format(e[0],e[1]))
                sys.stderr.flush()
    if err != 0:
        sys.stderr.write("Error: {} problem(s) found\n".format(err))
        return False

    nodeid_list = [_  for _ in G.nodes]
    nodeatt_list = [None for _ in G.nodes]
    edge_matrix = []
    for _ in range(0, len(nodeid_list)):
        edge_matrix.append([None for _ in range(0, len(nodeid_list))])
    for i,n in zip(range(0, len(nodeid_list)), nodeid_list):
        nodeatt_list[i] = {
            "forks": len(G[n].keys()),
            "forked": 0,
            "joins": len(rG[n].keys()),
            "joined": 0,
            "completed": False,
            "consumption_time": G.nodes[n]["consumption_time"],
            "consumed_time": 0,
            "start_time": None,
            "end_time": None,
        }
    for i,n in zip(range(0, len(nodeid_list)), nodeid_list):
        for j,m in zip(range(0, len(nodeid_list)), nodeid_list):
            if G.has_edge(n, m):
                edge_matrix[i][j] = {
                    "completed": False,
                    "consumption_time": G.edges[n,m]["consumption_time"],
                    "consumed_time": 0,
                    "start_time": None,
                    "end_time": None,
                }
    rG = None
    time = 0
    edges_to_start = []
    while True:
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            if nodeatt_list[i]["joined"] == nodeatt_list[i]["joins"]:
                if nodeatt_list[i]["start_time"] is None:
                    nodeatt_list[i]["start_time"] = time
                    nodeatt_list[i]["consumed_time"] = 0
        edges_to_start_next_time = []
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            if nodeatt_list[i]["start_time"] is not None and not nodeatt_list[i]["completed"]:
                nodeatt_list[i]["consumed_time"] += dt
                if nodeatt_list[i]["consumed_time"] >= nodeatt_list[i]["consumption_time"]:
                    nodeatt_list[i]["end_time"] = time + dt
                    nodeatt_list[i]["completed"] = True
                    for t in G[n].keys():
                        edges_to_start_next_time.append((i, nodeid_list.index(t)))
                    sys.stderr.write("Time {}: node {} completed\n".format(time+dt,n))
                    sys.stderr.flush()
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            for j,m in zip(range(0, len(nodeatt_list)), nodeid_list):
                if (i,j) in edges_to_start:
                    if edge_matrix[i][j]["start_time"] is None:
                        edge_matrix[i][j]["start_time"] = time
                        edge_matrix[i][j]["consumed_time"] = 0
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            for j,m in zip(range(0, len(nodeatt_list)), nodeid_list):
                if edge_matrix[i][j] is not None:
                    if edge_matrix[i][j]["start_time"] is not None and not edge_matrix[i][j]["completed"]:
                        edge_matrix[i][j]["consumed_time"] += dt
                        if edge_matrix[i][j]["consumed_time"] >= edge_matrix[i][j]["consumption_time"]:
                            edge_matrix[i][j]["end_time"] = time + dt
                            edge_matrix[i][j]["completed"] = True
                            nodeatt_list[j]["joined"] += 1
                            sys.stderr.write("Time {}: edge ({},{}) completed\n".format(time+dt,n,m))
                            sys.stderr.flush()
        edges_to_start = edges_to_start_next_time
        time += dt
        if time % 10 == 0:
            sys.stderr.write("{} passed..".format(time))
        task_remained = False
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            if nodeatt_list[i] is not None and not nodeatt_list[i]["completed"]:
                task_remained = True
                break
        if not task_remained:
            for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
                for j,m in zip(range(0, len(nodeatt_list)), nodeid_list):
                    if edge_matrix[i][j] is not None and not edge_matrix[i][j]["completed"]:
                        task_remained = True
                        break
                if task_remained:
                    break
        if not task_remained:
            break
    sys.stderr.write("Finished. Total consumption time: {}\n".format(time))
    sys.stderr.flush()
    return False


def simulate_workflow(dg, args:dict):
    rG = dg.reverse(copy=True)
    G = rG.reverse(copy=True)
    if "dt" in args.keys():
        dt = float(args["dt"])
    else:
        dt = 0.1
    err = 0
    for n in G.nodes:
        if "consumption_time" not in G.nodes[n].keys():
            err += 1
            sys.stderr.write("Error: node {} doesn't has 'consumption_time' property".format(n))
            sys.stderr.flush()
        else:
            try:
                _ = float(G.nodes[n]["consumption_time"])
                if _ <= 0:
                    err += 1
                    sys.stderr.write("Error: node {} has negative 'consumption_time' property:{}".format(n, _))
                    sys.stderr.flush()
            except:
                err += 1
                sys.stderr.write("Error: node {} has invalid 'consumption_time' property".format(n))
                sys.stderr.flush()
    for e in G.edges:
        if "consumption_time" not in G.edges[e[0],e[1]].keys():
            err += 1
            sys.stderr.write("Error: edge ({},{}) doesn't has 'consumption_time' property".format(e[0],e[1]))
            sys.stderr.flush()
        else:
            try:
                _ = float(G.edges[e[0],e[1]]["consumption_time"])
                if _ <= 0:
                    err += 1
                    sys.stderr.write("Error: edge ({},{}) has negative 'consumption_time' property:{}".format(e[0],e[1], _))
                    sys.stderr.flush()
            except:
                err += 1
                sys.stderr.write("Error: edge ({},{}) has invalid 'consumption_time' property".format(e[0],e[1]))
                sys.stderr.flush()
    if err != 0:
        sys.stderr.write("Error: {} problem(s) found\n".format(err))
        return False

    nodeid_list = [_  for _ in G.nodes]
    nodeatt_list = [None for _ in G.nodes]
    edge_matrix = []
    for _ in range(0, len(nodeid_list)):
        edge_matrix.append([None for _ in range(0, len(nodeid_list))])
    for i,n in zip(range(0, len(nodeid_list)), nodeid_list):
        nodeatt_list[i] = {
            "forks": len(G[n].keys()),
            "forked": 0,
            "joins": len(rG[n].keys()),
            "joined": 0,
            "completed": False,
            "consumption_time": G.nodes[n]["consumption_time"],
            "consumed_time": 0,
            "start_time": None,
            "end_time": None,
        }
    for i,n in zip(range(0, len(nodeid_list)), nodeid_list):
        for j,m in zip(range(0, len(nodeid_list)), nodeid_list):
            if G.has_edge(n, m):
                edge_matrix[i][j] = {
                    "completed": False,
                    "consumption_time": G.edges[n,m]["consumption_time"],
                    "consumed_time": 0,
                    "start_time": None,
                    "end_time": None,
                }
    rG = None
    time = 0
    edges_to_start = []
    while True:
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            if nodeatt_list[i]["joined"] == nodeatt_list[i]["joins"]:
                if nodeatt_list[i]["start_time"] is None:
                    nodeatt_list[i]["start_time"] = time
                    nodeatt_list[i]["consumed_time"] = 0
        edges_to_start_next_time = []
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            if nodeatt_list[i]["start_time"] is not None and not nodeatt_list[i]["completed"]:
                nodeatt_list[i]["consumed_time"] += dt
                if nodeatt_list[i]["consumed_time"] >= nodeatt_list[i]["consumption_time"]:
                    nodeatt_list[i]["end_time"] = time + dt
                    nodeatt_list[i]["completed"] = True
                    for t in G[n].keys():
                        edges_to_start_next_time.append((i, nodeid_list.index(t)))
                    sys.stderr.write("Time {}: node {} completed\n".format(time+dt,n))
                    sys.stderr.flush()
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            for j,m in zip(range(0, len(nodeatt_list)), nodeid_list):
                if (i,j) in edges_to_start:
                    if edge_matrix[i][j]["start_time"] is None:
                        edge_matrix[i][j]["start_time"] = time
                        edge_matrix[i][j]["consumed_time"] = 0
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            for j,m in zip(range(0, len(nodeatt_list)), nodeid_list):
                if edge_matrix[i][j] is not None:
                    if edge_matrix[i][j]["start_time"] is not None and not edge_matrix[i][j]["completed"]:
                        edge_matrix[i][j]["consumed_time"] += dt
                        if edge_matrix[i][j]["consumed_time"] >= edge_matrix[i][j]["consumption_time"]:
                            edge_matrix[i][j]["end_time"] = time + dt
                            edge_matrix[i][j]["completed"] = True
                            nodeatt_list[j]["joined"] += 1
                            sys.stderr.write("Time {}: edge ({},{}) completed\n".format(time+dt,n,m))
                            sys.stderr.flush()
        edges_to_start = edges_to_start_next_time
        time += dt
        if time % 10 == 0:
            sys.stderr.write("{} passed..".format(time))
        task_remained = False
        for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
            if nodeatt_list[i] is not None and not nodeatt_list[i]["completed"]:
                task_remained = True
                break
        if not task_remained:
            for i,n in zip(range(0, len(nodeatt_list)), nodeid_list):
                for j,m in zip(range(0, len(nodeatt_list)), nodeid_list):
                    if edge_matrix[i][j] is not None and not edge_matrix[i][j]["completed"]:
                        task_remained = True
                        break
                if task_remained:
                    break
        if not task_remained:
            break
    sys.stderr.write("Finished. Total consumption time: {}\n".format(time))
    sys.stderr.flush()
    return False


def do_simulate(dg, args:dict):
    simulator_args = {}
    for k in args.keys():
        simulator_args[k] = args[k]
#    return simulate_simple_workflow(dg, args)
    if "k" not in args.keys():
        k = "wf"
        #simulate_workflow(dg, args)
        #return False
    else:
        k = args["k"]
    if k in ("wf", "workflow"):
        simulatorClass = BasicWorkflowSimulator
        controllerClass = BasicWorkflowSimulatorController
    #elif k in ("time",):
    #    simulatorClass = WorkflowTimeSimulator
    #    controllerClass = WorkflowTimeSimulatorController
    else:
        sys.stderr.write("Error: no such kind simulator: {}\n", k)
        return False
    if "st" in args.keys():
        if args["st"] is None:
            once = False
        else:
            once = bool(args["st"])
    else:
        once = True
    simulator_args["st"] = not once
    if "i" not in args.keys():
        simulator_args["i"] = 100
    else:
        simulator_args["i"] = int(args["i"])
    if "dt" not in args.keys():
        simulator_args["dt"] = 0.1
    else:
        simulator_args["dt"] = float(args["dt"])
    simulator = simulatorClass(dg, simulator_args)
    controller = controllerClass(simulator, simulator_args)
    if "t" in args.keys():
        if not controller.test(simulator_args):
            return False
    if once:
        print("One time simulation")
        controller.run(simulator_args, once=True)
    else:
        print("Statistical test")
        controller.run(simulator_args, once=False)
    return False


def do_load(dg, args):
    if "f" in args.keys():
        with open(args["f"], "r") as f:
            json_data = json.load(f)
            dg.graph.clear()
            for k in json_data["graph"].keys():
                dg.graph[k] = json_data["graph"][k]
            for n in [_ for _ in dg.nodes]:
                dg.remove_node(n)
            for n in json_data["nodes"]:
                dg.add_node(n[0])
                for k in n[1].keys():
                    dg.nodes[n[0]][k] = n[1][k]
            for e in json_data["edges"]:
                dg.add_edge(e[0][0], e[0][1])
                for k in e[1].keys():
                    dg.edges[e[0][0], e[0][1]][k] = e[1][k]
    return False


def do_save(dg, args):
    json_data = {
        "graph": dg.graph,
        "nodes": [[_, dg.nodes[_]] for _ in dg.nodes],
        "edges": [[_, dg.edges[_[0],_[1]]] for _ in dg.edges],
    }
    if "f" in args.keys():
        with open(args["f"], "w") as f:
            f.write(json.dumps(json_data, indent=2))
    else:
        sys.stderr.write(json.dumps(json_data, indent=2))


def do_quit(dg, args:dict):
    return True


commands = {
    "sim": do_simulate,
    "simu": do_simulate,
    "simulate": do_simulate,
    "simulate": do_simulate,
    "walk": do_walk_naive,
    "walks": do_walk_naive,
    "grep-node": do_grep_node,
    "grep_node": do_grep_node,
    "grepnode": do_grep_node,
    "grep-edge": do_grep_edge,
    "grep_edge": do_grep_edge,
    "grepedge": do_grep_edge,
    "dump": do_dump,
    "rm-edge": do_remove_edge,
    "rm_edge": do_remove_edge,
    "rmedge": do_remove_edge,
    "rm-edges": do_remove_edge,
    "rm_edges": do_remove_edge,
    "rmedges": do_remove_edge,
    "remove-edge": do_remove_edge,
    "remove_edge": do_remove_edge,
    "removeedge": do_remove_edge,
    "remove-edges": do_remove_edge,
    "remove_edges": do_remove_edge,
    "removeedges": do_remove_edge,
    "add-edge": do_add_edge,
    "add_edge": do_add_edge,
    "addedge": do_add_edge,
    "add-edges": do_add_edge,
    "add_edges": do_add_edge,
    "addedges": do_add_edge,
    "callgraph": do_callgraph,
    "load": do_load,
    "save": do_save,
    "quit": do_quit,
    "exit": do_quit
}


def do_command(cmd:str, dg, args:dict):
    global commands
    try:
        if cmd in commands.keys():
            return commands[cmd](dg, args)
        else:
            sys.stderr.write("{}: command not found\n".format(cmd))
            return False
    except:
        sys.stderr.write(traceback.format_exc())
        return False


def parse_args(args):
    try:
        fin_pattern = re.compile(r"^\s*$")
        option_without_param = re.compile(r"^\-{1,2}([\w\d][\w\d\-]*)(\s+|$)")
        option_with_param    = re.compile(r"^\-{1,2}([\w\d][\w\d\-]*)=(([\w\d\-\.:]*)|(\"[^\"]*\"))(\s+|$)")
        arg_map = {}
        pos = 0
        while True:
            sys.stderr.flush()
            m = fin_pattern.search(args[pos:])
            if m is not None:
                return arg_map
            m = option_without_param.search(args[pos:])
            if m is not None:
                whole = m.group(0)
                arg = m.group(1)
                arg_map[arg] = None
                pos += len(whole)
                continue
            m = option_with_param.search(args[pos:])
            if m is not None:
                whole = m.group(0)
                arg = m.group(1)
                if m.group(3) is not None and len(m.group(3)) != 0:
                    value = m.group(3)
                else:
                    value = m.group(4)[1:len(m.group(4))-1]
                arg_map[arg] = value
                pos += len(whole)
                continue
            else:
                return None
    except:
        sys.stderr.write(traceback.format_exc())
        return None


def get_cmd(args):
    cmd_pattern = re.compile(r"^\s*(\w[\w\d\-]*)(\s+|$)")
    fin_pattern = re.compile(r"^\s*$")
    try:
        m = fin_pattern.search(args)
        if m is not None:
            return False, None, None
        m = cmd_pattern.search(args)
        if m is None:
            return True, None, None # invalid command
        whole = m.group(0)
        cmd = m.group(1)
        #print("Command:{}:".format(cmd))
        return False, cmd, args[len(whole):]
    except:
        return False, None , None # error


if __name__ == "__main__":
    dg = nx.DiGraph()
    for file in sys.argv[1:]:
        do_command("add-edge", dg, {"f":file, "ow":True})
    while True:
        user_input = input("$> ")
        user_input = user_input.strip()
        err, cmd, args = get_cmd(user_input)
        if err:
            sys.stderr.write("Invalid command line:{}\n".format(user_input))
        else:
            if cmd is None:
                continue
            elif cmd in commands.keys():
                arg_map = parse_args(args)
                if arg_map is None:
                    sys.stderr.write("argument error:{}\n".format(args))
                else:
                    q = do_command(cmd, dg, arg_map)
                    if q:
                        break
            else:
                sys.stderr.write("Error: command not found:{}\n".format(cmd))

