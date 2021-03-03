#!/usr/bin/env python3

import random
import string
import subprocess
import json
import os
#import drawgalaxy

TMP_DIR = '/tmp/'

def spiral_pattern(centre):
    cur_point = centre
    directions = [[1, 1], [0, 1], [-1, 0], [-1, -1], [0, -1], [1, 1]]
    ring = 0
    while True:
        cur_point[1] -= 1 # move up one to next ring
        ring += 1
        for direction in directions:
            for _ in range(ring):
                yield cur_point
                cur_point[0] == direction[0]
                cur_point[1] == direction[1]


def random_string(N):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(N))


def remove_other_chars(s, allowed):
    return ''.join(c for c in s if c in allowed)


GENERATE_ARGS = {
    "n_players": int,
    "seed": int,
    "layout": str,
    "race_selection_method": str,
    "races": lambda v: remove_other_chars(v, " 0123456789"),
    "star_by_star": bool,
    "pie_slice_assignment": bool,
    "creuss_gets_wormhole": bool,
    "muaat_gets_supernova": bool,
    "saar_get_asteroids": bool,
    "winnu_clear_path_to_mecatol": bool,
    "include_all_wormholes": bool,
    "mandatory_tiles": str,
    "res_inf_weight": float,
    "first_turn": bool,
    "resource_weight": bool,
    "influence_weight": bool,
    "tech_weight": bool,
    "trait_weight": bool,
    "ring_balance_weight": bool,
    "ring_balance": float,
    "use_ring_balance": bool,
    "tiles": str,
    "layout": str,
}

def generate_galaxy(args):
    n_players = 6
    if "n_players" in args:
        n_players = int(args["n_players"])

    galaxy_json_filename = os.path.join(TMP_DIR, 
                                        "galaxy_%s.json" % random_string(10))

    if "seed" in args:
        seed = int(args["seed"])
    else:
        random.seed()
        seed = random.randint(1000000,9999999)

    cmd = [os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                        "ti4-map-generator"),
           "-o", galaxy_json_filename,
           "-p", str(n_players),
           "-s", str(seed)]

    for arg, value in args.items():
        arg_type = GENERATE_ARGS[arg]
        arg_str = str(arg_type(value))
        cmd += [f"--{arg}", arg_str]

    p = subprocess.Popen(cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()
    if p.returncode:
        raise RuntimeError(err.decode("utf-8"))

    with open(galaxy_json_filename, "r") as f:
        generated = dict(json.load(f))
    generated["seed"] = seed

    galaxy_string = create_galaxy_string_from_grid(generated["grid"], generated["mecatol"])
    generated["galaxy_string"] = galaxy_string

    return generated


def create_galaxy_string_from_grid(grid, centre):
    galaxy_string = ""
    n_tiles = sum(sum(n != 0 for n in row) for row in grid)
    n_visted = 0

    for c in spiral_pattern(centre):
        # if the spiral pattern goes outside the grid enter a 0
        if c[0] < 0 or c[0] >= len(grid) or c[1] < 0 or c[1] >= len(grid[c[0]]):
            val = 0
        else:
            val = grid[c[0]][c[1]]

        if val != 0:
            n_visted += 1

        # Blank home systems are in grid as negative numbers, but output them
        # as 0
        if val < 0:
            val = 0
        galaxy_string += "%d" % val
        galaxy_string += " "

        # Done after visiting all spots in grid (except for mecatol)
        if n_visted == n_tiles - 1:
            break

    return galaxy_string


#if __name__ == "__main__":
#    galaxy = generate_galaxy({"layout":"./site/res/layouts/standard_hex.json",
#                              "tiles":"./site/cgi-bin/tiles.json"})
#    print(galaxy)
#    print("Loading images")
#    gd = drawgalaxy.GalaxyDrawer("./site/res/", "small-tile", 198, 172, "./site/res/Slider Regular.ttf", drawgalaxy.DisplayType.TileImagesWithNumbers)
#    print("Creating image 1")
#    image = gd.create_image(galaxy)
#    image.save("./galaxy.png", "PNG")
    
