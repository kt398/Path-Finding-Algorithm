import pygame
import math
import random
from queue import PriorityQueue
import heapq
from map_cell import Cell
#import memory_profiler
#from memory_profiler import profile
#from memory_profiler import memory_usage

#from memory_profiler import profile
#import line_profiler

#mem_prof = memory_profiler.MemoryProfiler()

# WINDOW SIZE IN PIXELS
LENGTH = 1120
WIDTH = 840
#----------------------

WINDOW = pygame.display.set_mode((LENGTH, WIDTH))
pygame.display.set_caption("A* Algorithm")

WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
BLUE = (52, 158, 235)
GRBLUE = (46, 86, 115)
RED = (255, 0, 0)
GREEN = (34, 255, 0)

maps=['map1.txt','map2.txt','map3.txt','map4.txt','map5.txt']
startendpoints=['se1.txt','se2.txt','se3.txt','se4.txt','se5.txt']
fringe = []
closed_set = {None}
h_list=["Manhattan_min","Euclidean_min","Diagonal","Manhattan","Euclidean"]


# Heuristic using manhattan distance between points
# crnt --> start Point (x1,y1)
# end --> end Point (x2,y2)
def h_manhat(crnt, end):
    x1 = crnt[0]
    y1 = crnt[1]
    x2 = end[0]
    y2 = end[1]
    return abs(x1-x2) + abs(y1-y2)

class Grid:
    #@profile
    def __init__(self, cols, rows, size_x, size_y):
        #initialize grid:
        self.grid = []
        self.cols = cols
        self.rows = rows
        self.size_x = size_x
        self.size_y = size_y

    def get_cols(self):
        return self.cols

    def get_rows(self):
        return self.rows

    def get_size_x(self):
        return self.size_x

    def get_size_y(self):
        return self.size_y

    def get_grid(self):
        return self.grid

    # SET COLOR OF A PARTICULAR CELL IN GRID
        # note row and col are a bit wonky for some reason, they seem flipped
    def set_cell_color(self, y, x, color):
        col = y
        row = x
        #print('COL,ROW:%d,%d'%(col,row))
        self.grid[col][row].set_color(color)

    # LOADS GRID WITH CELLS:
    #   - i --> Rows
    #   - j --> Columns
    def init_grid(self):
        cols = self.cols

        rows = self.rows
        size_x = self.size_x
        size_y = self.size_y
        gap = size_x // rows
        for i in range(cols):
            self.grid.append([])
            for j in range(rows):
                cell = Cell(i, j, gap, cols, rows)
                #CHANGED THIS
                self.grid[i].append(cell)
                #print(f"{i},{j}")
        print(f"Cols:{len(self.grid)}")
        return self.grid

    def draw_grid_lines(self, win, cols, rows, size_x, size_y):
        # gap = size_y // cols
        gap = size_x // rows
        for i in range(rows):
            # DRAWS HORIZONTAL LINES:
            pygame.draw.line(win, GREY, (0, i * gap), (size_y, i * gap))
            for j in range(cols):
                # DRAWS VERTICAL LINES:
                pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, size_x))

    def draw_map(self):
        win = WINDOW
        grid = self
        win.fill(WHITE)
        # rows = self.get_rows()
        # cols = self.get_cols()
        # size_x = self.get_size_x()
        # size_y = self.get_size_y()
        rows = grid.get_rows()
        cols = grid.get_cols()
        size_x = grid.get_size_x()
        size_y = grid.get_size_y()
        for row in grid.grid:
            for cell in row:
                cell.draw(win)
        grid.draw_grid_lines(win, cols, rows, size_x, size_y)
        pygame.display.update()

    def importMap(self, filepath):
        return

    def exportMap(self, filepath):
        return


    # This funciton adds blocked cells to the grid.
    # Starts by initializing an int array of size 19200(total # of cells)
    # Randomly selects 3840 cells from the list and marks them as blocks
    # Moves the number corresponding to selected cells to the end of the list so they are not selected twice
    def addBlockedCells(self):
        l=list(range(0,19200))
        #print(len(l))
        #print(l[19199])
        totalSelected=0
        x=0
        while totalSelected<3840:
            rand=random.randint(0,19199-x)
            y=l[rand]
            row=(y)//160
            col=y-(row*160)
            l[y],l[19199-x]=l[19199-x],l[y]
            if not(self.grid[col][row].is_highway() or self.grid[col][row].is_pb_highway()):
                self.grid[col][row].set_color(BLACK)
                totalSelected+=1
            x+=1
        return
    # This function selects 8 random coordinates and makes half of the cells in the 31x31 box around the selected coordinate partially blocked
    def addPartiallyBlocked(self):
        l=list(range(0,19200))
        center=[[0 for j in range(2)] for i in range(8)]
        totalSelected=0
        x=0
        # While loop selects 8 random coordinates and makes sure that they are all unique.
        # Coordinates are stored in center
        while totalSelected<8:
            rand=random.randint(0,19199-x)
            y=l[rand]
            #print(y)
            row=(y)//160
            col=y-(row*160)
            center[totalSelected][0]=col
            center[totalSelected][1]=row
            l[y],l[19199-x]=l[19199-x],l[y]
            totalSelected+=1
        #print(center)
        # Nested for loop goes through the 31x31 box around each coordinate pair
        # Sets half of the cells in the box to be partially blocked
        for i in range (0,8):
            #rows
            for j in range (max(0,center[i][1]-15),min(119,center[i][1]+16)):
                #columns
                for k in range (max(0,center[i][0]-15),min(159,center[i][0]+16)):
                    tf=random.randint(0,1)
                    if(tf==1):
                        if not(self.grid[k][j].is_pb_highway()):
                            if(self.grid[k][j].is_highway()):
                                #CHANGE TO BLUE GREY
                                self.grid[k][j].set_color(GRBLUE)
                            else:
                                self.grid[k][j].set_color(GREY)
        return center

    # Main highway generation method
    # Makes lists of tuples that are coordinates for the highways
    # Colors cells on the grid based on that
    def addHighways(self):

        highway_1 = []
        highway_2 = []
        highway_3 = []
        highway_4 = []

        while(highway_1 == []):
            highway_1.append(Grid.highwayStartpoint()) # first value is start point along boundary
            highway_1 = Grid.makeHighwayPaths(highway_1,highway_2,highway_3,highway_4)

        # makeHighwayPaths returns empty list if the highway isn't possible, so it loops and tries new startpoints until it works
        while(highway_2 == []):
            highway_2.append(Grid.highwayStartpoint()) # first value is start point along boundary
            highway_2 = Grid.makeHighwayPaths(highway_2,highway_1,highway_3,highway_4)

        while(highway_3 == []):
            highway_3.append(Grid.highwayStartpoint()) # first value is start point along boundary
            highway_3 = Grid.makeHighwayPaths(highway_3,highway_1,highway_2,highway_4)

        while(highway_4 == []):
            highway_4.append(Grid.highwayStartpoint()) # first value is start point along boundary
            highway_4 = Grid.makeHighwayPaths(highway_4,highway_1,highway_2,highway_3)

        # set cell colors based on the generated coordinates
        for i in highway_1:
            self.set_cell_color(i[0],i[1],(52, 158, 235))
        for i in highway_2:
            self.set_cell_color(i[0],i[1],(52, 158, 235))
        for i in highway_3:
            self.set_cell_color(i[0],i[1],(52, 158, 235))
        for i in highway_4:
            self.set_cell_color(i[0],i[1],(52, 158, 235))


    # Returns a tuple with random coordinates that are on the boundary of the map
    def highwayStartpoint():
        side = random.randint(1,4) # 1-top, 2-right, 3-bottom, 4-left
        if(side == 1 or side == 3): # top or bottom
            col_index = random.randint(0,159)
            if(side == 1):
                row_index = 0
            else:
                row_index = 119
        else: # left or right
            row_index = random.randint(0,119)
            if(side == 4):
                col_index = 0
            else:
                col_index = 159

        return (col_index,row_index)

    # Generates a list of tuple values that are highway coordinates
    # Tries twenty times to make a highway that is at least 100 coordinates and does not hit the other highway
    # After twenty attempts it returns empty list
    # If success then it returns the list of coordinates
    def makeHighwayPaths(highway_1, highway_2, highway_3, highway_4):

        highway_complete = False
        hit_highway = False # use this if a highway hits into another highway
        hit_boundary = False # if highway hits boundary

        # counts how many times a highway fails
        failed_attempts = 0 # if a highway fails numerous times it needs a new startpoint

        # set direction
        if(highway_1[0][0] == 0):
            direction = "right"
        elif(highway_1[0][0] == 159):
            direction = "left"
        elif(highway_1[0][1] == 0):
            direction = "down"
        else:
            direction = "up"

        # this loop breaks if the highway hits a boundary and the constraints are satisfied
        while(not highway_complete):

            # move twenty in the given direction
            for j in range(20):
                if(direction == "down"): # top wall, move down
                    new_index = (highway_1[len(highway_1)-1][0], highway_1[len(highway_1)-1][1]+1)
                elif(direction == "left"): # right wall, move left
                    new_index = (highway_1[len(highway_1)-1][0]-1, highway_1[len(highway_1)-1][1])
                elif(direction == "up"): # bottom wall, move up
                    new_index = (highway_1[len(highway_1)-1][0], highway_1[len(highway_1)-1][1]-1)
                elif(direction == "right"): # left wall, move right
                    new_index = ((highway_1[len(highway_1)-1][0]+1, highway_1[len(highway_1)-1][1]))

                # check if there's already a highway there
                if(new_index in highway_1 or new_index in highway_2 or new_index in highway_3 or new_index in highway_4):
                    hit_highway = True
                    break

                highway_1.append(new_index)

                # check if a boundary has been reached
                if(new_index[0] == 0 or new_index[0] == 159 or new_index[1] == 0 or new_index[1] == 119):
                    hit_boundary = True
                    break

            # if the highway hasn't broken any rules, then randomly change direction and continue
            if(not hit_highway and not hit_boundary):
                change_direction = random.randint(1,4)
                if(change_direction == 1):
                    direction_change = random.randint(1,2)
                    if(direction == "up" or direction == "down"):
                        if(direction_change == 0):
                            direction = "left"
                        else:
                            direction = "right"
                    else:
                        if(direction_change == 0):
                            direction = "up"
                        else:
                            direction = "down"
                continue

            # if length is less than 100 or a highway has been hit then reset
            if len(highway_1) < 100 or hit_highway:

                failed_attempts = failed_attempts + 1
                if failed_attempts > 20:
                    return []

                hit_highway = False
                highway_1 = highway_1[0:20] # slice array to first 20 elements (those will always be the same)

                # reset direction
                if(highway_1[0][0] == 0):
                    direction = "right"
                elif(highway_1[0][0] == 159):
                    direction = "left"
                elif(highway_1[0][1] == 0):
                    direction = "down"
                else:
                    direction = "up"

            else: # has not hit highway and it is long enough
                return highway_1


    def initStartEndpoints(self):

        #keep track of original color of cells
        color_s = ()
        color_e = ()

        start_top = random.randint(0,1) # randomly decide if start will be top or bottom
        end_top = random.randint(0,1)   # ^^^ for endpoint

        if(start_top == 1):
            row = random.randint(0,20)
        else:
            row = random.randint(100,119)
        col = random.randint(0,20)
        self.start = (col,row)
        color_s = self.grid[col][row].get_color()

        if(end_top == 1):
            row = random.randint(0,20)
        else:
            row = random.randint(100,119)
        col = random.randint(140,159)
        self.end = (col,row)
        color_e = self.grid[col][row].get_color()

        # color start and end yellow
        self.set_cell_color(self.start[0],self.start[1],GREEN)
        self.set_cell_color(self.end[0],self.end[1],RED)
        #print(color_s, color_e)
        return (self.start, self.end, color_s, color_e)


    def set_successors(self, point):
        cell = self.grid[point[1]][point[0]]
        succs = []
        cell_pos = cell.get_position()
        if cell_pos[1] < cell.get_rows() - 1 and not(self.grid[cell_pos[1] + 1][cell_pos[0]].is_blocked()): # RIGHT
            #print(1)
            succs.append(self.grid[cell_pos[1] + 1][cell_pos[0]])
        if cell_pos[1] < cell.get_rows() - 1 and cell_pos[0] > 0 and not(self.grid[cell_pos[1] - 1][cell_pos[0] + 1].is_blocked()): # BOTTOM-LEFT
            print(1)
            succs.append(self.grid[cell_pos[1] - 1][cell_pos[0] + 1])
        if cell_pos[1] > 0 and not(self.grid[cell_pos[1] - 1][cell_pos[0]].is_blocked()): #LEFT
            #print(2)
            succs.append(self.grid[cell_pos[1] - 1][cell_pos[0]])
        if cell_pos[1] > 0 and cell_pos[0] > 0 and not(self.grid[cell_pos[1] - 1][cell_pos[0] - 1].is_blocked()): #
            print(2)
            succs.append(self.grid[cell_pos[1] - 1][cell_pos[0] - 1])
        if cell_pos[1] < cell.get_rows() - 1 and not(self.grid[cell_pos[1]][cell_pos[0] + 1].is_blocked()): # DOWN
            #print(3)
            succs.append(self.grid[cell_pos[1]][cell_pos[0]+1])
        if cell_pos[1] > 0 and not(self.grid[cell_pos[1]][cell_pos[0] -1].is_blocked()): # UP
            #print(4)
            succs.append(self.grid[cell_pos[1]][cell_pos[0] -1])
        # if cell_pos[1] > 0 and cell_pos[0] > 0 and not(self.grid[cell_pos[1] - 1][cell_pos[0] - 1].is_blocked()):
        #     succs.append(self.grid[cell_pos[1]-1][cell_pos[0] -1])
        cell.set_successors(succs)
        #print(cell.get_successors())
        for s in succs:
            print(s.get_position(), s.get_color())
        return

    # Returns the list of adjacent cells to the cell S.
    # If the cell is blocked, it is not added to the list
    # Maximum size=8
    def getAdjacentCells(self, point):
        adjacent=[]
        #col,row = cell.get_position()
        col = point[0]
        row = point[1]
        # iterate through the coordinates in the 3x3 area surrounding the cell
        for i in range(3):
            for j in range(3):
                if(i == 1 and j == 1): # the current cell is self, don't check
                    #print(f"({i},{j}) is self")
                    continue
                if(col-1+i > 159 or col-1+i < 0 or row-1+j > 119 or row-1+j < 0): # index out of bounds, don't check
                    #print(f"({i},{j}) OUT OF BOUNDS")
                    continue
                if(self.grid[col-1+i][row-1+j].is_blocked()): # cell is black don't add
                    #print(f"({i},{j}) is BLOCKED")
                    #self.grid[row-1+j][col-1+i].set_color(RED)
                    #self.draw_map()
                    continue
                #print(f"({i},{j}) is VALID")
                adjacent.append((col-1+i,row-1+j))

        # for s in adjacent:
        #     print(s, self.grid[s[1]][s[0]].get_color())
        #self.grid[row][col].set_successors(adjacent)
        return adjacent
        # adjacent=[]
        # #col,row = cell.get_position()
        # col = point[0]
        # row = point[1]
        # #print(f"col: {col} Row: {row}")
        #
        # # iterate through the coordinates in the 3x3 area surrounding the cell
        # for i in range(3):
        #     for j in range(3):
        #         if(i == 1 and j == 1): # the current cell is self, don't check
        #             #print(f"({i},{j}) is self")
        #             continue
        #         if(col-1+i > 159 or col-1+i < 0 or row-1+j > 119 or row-1+j < 0): # index out of bounds, don't check
        #             #print(f"({i},{j}) OUT OF BOUNDS")
        #             continue
        #         if(self.grid[row-1+j][col-1+i].is_blocked()): # cell is black don't add
        #             #print(f"({i},{j}) is BLOCKED")
        #             #self.grid[row-1+j][col-1+i].set_color(RED)
        #             #self.draw_map()
        #             continue
        #         #print(f"({i},{j}) is VALID")
        #
        #         adjacent.append((row-1+j,col-1+i))
        #
        # # for s in adjacent:
        # #     self.grid[s[1]][s[0]].set_color((187, 230, 240))
        #
        # return adjacent

    # finds cost to move between two cells
    def find_travel_cost(self,cell_1,cell_2):
        adjacent = False
        if(cell_1.col == cell_2.col or cell_1.row == cell_2.row):
            adjacent = True
        cell_1_cost = 0.5
        cell_2_cost = 0.5
        if(cell_1.color[0] == 128 or cell_1.color[0] == 46): # partially blocked
            cell_1_cost *= 2
        if(cell_2.color[0] == 128 or cell_2.color[0] == 46): # partially blocked
            cell_2_cost *= 2
        if not adjacent: # add cost for being diagonal
            cell_1_cost *= math.sqrt(2)
            cell_2_cost *= math.sqrt(2)
        # check if both cells are highways
        if(cell_1.color[0] == 52 or cell_1.color[0] == 46 and cell_2.color[0] == 52 or cell_2.color[0] == 46):
            cell_1_cost /= 4
            cell_2_cost /= 4
        return cell_1_cost + cell_2_cost

    def find_travel_cost2(self,cell_1,cell_2):
        adjacent = False
        if cell_1.col == cell_2.col or cell_1.row == cell_2.row:
            adjacent = True
        totalType=cell_1.type+cell_2.type
        if adjacent:
            return totalType
        else:
            return math.sqrt(2*(totalType)**2)

    def find_uniform_cost(self,cell_1,cell_2):
        if cell_1.col == cell_2.col or cell_1.row == cell_2.row:
            return 1
        else:
            return math.sqrt(2)

    def travel_cost(self,cell_1,cell_2,isUniform):
        if isUniform:
            return self.find_uniform_cost(cell_1,cell_2)
        return self.find_travel_cost2(cell_1,cell_2)
    def Update_vertex(self, s, sp):
        return

    def astar_algo_2(self, start, end):
        count = 0
        fringe = []
        heapq.heapify(fringe)
        heapq.heappush(fringe, (0, count, start))
        parent = {}
        g = {Cell: float("inf") for row in self.grid for Cell in row}
        g[start] = 0
        f = {Cell: float("inf") for row in self.grid for Cell in row}
        f[start] = h_manhat(start, end)
        print(f"Distance From start to end  == {f[start]}")

        while len(fringe) > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            crnt = heapq.heappop(fringe)[2]
            print(f"CURRENT :: {crnt}")
            if crnt == end:
                print("Path Found")
                return True
            succs = self.getAdjacentCells(crnt)

            for s in succs:
                c = self.grid[s[1]][s[0]]
                new_g = g[crnt] + 1
                print(f"COMPARE {new_g} < {g[c]}")
                if new_g < g[c]:
                    parent[s] = crnt
                    g[s] = new_g
                    f[s] = new_g + h_manhat(s, end)
                    if s not in fringe:
                        count+=1
                        heapq.heappush(fringe, (f[s], count, s))
                        self.grid[s[1]][s[0]].set_color((187, 230, 240))
            self.draw_map()
            if(crnt != start):
                self.grid[crnt[1]][crnt[0]].set_color(RED)
        return False

    def astar_algo(self, start, end):
        global fringe
        if not(start == (-1,-1) and end == (-1,-1)): # Make sure the map has been populated before running algo
            print("Running A* . . .")
            s1 = start[0]
            s2 = start[1]
            e1 = end[0]
            e2 = end[1]
            cell_s = self.grid[s1][s2]
            g = {Cell: float("inf") for row in self.grid for Cell in row} # Give every cell a G-value of infinity
            g[cell_s] = 0 # Start cell has 0 distance to itself
            #print(g)
            cell_s.set_parent(start)
            print(f"start: {start} parent: {self.grid[start[0]][start[1]].parent}")
            fringe = [] # Reinitialize fringe so its empty
            heapq.heapify(fringe)
            f = {Cell: float("inf") for row in self.grid for Cell in row}
            #print(f"Heuristic: {h_manhat(start,end)}")
            f = g[cell_s] + h_manhat(start, end)
            heapq.heappush(fringe, (start, f))
            print(f"FRinge: {fringe}")

            #open_set = {start} # Supplement to the fringe --> Allows for searching/removing elements

            while len(fringe) > 0:
                #point = fringe.get()[0]
                popped = heapq.heappop(fringe)
                point = popped[0]
                print(f"POPPED :: {popped}")
                #open_set.remove(point)
                if point == end:
                    print("Path Found")
                    return "Path Found"
                print(f"Add {point} to closed set***")
                closed_set.add(point)
                self.draw_map()
                self.grid[point[0]][point[1]].set_color((187, 230, 240))

                print(f"CLOSED SET :: {closed_set}")
            #print(cell_s.tot_rows)
                succs = self.getAdjacentCells(point)
                #print(self.grid[point[1]][point[0]].get_successors())
                for sp in succs:
                    #print(f"Succ :: {sp} ---- Current Point :: {point}")
                    if sp not in closed_set:
                        print(f"{sp} Not in closed set!")
                        if sp not in fringe:
                            c = self.grid[sp[0]][sp[1]]
                            g[c] = "inf"
                            c.set_parent(None)
                        # self.Update_vertex(point, sp)
                        # UPDATE VERTEX:
                        c1 = self.grid[point[1]][point[0]]
                        c2 = self.grid[sp[1]][sp[0]]
                        if (h_manhat(start, point) + self.find_travel_cost(c1, c2)) < h_manhat(start, sp):
                            g[c2] = h_manhat(start, point) + self.find_travel_cost(c1, c2)
                            c2.set_parent(c1)
                            if sp in fringe:
                                #open_set.remove(sp)
                                fringe.remove(sp)
                                heapq.heapify(fringe)
                            #fringe.put(sp, g[c2] + h_manhat(sp, end))
                            f = g[c2] + h_manhat(sp, end)
                            print(f"PUSHING :: {(sp,f)}")
                            heapq.heappush(fringe, (sp, f))
                            #self.grid[sp[1]][sp[0]].set_color((142, 204, 133))
                            #self.draw_map()
            print("No Path Found")
            print("A* Concluded . . .")
            return "No Path Found"
        else:
            raise Exception("Start and End points don't exist/Not created yet!!!")
        print("A* Concluded . . .")
        return

    # fp = open('memory_log.txt', 'w+')
    # @profile(stream = fp)
    def kt_astar_algo(self,start_coord,end_coord,h,w,isUniform):
        fptr = open('output.txt', "w")
        fptr.truncate(0)
        fringe=[]
        closed = [[0 for i in range(120)] for j in range(160)]
        start=self.grid[start_coord[0]][start_coord[1]]
        end=self.grid[end_coord[0]][end_coord[1]]
        start.parent=start
        start.g_val=0
        heapq.heapify(fringe)
        start.h_val=self.calculate_h(end,start,h)
        start.f_val=start.h_val
        heapq.heappush(fringe,(self.calculate_f(start,end,start,h),start))
        heapq.heapify(fringe)
        print(fringe)
        print(self.getAdjacentCells((fringe[0][1].col,fringe[0][1].row)))
        closed[start.col][start.row]=1
        print(str(fringe))
        while len(fringe)!=0:
            fptr.write(str(fringe))
            fptr.write('\n')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            s=heapq.heappop(fringe)
            if s[1]==end:
                print('path found')
                cells_in_path = self.create_path(start,end)
                self.draw_map()
                #print(closed)
                return (closed, cells_in_path)
            closed[s[1].col][s[1].row]+=1
            self.set_color_closed(s[1],start_coord ,end_coord)
            #self.draw_map()
            adjacentCells=self.getAdjacentCells((s[1].col,s[1].row))
            #print(f"LENGTH:{len(adjacentCells)}")
            for i in range(len(adjacentCells)):
                current=self.grid[adjacentCells[i][0]][adjacentCells[i][1]]
                #print(f'i,current,currentrow,currentcol{i},{current},{current.col},{current.row}')
                if(closed[current.col][current.row]==0):
                    #print(f'i,current:{i},{current}')
                    #closed[current.col][current.row]=1

                    tf=False
                    if(current.g_val>s[1].g_val+self.travel_cost(s[1],current,isUniform)):
                        self.grid[adjacentCells[i][0]][adjacentCells[i][1]].g_val=s[1].g_val+self.travel_cost(s[1],current,isUniform)
                        self.grid[adjacentCells[i][0]][adjacentCells[i][1]].parent=s[1]
                        fringe=[i for i in fringe if i[1]!=current]
                        heapq.heapify(fringe)
                        f=self.calculate_h(end,current,h)*w+self.grid[adjacentCells[i][0]][adjacentCells[i][1]].g_val
                        current.h_val=self.calculate_h(end,current,h)
                        current.f_val=f
                        heapq.heappush(fringe,(f,current))
                        self.set_color_open(current, start_coord,end_coord)
                        #self.draw_map()
        print('no path found')
        return


    def sequential_f_val(self,end,current,i,w1):
        return current.sequential_g_val[i]+w1*self.calculate_h(end,current,h_list[i])

    def sequential_astar_algo(self,start_coord,end_coord,w,w1,w2):
        open=[[]]*5
        closed=[[[0 for i in range(120)] for j in range(160)]for k in range(5)]

        start=self.grid[start_coord[0]][start_coord[1]]
        end=self.grid[end_coord[0]][end_coord[1]]
        start.parent=start
        for i in range(5):
            start.sequential_parent[i]=start
            start.sequential_g_val[i]=0
            heapq.heapify(open[i])
            start.sequential_h_val[i]=self.calculate_h(end,start,h_list[i])
            start.sequential_f_val[i]=start.sequential_h_val[i]
            heapq.heappush(open[i],(self.calculate_f(start,end,start,h_list[i]),h_list[i],start))
            heapq.heapify(open[i])
        while open[0][0][0]<10000000:
        #for z in range(100):
            for m in range(1,5):
                if(open[m][0][0]<=w2*open[0][0][0]):
                    #print("LOOP1")
                    if(end.sequential_g_val[m]<=open[m][0][0]):
                        print('LOOP2')
                        #Lines 22-24
                        if(end.sequential_g_val[m]<10000000):
                            #finished
                            print('Found path')
                            cells_in_path = self.sequential_create_path(start,end,i)
                            self.draw_map()
                            return closed,cells_in_path
                    #Lines 25-28
                    else:
                        #Expand State in pseudocode
                        s=heapq.heappop(open[m])
                        adjacentCells=self.getAdjacentCells((s[2].col,s[2].row))
                        for x in range(len(adjacentCells)):
                            current=self.grid[adjacentCells[x][0]][adjacentCells[x][1]]
                            #if(closed[i][current.col][current.row]==0):
                            if(current.sequential_g_val[m]>s[2].sequential_g_val[m]+self.find_travel_cost2(current,s[2])):
                                current.sequential_g_val[m]=s[2].sequential_g_val[m]+self.find_travel_cost2(current,s[2])
                                current.sequential_parent[m]=s[2]
                                current.sequential_f_val[m]=self.sequential_f_val(end,current,m,w1)
                                if(closed[m][current.col][current.row]==0):
                                    open[m]=[j for j in open[m] if j[2]!=current]
                                    heapq.heapify(open[m])
                                    heapq.heappush(open[m],(current.sequential_f_val[m],h_list[m],current))
                                    self.set_color_open(current, start_coord,end_coord)
                        #End Expand State
                        closed[m][current.col][current.row]=1
                        self.set_color_closed(current, start_coord,end_coord)

                #Lines 30-36
                else:
                    #print("LOOPING HEREEEEE")
                    if end.sequential_g_val[0]<=open[0][0][0]:
                        if(end.sequential_g_val[0]<10000000):
                            #Finished
                            print("Found path")
                            cells_in_path = self.sequential_create_path(start,end,i)
                            self.draw_map()
                            return closed,cells_in_path
                    #Line 33-36
                    else:
                        s=heapq.heappop(open[0])
                        adjacentCells=self.getAdjacentCells((s[2].col,s[2].row))
                        for x in range(len(adjacentCells)):
                            current=self.grid[adjacentCells[x][0]][adjacentCells[x][1]]
                            #if(closed[0][current.col][current.row]==0):
                            if(current.sequential_g_val[0]>s[2].sequential_g_val[0]+self.find_travel_cost2(current,s[2])):
                                current.sequential_g_val[0]=s[2].sequential_g_val[0]+self.find_travel_cost2(current,s[2])
                                current.sequential_parent[0]=s[2]
                                current.sequential_f_val[0]=self.sequential_f_val(end,current,0,w1)
                                if(closed[0][current.col][current.row]==0):
                                    open[0]=[j for j in open[0] if j[2]!=current]
                                    heapq.heapify(open[0])
                                    heapq.heappush(open[0],(current.sequential_f_val[0],h_list[0],current))
                        closed[0][current.col][current.row]=1
                        self.set_color_closed(current, start_coord,end_coord)
            #print(open)
        print('No Path Found')
        return closed, 0











    def set_color_closed(self, cell, strtpnt,endpnt):
        if not(cell.col == endpnt[0] and cell.row == endpnt[1]) and not(cell.col == strtpnt[0] and cell.row == strtpnt[1]):
            crnt_color = cell.get_color()
            r = max(crnt_color[0] - 10, 0)
            if crnt_color == GREY:
                cell.set_color((254,254,254))
            if crnt_color == WHITE:
                r = 255
            g = max(crnt_color[1] - 30,0)
            b = max(crnt_color[2] - 30,0)
            #print(crnt_color)
            #r = crnt_color[0] - 40
            #g = max(crnt_color[1] - 20,0)
            #b = max(crnt_color[2] - 20,0)
            cell.set_color((255, g, b))

    def set_color_open(self, cell, strtpnt,endpnt):
        if not(cell.col == endpnt[0] and cell.row == endpnt[1]) and not(cell.col == strtpnt[0] and cell.row == strtpnt[1]):
            crnt_color = cell.get_color()
            g = max(crnt_color[1] - 10, 0)
            if crnt_color == GREY:
                cell.set_color((254,254,254))
            if(crnt_color == WHITE):
                g = 255
            r = max(crnt_color[0] - 30,0)
            b = max(crnt_color[2] - 30,0)
            #print(crnt_color)
            # r = max(crnt_color[0] - 40,0)
            # g = max(0,crnt_color[1] - 40)
            cell.set_color((r, g, b))

    def create_path(self,start,end):
        count = 0
        ptr=end
        #print('here')
        while ptr.parent!=start:
            ptr.parent.set_color((255,255,0))
            ptr=ptr.parent
            count += 1
        return count

    def sequential_create_path(self,start,end,i):
        count = 0
        ptr=end
        x=i
        while ptr.sequential_parent[x]==None:
            x=(x+1)%5
        while ptr.sequential_parent[x]!=start:
            ptr.sequential_parent[x].set_color((255,255,0))
            count += 1
            ptr=ptr.sequential_parent[x]
            while ptr.sequential_parent[x]==None:
                x=(x+1)%5
        return count

    def calculate_f(self,start,end,current,heuristic):
        return self.calculate_g(start,current)+self.calculate_h(end,current,heuristic)



    def calculate_h_original(self,end,current):
        return (math.sqrt(abs(end.col-current.col)**2+abs(end.row-current.row)**2))*.25

    # Calculates H based on a given cell and the end cell
    # Uses a heuristic that is determined by the inputted heuristic type
    # Heuristics ---- Euclidean, Manhattan,
    def calculate_h(self,end,current,heuristic):
        x1 = current.col
        y1 = current.row
        x2 = end.col
        y2 = end.row

        # Standard Manhattan distance
        # Assumes unblocked cells but no highways
        # INADMISSIBLE
        if heuristic == "Manhattan":
            return abs(x1-x2) + abs(y1-y2)

        # This version of Manhattan is the cost for if the agent travels
        # along highways for the entirety of the x and y distance on unblocked cells
        # ADMISSIBLE
        elif heuristic == "Manhattan_min":
            return 0.25*(abs(x1-x2) + abs(y1-y2))

        # Straight line distance
        # Assumes unblocked cells but no highway use
        # INADMISSIBLE
        elif heuristic == "Euclidean":
            return(math.sqrt(abs(end.col-current.col)**2+abs(end.row-current.row)**2))

        elif heuristic == "Euclidean_min":
            return(math.sqrt(abs(end.col-current.col)**2+abs(end.row-current.row)**2)*0.25)

        # Shortest possible path if there are no highways or blocked cells
        # Combination of diagonal and straight movement
        elif heuristic == "Diagonal":
            shorter_len = min(abs(x1-x2),abs(y1-y2))
            longer_len = max(abs(x1-x2),abs(y1-y2))
            diagonal_len = math.sqrt(2*shorter_len*shorter_len) # diagonal that travels the entirety of the x or y distances
            straight_len = longer_len-shorter_len # straight part that goes from end of diagonal to goal
            return diagonal_len + straight_len

        # Same as regular diagonal but treats the staight segment as a highway
        elif heuristic == "Diagonal_min":
            shorter_len = min(abs(x1-x2),abs(y1-y2))
            longer_len = max(abs(x1-x2),abs(y1-y2))
            diagonal_len = math.sqrt(2*shorter_len*shorter_len) # diagonal that travels the entirety of the x or y distances
            straight_len = longer_len-shorter_len # straight part that goes from end of diagonal to goal
            return diagonal_len + 0.25*straight_len
        else:
            raise Exception("INVALID HEURISTIC REQUESTED")

    def calculate_g(self,start,current):
        return 1

    def get_clicked_pos(self, position, width):
        gap = width // self.rows
        x, y = position
        row = y // gap
        col = x // gap
        return col, row

    def get_cell_values(self, width):
        print("RUNNING get_cell_values()... Press Middle Mouse to stop ***")
        run = True
        while run:
            #map.draw_map()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    run = False
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    col, row = self.get_clicked_pos(pos, width)
                    print("---------------------------------------")
                    print(f"CLICKED CELL :: ({col},{row})")
                    print(f"    Gval:{self.grid[col][row].g_val}")
                    print(f"    HVal:{self.grid[col][row].h_val}")
                    print(f"    FVal:{self.grid[col][row].f_val}")
                    print("---------------------------------------\n")
                elif pygame.mouse.get_pressed()[1]:
                    run = False
        print("STOPPED RUNNING get_cell_values()")

    #@profile
    def get_screenshot(self, bench_name, index,weight,isUniform):
        if isUniform:
            s="Uniform"
        else:
            s="Variable"

        filename = "screenshot_" +s+"_Weight-"+str(weight)+"_"+bench_name +"_" + index
        filepath = "./Screenshots/" + filename + ".jpg"
        #print(filepath)
        pygame.image.save(WINDOW, filepath)



def main(win, size_x, size_y):
    # ROWS = 12
    # COLS = 16
    # START = (2,2)
    # END = (10,10)
    # map = Grid(COLS, ROWS, size_x, size_y)
    # map.init_grid()
    # map.astar_algo_2(START, END)
    #
    # map.grid[START[1]][START[0]].set_color(GREEN)
    # map.grid[END[1]][END[0]].set_color(RED)
    #map.addHighways()
    #map.addPartiallyBlocked()
    #map.addBlockedCells()
    #grid = map.get_grid()
    #map.initStartEndpoints()
    run = True
    while run:
        #map.draw_map()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                col, row = get_clicked_pos(pos)
                print(f"CLICKED CELL :: ({col},{row})")

    pygame.quit()

#main(WINDOW, WIDTH, LENGTH)
