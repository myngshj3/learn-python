

import sys
import traceback
import re


def delete_comments(target_text):
    target_text = re.sub(r"//.*(\n|$)", "", target_text, re.M)
    while True:
        m = re.search(r"/\*", target_text, re.M)
        if m is None:
            break
        else:
            comment_start = m.start()
            m = re.search(r"\*/", target_text[comment_start+2:])
            if m is None:
                print("Something wrong!")
                break
            else:
                comment_end = comment_start + 2 + m.end()
                if comment_start == 0:
                    target_text = target_text[comment_end:]
                else:
                    target_text = target_text[:comment_start-1] + target_text[comment_end:]
    return target_text


def find_decls(text):
    decls = []
    tmp_text = text
    while True:
        m = re.search(r"(private|public|protected)\s+((static)\s+|)((\w|[^\x00-\x7F])+\.)*(\w|[^\x00-\x7F])+\s+((\w|[^\x00-\x7F])*[^\x00-\x7F]+(\w|[^\x00-\x7F])*)(\s*\()", tmp_text, re.M)
        if m is None:
            break
        decl_start = m.start()
        decl_end = m.end()
        if m.group(7) not in decls:
            decls.append(m.group(7))
        tmp_text = tmp_text[decl_end:]
    return decls


def find_calls(text):
    calls = []
    tmp_text = text
    while True:
        m = re.search(r"[\.\s\(,;]((\w|[^\x00-\x7F])*[^\x00-\x7F]+(\w|[^\x00-\x7F])*)(\s*\()", tmp_text, re.M)
        if m is None:
            break
        call_start = m.start()
        call_end = m.end()
        if m.group(1) not in calls:
            calls.append(m.group(1))
        tmp_text = tmp_text[call_end:]
    return calls



def read_target_file(target_file):
    with open(target_file, "r", encoding="utf8") as f:
        target_text = f.read()
        return target_text

def read_file_entries(fp):
    entries = []
    while True:
        line = fp.readline()
        if line is None or len(line) == 0:
            break
        else:
            entries.append(line.strip())
    return entries


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage:")
        print("python extract_functions.py {output-rule-file} [{java-file-list-file}]")
    else:
        output_rule_file = sys.argv[1]
        if len(sys.argv) == 2:
            file_entries = read_file_entries(sys.stdin)
        else:
            with open(sys.argv[2], "r") as f:
                file_entries = read_file_entries(f)
        with open(output_rule_file, "w", encoding="utf8") as f:
            fno = 0
            for file in file_entries:
                sys.stdout.write("Start processing " + file + " ... ")
                fno += 1
                target_text = read_target_file(file)
                sys.stdout.write("loaded ... ")
                target_text = delete_comments(target_text)
                decls = find_decls(target_text)
                calls = find_calls(target_text)
                sys.stdout.write("symbols extracted ... ")
                decls.sort(key=len, reverse=True)
                calls.sort(key=len, reverse=True)
                mno = 0
                for d in decls:
                    mno += 1
                    f.write("D\t{}\t{}\t{}\n".format(file, "_____F{}D{}_____".format(fno,mno),d))
                for c in calls:
                    mno += 1
                    f.write("C\t{}\t{}\t{}\n".format(file, "_____F{}C{}_____".format(fno,mno),c))
                sys.stdout.write("done.\n")

