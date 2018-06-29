from PIL import Image, ImageFont, ImageDraw
import json
import os

TILE_IMAGES = {}
TILE_DIR = "./res"
TILE_IMAGE_X = 900
TILE_IMAGE_Y = 774
FONT_PATH = "./res/Slider Regular.ttf"


def get_tile_image(number):
    if not number:
        return None

    try:
        return TILE_IMAGES[number]
    except KeyError:
        pass

    if (number < 0):
        image_filename = os.path.join(TILE_DIR, "tilehome.png")
    else:
        image_filename = os.path.join(TILE_DIR, "tile%d.png" % number)

    try:
        TILE_IMAGES[number] = Image.open(image_filename)
    except:
        print("Could not find " + image_filename)
        return None
    return TILE_IMAGES[number]

def draw_number_at_coordinates(number, fnt, image, coords):
    d.text(coords, str(number), font=fnt)


def calc_coordinates(i, j, n_row_offset):
    start_offset = n_row_offset * (TILE_IMAGE_Y) / 2
    out_x = (TILE_IMAGE_X * 3 / 4) * i
    out_y = start_offset + j * TILE_IMAGE_Y - i * (TILE_IMAGE_Y/2)
    return (out_x, out_y)

def calc_text_coords(i, j, n_row_offset):
    coords = calc_coordinates(i, j, n_row_offset)
    return (coords[0] + TILE_IMAGE_X / 8,
            coords[1] + TILE_IMAGE_Y / 3)


def create_galaxy_image(grid):
    output = Image.new('RGBA',
                       (int(TILE_IMAGE_X * (6 * 0.75 + 1)), TILE_IMAGE_Y * 7),
                       (0, 0, 0, 0 ))
    txt = Image.new('RGBA',
                     (int(TILE_IMAGE_X * (6 * 0.75 + 1)), TILE_IMAGE_Y * 7),
                     (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    font = ImageFont.truetype(FONT_PATH, size=TILE_IMAGE_Y/3)
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            tile_image = get_tile_image(grid[i][j])
            if (tile_image is None):
                continue
            coords = calc_coordinates(i, j, 3)
            text_coords = calc_text_coords(i, j, 3)
            output.paste(tile_image, coords, tile_image)
            d.text(text_coords, str(grid[i][j]), font=font, fill=(255,255,255,255))

    output = Image.alpha_composite(output, txt)
    return output

if __name__ == "__main__":
    json_file = open("galaxy.json")
    galaxy = json.load(json_file)
    image = create_galaxy_image(galaxy["grid"])
    image.resize((900, 900), Image.BICUBIC).save("test.png", "PNG")


1
