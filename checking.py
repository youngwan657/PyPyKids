import sys, ast, os
from solution import solve
        
def main(argv):
    if len(argv) == 1:
        return solve(ast.literal_eval(argv[0]))
    elif len(argv) == 2:
        return solve(ast.literal_eval(argv[0]), ast.literal_eval(argv[1]))
    elif len(argv) == 3:
        return solve(ast.literal_eval(argv[0]), ast.literal_eval(argv[1]), ast.literal_eval(argv[2]))

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
