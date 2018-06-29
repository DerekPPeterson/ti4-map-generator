#!/usr/bin/python

import cgi
import random
import string
import cgitb
import os, errno
import sys
import subprocess
import draw_galaxy

GENERATED_DIR = "../generated"

def random_string(N):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(N))

def generate_galaxy(n_players):
    try:
        os.makedirs(GENERATED_DIR)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    id = random_string(6)
    galaxy_json_filename = "galaxy_%s.json" % id
    galaxy_png_filename = "galaxy_%s.png" % id
    subprocess.Popen(["./ti4-map-generator",
                     "-t", "tiles.json",
                     "-o", os.path.join(GENERATED_DIR, galaxy_json_filename),
                     "-p", str(n_players)
                      ],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    draw_galaxy.create_galaxy_image(
        os.path.join(GENERATED_DIR, galaxy_json_filename),
        os.path.join(GENERATED_DIR, galaxy_png_filename))
    return galaxy_png_filename

def return_image(image):
    filename = os.path.join(GENERATED_DIR, image)
    print('Content-type: image/png\n')
    #print("Content-Length: " + str(os.stat(filename).st_size) + "\n")
    with open(filename) as f:
        sys.stdout.flush()
        sys.stdout.write(f.read())

def return_main_page(args):
    print("Content-Type: text/html;charset=utf-8\n")
    print("""
    <h1>Twilight Imperium IV Balanced Map Generator</h1>
        """)

    if "bw" in args:
        draw_galaxy.BW = True
    n_players = 6
    if "n_players" in args:
        n_players = args["n_players"].value
    galaxy_img_name = generate_galaxy(n_players)

    print('<img src="./test.py?image=%s"/>' % galaxy_img_name)

cgitb.enable()
args = cgi.FieldStorage()
if "image" in args:
    return_image(args["image"].value)
else:
    return_main_page(args)



1
