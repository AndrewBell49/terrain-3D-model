# Written by Andrew Bell in 2023/24
# Data got from https://www.swisstopo.admin.ch/en/geodata/height/dhm25.html
# Program to make a Terrain model from Swiss coordinates

from Terrain import Terrain
import numpy as np

POINT_SPACING = 25 # 25 metres in between each data-point

# coordinates of the "start of Switzerland"
LEFT_EXTREME = 479987.5
BOTTOM_EXTREME = 73987.5

def makeTerrain(bottomLeft, topRight, zScale):

    with open("Switzerland\\dhm25_grid_raster.asc", "r") as r:
        linesRead = r.read().split("\n")[6:-1]
    
    lines = linesRead[::-1] # reverse as this is the way data needs to be accessed
    
    length = topRight[0] - bottomLeft[0]
    height = topRight[1] - bottomLeft[1]
    
    terrain = np.empty(shape=[height * length, 3])

    for y in range(bottomLeft[1], topRight[1]):
        yCoord = y - bottomLeft[1]
        points = lines[y].split(" ")
        for x in range(bottomLeft[0], topRight[0]):
            altitude = round((float(points[x]) / POINT_SPACING) * zScale, 2)
            if altitude < 0.01:
                altitude = 0.01
            xCoord = x - bottomLeft[0]
            terrain[yCoord*length + xCoord] = [yCoord, xCoord, altitude]
    
    return length, height, terrain

# save the terrain to a file, and estimate time. zScale=1.5 is the best scale for Switzerland imo
def saveTerrain(bottomLeftMap, topRightMap, fileName, zScale=1.5):

    # every points are every 25 metres
    bottomLeft = (round((bottomLeftMap[0]-LEFT_EXTREME)/POINT_SPACING), 
                  round((bottomLeftMap[1]-BOTTOM_EXTREME)/POINT_SPACING))
    topRight = (round((topRightMap[0]-LEFT_EXTREME)/POINT_SPACING), 
                round((topRightMap[1]-BOTTOM_EXTREME)/POINT_SPACING))
   
    width, height, terrainPoints = makeTerrain(bottomLeft, topRight, zScale)
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
    # coordinates from https://map.geo.admin.ch/
    # coordinates are in CH1903/LV03 format
    bottomLeftMap = (612970.98, 193766.37)
    topRightMap = (629808.69, 203744.78)

    fileName = "Langnau"
    zScale = 1.5

    # same way of doing this as with UK map
    saveTerrain(bottomLeftMap, topRightMap, fileName, zScale)