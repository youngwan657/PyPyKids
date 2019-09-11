from django.shortcuts import render
from list.views.common import *


def playground(request):
    context = {}
    context["username"] = get_username(request)
    if request.method == "POST":
        f = open("playground.py", "w+")
        code = request.POST['answer']
        f.write(code)
        f.close()
        try:
            process = subprocess.Popen(['python', 'playground.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            outs, errs = process.communicate(timeout=1)
            stdout = outs.decode("utf-8")
        except subprocess.TimeoutExpired:
            process.kill()
            stdout = "TIMEOUT ERROR"

        context['code'] = code
        context['stdout'] = stdout

    return render(request, 'list/playground.html', context)
