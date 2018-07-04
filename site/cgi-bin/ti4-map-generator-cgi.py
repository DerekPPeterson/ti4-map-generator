#!/usr/bin/python

import cgi
import random
import string
import cgitb
import os
import sys
import subprocess
import draw_galaxy

GENERATED_DIR = "../generated"


def random_string(N):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(N))


def generate_galaxy(args):

    if "bw" in args and args["bw"].value == "true":
        draw_galaxy.BW = True
    n_players = 6
    if "n_players" in args:
        n_players = int(args["n_players"].value)

    id = random_string(6)
    galaxy_json_filename = "galaxy_%s.json" % id
    galaxy_png_filename = "galaxy_%s.png" % id
    cmd = ["./ti4-map-generator",
           "-t", "tiles.json",
           "-o", os.path.join(GENERATED_DIR, galaxy_json_filename),
           "-p", str(n_players)]
    if "race_selection_method" in args:
        if args["race_selection_method"].value == "random":
            cmd += ["--random_homes"]
        elif args["race_selection_method"].value == "chosen":
            cmd += ["--choose_homes", "--races", args["races"].value]
        else:
            cmd += ["--dummy_homes"]

    if "creuss_gets_wormhole" in args and args["creuss_gets_wormhole"].value == "true":
        cmd += ["--creuss_gets_wormhole", "1"]
    elif args["creuss_gets_wormhole"].value == "false":
        cmd += ["--creuss_gets_wormhole", "0"]

    if "muaat_gets_supernova" in args and args["muaat_gets_supernova"].value == "true":
        cmd += ["--muaat_gets_supernova", "1"]
    elif args["muaat_gets_supernova"].value == "false":
        cmd += ["--muaat_gets_supernova", "0"]

    if "winnu_clear_path_to_mecatol" in args and args["winnu_clear_path_to_mecatol"].value == "true":
        cmd += ["--winnu_have_clear_path_to_mecatol", "1"]
    elif args["winnu_clear_path_to_mecatol"].value == "false":
        cmd += ["--winnu_have_clear_path_to_mecatol", "0"]

    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()
    if p.returncode:
        raise Exception(err)

    draw_galaxy.create_galaxy_image(
        os.path.join(GENERATED_DIR, galaxy_json_filename),
        os.path.join(GENERATED_DIR, galaxy_png_filename))
    return galaxy_png_filename


def return_image(image):
    filename = os.path.join(GENERATED_DIR, image)
    print('Content-type: image/png\n')
    with open(filename) as f:
        sys.stdout.flush()
        sys.stdout.write(f.read())


def return_main_page(args):
    print("Content-Type: text/html;charset=utf-8\n")

    galaxy_img_name = generate_galaxy(args)

    print('<img src="./cgi-bin/ti4-map-generator-cgi.py?image=%s"/>' % galaxy_img_name)

cgitb.enable()
args = cgi.FieldStorage()
if "image" in args:
    return_image(args["image"].value)
else:
    return_main_page(args)



2
