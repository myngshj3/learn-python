
import networkx as nx
import csv
import json
import sys
import re


class GraphEzShell:
    def __init__(self, node_file, edge_file):
        self.graph = nx.DiGraph()
        self.node_file = node_file
        self.edge_file = edge_file
        self.load_nodes()
        self.load_edges()

    def load_csv(self, file):
        with open(file, 'r') as f:
            reader = csv.reader(f)
            # rows = [row for row in reader]
            rows = []
            for row in reader:
                # print(row)
                rows.append(row)
            return rows

    def load_nodes(self):
        # g = nx.DiGraph()
        table = self.load_csv(self.node_file)
        for r in table:
            if len(r) < 2:
                print("node invalid column count: {}".format(r))
                continue
            node = r[0]
            attr_string = r[1]
            try:
                attrs = json.loads(attr_string)
                self.graph.add_node(node)
                for k in attrs.keys():
                    self.graph.nodes[node][k] = attrs[k]
            except Exception as ex:
                print(ex)
                print("node attribute error: {}".format(attr_string))

    def load_edges(self):
        # g = nx.DiGraph()
        table = self.load_csv(self.edge_file)
        for r in table:
            if len(r) < 4:
                print("edge invalid column count: {}".format(r))
                continue
            src = r[0]
            # edge_symbol = r[1]
            dst = r[2]
            attr_string = r[3]
            try:
                attrs = json.loads(attr_string)
                self.graph.add_edge(src, dst)
                for k in attrs.keys():
                    self.graph.edges[src, dst][k] = attrs[k]
            except Exception as ex:
                print(ex)
                print("edge attribute error: {}".format(attr_string))

    def clear(self):
        self.graph.clear()

    def parse(self, cmd):
        args = cmd.split(" ")
        if len(args) < 1:
            return
        cmd = args[0]
        args = args[1:]
        if cmd == "nodes":
            self.print_nodes(args)
        elif cmd == "edges":
            self.print_edges(args)
        elif cmd == "paths":
            self.print_paths(args)
        elif cmd == "write":
            self.write_graph(args)
        elif cmd == "render":
            self.render_graph(args)
        else:
            print("command {} not found".format(cmd))

    def match_attrs(self, pattern, attrs):
        strs = pattern.split("~=")
        if len(strs) >= 2:
            # regular expression matching
            re.compile(strs[1])
            if strs[0] in attrs.keys() and re.match(strs[1], attrs[strs[0]]):
                return True
        strs = pattern.split("=")
        if len(strs) >= 2:
            # complete matching
            if strs[0] in attrs.keys() and strs[1] == attrs[strs[0]]:
                return True
        return False

    def find_nodes(self, args):
        # print("find_nodes({})".format(args))
        nodes = []
        for node in self.graph.nodes:
            n = self.graph.nodes[node]
            unmatched = False
            for a in args:
                if not self.match_attrs(a, n):
                    unmatched = True
                    break
            if not unmatched and node not in nodes:
                nodes.append(node)
        return nodes

    def print_nodes(self, args):
        nodes = self.find_nodes(args)
        for node in nodes:
            n = self.graph.nodes[node]
            print("{}:{}".format(node, n))

    def find_edges(self, args):
        edges = []
        for edge in self.graph.edges:
            e = self.graph.edges[edge[0], edge[1]]
            unmatched = False
            for a in args:
                if not self.match_attrs(a, e):
                    unmatched = True
                    break
            if not unmatched and edge not in edges:
                edges.append(edge)
        return edges

    def print_edges(self, args):
        edges = self.find_edges(args)
        for edge in edges:
            e = self.graph.edges[edge[0], edge[1]]
            print("{}:{}".format(edge, e))

    def print_paths(self, args):
        if len(args) < 1:
            print("argument short")
            return
        nodes = args[0].split("-..->")
        source = nodes[0]
        target = nodes[1]
        sources = []
        targets = []
        if source == "*":
            sources = self.graph.nodes
        elif source[0] == "*":
            condition = source[1:]
            if condition[0] == "[" and condition[len(condition) - 1] == "]":
                condition = condition[1:len(condition) - 1]
                sources = self.find_nodes([condition])
        else:
            sources.append(source)

        if target == "*":
            targets = self.graph.nodes
        elif target[0] == "*":
            condition = target[1:]
            if condition[0] == "[" and condition[len(condition) - 1] == "]":
                condition = condition[1:len(condition) - 1]
                targets = self.find_nodes([condition])
        else:
            targets.append(target)

        for s in sources:
            for t in targets:
                paths = nx.all_simple_paths(self.graph, source=s, target=t)
                # paths = nx.all_simple_paths(self.graph, nodes[0], nodes[1])
                # print("paths:{}".format(paths))
                for path in paths:
                    # print(path)
                    symbols = ""
                    top = True
                    for node in path:
                        if not top:
                            symbols += "->"
                        else:
                            top = False
                        symbols += node
                    print(symbols)

    def write_graph(self, args):
        if len(args) < 2:
            print("too short argument count")
            return
        with open(args[0], "w") as f:
            writer = csv.writer(f)
            for node in self.graph.nodes:
                n = self.graph.nodes[node]
                writer.writerow([node, json.dumps(n)])

        with open(args[1], "w") as f:
            writer = csv.writer(f)
            for edge in self.graph.edges:
                e = self.graph.edges[edge]
                writer.writerow([edge[0], "->", edge[1], json.dumps(e)])

    def render_graph(self, args):
        pass


def main():
    node_file = ""
    edge_file = ""
    if len(sys.argv) == 1:
        node_file = "nodes.csv"
        edge_file = "edges.csv"
    elif len(sys.argv) < 3:
        print("too short argument count")
    else:
        node_file = sys.argv[1]
        edge_file = sys.argv[2]
    shell = GraphEzShell(node_file, edge_file)
    while True:
        line = sys.stdin.readline(1024)
        line = line[0:len(line)-1]
        # print(line)
        if line == "quit" or line == "exit":
            break
        try:
            shell.parse(line)
        except Exception as ex:
            print(ex)


if __name__ == "__main__":
    main()
