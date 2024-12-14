from PIL import Image
import utils
import sys
import random

argn = len(sys.argv)

'''
if argn < 1:
    print("no input file")
    exit(-1)
inputFileName, format = sys.argv[1].rsplit(".", 1)
'''

COLORS_COUNT = 8
DRAW_PALETTE = False
REPAINTS_COUNT = 0
SHIFTS_COUNT = 0
FILENAME = None
NAME = None
EXT = None
FORMAT = None

def argAsNum(i):
    try:
        return int(sys.argv[i])
    except ValueError as e:
        print(f"Error: The number expected at #{i} arg but \"{sys.argv[i]}\" got")
        exit(-2)

for i in range(1, argn):
    match sys.argv[i]:
        case "--input-file" | "-i":
            FILENAME = sys.argv[i + 1]
            NAME, EXT = FILENAME.rsplit(".", 1)
        case "--color-count" | "-c":
            COLORS_COUNT = argAsNum(i + 1)
        case "--draw-palette" | "-p":
            DRAW_PALETTE = True
        case "--repaints-count" | "-r":
            REPAINTS_COUNT = argAsNum(i + 1)
        case "--shifts-count" | "-s":
            SHIFTS_COUNT = argAsNum(i + 1)
        case "--output-format" | "-o":
            FORMAT = sys.argv[i + 1]

if FILENAME is None:
    print("Error: No input file")
    exit(-1)

if FORMAT is None:
    FORMAT = EXT if EXT is not None else "png"

print(f"file: {FILENAME}")

random.seed()

im = Image.open(f"{FILENAME}")
inputSequence = list(im.getdata())
size = (im.width, im.height)
print(f"size: {size}")

inputSequence = list(map(utils.reduceDepth(), inputSequence))

mainColors, idxToCl = utils.clusterize(inputSequence, COLORS_COUNT)

def re(pixel):
    index = utils.toIndex(pixel)
    cluster = idxToCl[index]
    return mainColors[cluster]

outputSequence = list(map(re, inputSequence))
utils.saveSequence(outputSequence, f"{NAME}_out.{FORMAT}", FORMAT, size)

for i in range(1, REPAINTS_COUNT):
    repaint = [utils.generateRandomColor() for it in range(COLORS_COUNT)]
    repaintSequence = list(map(re, inputSequence))
    utils.saveSequence(repaintSequence, f"{NAME}_rep_{i}.{FORMAT}", FORMAT, size)

for i in range(1, SHIFTS_COUNT):
    shiftedSequence = list(map(utils.shift(i / (SHIFTS_COUNT + 1)), outputSequence))
    utils.saveSequence(shiftedSequence, f"{NAME}_sh_{i}.{FORMAT}", FORMAT, size)

print("Done")

if DRAW_PALETTE:
    utils.drawPalette(outputSequence, COLORS_COUNT, NAME, FORMAT)