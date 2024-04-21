
import json
import re
import sys
import traceback


def output_class(cgmap, clazz):
    with open(clazz + ".c", "w", encoding="utf8") as c:
        c.write("#include <common.h>\n")
        sys.stderr.write("#include <common.h>\n")
        for m in cgmap[clazz].keys():
            c.write("void {}___dot___{}(){}\n".format(clazz, m, "{"))
            sys.stderr.write("void {}___dot___{}(){}\n".format(clazz, m, "{"))
            for s in cgmap[clazz][m]:
                c.write("  {}___dot___{}();\n".format(s[0],s[1]))
                sys.stderr.write("  {}___dot___{}();\n".format(s[0],s[1]))
            c.write("}\n")
            sys.stderr.write("}\n")
        c.flush()

        
def output_headers(cgmap):
    with open("common.h", "w", encoding="utf8") as h:
        for clazz in cgmap.keys():
            for m in cgmap[clazz].keys():
                h.write("void {}___dot___{}();\n".format(clazz,m))
        h.flush()
   
        
def get_cgedges(fp):
    cgedges = []
    while True:
        line = fp.readline()
        if line is None or len(line) == 0:
            break
        cgedges.append(line.strip())
    return cgedges
        
        

if __name__ == "__main__":
    cgedges = []
    if len(sys.argv)==1:
        for e in get_cgedges(sys.stdin):
            if e not in cgedges:
                cgedges.append(e)
    else:
        for file in sys.argv[1:]:
            with open(file, "r", encoding="utf8") as f:
                for e in get_cgedges(f):
                    if e not in cgedges:
                        cgedges.append(e)
    cgmap = {}
    pattern = re.compile(r"(\w+)::(\w+)\(\)\-\>(\w+)::(\w+)\(\)")
    for e in cgedges:
        m = pattern.search(e)
        if m is not None:
            caller_class = m.group(1)
            caller_method= m.group(2)
            callee_class = m.group(3)
            callee_method= m.group(4)
            if caller_class not in cgmap.keys():
                cgmap[caller_class] = {}
            if caller_method not in cgmap[caller_class].keys():
                cgmap[caller_class][caller_method] = []
            cgmap[caller_class][caller_method].append(
                [callee_class, callee_method])
            sys.stderr.write("{}::{}()->{}::{}()\n".format(
                caller_class, caller_method, callee_class, callee_method))
            if callee_class not in cgmap.keys():
                cgmap[callee_class] = {}
            if callee_method not in cgmap[callee_class].keys():
                cgmap[callee_class][callee_method] = []
        else:
            sys.stderr.write("Something wrong!")
            sys.stderr.flush()

    for clazz in cgmap.keys():
        output_class(cgmap, clazz)

    output_headers(cgmap);

    #print(json.dumps(cgmap, indent=2))
