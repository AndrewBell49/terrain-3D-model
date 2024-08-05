# terrain-3D-model
A project which creates a 3D model (.stl) out of elevation data, as a visualisation of terrain

Currently the only countries this works with are the UK and Switzerland

UK data is got from Ordnance Survey (https://osdatahub.os.uk/downloads/open/Terrain50)
A good guide to understanding how os grid references work: https://getoutside.ordnancesurvey.co.uk/guides/beginners-guide-to-grid-references/

Switzerland data is got from Swiss Topo (https://www.swisstopo.admin.ch/en/geodata/height/dhm25.html)
The file will need to be downloaded from here, and copied into the /Switzerland directory, as the file is too big for github

The Terrain class can be used for any data, as long as it is read in the correct way
This format is a numpy array, containing an array of 3 elements: the x and y coordinate, and then the elevation [x, y, elevation]