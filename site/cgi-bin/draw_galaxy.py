from PIL import Image, ImageFont, ImageDraw
import json
import os
from enum import Enum

class DisplayType(Enum):
    TileImagesWithNumbers = 1
    TileImagesOnly = 2
    NumbersOnly = 3


TILE_IMAGES = {}
TILE_DIR = "../res"
TILE_IMAGE_X = 198
TILE_IMAGE_Y = 172
FONT_PATH = "../res/Slider Regular.ttf"
DISPLAY_TYPE = DisplayType.TileImagesWithNumbers
SPIRAL_PATTERN = [[3,2], [4,3], [4,4], [3,4], [2,3], [2,2], [3,1], [4,2], [5,3], [5,4], [5,5], [4,5], [3,5], [2,4], [1,3], [1,2], [1,1], [2,1], [3,0], [4,1], [5,2], [6,3], [6,4], [6,5], [6,6], [5,6], [4,6], [3,6], [2,5], [1,4], [0,3], [0,2], [0,1], [0,0], [1,0], [2,0]]


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


def create_galaxy_image_from_grid(grid):
    width = TILE_IMAGE_X * len(grid)
    max_length = max([len(tmp) for tmp in grid])
    height = TILE_IMAGE_Y * max_length + TILE_IMAGE_Y / 2 * len(grid) / 2
    output = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    txt = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    font = ImageFont.truetype(FONT_PATH, size=int(TILE_IMAGE_Y/3))
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

            if grid[i][j] > 0:
                outline_thickness = 2
                if DISPLAY_TYPE == DisplayType.TileImagesWithNumbers:
                    d.text((text_coords[0] - outline_thickness, text_coords[1] + outline_thickness), str(grid[i][j]), font=font, fill=(0, 0, 0, 100))
                    d.text((text_coords[0] - outline_thickness, text_coords[1] - outline_thickness), str(grid[i][j]), font=font, fill=(0, 0, 0, 100))
                    d.text((text_coords[0] + outline_thickness, text_coords[1] + outline_thickness), str(grid[i][j]), font=font, fill=(0, 0, 0, 100))
                    d.text((text_coords[0] + outline_thickness, text_coords[1] - outline_thickness), str(grid[i][j]), font=font, fill=(0, 0, 0, 100))
                if DISPLAY_TYPE != DisplayType.TileImagesOnly:
                    d.text(text_coords, str(grid[i][j]), font=font, fill=text_color)
            #d.text(text_coords, "{},{}".format(i, j), font=font, fill=text_color)

    output = Image.alpha_composite(output, txt)
    return output


def create_galaxy_string_from_grid(grid):
    string = ""
    for c in SPIRAL_PATTERN:
        try:
            val = grid[c[0]][c[1]]
        except IndexError:
            break
        if(val < 0):
            val = 0
        string += "%d" % val
        string += " "
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
    image = create_galaxy_image_from_grid(galaxy["grid"])
    image = resize_crop_to(image, 900)
    image.save(output_filename, "PNG")
    return create_galaxy_string_from_grid(galaxy["grid"])


if __name__ == "__main__":
    create_galaxy_image("galaxy.json", "galaxy.png")

1
