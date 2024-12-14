import colorsys
import math
import random
from PIL import Image, ImageDraw
from sklearn.cluster import KMeans

MAX = 0x1000000

def getTop(hist):
    items = dict(enumerate(hist)).items()
    ordered = sorted(items, key = lambda entry: entry[1], reverse = True)
    return dict(filter(lambda e: e[1] > 0, ordered))

def calcHist(seq):
    hist = [0] * MAX
    for pixel in seq:
        index = toIndex(pixel)
        hist[index] += 1
    return getTop(hist)

def toIndex(pixel):
    return (pixel[0] << 16) + (pixel[1] << 8) + pixel[2]

def toColor(index):
    return (index >> 16, (index >> 8) & 0xFF, index & 0xFF) 

def shift(offset = 0.4):
    def inner(pixel):
        (h,s,v) = colorsys.rgb_to_hsv(pixel[0]/256, pixel[1]/256, pixel[2]/256)
        rgb = colorsys.hsv_to_rgb(h + offset, s, v)
        return (round(rgb[0]*256), round(rgb[1]*256), round(rgb[2]*256))
    return inner

def reduceDepth(mask = 0xFA):
    def inner(pixel):
        return (pixel[0] & mask, pixel[1] & mask, pixel[2] & mask)
    return inner

def generateRandomColor():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

def clusterize(sequence, n):
    hist = calcHist(sequence)
    indices, weights = zip(*hist.items())
    colors = list(map(toColor, indices))
    kmeans = KMeans(n_clusters = n)
    clusters = list(map(int, kmeans.fit_predict(colors, None, weights)))
    mainColors = list(map(lambda item: tuple(map(int, item)), kmeans.cluster_centers_))
    idxToCl = dict(zip(indices, clusters))
    return (mainColors, idxToCl)

def saveSequence(seq, filename, format, size):
    im = Image.new("RGB", size)
    im.putdata(seq)
    im.save(filename, format)
    print(f"\"{filename}\" saved")

def drawPalette(seq, count, name, format):
    tileX = 20
    tileY = 20
    tilesInRow = 8
    tilesInCol = math.ceil(count / tilesInRow)

    palette = list(map(toColor, calcHist(seq).keys()))
    paletteImg = Image.new("RGB", (tileX*tilesInRow, tileY*tilesInCol))
    draw = ImageDraw.Draw(paletteImg)

    for i in range(tilesInRow):
        for j in range(tilesInCol):
            draw.rectangle([i*tileX, j*tileY, (i + 1)*tileX -1, (j + 1)*tileY - 1], palette[j*tilesInRow + i])
    paletteImg.save(f"{name}_palette.{format}", format)