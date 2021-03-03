import logging
import json
import os
import traceback

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.conf import Settings
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response as RestRespose

from .forms import OptimizeForm

from .mapgenwrapper.ti4mapgenwrapper import generate_galaxy
#from .mapgenwrapper.drawgalaxy import GalaxyDrawer


logger = logging.getLogger(__name__)


def index(request):
    optimize_form = OptimizeForm()
    return render(request, 'mapgen/index.html', {'optimize_form': optimize_form})

# TODO configure this better or store tiles in db
LAYOUT_DIR = "/Users/derekpeterson/devel/ti4-map-generator/site/res/layouts/"
TILESET_DIR = "/Users/derekpeterson/devel/ti4-map-generator/site/cgi-bin/"

class GenerateException(APIException):
    status_code = 500
    default_detail = "Something went wrong generating an optimized map"
    default_code = "generation_error"

@api_view(['POST'])
def generate_map(request: HttpRequest):
    generate_args = json.loads(request.body)

    # expand arguments to full directories
    try:
        generate_args["tiles"] = os.path.join(TILESET_DIR, generate_args["tiles"])
    except KeyError:
        raise APIException("Must provide tiles argument")

    try:
        generate_args["layout"] = os.path.join(LAYOUT_DIR, generate_args["layout"])
    except KeyError:
        raise APIException("Must provide layout argument argument")

    try:
        galaxy = generate_galaxy(generate_args)
    except Exception as e:
        tb = traceback.format_exc()
        #tb = str(e)
        raise GenerateException(tb)

    return RestRespose(galaxy)

