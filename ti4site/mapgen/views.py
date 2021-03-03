from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.conf import Settings
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response as RestRespose

from .forms import OptimizeForm

from .mapgenwrapper.ti4mapgenwrapper import generate_galaxy
#from .mapgenwrapper.drawgalaxy import GalaxyDrawer

import logging
import json
import traceback

logger = logging.getLogger(__name__)


def index(request):
    optimize_form = OptimizeForm()
    return render(request, 'mapgen/index.html', {'optimize_form': optimize_form})

class GenerateException(APIException):
    status_code = 500
    default_detail = "Something went wrong generating an optimized map"
    default_code = "generation_error"

@api_view(['POST'])
def generate_map(request: HttpRequest):
    generate_args = json.loads(request.body)
    
    try:
        galaxy = generate_galaxy(generate_args)
    except Exception as e:
        #tb = traceback.format_exc()
        tb = str(e)
        raise GenerateException(tb)

    return RestRespose(galaxy)

