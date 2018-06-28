from PIL import Image
import json
import os

TILE_IMAGES = {}
TILE_DIR = "./res"
TILE_IMAGE_X = 900
TILE_IMAGE_Y = 774


def get_tile_image(number):
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


def calc_coordinates(i, j, image_x, image_y, n_row_offset):
    start_offset = n_row_offset * (image_y) / 2
    out_x = (image_x * 3 / 4) * i
    out_y = start_offset + j * image_y - i * (image_y/2)
    return (out_x, out_y)


def create_galaxy_image(grid):
    output = Image.new('RGBA', (int(TILE_IMAGE_X * (6 * 0.75 + 1)), TILE_IMAGE_Y * 7), (0, 0, 0, 1))
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            tile_image = get_tile_image(grid[i][j])
            if (tile_image is None):
                continue
            output.paste(tile_image,
                         calc_coordinates(i, j, TILE_IMAGE_X, TILE_IMAGE_Y, 3),
                         tile_image)

    return output

if __name__ == "__main__":
    json_file = open("galaxy.json")
    galaxy = json.load(json_file)
    image = create_galaxy_image(galaxy["grid"])
    image.save("test.png", "PNG")


1
