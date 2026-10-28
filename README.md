# 1 - preprep_data

* Import data
  * Greater London boundary
  * Roads
  * Water
  * Landuse (for parks and greenspaces)
* Filter out unecessary roads and greenspaces
* Keep only shapes inside the Greater London boundary
* Output the new shapefiles

# 2 - create_graph

* Split the roads in major, middle and minor roads
* Create a single shape that is the major roads buffered to give them width and output to file
* Create another shape that is all the roads buffered by different amounts and output to file
* Unbuffer the major roads into a multilinestring and output the resulting polygons to file
* Create an adjacency graph from the polygons where each node is a polygon and each edge represents a shared boundary.
Output to file

# 3 - color_graph

* N.B. This notebook uses the sage package and must be run in linux (see instructions below)
* Read in the networkx graph and convert to sage Graph
* Remove edges that are below a certain length. This is required to reduce the complexity of the graph
* Find the most equitable coloring by area or number of nodes. Output to file
* Output the colored adjacency graph

# 4 - create_map

* Import data
  * Single buffered roads shape
  * Polygons
  * Colored adjacency graph
  * Water and greenspace
* Create a colored image and output to jpg


# Steps to install and run sagemath

install ubuntu

run the following commands:

1. Install curl if needed:

```
sudo apt update
sudo apt install curl -y
```

2. Download and run the Miniforge installer:
```
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

3. Reload your shell configuration:
```
source ~/.bashrc
```

4. Install SageMath:
  ```
  conda create -n sage sage python=3.12
  ```

5. Run a sage notebook
```
conda activate sage
sage --version
sage -n jupyter
```