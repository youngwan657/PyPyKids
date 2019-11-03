import ast
import json
import subprocess
from datetime import datetime

import os

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render

from list.views.common import *
from django.utils.html import strip_tags


def convert_node(input):
    if input.startswith("Node"):
        nodes = ast.literal_eval(input[4:])
        ans = str(nodes[0])
        del nodes[0]
        while nodes:
            ans += " -> " + str(nodes[0])
            del nodes[0]
        return ans
    return input


def show(request, title):
    context = {}
    username = get_profile(request, context)

    answers = Answer.objects.filter(customuser__name=username)

    quiz = get_object_or_404(Quiz, title=title.replace("-", " "))

    answer = answers.filter(quiz__order=quiz.order).first()

    # default answer header
    context['user_answer'] = quiz.answer_header
    if answer:
        context['user_answer'] = answer.answer
        context['answer'] = answer

    context['next'] = get_unsolved_quizzes(username, quiz.order).first().set_title_url()
    context['difficulty'] = quiz.category.difficulty.set_name_url()
    context['category'] = quiz.category.set_name_url()
    context['quiz'] = quiz.set_title_url().set_pretty_code()
    context['clicked'] = QuizScore.objects.filter(customuser__name=username, quiz_id=quiz.id).exists()

    context['page_title'] = title.replace("-", " ")
    context['page_description'] = get_description(strip_tags(quiz.explanation.replace("&nbsp;", " ").replace("&quot;", "").replace("&bull;", "").replace("&#39;", "")))

    return render(request, 'list/show.html', context)


def answer(request, quiz_order):
    username = get_username(request)
    quiz = get_object_or_404(Quiz, order=quiz_order)
    testcases = Testcase.objects.filter(quiz__order=quiz_order)
    customuser = CustomUser.objects.get(name=username)
    answer, _ = Answer.objects.get_or_create(quiz_id=quiz.id, customuser=customuser)
    answer.customuser = CustomUser.objects.get(name=username)
    answer.quiz = quiz
    answer.answer = request.POST['answer']

    if answer.right not in [Right.RIGHT.value, Right.WAS_RIGHT.value]:
        answer.date = datetime.now()

    answer.modified_date = datetime.now()

    if quiz.quiz_type.name == "Code":
        check_answer(get_username(request), testcases, answer)
    elif quiz.quiz_type.name in ["Answer", "MultipleChoice"]:
        # answer
        answer.answer = answer.answer.replace(" ", "").strip()
        if answer.answer[0] == '"' and answer.answer[-1] == '"':
            answer.answer = answer.answer[1:-1]
        if answer.answer[0] == "'" and answer.answer[-1] == "'":
            answer.answer = answer.answer[1:-1]
        if answer.answer.replace(" ", "").strip() == testcases[0].expected_output:
            answer.right = Right.RIGHT.value
            answer.output = ""
        else:
            if answer.right in [Right.RIGHT.value, Right.WAS_RIGHT.value]:
                answer.right = Right.WAS_RIGHT.value
            else:
                answer.right = Right.WRONG.value
            answer.output = testcases[0].expected_output

    answer.save()

    response = {
        "right": answer.right,
        "input": answer.input,
        "output": answer.output,
        "stdout": answer.stdout,
        "expected_output": answer.expected_output,
        "new_badges": add_badge(username),
    }
    return JsonResponse(json.dumps(response), safe=False)


def quiz_score(request, quiz_order, score):
    quiz = get_object_or_404(Quiz, order=quiz_order)
    customuser = CustomUser.objects.get(name=get_username(request))
    quiz_score, _ = QuizScore.objects.get_or_create(customuser=customuser, quiz_id=quiz.id)
    quiz.score += score - quiz_score.score
    quiz.save()

    quiz_score.customuser = customuser
    quiz_score.quiz = quiz
    quiz_score.score = score
    quiz_score.save()

    return HttpResponseRedirect('/quiz/' + str(quiz.get_title_url()))


def check_answer(username, testcases, answer):
    folder = "/tmp"
    f = open("%s/solution_%s.py" % (folder, username), "w+")
    answer.answer = remove_unsafe_code(answer.answer)
    f.write(answer.answer)
    f.close()

    if os.path.exists("%s/answer_%s" % (folder, username)):
        os.remove("%s/answer_%s" % (folder, username))

    f = open("%s/check_%s.py" % (folder, username), "w+")
    f.write(create_checking_code(username))
    f.close()

    for testcase in testcases:
        output = "None"
        try:
            if testcase.expected_stdout:
                process = subprocess.Popen(
                    ['python', '%s/solution_%s.py' % (folder, username)] + testcase.input.split("\n"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
                outs, errs = process.communicate(timeout=1)
                stdout = outs.decode("utf-8")
            else:
                process = subprocess.Popen(
                    ['python', '%s/check_%s.py' % (folder, username)] + testcase.input.split("\n"),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
                outs, errs = process.communicate(timeout=1)
                stdout = outs.decode("utf-8")

            if "Traceback (most recent call last):" in stdout:
                i = 0
                lines = stdout.split("\n")
                while i < len(lines):
                    if "File \"/tmp/check_" in lines[i]:
                        del lines[i:i+2]
                    else:
                        i += 1

                stdout = "\n".join(lines)
                stdout = stdout.replace("File \"/private/tmp/solution_{}.py\", ".format(username), "")

            if os.path.exists("%s/answer_%s" % (folder, username)):
                f = open("%s/answer_%s" % (folder, username), "r")
                output = f.read().strip()
                f.close()
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "TIMEOUT ERROR"

        testcase.expected_output = testcase.expected_output.replace("\r\n", "\n")

        # Check stdout
        if testcase.expected_stdout:
            testcase.expected_stdout = testcase.expected_stdout.replace("\r\n", "\n")
            if str(stdout).strip() == testcase.expected_stdout.strip():
                answer.right = Right.RIGHT.value
                answer.input = ""
                answer.stdout = ""
                answer.output = ""
                answer.expected_stdout = ""
                answer.expected_output = ""
            else:
                if answer.right in [Right.RIGHT.value, Right.WAS_RIGHT.value]:
                    answer.right = Right.WAS_RIGHT.value
                else:
                    answer.right = Right.WRONG.value
                answer.input = convert_node(testcase.input)
                answer.output = stdout
                answer.expected_output = testcase.expected_stdout
                break
        # Check output
        elif testcase.expected_output:
            if str(output) == testcase.expected_output.strip():
                answer.right = Right.RIGHT.value
                answer.input = ""
                answer.stdout = ""
                answer.output = ""
                answer.expected_stdout = ""
                answer.expected_output = ""
            else:
                if answer.right in [Right.RIGHT.value, Right.WAS_RIGHT.value]:
                    answer.right = Right.WAS_RIGHT.value
                else:
                    answer.right = Right.WRONG.value
                answer.input = convert_node(testcase.input)
                answer.stdout = stdout
                answer.output = output
                answer.expected_stdout = ""
                answer.expected_output = testcase.expected_output
                break


def create_checking_code(username):
    return """
import sys, ast, os

from solution_%s import *

def main(argv):
    if len(argv[0]) == 0:
        return output(solve())
    elif len(argv) == 1:
        return output(solve(input(argv[0])))
    elif len(argv) == 2:
        return output(solve(input(argv[0]), input(argv[1])))
    elif len(argv) == 3:
        return output(solve(input(argv[0]), input(argv[1]), input(argv[2])))
    elif len(argv) == 4:
        return output(solve(input(argv[0]), input(argv[1]), input(argv[2]), input(argv[3])))

def input(param):
    if param.startswith("Node"):
        nodes = ast.literal_eval(param[4:])
        return next(nodes, 0)
    elif param.startswith("Tree"):
        tree = ast.literal_eval(param[4:]) 
        return convert_list_to_tree(tree)
    else:
        return ast.literal_eval(param)

def output(param):
    try:
        if type(param) == Node:
            ans = str(param.val)
            param = param.next
            while param != None:
                ans += " -> " + str(param.val)
                param = param.next
            return ans
        else:
            return param
    except:
        try:
            if type(param) == Tree:
                list = convert_tree_to_list(param)
                    
                return "Tree" + str(list)
            else:
                return param
        except:
            return param


def next(nodes, i):
    if len(nodes) <= i:
        return None

    n = Node(nodes[i])
    n.next = next(nodes, i + 1)
    return n
    
    
def convert_tree_to_list(tree):
    level = []
    queue = [[tree, 0]]
    while True:
        t = queue.pop(0)
        if len(level) < t[1] + 1:
            level.append([])
        
        if t[0] != None:
            level[t[1]].append(t[0].val)
            queue.append([t[0].left, t[1] + 1])
            queue.append([t[0].right, t[1] + 1])
        else:
            level[t[1]].append(None)
            queue.append([None, t[1] + 1])
            queue.append([None, t[1] + 1])
            
        for q in queue:
            if q[0] != None:
                break
        else:
            break
    
    ans = []
    for l in level:
        ans += l
    return ans
    
    
def convert_list_to_tree(list):
    tree = Tree(list[0])
    store = [tree]
    for i in range(1, len(list)):
        if store[int((i - 1) / 2)] != None:
            if list[i] == None:
                node = None
            else:
                node = Tree(list[i])
            store.append(node)
            if i %% 2 == 1:
                store[int((i - 1) / 2)].left = node
            else:
                store[int((i - 1) / 2)].right = node
    
    return tree

if __name__ == "__main__":
    answer = main(sys.argv[1:])
    f = open("/tmp/answer_%s", "w+")
    if type(answer) == tuple:
        for line in answer:
            f.write(str(line) + "\\n")
    else:
        f.write(str(answer))
    f.close()""" % (username, username)


# TODO:: unlock the quiz
# TODO:: forget password
