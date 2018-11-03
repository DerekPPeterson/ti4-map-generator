from PIL import Image, ImageFont, ImageDraw, ImageFilter
import json
import os
import math
from enum import Enum

class DisplayType(Enum):
    TileImagesWithNumbers = 1
    TileImagesOnly = 2
    NumbersOnly = 3


# Hardcoded constants
TILE_IMAGES = {}
TILE_DIR = "../res"
TILE_IMAGE_X = 198
TILE_IMAGE_Y = 172
FONT_PATH = "../res/Slider Regular.ttf"
DISPLAY_TYPE = DisplayType.TileImagesWithNumbers


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
        image_filename = os.path.join(TILE_DIR, "small-tilebw.png")
    elif (number < 0):
        image_filename = os.path.join(TILE_DIR, "small-tilehome.png")
    else:
        image_filename = os.path.join(TILE_DIR, "small-tile%d.png" % number)

    try:
        TILE_IMAGES[number] = Image.open(image_filename)
    except:
        print("Could not find " + image_filename)
        return None
    return TILE_IMAGES[number]


def calc_coordinates(i, j, n_row_offset):
    start_offset = n_row_offset * (TILE_IMAGE_Y) / 2
    out_x = (TILE_IMAGE_X * 3 / 4) * i
    out_y = start_offset + j * TILE_IMAGE_Y - i * (TILE_IMAGE_Y/2)
    return (out_x, out_y)


def calc_text_coords(i, j, n_row_offset):
    coords = calc_coordinates(i, j, n_row_offset)
    if DISPLAY_TYPE == DisplayType.NumbersOnly:
        return (coords[0] + int(TILE_IMAGE_X / 3.5),
                coords[1] + TILE_IMAGE_Y / 3)
    else:
        return (coords[0] + TILE_IMAGE_X / 8,
                coords[1] + TILE_IMAGE_Y / 3)

def normalize_angle(angle):
    while angle <= -180:
        angle += 360
    while angle > 180:
        angle -= 360
    return angle

def min_angle_difference(a, b):
    r = a - b
    return (r + 180) % 360 - 180

def draw_warp_lines(grid, warp_connections, image):
    angles_directions = {
        -30: [1, 1],
        -90: [0, 1],
        -150: [-1, 0],
        150: [-1, -1],
        90: [0, -1],
        30: [1, 0]
    }

    for wc in warp_connections:
        l = ImageDraw.Draw(image)
        line_coords = [tuple(calc_coordinates(gl[0], gl[1], len(grid) / 2)) for gl in wc]
        direct_angle = -math.degrees(math.atan2(line_coords[1][1] - line_coords[0][1],
                                               line_coords[1][0] - line_coords[0][0]))
        angles_diffs = [[a, abs(min_angle_difference(direct_angle, a))] for a in angles_directions]
        angles_diffs.sort(key=lambda x: x[1])
        for angle in [x[0] for x in angles_diffs]:
            if (not grid[wc[0][0] + angles_directions[angle][0]]
                        [wc[0][1] + angles_directions[angle][1]]):
                wc[0][0] += float(angles_directions[angle][0]) * 0.45
                wc[0][1] += float(angles_directions[angle][1]) * 0.45
                break

        direct_angle = normalize_angle(direct_angle + 180)
        angles_diffs = [[a, abs(min_angle_difference(direct_angle, a))] for a in angles_directions]
        angles_diffs.sort(key=lambda x: x[1])
        for angle in [x[0] for x in angles_diffs]:
            if (not grid[wc[1][0] + angles_directions[angle][0]]
                        [wc[1][1] + angles_directions[angle][1]]):
                wc[1][0] += float(angles_directions[angle][0]) * 0.45
                wc[1][1] += float(angles_directions[angle][1]) * 0.45
                break

        line_coords = [tuple(calc_coordinates(gl[0], gl[1], len(grid) / 2)) for gl in wc]
        line_coords = [(c[0] + TILE_IMAGE_X / 2, c[1] + TILE_IMAGE_Y / 2) for c in line_coords]
        l.line(line_coords, (50, 50, 100, 255), int(TILE_IMAGE_X / 10))
        l.line(line_coords, (255, 255, 255, 255), int(TILE_IMAGE_X / 30))


def create_galaxy_image_from_json_data(galaxy):
    grid = galaxy["grid"]

    width = TILE_IMAGE_X * len(grid)
    max_length = max([len(tmp) for tmp in grid])
    height = TILE_IMAGE_Y * max_length + TILE_IMAGE_Y / 2 * len(grid) / 2
    output = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    txt = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    font = ImageFont.truetype(FONT_PATH, size=int(TILE_IMAGE_Y/3))

    try:
        warp_connections = galaxy["warp_connections"]
        draw_warp_lines(grid, warp_connections, output)
        output = output.filter(ImageFilter.SMOOTH_MORE)
        output = output.filter(ImageFilter.BLUR)
    except:
        pass

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            tile_image = get_tile_image(grid[i][j])
            if (tile_image is None):
                continue
            coords = calc_coordinates(i, j, len(grid) / 2)
            text_coords = calc_text_coords(i, j, len(grid) / 2)
            output.paste(tile_image, coords, tile_image)
            if DISPLAY_TYPE == DisplayType.NumbersOnly:
                text_color = (0, 0, 0, 255)
            else:
                text_color = (255, 255, 255, 255)

            label = str(grid[i][j])
            if grid[i][j] < 0:
                label = "HS" + str(-grid[i][j])

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
        try:
            val = grid[c[0]][c[1]]
            if val != 0:
                n_visted += 1
        except IndexError:
            # if the spiral pattern goes outside the grid enter a 0
            val = 0

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
    cur_width, cur_height = image.size
    factor = 0
    if cur_width > cur_height:
        factor = 900.0 / cur_width
    else:
        factor = 900.0 / cur_height
    image = image.resize((int(cur_width * factor), int(cur_height * factor)), Image.BICUBIC)
    return image.crop(image.getbbox())



def create_galaxy_image(galaxy_json_filename, output_filename, box=(900, 900)):
    json_file = open(galaxy_json_filename)
    galaxy = json.load(json_file)
    image = create_galaxy_image_from_json_data(galaxy)
    image = resize_crop_to(image, 900)
    image.save(output_filename, "PNG")
    return create_galaxy_string_from_grid(galaxy["grid"], galaxy["mecatol"])


if __name__ == "__main__":
    create_galaxy_image("galaxy.json", "galaxy.png")

1
