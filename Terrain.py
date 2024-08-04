# Written by Andrew Bell in 2023/2024
# Program that reads in a numpy array, converts it to a terrain mesh and then saves the file
# Using numpy-stl library, some code used from https://pythonhosted.org/numpy-stl/usage.html#creating-mesh-objects-from-a-list-of-vertices-and-faces

import numpy as np
from stl import mesh
import os
import time

class Terrain:

    def __init__(self, width, length, elevationArray):
        self.length = length
        self.width = width
        self.numOfVertices = length*width
        self.elevationArray = elevationArray

        # input in correct format
        if type(elevationArray) == np.ndarray and elevationArray.shape == (self.numOfVertices, 3):
            self.vertices = np.zeros(shape=[self.numOfVertices*2, 3])
            self.faces = np.empty(shape=[0, 3])
        else:
            print("Error: Incorrect format of array given")

    # adds vertices and faces to data structures
    def setVerticesAndFaces(self):
        index = 0
        start = time.time()

        for y in range(self.length):
            for x in range(self.width):
                coord = self.elevationArray[index]

                # each vertex just contains the altitude
                self.vertices[index] = coord # vertex for top of terrain
                self.vertices[index+self.numOfVertices] = [coord[0], coord[1], 0] # vertex for base

                if x != 0 and y != self.length-1:
                    # faces are triangles, and 2 are calculated for each "square" of 4 points
                    # very edge are ignored, as this has no "square" (only in 1 dimension)
                    # faces contain just the index of the vertices at which to make the mesh out of

                    # faces for the top of the terrain
                    self.faces = np.append(self.faces, [[index, index-1, index+self.width-1]], axis=0)
                    self.faces = np.append(self.faces, [[index, index+self.width-1, index+self.width]], axis=0)

                    # faces for the base
                    self.faces = np.append(self.faces, [[self.numOfVertices+index, self.numOfVertices+index+self.width-1, self.numOfVertices+index-1]], axis=0)
                    self.faces = np.append(self.faces, [[self.numOfVertices+index, self.numOfVertices+index+self.width, self.numOfVertices+index+self.width-1]], axis=0)

                index += 1

                # print time every 5000 points made
                if index % 5000 == 0:
                    print(f'Index: {index}, time: {time.time()-start}')
                    start = time.time()
    
    # making faces for the vertical edges (in-between top and bottom, for the very edge)
    def setEdgeFaces(self):
        n = self.numOfVertices # so the code is more readable
        w = self.width

        #south edge
        for x in range(1, w):
            self.faces = np.append(self.faces, [[x, n+x-1, x-1]], axis=0)
            self.faces = np.append(self.faces, [[x, n+x, n+x-1]], axis=0)

        #north edge
        for x in range(n-w+1, n):
            self.faces = np.append(self.faces, [[x, x-1, n+x-1]], axis=0)
            self.faces = np.append(self.faces, [[x, n+x-1, n+x]], axis=0)

        #west edge
        for y in range(w, n, w):
            self.faces = np.append(self.faces, [[y, y-w, n+y-w]], axis=0)
            self.faces = np.append(self.faces, [[y, n+y-w, n+y]], axis=0)

        #east edge
        for y in range(2*w-1, n, w):
            self.faces = np.append(self.faces, [[y, n+y-w, y-w]], axis=0)
            self.faces = np.append(self.faces, [[y, n+y, n+y-w]], axis=0)

    # edited from https://pythonhosted.org/numpy-stl/usage.html#creating-mesh-objects-from-a-list-of-vertices-and-faces
    def createMesh(self):
        terrain = mesh.Mesh(np.zeros(self.faces.shape[0], dtype=mesh.Mesh.dtype))

        for i, f in enumerate(self.faces):
            for j in range(3):
                terrain.vectors[i][j] = self.vertices[int(f[j]),:]

        return terrain
    
    # saves the file 
    def saveFile(self, fileName="terrain"):
        self.setVerticesAndFaces()
        print("Vertices and Faces set")
        self.setEdgeFaces()
        print("Edges set")

        terrain = self.createMesh()
        print("Mesh made")

        # saves to separate folder
        filePath = os.path.dirname(os.path.abspath(__file__)) + '\\3dObjects\\' + fileName + '.stl'
        terrain.save(filePath)
        print(f'Saved terrain to {filePath}')