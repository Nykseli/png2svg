from PIL import Image

def svg_header(width, height):
    return """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="%d" height="%d"
     xmlns="http://www.w3.org/2000/svg" version="1.1">
""" % (width, height)


class SVGBlock:
    # color is rgb color list, PIL.Image.getpixel can be used
    def __init__(self, color:list, x:int, y:int, h:int, w:int):
        self.color = color
        self.x = x
        self.y = y
        self.h = h
        self.w = w

    def __str__(self):
        return '<rect x="{}" y="{}" width="{}" height="{}" fill="rgb({},{},{})"/>'.format(
            self.x,
            self.y,
            self.w,
            self.h,
            self.color[0],
            self.color[1],
            self.color[2],
        )

class PngImage:
    def __init__(self, imgPath: str):
        self.imagedata = Image.open(imgPath)
        self.width, self.height = self.imagedata.size
        self.x = 0
        self.y = 0
        # list of scanned SVGBlocks
        self.scanned_blocks = {}
        print(svg_header(self.width, self.height))

    def set_and_find_next_xy(self):
        self.x = 0
        self.y = 0
        for y in range(self.height):
            self.y = y
            if not y in self.scanned_blocks:
                self.x = 0
                break
            for x in range(self.width):
                if not x in self.scanned_blocks[y]:
                    self.y = y
                    self.x = x
                    return (self.x, self.y)
        return (self.x, self.y)


    def add_block(self, block):
        for y in range(block.y, block.h + block.y):
            if not y in self.scanned_blocks:
                self.scanned_blocks[y] = {}
            for x in range(block.x, block.w + block.x):
                self.scanned_blocks[y][x] = 1

    def match_right(self, pixel):
        if self.x >= self.width - 1:
            return False

        return self.imagedata.getpixel((self.x + 1, self.y)) == pixel

    def match_bottom(self, pixel):
        if self.y >= self.height - 1:
            return True

        return self.imagedata.getpixel((self.x, self.y + 1)) == pixel

    def scan_block(self):
        start_x, start_y = self.set_and_find_next_xy()
        line_width = 0
        block_color = self.imagedata.getpixel((self.x, self.y))

        while self.y < self.height:
            bad_line = False
            while self.x < self.width:
                if not self.match_right(block_color):
                    if line_width == 0:
                        line_width = self.x - start_x + 1
                    elif self.x - start_x + 1 != line_width:
                        bad_line = True
                    break
                self.x += 1

            # TODO: mach bottom should traverse all the pixels below based on length
            if not self.match_bottom(block_color):
                break

            self.y += 1
            if self.match_right(block_color):
                self.y -= 1
                break

            if bad_line:
                self.y -= 2
                break
            else:
                # list are 0 indexed so the width is always 1 too small
                line_width = self.x - start_x + 1

            self.x = start_x

        block = SVGBlock(
            block_color,
            start_x,
            start_y,
            self.y - start_y + 1, # list are 0 indexed so the height is always 1 too small
            line_width,
        )
        print(block)
        self.add_block(block)

        # Reset y if the full line hasn't been scanned
        if self.x != self.width - 1:
            self.y = start_y
        else:
            self.x = 0

    def dumb_scan(self):
        for y in range(self.height):
            for x in range(self.width):
                block_color = self.imagedata.getpixel((x, y))
                print(SVGBlock(
                    block_color,
                    x,
                    y,
                    1,
                    1,
                ))

    def is_traversed(self):
        if len(self.scanned_blocks) < self.height:
            return False

        for i in range(len(self.scanned_blocks)):
            if len(self.scanned_blocks[i]) < self.width:
                return False

        return True

    def convert(self):
        while not self.is_traversed():
            self.scan_block()
        #while self.y < self.height and self.x < self.width:
        #    self.scan_block()

    def __del__(self):
        print('</svg>')
        self.imagedata.close()


img = PngImage('pixel-art.png')
img.convert()
