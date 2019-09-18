from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from list.views.common import *


def show(request, title):
    context = {}
    username = get_username(request)
    context['username'] = username

    answers = Answer.objects.filter(name=username)

    quiz = get_object_or_404(Quiz, title=title.replace("-", " "))

    right_modal = request.GET.get('right_modal')
    answer = answers.filter(quiz__order=quiz.order).first()

    # default answer header
    context['user_answer'] = quiz.answer_header
    if answer:
        context['user_answer'] = answer.answer
        context['answer'] = answer

    context['next'] = get_unsolved_quizzes(username, quiz.order).first()
    context['difficulty'] = quiz.category.difficulty
    context['category'] = quiz.category.name
    context['new_badge'] = add_badge(username)
    context['quiz'] = quiz.set_title_url()
    context['right_modal'] = right_modal
    # TODO:: change to configurable image for quiz
    context['quiz_image'] = 'theme/devices/airpods.svg'

    context['clicked'] = QuizScore.objects.filter(custom_user_id=request.user.id, quiz_id=quiz.id).exists()

    return render(request, 'list/show.html', context)


# TODO:: ajax
# TODO:: check the object input
# TODO:: dynamic function name depending on quiz.
def answer(request, quiz_order):
    quiz = get_object_or_404(Quiz, order=quiz_order)
    testcases = Testcase.objects.filter(quiz__order=quiz_order)
    answer, _ = Answer.objects.get_or_create(quiz_id=quiz.id, name=get_username(request))
    answer.quiz = quiz
    answer.answer = request.POST['answer']
    if answer.right not in [Right.RIGHT.value, Right.WAS_RIGHT.value]:
        answer.date = datetime.now()

    if quiz.quiz_type.name == "Code":
        check_answer(get_username(request), testcases, answer)
    elif quiz.quiz_type.name in ["Answer", "MultipleChoice"]:
        # answer
        if answer.answer.replace(" ", "").strip() == testcases[0].expected_answer:
            answer.right = Right.RIGHT.value
            answer.output = ""
        else:
            if answer.right in [Right.RIGHT.value, Right.WAS_RIGHT.value]:
                answer.right = Right.WAS_RIGHT.value
            else:
                answer.right = Right.WRONG.value
            answer.output = answer.answer

    answer.save()

    return HttpResponseRedirect('/' + str(quiz.order) + "?right_modal=" + str(answer.right))


def quiz_score(request, quiz_order, score):
    quiz = get_object_or_404(Quiz, order=quiz_order)

    quiz_score, _ = QuizScore.objects.get_or_create(custom_user_id=request.user.id, quiz_id=quiz.id)
    quiz.score += score - quiz_score.score
    quiz.save()

    quiz_score.custom_user_id = request.user.id
    quiz_score.quiz = quiz
    quiz_score.score = score
    quiz_score.save()

    return HttpResponseRedirect('/' + str(quiz.order))


def check_answer(username, testcases, answer):
    folder = "./list/users"
    f = open("%s/checks/solutions/%s.py" % (folder, username), "w+")
    f.write(answer.answer)
    f.close()

    f = open("%s/checks/%s.py" % (folder, username), "w+")
    f.write("""
import sys, ast, os
from node import Node

from solutions.dayeon import solve

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
    if os.path.exists("./list/users/answers/%s"):
        os.remove("./list/users/answers/%s")
    f = open("./list/users/answers/%s", "w+")
    if type(answer) == tuple:
        for line in answer:
            f.write(line + "\\n")
    else:
        f.write(str(answer))
    f.close()
    """ % (username, username, username))
    f.close()

    for testcase in testcases:
        output = "None"
        stdout = ""
        try:
            process = subprocess.Popen(
                ['python', '%s/checks/%s.py' % (folder, username)] + testcase.test.split("\n"),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            outs, errs = process.communicate(timeout=1)
            stdout = outs.decode("utf-8")
            if os.path.exists("%s/answers/%s" % (folder, username)):
                f = open("%s/answers/%s" % (folder, username), "r")
                output = f.read().strip()
                f.close()
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "TIMEOUT ERROR"

        testcase.expected_answer = testcase.expected_answer.replace("\r\n", "\n")
        if str(output) != testcase.expected_answer.strip():
            if answer.right in [Right.RIGHT.value, Right.WAS_RIGHT.value]:
                answer.right = Right.WAS_RIGHT.value
            else:
                answer.right = Right.WRONG.value
            answer.testcase = testcase.test
            answer.expected_answer = testcase.expected_answer
            answer.output = output
            answer.stdout = stdout
            return

    answer.right = Right.RIGHT.value
    answer.testcase = ""
    answer.expected_answer = ""
    answer.output = ""
    answer.stdout = ""
