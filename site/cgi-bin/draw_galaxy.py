from PIL import Image, ImageFont, ImageDraw, ImageFilter
import json
import os
import math
from enum import Enum
from copy import deepcopy

class DisplayType(Enum):
    TileImagesWithNumbers = 1
    TileImagesOnly = 2
    NumbersOnly = 3


# Globals
# FIXME globals are evil. need to have a better configuration setup
TILE_IMAGES = {}
TILE_DIR = "../res"

HI_RES = True

BIG_TILE_PREFIX = "tile"
SMALL_TILE_PREFIX = "small-tile"

BIG_TILE_IMAGE_X = 900
BIG_TILE_IMAGE_Y = 775
SMALL_TILE_IMAGE_X = 198
SMALL_TILE_IMAGE_Y = 172

TILE_PREFIX = SMALL_TILE_PREFIX
TILE_IMAGE_X = SMALL_TILE_IMAGE_X
TILE_IMAGE_Y = SMALL_TILE_IMAGE_Y

FONT_PATH = "../res/Slider Regular.ttf"
DISPLAY_TYPE = DisplayType.TileImagesWithNumbers


def enable_hi_res():
    global TILE_PREFIX
    global TILE_IMAGE_X
    global TILE_IMAGE_Y
    TILE_PREFIX = BIG_TILE_PREFIX
    TILE_IMAGE_X = BIG_TILE_IMAGE_X
    TILE_IMAGE_Y = BIG_TILE_IMAGE_Y


# Returns list of locations in each ring around mecatol rex
def spiral_pattern(centre):
    cur_point = centre
    directions = [[1, 1], [0, 1], [-1, 0], [-1, -1], [0, -1], [1, 0]]
    ring = 0
    while True:
        cur_point[1] -= 1  # move up one to next ring
        ring += 1
        for direction in directions:
            for i in range(ring):
                yield cur_point
                cur_point[0] += direction[0]
                cur_point[1] += direction[1]


def get_tile_image(number):
    if not number:
        return None

    try:
        return TILE_IMAGES[number]
    except KeyError:
        pass

    if (DISPLAY_TYPE == DisplayType.NumbersOnly):
        number = 0
        image_filename = os.path.join(TILE_DIR, TILE_PREFIX + "bw.png")
    elif (number < 0):
        image_filename = os.path.join(TILE_DIR, TILE_PREFIX + "home.png")
    else:
        image_filename = os.path.join(TILE_DIR, TILE_PREFIX + "%d.png" % number)

    try:
        TILE_IMAGES[number] = Image.open(image_filename)
    except:
        print("Could not find " + image_filename)
        return None
    return TILE_IMAGES[number]


def calc_coordinates(i, j, n_row_offset):
    start_offset = n_row_offset * (TILE_IMAGE_Y) / 2
    out_x = int(TILE_IMAGE_X * 3 / 4) * i
    out_y = int(start_offset + j * TILE_IMAGE_Y - i * (TILE_IMAGE_Y/2))
    return (out_x, out_y)


def calc_text_coords(i, j, n_row_offset):
    coords = calc_coordinates(i, j, n_row_offset)
    if DISPLAY_TYPE == DisplayType.NumbersOnly:
        return (coords[0] + int(TILE_IMAGE_X / 3.5),
                coords[1] + int(TILE_IMAGE_Y / 3))
    else:
        return (coords[0] + int(TILE_IMAGE_X / 8),
                coords[1] + int(TILE_IMAGE_Y / 3))


def min_angle_difference(a, b):
    r = abs(a - b)
    return math.fmod((r + math.pi) , 2 * math.pi) - math.pi

def calculate_line_end_adjust_angle(grid, wc):
    wc = deepcopy(wc)
    #print wc

    angles_directions = {
        math.radians(-30): [1, 1],
        math.radians(-90): [0, 1],
        math.radians(-150): [-1, 0],
        math.radians(150): [-1, -1],
        math.radians(90): [0, -1],
        math.radians(30): [1, 0]
    }

    line_coords = [tuple(calc_coordinates(gl[0], gl[1], len(grid))) for gl in wc]
    # angle from centre of one tile to centre of other
    direct_angle = -(math.atan2(line_coords[1][1] - line_coords[0][1],
                                line_coords[1][0] - line_coords[0][0]))
    #print direct_angle
    # figure out which edges have no tiles beside them
    valid_angles = []
    for angle in angles_directions:
        try:
            if (not grid[wc[0][0] + angles_directions[angle][0]]
                        [wc[0][1] + angles_directions[angle][1]]):
                valid_angles.append(angle)
        except IndexError:
            valid_angles.append(angle)
    #print(valid_angles)

    # figure out the minimum difference between the tile edge
    angles_diffs = [[a, abs(min_angle_difference(direct_angle, a))] for a in valid_angles]
    angles_diffs.sort(key=lambda x: x[1])
    #print angles_diffs

    angle = 0;
    vec = [0, 0]
    if (len(angles_diffs) > 1 and angles_diffs[0][1] < math.pi/3 and angles_diffs[1][1] < math.pi/3):
        angle = math.atan2(0.5 * (math.sin(angles_diffs[0][0]) +
                                  math.sin(angles_diffs[1][0])),
                           0.5 * (math.cos(angles_diffs[0][0]) +
                                  math.cos(angles_diffs[1][0])))

    else:
        angle = angles_diffs[0][0]
    #print angle
    return angle


def draw_warp_lines(grid, warp_connections, image):

    for wc in warp_connections:
        l = ImageDraw.Draw(image)

        angles = [0,0]
        angles[0] = calculate_line_end_adjust_angle(grid, wc)
        angles[1] = calculate_line_end_adjust_angle(grid, [wc[1], wc[0]])

        line_coords = [list(calc_coordinates(gl[0], gl[1], len(grid))) for gl in wc]
        line_coords = [[c[0] + TILE_IMAGE_X / 2, c[1] + TILE_IMAGE_Y / 2] for c in line_coords]
        #print line_coords

        line_coords[0][0] += TILE_IMAGE_X / 2.5 * math.cos(angles[0])
        line_coords[0][1] += TILE_IMAGE_Y / 2.5 * -math.sin(angles[0])
        line_coords[1][0] += TILE_IMAGE_X / 2.5 * math.cos(angles[1])
        line_coords[1][1] += TILE_IMAGE_Y / 2.5 * -math.sin(angles[1])
        #print line_coords

        line_coords = tuple([tuple(x) for x in line_coords])

        l.line(line_coords, (50, 50, 100, 255), int(TILE_IMAGE_X / 10))
        l.line(line_coords, (255, 255, 255, 255), int(TILE_IMAGE_X / 30))


def create_galaxy_image_from_json_data(galaxy):
    grid = galaxy["grid"]

    width = int(TILE_IMAGE_X * len(grid))
    max_length = max([len(tmp) for tmp in grid])
    height = int(TILE_IMAGE_Y * max_length + TILE_IMAGE_Y / 2 * len(grid))
    output = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    txt = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    font = ImageFont.truetype(FONT_PATH, size=int(TILE_IMAGE_Y/3))

    try:
        warp_connections = galaxy["warp_connections"]
    except KeyError:
        pass
    else:
        draw_warp_lines(grid, warp_connections, output)
        output = output.filter(ImageFilter.SMOOTH_MORE)
        output = output.filter(ImageFilter.BLUR)

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            tile_image = get_tile_image(grid[i][j])
            if (tile_image is None):
                continue
            coords = calc_coordinates(i, j, len(grid))
            text_coords = calc_text_coords(i, j, len(grid))
            output.paste(tile_image, coords, tile_image)
            if DISPLAY_TYPE == DisplayType.NumbersOnly:
                text_color = (0, 0, 0, 255)
            else:
                text_color = (255, 255, 255, 255)

            label = str(grid[i][j])
            if grid[i][j] < 0:
                label = "HS" + str(-grid[i][j])
            # label = "{},{}".format(i, j)

            outline_thickness = 2
            if DISPLAY_TYPE == DisplayType.TileImagesWithNumbers:
                d.text((text_coords[0] - outline_thickness, text_coords[1] + outline_thickness), label, font=font, fill=(0, 0, 0, 100))
                d.text((text_coords[0] - outline_thickness, text_coords[1] - outline_thickness), label, font=font, fill=(0, 0, 0, 100))
                d.text((text_coords[0] + outline_thickness, text_coords[1] + outline_thickness), label, font=font, fill=(0, 0, 0, 100))
                d.text((text_coords[0] + outline_thickness, text_coords[1] - outline_thickness), label, font=font, fill=(0, 0, 0, 100))
            if DISPLAY_TYPE != DisplayType.TileImagesOnly:
                d.text(text_coords, label, font=font, fill=text_color)
            #d.text(text_coords, "{},{}".format(i, j), font=font, fill=text_color)


    output = Image.alpha_composite(output, txt)
    return output


def create_galaxy_string_from_grid(grid, centre):
    string = ""
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
        if(val < 0):
            val = 0
        string += "%d" % val
        string += " "

        # Done after visiting all spots in grid (except for mecatol)
        if n_visted == n_tiles - 1:
            break

    return string

def resize_crop_to(image, max_dim):
    image = image.crop(image.getbbox())
    cur_width, cur_height = image.size
    factor = 0
    max_dim = float(max_dim)
    if cur_width > cur_height:
        factor = max_dim / cur_width
    else:
        factor = max_dim / cur_height
    image = image.resize((int(cur_width * factor), int(cur_height * factor)), Image.BICUBIC)
    return image



def create_galaxy_image(galaxy_json_filename, output_filename):
    json_file = open(galaxy_json_filename)
    galaxy = json.load(json_file)
    if HI_RES:
        enable_hi_res()
        image = create_galaxy_image_from_json_data(galaxy)
        image = resize_crop_to(image, 2700)
    else:
        image = create_galaxy_image_from_json_data(galaxy)
        image = resize_crop_to(image, 900)
    image.save(output_filename, "PNG")
    return create_galaxy_string_from_grid(galaxy["grid"], galaxy["mecatol"])


if __name__ == "__main__":
    create_galaxy_image("galaxy.json", "galaxy.png")

1
