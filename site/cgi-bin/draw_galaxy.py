from PIL import Image, ImageFont, ImageDraw
import json
import os

TILE_IMAGES = {}
TILE_DIR = "../res"
TILE_IMAGE_X = 900
TILE_IMAGE_Y = 774
FONT_PATH = "../res/Slider Regular.ttf"
BW = False


def get_tile_image(number):
    if not number:
        return None

    try:
        return TILE_IMAGES[number]
    except KeyError:
        pass

    if (BW):
        number = 0
        image_filename = os.path.join(TILE_DIR, "tilebw.png")
    elif (number < 0):
        image_filename = os.path.join(TILE_DIR, "tilehome.png")
    else:
        image_filename = os.path.join(TILE_DIR, "tile%d.png" % number)

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
    if BW:
        return (coords[0] + int(TILE_IMAGE_X / 3.5),
                coords[1] + TILE_IMAGE_Y / 3)
    else:
        return (coords[0] + TILE_IMAGE_X / 8,
                coords[1] + TILE_IMAGE_Y / 3)



def create_galaxy_image_from_grid(grid):
    output = Image.new('RGBA',
                       (int(TILE_IMAGE_X * (6 * 0.75 + 1)), TILE_IMAGE_Y * 7),
                       (0, 0, 0, 0))
    txt = Image.new('RGBA',
                    (int(TILE_IMAGE_X * (6 * 0.75 + 1)), TILE_IMAGE_Y * 7),
                    (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    font = ImageFont.truetype(FONT_PATH, size=int(TILE_IMAGE_Y/3))
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            tile_image = get_tile_image(grid[i][j])
            if (tile_image is None):
                continue
            coords = calc_coordinates(i, j, 3)
            text_coords = calc_text_coords(i, j, 3)
            output.paste(tile_image, coords, tile_image)
            if BW:
                text_color = (0, 0, 0, 255)
            else:
                text_color = (255, 255, 255, 255)

            if grid[i][j] > 0:
                d.text(text_coords, str(grid[i][j]), font=font, fill=text_color)
            #d.text(text_coords, "{},{}".format(i, j), font=font, fill=text_color)

    output = Image.alpha_composite(output, txt)
    return output


def create_galaxy_image(galaxy_json_filename, output_filename, box=(900, 900)):
    json_file = open(galaxy_json_filename)
    galaxy = json.load(json_file)
    image = create_galaxy_image_from_grid(galaxy["grid"])
    image = image.resize(box, Image.BICUBIC)
    image = image.crop(image.getbbox())
    image.save(output_filename, "PNG")


if __name__ == "__main__":
    create_galaxy_image("galaxy.json", "galaxy.png")

1
