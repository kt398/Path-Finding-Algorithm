# Ai_Assignment1
Group project for intro to Ai assignment 1
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
# INSTRUCTIONS:
(Requires pygame, tkinter, and packages for monitoring resource usage)

  * Launch using Astar_menu.py

  * Generate Map: clicking this creates a new map
  * Export Map: Opens save as dialog to save the current map in text file
  * Import Map: Opens file dialog to select which map file to load
  * Generate Endpoints: Make new random endpoints for the map
  * Run Algorithm: Calculates the shortest path using the selected A*
    settings, or the default settings.
  * Reset map: Clears the map of the previous algorithm effects
  * Get Cell Values: Clicking this activates "Cell Values" mode, where you
    can now click on any cell to view its h,g,f values in the terminal. (CLICK MIDDLE MOUSE ON THE GRID TO EXIT THIS MODE)
  * Run benchmark test: Is only used for the purpose of writing the final report for the project

  Settings:
    * input weight field: input a weight and click update
    * Select cost variant: use the list to select which type of cost function
      you want the program to use to run the algorithm, then click update
    * Select Heuristic: Use the list to select the heuristic you want the algorithm
      to use, then click update. (Note: Using Sequential H Algo will use a separate algorithm,
         weights for this cannot currently be changed)

 ** When you wish to exit this program properly, exit by closing the A* Menu to avoid causing the program to hang **
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
# ISSUES:
There are currently some obvious issues with the code that have not yet been addressed.

* Runtime seems to always increase when outputting to the terminal on every iteration of the algorithm.
  This is clearly is not accurate since visibly the runtime doesn't actually change much. This means the
  runtime value is simply adding to itself on every run. (THIS WAS ACCOUNTED FOR IN THE REPORT)

* THE USE OF MEMORY TRACKING HAS INCREASED THE RUNTIME RATHER SIGNIFICANTLY.

* After running sequential algorithm, using get_cell_values() will not show any data (Only normal A* has this functionality)

* If you generate a new map without generating new endpoints, the algorithm will use the last values but not show the points
  on the map. Algorithm will still run. 
