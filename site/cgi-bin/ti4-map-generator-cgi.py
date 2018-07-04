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


def remove_other_chars(s, allowed):
    return ''.join(c for c in s if c in allowed)


def generate_galaxy(args):

    if "bw" in args and args["bw"].value == "true":
        draw_galaxy.BW = True
    n_players = 6
    if "n_players" in args:
        n_players = int(args["n_players"].value)

    id = random_string(6)
    galaxy_json_filename = "galaxy_%s.json" % id
    galaxy_png_filename = "galaxy_%s.png" % id

    if "seed" in args:
        seed = int(args["seed"].value)
    else:
        random.seed()
        seed = random.randint(1000000,9999999)

    cmd = ["./ti4-map-generator",
           "-t", "tiles.json",
           "-o", os.path.join(GENERATED_DIR, galaxy_json_filename),
           "-p", str(n_players),
           "-s", str(seed)]

    if "race_selection_method" in args:
        if args["race_selection_method"].value == "random":
            cmd += ["--random_homes"]
        elif args["race_selection_method"].value == "chosen":
            cmd += ["--choose_homes", "--races",
                    remove_other_chars(args["races"].value, " 012345678")]
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

    if "resource_weight" in args:
        cmd += ["--resource_weight", str(float(args["resource_weight"].value))]
    if "influence_weight" in args:
        cmd += ["--influence_weight", str(float(args["influence_weight"].value))]
    if "tech_weight" in args:
        cmd += ["--tech_weight", str(float(args["tech_weight"].value))]


    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()
    if p.returncode:
        raise Exception(err)

    draw_galaxy.create_galaxy_image(
        os.path.join(GENERATED_DIR, galaxy_json_filename),
        os.path.join(GENERATED_DIR, galaxy_png_filename))
    return galaxy_png_filename, seed


def return_image(image):
    filename = os.path.join(GENERATED_DIR, image)
    print('Content-type: image/png\n')
    with open(filename) as f:
        sys.stdout.flush()
        sys.stdout.write(f.read())


def return_main_page(args):
    print("Content-Type: text/html;charset=utf-8\n")

    galaxy_img_name, seed = generate_galaxy(args)

    print('<div align="right">Seed: %d</div><br>' % seed)
    print('<img src="./cgi-bin/ti4-map-generator-cgi.py?image=%s"/>' % galaxy_img_name)

cgitb.enable()
args = cgi.FieldStorage()
if "image" in args:
    return_image(args["image"].value)
else:
    return_main_page(args)



2
