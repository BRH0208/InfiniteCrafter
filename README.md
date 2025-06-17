This is a helper script for the game Infinite Craft(https://neal.fun/infinite-craft/)
Given a dataset of recipes, it attempts to find an optimal path to create that item using an A* pathfinding algorithm

How to use: 
1) Run InfiniteCraft.py. 
2) Provide the element you want
3) Wait. Every ten seconds, it will provide debug information, including a number that roughly estimates how much progress it is making

What is this:

Infinitecraft is an "element-combining " game in which two "elements" can be combined to form a new element. This process is AI-generated in the game, leading to thousands of valid recipes. 
This script can find the shortest combinations to make a desired element from the base elements. 
![Garage](https://github.com/user-attachments/assets/3e543a80-0610-4120-ac0e-7be5843644d2)

This problem is interesting, as the search space is extremely large.
It works by first doing a forward pass to get the minimum "depth" of an item. This minimum depth is then used as a heuristic for A* search, which starts from the desired element and works backwards
to find a path to the base elements. The heuristic lets the algorithm assume that a path will take no shorter than the depth of its simplest element, giving the algorithm a sense of "direction" towards simpler states. The path is guaranteed shortest only for combinations included in the dataset. 

This repository contains .pkl files that are saved from pre-processing steps for a large dictionary of valid combinations. 
This speeds up processing, but if you desire to use your own dataset, Encoder.py must be provided 'InfiniteCraft.tsv' as a tab-separated value document in the format of
```
first \t second \t result
first \t second \t result
first \t second \t result
```
With a header line. For example, see included InfiniteCraft.tsv.
