# Written by Andrew Bell in 2023
# Data got from https://osdatahub.os.uk/downloads/open/Terrain50
# Program to get os grid reference coordinates, convert to a numpy array, then make a Terrain model

import os
import zipfile
import math
from Terrain import Terrain
import numpy as np

GRID_COUNT = 200 #200 data points in each grid (per row)
GRID_SIZE = 10000 #10,000m in each grid square

# downloaded files were all in separate zip files
def unzipAll():
    nationalGrid, pathToSquares = getNationalGrid()
    for grid in nationalGrid:
        squares = os.listdir(f"{pathToSquares}\\{grid}")
        for square in squares:
            path = f"{pathToSquares}\\{grid}\\{square}"
            if len(path) > 4 and path[-4:] == ".zip":
                with zipfile.ZipFile(path, "r") as zip_ref:
                    zip_ref.extractall(path[:-4])
                os.remove(path)
        print(f"Extracted and removed all from {pathToSquares}\\{grid}")

# national grid squares are in separate folders
def getNationalGrid():
    pathToSquares = f"{os.path.dirname(os.path.abspath(__file__))}\\UK\\data"
    nationalGrid = os.listdir(pathToSquares)
    return nationalGrid, pathToSquares


def getAllGridReferences():
    nationalGrid, pathToSquares = getNationalGrid()
    # dictionary, containing the top left grid reference as key
    # and the file path as value
    gridReferenceAndFile = {}

    for grid in nationalGrid:
        squares = os.listdir(f"{pathToSquares}\\{grid}")
        for square in squares:
            files = os.listdir(f"{pathToSquares}\\{grid}\\{square}")
            for file in files:
                # only get the .asc files (with the data i want in)
                if file[-4:] == ".asc":
                    with open(f"{pathToSquares}\\{grid}\\{square}\\{file}", "r") as r:
                        rows = r.read().split("\n")
                        xCoord = int(rows[2].split(" ")[1]) # grid reference stored at top of file
                        yCoord = int(rows[3].split(" ")[1])
                        gridReferenceAndFile[(xCoord, yCoord)] = f"{pathToSquares}\\{grid}\\{square}\\{file}"

    return gridReferenceAndFile


def getFilesFromCorners(topLeft, bottomRight):
    osGrid = [
        ["SV", "SW", "SX", "SY", "SZ", "TV", "  "],  # national grid lines
        ["  ", "SR", "SS", "ST", "SU", "TQ", "TR"],
        ["  ", "SM", "SN", "SO", "SP", "TL", "TM"],
        ["  ", "  ", "SH", "SJ", "SK", "TF", "TG"],
        ["  ", "  ", "SC", "SD", "SE", "TA", "  "],
        ["  ", "NW", "NX", "NY", "NZ", "OV", "  "],
        ["  ", "NR", "NS", "NT", "NU", "  ", "  "],
        ["NL", "NM", "NN", "NO", "NP", "  ", "  "],
        ["NF", "NG", "NH", "NJ", "NK", "  ", "  "],
        ["NA", "NB", "NC", "ND", "NE", "  ", "  "],
        ["  ", "HW", "HX", "HY", "HZ", "  ", "  "],
        ["  ", "  ", "  ", "HT", "HU", "  ", "  "],
        ["  ", "  ", "  ", "HO", "HP", "  ", "  "]]

    topLeftX = int(topLeft[1] / GRID_SIZE) * GRID_SIZE  # rounding down to nearest GRID_SIZEth
    topLeftY = int(topLeft[2] / GRID_SIZE) * GRID_SIZE
    bottomRightX = int(bottomRight[1] / GRID_SIZE) * GRID_SIZE
    bottomRightY = int(bottomRight[2] / GRID_SIZE) * GRID_SIZE

    # adding national grid references to local grid reference
    # this is the 2 letters, which means the program can be run over multiple national grid lines
    # each "letter increase" is 100000 more
    for y in range(len(osGrid)):
        for x in range(len(osGrid[y])):
            if osGrid[y][x] == topLeft[0]:
                topLeftX += x * 100000
                topLeftY += y * 100000
            if osGrid[y][x] == bottomRight[0]:
                bottomRightX += x * 100000
                bottomRightY += y * 100000

    allGridFiles = getAllGridReferences()
    usefulGridFiles = []

    # getting all the different .asc files needed for the selection
    for y in range(topLeftY, bottomRightY - 1, -GRID_SIZE):
        row = []
        for x in range(topLeftX, bottomRightX + 1, GRID_SIZE):
            if (x, y) in allGridFiles:
                print(allGridFiles[(x, y)])
                row.append(allGridFiles[(x, y)])
            else:
                print("None")
                row.append(None)
        usefulGridFiles.append(row)

    return usefulGridFiles

# returns the coordinate in the furthest grid square to begin from
def getPartialSquares(topLeft, bottomRight):
    OS_TO_FILE = GRID_SIZE/GRID_COUNT  # how many os grid references in each one number in the file

    topLeftX = int(topLeft[1] / GRID_SIZE) * GRID_SIZE  # rounding down to 10000th
    topLeftY = int(topLeft[2] / GRID_SIZE) * GRID_SIZE
    bottomRightX = int(bottomRight[1] / GRID_SIZE) * GRID_SIZE
    bottomRightY = int(bottomRight[2] / GRID_SIZE) * GRID_SIZE

    leftOverflow = topLeft[1] - topLeftX  # how far into the left most grid the range is
    topOverflow = topLeft[2] - topLeftY # same for into the top most grid...
    rightOverflow = bottomRight[1] - bottomRightX # """
    bottomOverflow = bottomRight[2] - bottomRightY # """

    leftBegin =  math.floor(leftOverflow/OS_TO_FILE)  # which point in the file to start on
    topBegin = GRID_COUNT - math.ceil(topOverflow/OS_TO_FILE)
    rightBegin = math.ceil(rightOverflow/OS_TO_FILE)
    bottomBegin = GRID_COUNT - math.floor(bottomOverflow/OS_TO_FILE)

    return leftBegin, topBegin, rightBegin, bottomBegin

# used in makeTerrain method, to deal with edge cases
def getEndAndBegin(count, height, top, bottom):
    size = GRID_COUNT
    begin = 0
    end = GRID_COUNT
    if count == 0:
        size -= top
        begin += top
    if count == height - 1:
        size -= (GRID_COUNT - bottom)
        end -= (GRID_COUNT - bottom)
    return size, begin, end

# when full row is finished, add to the terrain structure
def addRowToTerrain(row, terrain):
    for j in range(np.shape(row)[0]):
        for i in range(np.shape(row)[1]):
            terrain = np.append(terrain, [row[j, i]], axis=0)
    return terrain

# makes the terrain from the top left and bottom right grid reference
def makeTerrain(topLeft, bottomRight, zScale):
    files = getFilesFromCorners(topLeft, bottomRight)

    scaleConvert = (zScale * GRID_COUNT)/GRID_SIZE

    leftBegin, topBegin, rightBegin, bottomBegin = getPartialSquares(topLeft, bottomRight)
    gridHeight, gridLength = np.shape(files)
    terrainPoints = np.empty(shape=[0, 3])

    width = GRID_COUNT*(gridLength-2) + (GRID_COUNT-leftBegin) + rightBegin
    height = 0
    colCount = 0
    yCount = 0
    ySave = 0

    for fileRow in files:

        rowHeight, yBegin, yEnd = getEndAndBegin(colCount, gridHeight, topBegin, bottomBegin)

        height += rowHeight
        row = np.empty(shape=[rowHeight, width, 3])
        rowCount = 0
        xSave = 0 # variable to save the progress of x from file to file

        for file in fileRow:
            try:
                with open(file, "r") as r:
                    rows = r.read().split("\n")[5:] # ignore first 5 rows (not the elevation data)
            except: # if file is "none", populate rows with 0s
                emptyRow = "0 " * GRID_COUNT
                rows = []
                for i in range(GRID_COUNT):
                    rows.append(emptyRow)

            _, xBegin, xEnd = getEndAndBegin(rowCount, gridLength, leftBegin, rightBegin)

            yCount = ySave
            for y in range(yBegin, yEnd):
                points = rows[y].split(" ")[:GRID_COUNT]
                xCount = xSave
                for x in range(xBegin, xEnd):
                    # /50 to convert between altitude (in metres) and 1m in between individual points
                    # zScale because a scale of 1 makes mountains look very flat
                    altitude = round(float(points[x]) * scaleConvert, 3)
                    if altitude < 0.01:
                        altitude = 0.01
                    # row beginning at (0, 0), containing the x and y coordinate for the whole map as well as altitude 
                    row[y-yBegin, xCount] = [yCount, xCount, altitude]
                    xCount += 1
                yCount += 1

            xSave = xCount
            rowCount += 1

        ySave = yCount
        colCount += 1

        # add row after all files in row have been read
        terrainPoints = addRowToTerrain(row, terrainPoints)
    
    return width, height, terrainPoints

# save the terrain to a file, and estimate time. zScale=2 is the best scale imo
def saveTerrain(topLeft, bottomRight, fileName, zScale=2):
    width, height, terrainPoints = makeTerrain(topLeft, bottomRight, zScale)
    numOfPoints = width * height

    # very rough estimate, based on my pc
    estimatedTimeSeconds = int((0.0000000454 * numOfPoints * numOfPoints) - (0.0003619093 * numOfPoints) - 1.9100171003)
    hours = int(estimatedTimeSeconds/3600)
    minutes = int((estimatedTimeSeconds-(hours*3600))/60)
    seconds = estimatedTimeSeconds - minutes*60 - hours*3600
    print(f"Estimated time: {hours}:{minutes}:{seconds}")

    terrain = Terrain(width, height, terrainPoints)

    terrain.saveFile(fileName)

if __name__ == "__main__":
    topLeft = ("NY", 31838, 18230)
    bottomRight = ("NY", 41446, 5445)
    zScale = 2
    fileName = "Helvellyn"
    saveTerrain(topLeft, bottomRight, fileName, zScale)