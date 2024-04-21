
import sys
import traceback


def read_rule(rule_file):
    with open(rule_file, "r", encoding="utf8") as f:
        rules = []
        while True:
            line = f.readline()
            if line is not None and len(line) != 0:
                line = line.strip()
                fields = line.split("\t")
                rules.append(fields)
            else:
                return rules

def read_target_file(target_file):
    with open(target_file, "r", encoding="utf8") as f:
        target_text = f.read()
        return target_text


def write_target_file(target_file, target_text):
    with open(target_file, "w", encoding="utf8") as f:
        f.write(target_text)


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] not in ("forward", "backward"):
        print("Usage:")
        print("python replace.py forward|backward {rule-file} {replace-target-file}")
    else:
        direction = sys.argv[1]
        rule_file = sys.argv[2]
        target_file = sys.argv[3]
        rule = read_rule(rule_file)
        target_text = read_target_file(target_file)
        if direction == "forward":
            sindex = 3
            tindex = 2
        else:
            sindex = 2
            tindex = 3
        for r in rule:
            print("replaing", r[sindex], "to", r[tindex])
            target_text = target_text.replace(r[sindex], r[tindex])
        write_target_file(target_file, target_text)

