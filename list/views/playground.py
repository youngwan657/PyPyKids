import json

from django.http import JsonResponse
from django.shortcuts import render
from list.views.common import *


def playground(request):
    context = {}
    username = get_username(request)
    context['username'] = username
    context['profile_badge_count'] = get_badge_count(username)
    filename = "./list/users/playgrounds/" + context['username'] + ".py"
    if request.method == "POST":
        f = open(filename, "w+")
        code = request.POST['answer']
        f.write(code)
        f.close()
        try:
            process = subprocess.Popen(['python', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            outs, errs = process.communicate(timeout=1)
            stdout = outs.decode("utf-8")
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "TIMEOUT ERROR"

        response = {
            'output': stdout,
        }
        return JsonResponse(json.dumps(response), safe=False)

    return render(request, 'list/playground.html', context)
