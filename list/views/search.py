import json

from django.http import JsonResponse


def search(request):
    response = {
        "test": "abc",
    }
    return JsonResponse(json.dumps(response), safe=False)

