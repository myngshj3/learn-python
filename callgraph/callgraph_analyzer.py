
import json
import networkx as nx
import re
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
            f.write("{}{}{}{}{}\n".format(e[0], json.dumps(dg.nodes[e[0]]), delim, e[1], json.dumps(dg.nodes[e[1]])))
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
            if e is None or type(e) is not list or len(e) != 2:
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


def add_edge(dg, edge):
    n = []
    a = []
    for _n in edge:
        _n, _na = split_node(_n)
        n.append(_n)
        a.append(_na)
    if dg.has_edge(n[0], n[1]):
        dg.remove_edge(n[0], n[1])
    dg.add_edge(n[0], n[1])
    for _n, _a in zip(n, a):
        dg.nodes[_n].clear()
        for k in _a.keys():
            dg.nodes[_n][k] = _a[k]


def do_add_edge_from_file(dg, file, delim):
    with open(file, "r", encoding="utf8") as f:
        n = 0
        while True:
            line = f.readline()
            if line is None or len(line) == 0:
                break
            line = line.strip()
            e = line.split(delim)
            if e is None or type(e) is not list or len(e) != 2:
                sys.stderr.write("Error: wrong edge data:{}\n".format(line))
                sys.stderr.flush()
            else:
                n += 1
                add_edge(dg, e)
                if n % 1000 == 0:
                    sys.stderr.write("{}..".format(n))
                    sys.stderr.flush()
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
    if "a" in args.keys():
        attr_needed = True
    else:
        attr_needed = False
    if "r" in args.keys():
        rev = True
    else:
        rev = False
    if "d" in args.keys():
        delim = args["d"]
    else:
        delim = "\t"
    if "s" in args.keys():
        sl.append(args["s"])
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
    if "t" in args.keys():
        tl.append(args["t"])
    if "f" in args.keys():
        with open(args["f"], "w", encoding="utf8") as f:
            for s in sl:
                for t in tl:
                    if s in dg.nodes and t in dg.nodes:
                        for p in nx.all_simple_paths(dg, source=s, target=t):
                            if len(p) < 2:
                                continue
                            if rev:
                                p = reversed(p)
                            if attr_needed:
                                p = [_ + json.dumps(dg.nodes[_]) for _ in p]
                            f.write("{}\n".format(delim.join(p)))
                    else:
                        sys.stderr.write("Error: node doesn't exist: {} or {}\n".format(s,t))
    else:
        for s in sl:
            for t in tl:
                if s in dg.nodes and t in dg.nodes:
                    for p in nx.all_simple_paths(dg, source=s, target=t):
                        if len(p) < 2:
                            continue
                        if rev:
                            p = reversed(p)
                        if attr_needed:
                            p = [_ + json.dumps(dg.nodes[_]) for _ in p]
                        sys.stdout.write("{}\n".format(delim.join(p)))
                else:
                    sys.stderr.write("Error: node doesn't exist: {} or {}\n".format(s,t))
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


def do_quit(dg, args:dict):
    return True


commands = {
    "grep-node": do_grep_node,
    "grep_node": do_grep_node,
    "grepnode": do_grep_node,
    "grep-edge": do_grep_edge,
    "grep_edge": do_grep_edge,
    "grepedge": do_grep_edge,
    "dump": do_dump,
    "remove-edge": do_remove_edge,
    "remove_edge": do_remove_edge,
    "removeedge": do_remove_edge,
    "add-edge": do_add_edge,
    "add_edge": do_add_edge,
    "addedge": do_add_edge,
    "callgraph": do_callgraph,
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
                    if do_command(cmd, dg, arg_map):
                        break
            else:
                sys.stderr.write("Error: command not found:{}\n".format(cmd))

