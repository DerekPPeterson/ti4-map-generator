#!/usr/bin/python

import cgi
import random
import string
import cgitb
import os
import sys
import subprocess
import draw_galaxy
import json
from glob import glob

GENERATED_DIR = "../generated"
LAYOUTS_DIR = "../res/layouts"

def spiral_pattern(centre):
    cur_point = centre
    directions = [[1, 1], [0, 1], [-1, 0], [-1, -1], [0, -1], [1, 1]]
    ring = 0
    while True:
        cur_point[1] -= 1; # move up one to next ring
        ring += 1
        for direction in directions:
            for i in range(ring):
                yield cur_point
                cur_point[0] == direction[0]
                cur_point[1] == direction[1]




def random_string(N):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(N))


def remove_other_chars(s, allowed):
    return ''.join(c for c in s if c in allowed)


def generate_galaxy(args):

    if "display_type" in args:
        if args["display_type"].value == "tile_images_with_numbers":
            draw_galaxy.DISPLAY_TYPE = draw_galaxy.DisplayType.TileImagesWithNumbers
        elif args["display_type"].value == "tile_images_only":
            draw_galaxy.DISPLAY_TYPE = draw_galaxy.DisplayType.TileImagesOnly
        elif args["display_type"].value == "numbers_only":
            draw_galaxy.DISPLAY_TYPE = draw_galaxy.DisplayType.NumbersOnly

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
           "-l", args["layout"].value,
           "-o", os.path.join(GENERATED_DIR, galaxy_json_filename),
           "-p", str(n_players),
           "-s", str(seed)]

    if "race_selection_method" in args:
        if args["race_selection_method"].value == "random":
            cmd += ["--random_homes"]
        elif args["race_selection_method"].value == "chosen":
            cmd += ["--choose_homes", "--races",
                    remove_other_chars(args["races"].value, " 0123456789")]
        else:
            cmd += ["--dummy_homes"]

    if "star_by_star" in args and args["star_by_star"].value == "true":
        cmd += ["--star_by_star"]

    if "pie_slice_assignment" in args and args["pie_slice_assignment"].value == "true":
        cmd += ["--pie_slice_assignment"]

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

    if "include_all_wormholes" in args and args["include_all_wormholes"].value == "true":
        cmd += ["--mandatory_tiles", "25 26 39 40"]

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

    string = draw_galaxy.create_galaxy_image(
        os.path.join(GENERATED_DIR, galaxy_json_filename),
        os.path.join(GENERATED_DIR, galaxy_png_filename))
    return galaxy_png_filename, galaxy_json_filename, seed, string


def return_image(image):
    filename = os.path.join(GENERATED_DIR, image)
    print('Content-type: image/png\n')
    with open(filename) as f:
        sys.stdout.flush()
        sys.stdout.write(f.read())


def return_layouts():
    layouts = {}
    for layout_file in glob(LAYOUTS_DIR + "/*"):
        with open(layout_file, "r") as f:
            layout = json.load(f)
            layouts[layout_file] = {}
            layouts[layout_file]["layout_name"] = layout["layout_name"]
            layouts[layout_file]["supports_players"] = []
            for n_players in layout["home_tile_positions"]:
                layouts[layout_file]["supports_players"].append(n_players)

            layouts[layout_file]["default"] = "false"
            try:
                if (layout["default"] == "true"):
                    layouts[layout_file]["default"] = "true"
            except:
                pass

    sys.stdout.write("Content-Type: application/json")
    sys.stdout.write("\n")
    sys.stdout.write("\n")
    sys.stdout.write(json.dumps(layouts))


def return_galaxy_image_div(args):
    print("Content-Type: text/html;charset=utf-8\n")

    galaxy_img_name, galaxy_json_filename, seed, string = generate_galaxy(args)

    print('<img src="./cgi-bin/ti4-map-generator-cgi.py?image=%s"/>' % galaxy_img_name)
    print('<div id="result_info" class="rounded_background">Seed: %d<br>' % seed)
    print('<button onclick="display_stats(\'%s\')">Display Balance Details</button><br>' % galaxy_json_filename)
    print('Map String '
          '(for use with <a href="https://steamcommunity.com/sharedfiles/filedetails/?id=1466689117">this tabletop simulator mod</a>):'
          '<br>{map_string}</div>'.format(map_string=string))


def create_html_table(id, data):
    table_str = '<table id="%s">' % id;
    for row in data:
        table_str += "<tr>"
        for elem in row:
            table_str += "<td>" + str(elem) + "</td>"
        table_str += "</tr>"
    table_str += "</table>"
    return table_str


def return_stats(args):
    print("Content-Type: text/html;charset=utf-8\n")

    galaxy_json_filename = os.path.join(GENERATED_DIR, args["get_stats"].value)

    json_file = open(galaxy_json_filename)
    galaxy = json.load(json_file)
    json_file.close()

    races = galaxy["scores"].keys()
    races.sort()

    score_data = [["Race", "Resource Share", "Influence Share", "Tech Share"]]
    for race in races:
        score_data.append([
            race,
            "{:.3f}".format(galaxy["scores"][race]["resource"]),
            "{:.3f}".format(galaxy["scores"][race]["influence"]),
            "{:.3f}".format(galaxy["scores"][race]["tech"])
        ])
    print "<h3>Resource shares by race</h3>"
    print create_html_table("score_stats", score_data)

    stake_data = [["Tile"] + [r for r in races]]
    tiles = galaxy["stakes"].keys()
    tiles.sort()
    for tile in tiles:
        row = [tile]
        for race in races:
            try:
                stake = galaxy["stakes"][tile][race];
                row.append("{:.1f}%".format(stake * 100))
            except KeyError:
                row.append(0.0)
        stake_data.append(row)
    print "<h3>Race stakes in each system</h3>"
    print create_html_table("stake_stats", stake_data)


if __name__ == "__main__":
    cgitb.enable()
    args = cgi.FieldStorage()
    if "image" in args:
        return_image(args["image"].value)
    elif "get_layouts" in args:
        return_layouts()
    elif "get_stats" in args:
        return_stats(args)
    else:
        return_galaxy_image_div(args)


