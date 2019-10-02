import json
from datetime import datetime


from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render

from list.views.common import *
from django.utils.html import strip_tags


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
    context['difficulty'] = quiz.category.difficulty
    context['category'] = quiz.category.name
    context['quiz'] = quiz.set_title_url()
    context['clicked'] = QuizScore.objects.filter(customuser__name=username, quiz__id=quiz.id).exists()

    context['page_title'] = title
    context['page_description'] = get_description(strip_tags(quiz.explanation.replace("&nbsp;", " ").replace("&quot;", "").replace("&bull;", "").replace("&#39;", "")))

    return render(request, 'list/show.html', context)


def answer(request, quiz_order):
    username = get_username(request)
    quiz = get_object_or_404(Quiz, order=quiz_order)
    testcases = Testcase.objects.filter(quiz__order=quiz_order)
    answer, _ = Answer.objects.get_or_create(quiz_id=quiz.id, customuser__name=get_username(request))
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
            answer.output = answer.answer

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
    f.write(answer.answer)
    f.close()

    if os.path.exists("%s/answer_%s" % (folder, username)):
        os.remove("%s/answer_%s" % (folder, username))

    f = open("%s/check_%s.py" % (folder, username), "w+")
    f.write(create_checking_code(username))
    f.close()

    for testcase in testcases:
        output = "None"
        stdout = ""
        try:
            outs, errs, stdout = "", "", ""
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
                answer.input = testcase.input
                answer.output = stdout
                answer.expected_output = testcase.expected_stdout
            return

        # Check output
        if testcase.expected_output:
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
                answer.input = testcase.input
                answer.stdout = stdout
                answer.output = output
                answer.expected_stdout = ""
                answer.expected_output = testcase.expected_output
                return

def create_checking_code(username):
    return """
import sys, ast, os

from solution_%s import solve

class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

def main(argv):
    if len(argv) == 1:
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
    else:
        return ast.literal_eval(param)

def output(param):
    if type(param) == Node:
        list = []
        while param != None:
            list.append(param.val)
            param = param.next

        return "Node" + str(list)
    else:
        return param

def next(nodes, i):
    if len(nodes) <= i:
        return None

    n = Node(nodes[i])
    n.next = next(nodes, i + 1)
    return n

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
# TODO:: daily login for coin
