#!/usr/bin/python

import cgi
import random
import string
import cgitb
import os, errno
import sys
import subprocess
import draw_galaxy

GENERATED_DIR = "/var/web_tmp"

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

def print_form():
    print ("""
<form action="./ti4-map-generator-cgi.py">
    Number of Players:
    <select name="n_players">
        <option value=6>6</option>
        <option value=5>5</option>
        <option value=4>4</option>
        <option value=3>3</option>
    </select>
    <br>

    Display in:
    <input type="radio" name="bw" value="false" checked> Full Colour
    <input type="radio" name="bw" value="true"> Tile Numbers Only<br>

    <input type="submit" value="Submit">
</form>
    """)

def return_main_page(args):
    print("Content-Type: text/html;charset=utf-8\n")
    print("""
    <head>
        <link rel="stylesheet" type="text/css" href="../../style.css">
    </head>
          <body>
    <h1>Twilight Imperium IV Balanced Map Generator</h1>
        """)

    if "bw" in args and args["bw"].value == "true":
        draw_galaxy.BW = True
    n_players = 6
    if "n_players" in args:
        n_players = args["n_players"].value
    galaxy_img_name = generate_galaxy(n_players)

    print_form()

    print('<img src="./test.py?image=%s"/>' % galaxy_img_name)
    print('</body>')

cgitb.enable()
args = cgi.FieldStorage()
if "image" in args:
    return_image(args["image"].value)
else:
    return_main_page(args)



1
