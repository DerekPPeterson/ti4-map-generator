from PIL import Image, ImageFont, ImageDraw, ImageFilter
import json
import os
import math
from enum import Enum
from copy import deepcopy
from glob import glob


def min_angle_difference(a, b):
    r = abs(a - b)
    return math.fmod((r + math.pi) , 2 * math.pi) - math.pi


class DisplayType(Enum):
    TileImagesWithNumbers = 1
    TileImagesOnly = 2
    NumbersOnly = 3

class GalaxyDrawer:
    def __init__(self, tile_dir, tile_prefix, image_x, image_y, font_path,
                 display_type):
        self.tile_prefix = tile_prefix
        self.image_x = image_x
        self.image_y = image_y
        self.display_type = display_type

        tile_image_filenames = glob(os.path.join(tile_dir, f"{tile_prefix}*.png"))
        self.tile_images = {}
        for filename in tile_image_filenames:
            image = Image.open(filename)
            self.tile_images[os.path.basename(filename)] = image

        self.font = ImageFont.truetype(font_path, size=int(image_y/3))

    def get_tile_image(self, number):
        if not number:
            return None

        if (self.display_type == DisplayType.NumbersOnly):
            image_filename = f"{self.tile_prefix}bw.png"
        elif (number < 0):
            image_filename = f"{self.tile_prefix}home.png"
        else:
            image_filename = f"{self.tile_prefix}{number}.png"

        try:
            image = self.tile_images[image_filename]
        except KeyError:
            raise RuntimeWarning(f"Could not find image for tile {number}")

        return image

    def calc_coordinates(self, i, j, n_row_offset):
        start_offset = n_row_offset * (self.image_y) / 2
        out_x = int(self.image_x * 3 / 4) * i
        out_y = int(start_offset + j * self.image_y - i * (self.image_y/2))
        return (out_x, out_y)


    def calc_text_coords(self, i, j, n_row_offset):
        coords = self.calc_coordinates(i, j, n_row_offset)
        if self.display_type == DisplayType.NumbersOnly:
            return (coords[0] + int(self.image_x / 3.5),
                    coords[1] + int(self.image_y / 3))
        else:
            return (coords[0] + int(self.image_x / 8),
                    coords[1] + int(self.image_y / 3))


    def calculate_line_end_adjust_angle(self, grid, wc):
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

        line_coords = [tuple(self.calc_coordinates(gl[0], gl[1], len(grid))) for gl in wc]
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


    def draw_warp_lines(self, grid, warp_connections, image):

        for wc in warp_connections:
            l = ImageDraw.Draw(image)

            angles = [0,0]
            angles[0] = self.calculate_line_end_adjust_angle(grid, wc)
            angles[1] = self.calculate_line_end_adjust_angle(grid, [wc[1], wc[0]])

            line_coords = [list(self.calc_coordinates(gl[0], gl[1], len(grid))) for gl in wc]
            line_coords = [[c[0] + self.image_x / 2, c[1] + self.image_y / 2] for c in line_coords]

            line_coords[0][0] += self.image_x / 2.5 * math.cos(angles[0])
            line_coords[0][1] += self.image_y / 2.5 * -math.sin(angles[0])
            line_coords[1][0] += self.image_x / 2.5 * math.cos(angles[1])
            line_coords[1][1] += self.image_y / 2.5 * -math.sin(angles[1])
            #print line_coords

            line_coords = tuple([tuple(x) for x in line_coords])

            l.line(line_coords, (50, 50, 100, 255), int(self.image_x / 10))
            l.line(line_coords, (255, 255, 255, 255), int(self.image_x / 30))


    def create_image(self, galaxy, crop_to=None):
        if crop_to is None:
            crop_to = self.image_x * 4.5

        grid = galaxy["grid"]

        width = int(self.image_x * len(grid))
        max_length = max([len(tmp) for tmp in grid])
        height = int(self.image_y * max_length + self.image_y / 2 * len(grid))
        output = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        txt = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        d = ImageDraw.Draw(txt)

        try:
            warp_connections = galaxy["warp_connections"]
        except KeyError:
            pass
        else:
            self.draw_warp_lines(grid, warp_connections, output)
            output = output.filter(ImageFilter.SMOOTH_MORE)
            output = output.filter(ImageFilter.BLUR)

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                tile_image = self.get_tile_image(grid[i][j])
                if (tile_image is None):
                    continue
                coords = self.calc_coordinates(i, j, len(grid))
                text_coords = self.calc_text_coords(i, j, len(grid))
                output.paste(tile_image, coords, tile_image)
                if self.display_type == DisplayType.NumbersOnly:
                    text_color = (0, 0, 0, 255)
                else:
                    text_color = (255, 255, 255, 255)

                label = str(grid[i][j])
                if grid[i][j] < 0:
                    label = "HS" + str(-grid[i][j])
                # label = "{},{}".format(i, j)

                outline_thickness = 2
                if self.display_type == DisplayType.TileImagesWithNumbers:
                    d.text((text_coords[0] - outline_thickness, text_coords[1] + outline_thickness), label, font=self.font, fill=(0, 0, 0, 100))
                    d.text((text_coords[0] - outline_thickness, text_coords[1] - outline_thickness), label, font=self.font, fill=(0, 0, 0, 100))
                    d.text((text_coords[0] + outline_thickness, text_coords[1] + outline_thickness), label, font=self.font, fill=(0, 0, 0, 100))
                    d.text((text_coords[0] + outline_thickness, text_coords[1] - outline_thickness), label, font=self.font, fill=(0, 0, 0, 100))
                if self.display_type != DisplayType.TileImagesOnly:
                    d.text(text_coords, label, font=self.font, fill=text_color)

        output = Image.alpha_composite(output, txt)
        if crop_to is not None:
            output = resize_crop_to(output, crop_to)
        return output




# Globals
# FIXME globals are evil. need to have a better configuration setup
#TILE_IMAGES = {}
#TILE_DIR = "../res"
#
#HI_RES = True
#
#BIG_TILE_PREFIX = "tile"
#SMALL_TILE_PREFIX = "small-tile"
#
#BIG_TILE_IMAGE_X = 900
#BIG_TILE_IMAGE_Y = 775
#SMALL_TILE_IMAGE_X = 198
#SMALL_TILE_IMAGE_Y = 172
#
#TILE_PREFIX = SMALL_TILE_PREFIX
#TILE_IMAGE_X = SMALL_TILE_IMAGE_X
#TILE_IMAGE_Y = SMALL_TILE_IMAGE_Y
#
FONT_PATH = "../res/Slider Regular.ttf"
#DISPLAY_TYPE = DisplayType.TileImagesWithNumbers



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
