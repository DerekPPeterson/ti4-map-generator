from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.conf import Settings

from .forms import OptimizeForm

from .mapgenwrapper.ti4mapgenwrapper import generate_galaxy
#from .mapgenwrapper.drawgalaxy import GalaxyDrawer

import logging
import json

logger = logging.getLogger(__name__)


def index(request):
    optimize_form = OptimizeForm()
    return render(request, 'mapgen/index.html', {'optimize_form': optimize_form})


def generate_map(request: HttpRequest):
    if request.is_ajax() and request.method == "POST":
        generate_args = json.loads(request.body)
    else:
        return HttpResponse("bad request", 400)
    
    galaxy = generate_galaxy(generate_args)

    return JsonResponse(galaxy)

        



