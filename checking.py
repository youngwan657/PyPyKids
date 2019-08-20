import sys, ast, os
from solution import solve
from node import Node
        
def main(argv):
    if len(argv) == 1:
        return solve(convert(argv[0]))
    elif len(argv) == 2:
        return solve(convert(argv[0]), convert(argv[1]))
    elif len(argv) == 3:
        return solve(convert(argv[0]), convert(argv[1]), convert(argv[2]))
    elif len(argv) == 4:
        return solve(convert(argv[0]), convert(argv[1]), convert(argv[2]), convert(argv[3]))

def next(nodes, i):
    if len(nodes) <= i:
        return None

    n = Node(nodes[i])
    n.next = next(nodes, i + 1)
    return n

def convert(param):
    if param.startswith("Node"):
        nodes = ast.literal_eval(param[4:])
        return next(nodes, 0)
    else:
        return ast.literal_eval(param)

if __name__ == "__main__":
    answer = main(sys.argv[1:])
    if os.path.exists("checking_answer"):
        os.remove("checking_answer")
    f = open("checking_answer", "w+")
    if type(answer) == tuple:
        for line in answer:
            f.write("%s\n" % line)
    else:
        f.write("%s" % answer)
    f.close()
