import json

from django.http import JsonResponse
from django.shortcuts import render
from list.views.common import *


def playground(request):
    context = {}
    username = get_profile(request, context)
    filename = "/tmp/playground_" + username + ".py"
    if request.method == "POST":
        f = open(filename, "w+")
        code = request.POST['answer']
        code = remove_unsafe_code(code)
        f.write(code)
        f.close()
        try:
            process = subprocess.Popen(['python', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            outs, errs = process.communicate(timeout=1)
            stdout = outs.decode("utf-8")
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "Timeout Error"

        if "Traceback (most recent call last):" in stdout:
            stdout = stdout.replace("File \"/tmp/playground_{}.py\", ".format(username), "")

        response = {
            'output': stdout,
        }
        return JsonResponse(json.dumps(response), safe=False)

    return render(request, 'list/playground.html', context)
