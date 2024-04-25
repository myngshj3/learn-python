
import networkx as nx
import re
import sys
import traceback


def do_dump_to_file(dg, file):
    with open(file, "w", encoding="utf8") as f:
        sys.stderr.write("dump to {}..".format(file))
        n = 0
        for e in dg.edges:
            n += 1
            f.write("{}\t{}\n".format(e[0], e[1]))
            if n % 1000 == 0:
                sys.stderr.write("{}..".format(n))
        sys.stderr.write("{} edges dumped\n".format(n))


def do_dump(dg, args:dict):
    if "f" in args.keys():
        file = args["f"]
        do_dump_to_file(dg, file)
    pass


def do_remove_edge_from_file(dg, file):
    with open(file, "r", encoding="utf8") as f:
        while True:
            line = f.readline()
            if line is None or len(line) == 0:
                break
            line = line.strip()
            e = line.split("\t")
            if e is None or type(e) is not list or len(e) != 2:
                sys.stderr.write("Error: wrong edge data:{}\n", line)
            else:
                if dg.has_edge(e[0], e[1]):
                    dg.remove_edge(e[0], e[1])


def do_remove_edge(dg, args:dict):
    if "f" in args.keys():
        file = args["f"]
        do_remove_edge_from_file(dg, file)
    pass


def do_add_edge_from_file(dg, file):
    with open(file, "r", encoding="utf8") as f:
        n = 0
        while True:
            line = f.readline()
            if line is None or len(line) == 0:
                break
            line = line.strip()
            e = line.split("\t")
            if e is None or type(e) is not list or len(e) != 2:
                sys.stderr.write("Error: wrong edge data:{}\n".format(line))
            else:
                if dg.has_edge(e[0], e[1]):
                    dg.remove_edge(e[0], e[1])
                n += 1
                dg.add_edge(e[0], e[1])
                if n % 1000 == 0:
                    sys.stderr.write("{}..".format(n))
        sys.stderr.write("{} edges added\n".format(n))
                

def do_add_edge(dg, args:dict):
    if "f" in args.keys():
        file = args["f"]
        do_add_edge_from_file(dg, file)
    pass


def do_callgraph(dg, args:dict):
    s = None
    t = None
    if "s" in args.keys():
        s = args["s"]
    if "t" in args.keys():
        t = args["t"]
    if s is None:
        sys.stderr.write("Error: source node not specified\n")
    if t is None:
        sys.stderr.write("Error: target node not specified\n")
    if s in dg.nodes and t in dg.nodes:
        if "f" in args.keys():
            with open(args["f"], "w", encoding="utf8") as f:
                for p in nx.all_simple_paths(dg, s, t):
                    f.write("{}\n".format("\t".join(p)))
        else:
            for p in nx.all_simple_paths(dg, s, t):
                sys.stdout.write("{}\n".format("\t".join(p)))
    else:
        sys.stderr.write("Error: node doesn't exist: {} or {}\n".format(s,t))


def do_quit(dg, args:dict):
    exit(0)


commands = {
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
            commands[cmd](dg, args)
        else:
            sys.stderr.write("{}: command not found\n".format(cmd))
    except:
        sys.stderr.write(traceback.format_exc())


def parse_args(args):
    try:
        fin_pattern = re.compile(r"^\s*$")
        option_without_param = re.compile(r"^\-{1,2}([\w\d][\w\d\-]*)(\s+|$)")
        option_with_param    = re.compile(r"^\-{1,2}([\w\d][\w\d\-]*)=([\w\d\-\.:]*)(\s+|$)")
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
                value = m.group(2)
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
    try:
        m = cmd_pattern.search(args)
        if m is None:
            return True, None, None # invalid command
        whole = m.group(0)
        cmd = m.group(1)
        print("Command:{}:".format(cmd))
        return False, cmd, args[len(whole):]
    except:
        return False, None , None # error


if __name__ == "__main__":
    dg = nx.DiGraph()
    for file in sys.argv[1:]:
        do_command("add-edge", dg, {"f":file, "ow":True})
    while True:
        user_input = input("$>")
        user_input = user_input.strip()
        err, cmd, args = get_cmd(user_input)
        if err:
            sys.stderr.write("Invalid command line:{}\n".format(user_input))
        else:
            print("cmd/{}/".format(cmd))
            if cmd is None or len(cmd) == 0:
                pass
            else:
                arg_map = parse_args(args)
                if arg_map is None:
                    sys.stderr.write("argument error:{}\n".format(args))
                else:
                    do_command(cmd, dg, arg_map)

