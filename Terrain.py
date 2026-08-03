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
        
        # Use a standard Python list for fast appends
        faces_list = [] 

        for y in range(self.length):
            for x in range(self.width):
                coord = self.elevationArray[index]

                self.vertices[index] = coord 
                self.vertices[index+self.numOfVertices] = [coord[0], coord[1], 0] 

                if x != 0 and y != self.length-1:
                    # Append flat lists of triangles directly to our Python list
                    faces_list.append([index, index-1, index+self.width-1])
                    faces_list.append([index, index+self.width-1, index+self.width])

                    faces_list.append([self.numOfVertices+index, self.numOfVertices+index+self.width-1, self.numOfVertices+index-1])
                    faces_list.append([self.numOfVertices+index, self.numOfVertices+index+self.width, self.numOfVertices+index+self.width-1])

                index += 1

                if index % 50000 == 0: # Increased log interval since it will run much faster
                    print(f'Index: {index}, time: {time.time()-start}')
                    start = time.time()
                    
        # Convert to numpy array exactly once
        self.faces = np.array(faces_list)
    
    # making faces for the vertical edges (in-between top and bottom, for the very edge)
    def setEdgeFaces(self):
        n = self.numOfVertices 
        w = self.width
        
        edge_faces_list = []

        # south edge
        for x in range(1, w):
            edge_faces_list.extend([[x, n+x-1, x-1], [x, n+x, n+x-1]])

        # north edge
        for x in range(n-w+1, n):
            edge_faces_list.extend([[x, x-1, n+x-1], [x, n+x-1, n+x]])

        # west edge
        for y in range(w, n, w):
            edge_faces_list.extend([[y, y-w, n+y-w], [y, n+y-w, n+y]])

        # east edge
        for y in range(2*w-1, n, w):
            edge_faces_list.extend([[y, n+y-w, y-w], [y, n+y, n+y-w]])
            
        # Concatenate the new edge faces to the existing faces array
        self.faces = np.concatenate((self.faces, np.array(edge_faces_list)), axis=0)

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