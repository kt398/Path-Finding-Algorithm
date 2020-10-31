import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from map_cell import Cell
from grid import Grid
#from memory_profiler import profile
#from memory_profiler import memory_usage
#import line_profiler
import cProfile
import pstats
import io
import os
from guppy import hpy
from datetime import datetime
import pandas as pd
import numpy as np

pr = cProfile.Profile()
#profiler_l = line_profiler.LineProfiler()

LENGTH = 1120
WIDTH = 840
ROWS = 120
COLS = 160

WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
BLUE = (52, 158, 235)
GRBLUE = (46, 86, 115)
RED = (255, 0, 0)
GREEN = (34, 255, 0)
maps_list=['./maps_and_points/map1.txt','./maps_and_points/map2.txt','./maps_and_points/map3.txt','./maps_and_points/map4.txt','./maps_and_points/map5.txt']
startendpoints=['./maps_and_points/se1.txt','./maps_and_points/se2.txt','./maps_and_points/se3.txt','./maps_and_points/se4.txt','./maps_and_points/se5.txt']


map = Grid(COLS, ROWS, WIDTH, LENGTH)
START = (-1,-1) #coordinate of start position (initially doesn't exist)
END = (-1,-1) #coordinate of end position (initially doesn't exist)
color_s = (999,999,999)
color_e = (999,999,999)
PB_CENTERS = [] #coordinate pairs for the partially blocked region centers
heuristic = "Manhattan"
weight = 1
seq_w1 = 2
seq_w2 = 1.75
cost_type = "Variable"

#@profile
def generate_map():
    global PB_CENTERS
    if map.grid == []:
        map.init_grid()
    else:
        map.grid = []
        START = (-1,-1)
        END = (-1,-1)
        map.init_grid()
    print("New Map Generated. . . Start/End Coordinates set to (-1,-1). . .")
    map.addHighways()
    PB_CENTERS = map.addPartiallyBlocked()
    print(f"Centers of partial blocked :: {PB_CENTERS}")
    map.addBlockedCells()
    map.draw_map()
    return


def generate_endpnts():
    global START
    global END
    global color_s
    global color_e

    # print(f"(INITIAL) :: Start: {START}. . . Color: {color_s}")
    # print(f"(INITIAL) :: End: {END}. . . Color: {color_e}")

    if(START == (-1,-1) and END == (-1,-1)):
        s_e_values = map.initStartEndpoints()
        START = s_e_values[0]
        END = s_e_values[1]
        color_s = s_e_values[2]
        color_e = s_e_values[3]
        map.draw_map()
    else:
        #print(START, END)
        map.set_cell_color(START[0], START[1], color_s)
        map.set_cell_color(END[0], END[1], color_e)
        s_e_values = map.initStartEndpoints()
        START = s_e_values[0]
        END = s_e_values[1]
        color_s = s_e_values[2]
        color_e = s_e_values[3]
        map.draw_map()
    print(f"Start/End Generated. . . New Start: ({START[1]},{START[0]}) New End: ({END[1]},{END[0]})")
    return

#@profile
def run_algo_parent():
    if cost_type=="Variable":
        run_algo('',False)
    else:
        run_algo('',True)
    return
def run_algo(map_SE,isUniform):
    #map.astar_algo_2(START, END)
    # heuristic = "Manhattan"
    h = hpy()
    heap_start = h.heap()
    heap_end = heap_start
    #print(f"HEAP SIZE BEFORE ALGO :: {heap_start.size} bytes")
    print("__________________________________________________________________")
    if heuristic == "*Sequential H Algo*":
        print(f"Using Sequential Heuristic Algorithm")
        #map.sequential_astar_algo(START,END,weight,1,1.25)
        #profiler_l.add_function(map.sequential_astar_algo(START,END,weight,1,1.25))
        pr.enable()
        outputs = map.sequential_astar_algo(START,END,weight,seq_w1,seq_w2)
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
        ps.print_stats()
        with open('runtime_dump.txt', 'w+') as f:
            f.write(s.getvalue())
        f.close()
        map.get_screenshot("Sequential_test", "1",weight,isUniform)
        runtime = get_runtime_from_file()
        #print(outputs)
        cells_in_path = outputs[1]
        num_closed = get_num_closed_sequential(outputs[0])
        h_eff = -1
        path_length = min(map.grid[END[0]][END[1]].sequential_g_val)
        print(f"ALGO RUNTIME :: {runtime}s")
        print(f"Path Length = {path_length}")
        print(f"Number of cells along path = {cells_in_path}")
        print(f"Number of closed cells = {num_closed}")
        heap_end = h.heap()
        seq_weight_str = "("+str(seq_w1)+"-"+str(seq_w2)+")"
        # if(map_SE!=''):
        #     map.get_screenshot("Sequential", map_SE,weight,isUniform)
        #print(f"HEAP SIZE AFTER ALGO :: {heap_end.size} bytes")

        #cProfile.run('map.sequential_astar_algo(START,END,weight,1,1.25)')
    else:
        print(f"Using Heuristic :: {heuristic}")
        print(f"Using Weight :: {weight}")
        #profiler_l.add_function(map.kt_astar_algo(START,END,heuristic,weight))
        pr.enable()
        outputs = map.kt_astar_algo(START,END,heuristic,weight,isUniform)
        #print(outputs[1])
        num_closed = get_num_closed(outputs[0])
        cells_in_path = outputs[1]
        h_eff = calc_h_eff(num_closed, cells_in_path)
        path_length = map.grid[END[0]][END[1]].g_val
        print(f"Number of closed cells = {num_closed}")
        print(f"Number of cells along path = {cells_in_path}")
        print(f"Heuristic Efficiency = {h_eff}")
        print(f"Path Length = {path_length}")
        pr.disable()
        #print(f"ALGO MEMORY USAGE ==> {mem} MiB")
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
        ps.print_stats()
        with open('runtime_dump.txt', 'w+') as f:
            f.write(s.getvalue())
        #f = open('runtime_dump.txt', 'r')
        f.close()
        if(map_SE!=''):
            map.get_screenshot(heuristic, map_SE,weight,isUniform)
        runtime = get_runtime_from_file()
        print(f"ALGO RUNTIME :: {runtime}s")
        heap_end = h.heap()
        #print(f"HEAP SIZE AFTER ALGO :: {heap_end.size} bytes")
        #cProfile.run('map.kt_astar_algo(START,END,heuristic,weight)')
    print(f"TOTAL ALGORITHM SPACE :: {heap_end.size - heap_start.size} bytes")
    print("__________________________________________________________________\n")
    return f"{heuristic},{runtime},{heap_end.size - heap_start.size},{num_closed},{h_eff},{path_length}"

#runtime, memoryspace,nodes expanded
def run_get_cell_vals():
    map.get_cell_values(WIDTH)

def reset_map():
    for i in range(160):
        for j in range(120):
            k=map.grid[i][j].type
            map.grid[i][j].reset_vals()
            if k==.5:
                map.set_cell_color(i,j,WHITE)
            elif k==1:
                map.set_cell_color(i,j,GREY)
            elif k==.125:
                map.set_cell_color(i,j,BLUE)
            elif k==.25:
                map.set_cell_color(i,j,GRBLUE)
            elif k==-1:
                map.set_cell_color(i,j,BLACK)
    map.set_cell_color(START[0],START[1],GREEN)
    map.set_cell_color(END[0],END[1],RED)
    map.draw_map()

def write_map():
    white = (255, 255, 255)
    grey = (128, 128, 128)
    black = (0, 0, 0)
    blue = (52, 158, 235)
    navy = (46, 86, 115)
    red = (255, 0, 0)
    green = (34, 255, 0)

    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )

    if not filepath:
        print("Export Error: Not a file path")
        return

    f = open(filepath, "x")
    f.write(f"{START[0]},{START[1]}\n")
    f.write(f"{END[0]},{END[1]}\n")

    f.write(f"{PB_CENTERS[0][0]},{PB_CENTERS[0][1]}\n")
    f.write(f"{PB_CENTERS[1][0]},{PB_CENTERS[1][1]}\n")
    f.write(f"{PB_CENTERS[2][0]},{PB_CENTERS[2][1]}\n")
    f.write(f"{PB_CENTERS[3][0]},{PB_CENTERS[3][1]}\n")
    f.write(f"{PB_CENTERS[4][0]},{PB_CENTERS[4][1]}\n")
    f.write(f"{PB_CENTERS[5][0]},{PB_CENTERS[5][1]}\n")
    f.write(f"{PB_CENTERS[6][0]},{PB_CENTERS[6][1]}\n")
    f.write(f"{PB_CENTERS[7][0]},{PB_CENTERS[7][1]}\n")
    for y in range(120):
        for x in range(160):
            if map.grid[x][y].get_color() == white:
                f.write("1")
            elif map.grid[x][y].get_color() == grey:
                f.write("2")
            elif map.grid[x][y].get_color() == black:
                f.write("0")
            elif map.grid[x][y].get_color() == blue:
                f.write("a")
            elif map.grid[x][y].get_color() == navy:
                f.write("b")
        f.write("\n")

def export_map():
    # Opens filepath dialog
    #-----------------------------------------------
    # CALL FUNCTION TO WRITE MAP DATA TO FILE HERE
    write_map()
    #-----------------------------------------------
    return

def read_se_file(filepath):
    fptr=open(filepath,'r')
    sepoints=[]*10
    for i in range(10):
        line=fptr.readline()
        coords=line.split(',')
        sepoints.append((int(coords[0]),int(coords[1]),int(coords[2]),int(coords[3])))
    fptr.close()
    return sepoints

def getColor(point):
    x=map.grid[point[0]][point[1]].type
    if(x==.125):
        return BLUE
    elif x==.25:
        return GRBLUE
    elif x==.5:
        return WHITE
    elif x==1:
        return GREY
    elif x==-1:
        return BLACK
def benchmarkSetPoints(points):
    global START
    global END
    print(points)
    if(START!=(-1,-1)):
        map.grid[START[0]][START[1]].set_color(getColor(START))
        map.grid[END[0]][END[1]].set_color(getColor(END))
    map.grid[points[0]][points[1]].set_color(GREEN)
    map.grid[points[2]][points[3]].set_color(RED)
    START=(points[0],points[1])
    END=(points[2],points[3])
    return


def loop():
    #algorithm
    global weight
    global heuristic
    h_list=["Manhattan_min","Euclidean_min","Diagonal","Manhattan","Euclidean"]
    global maps_list
    global heuristic
    if not os.path.isdir('./benchmark'):
        os.mkdir('./benchmark')
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")
    if heuristic != "*Sequential H Algo*":
        d = ['Heuristic','Runtime','Memory-Usage','G value','Nodes expanded','Heuristic Efficiency','Map','StartEndpointPair','weight','Uniform?']
        df=pd.DataFrame(columns=d)
        #heuristic, runtime, memoryspace,g_value,nodes expanded,h efficiency
        #f.write('Heuristic,Runtime,Memory-Usage,Nodes expanded,Heuristic Efficiency,Map,StartEndpointPair,weight,Uniform?\n')
        for w in range(4):
            if w==0:
                weight=1
            elif w==1:
                weight=1.5
            elif w==2:
                weight=2
            elif w==3:
                weight=1
            for i in range(5):
                heuristic=h_list[i]
                #map
                for j in range(5):
                    readMap(maps_list[j])
                    startgoal=read_se_file(startendpoints[j])
                    print(startgoal)
                    #start and end points
                    for k in range(10):
                        reset_map()
                        benchmarkSetPoints(startgoal[k])
                        if(w!=3):
                            algo_output=run_algo(f"{j}_{k}",False)
                        else:
                            algo_output=run_algo(f"{j}_{k}",True)
                            f.write(f"{algo_output},{j},{k+1},{weight},{w==3}")
                            f.write('\n')
                            p=algo_output.split(',')
                            new_row={'Heuristic':p[0],'Runtime':p[1],'Memory-Usage':p[2],'G value':p[5],'Nodes expanded':p[3],'Heuristic Efficiency':p[4],'Map':f'{j}','StartEndpointPair':f'{k+1}','weight':f'{weight}','Uniform?':f'{w==3}'}
                            #df2=pd.DataFrame([p[0],p[1],p[2],p[3],p[4],p[5],f'{j}',f'{k+1}',f'{weight}',f'{w==3}'],columns=d)
                            df=df.append(new_row,ignore_index=True)
        df.to_csv(f'benchmark/benchmarkdata_{dt_string}.csv')
    else:
        f=open(f'benchmark/benchmarkdata_{dt_string}.csv','w')
        f.write('Heuristic,Runtime,Memory-Usage,Nodes expanded,Heuristic Efficiency,Path Length (gval),Map,StartEndpointPair,weight,Uniform?\n')
        print("**USING Sequential***")
        for i in range(2):
            if i == 0:
                w1 = 2
                w2 = 1.75
            elif i == 1:
                w1 = 1
                w2 = 2
            for j in range(5):
                readMap(maps_list[j])
                startgoal = read_se_file(startendpoints[j])
                print(startgoal)
                for k in range(10):
                    reset_map()
                    benchmarkSetPoints(startgoal[k])
                    seq_w1 = w1
                    seq_w2 = w2
                    algo_output = run_algo(f"{j}_{k}",False)
                    print(f"Seq_weight 1 == {seq_w1}")
                    print(f"Seq_weight 2 == {seq_w2}")
                    f.write(f"{algo_output},{j},{k+1},{seq_w1}-{seq_w2},False")
                    f.write('\n')
    return


def import_map():
    filepath = askopenfilename(
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        print("Import Error: Not a file path")
        return
    #-----------------------------------------------
    readMap(filepath)
    map.draw_map()
    #-----------------------------------------------
    return

def readMap(filepath):
    global START
    global END
    global PB_CENTERS
    global map
    map=None
    map = Grid(COLS, ROWS, WIDTH, LENGTH)
    PB_CENTERS=[[0 for j in range(2)] for i in range(8)]
    map.init_grid()
    f = open(filepath, "r")
    line=f.readline()
    coords=line.split(",")
    START=(int(coords[0]),int(coords[1]))
    print(START)
    line=f.readline()
    coords=line.split(",")
    END=(int(coords[0]),int(coords[1]))
    print(END)
    i=0
    while i<8:
        line=f.readline()
        coords=line.split(",")
        PB_CENTERS[i]=[int(coords[0]),int(coords[1])]
        i+=1
    i=0
    j=0
    while i<120:
        line=f.readline()
        while j<160:
            c=line[j]
            if c=='0':
                map.set_cell_color(j,i,BLACK)
            elif c=='1':
                map.set_cell_color(j,i,WHITE)
            elif c=='2':
                map.set_cell_color(j,i,GREY)
            elif c=='a':
                map.set_cell_color(j,i,BLUE)
            elif c=='b':
                map.set_cell_color(j,i,GRBLUE)
            j+=1
        i+=1
        j=0
    map.set_cell_color(START[0],START[1],GREEN)
    map.set_cell_color(END[0],END[1],RED)

def get_runtime_from_file():
    f = open('./runtime_dump.txt', 'r')
    line = f.readline()
    #print(line)
    l = line.split()
    #print(l[7])
    return l[7]

def get_num_closed(closed):
    count = 0
    #print(closed)
    for i in range(120):
        for j in range(160):
            if closed[j][i] > 0:
                count+=1
    return count

def get_num_closed_sequential(closed):
    count = 0
    #print(closed)
    for i in range(120):
        for j in range(160):
            for k in range(5):
                if closed[k][j][i] > 0:
                    count+=1
    return count

def calc_h_eff(num_closed, num_on_path):
    return num_on_path/num_closed

window = tk.Tk()
window.title("A* Menu")
frame_left = tk.Frame(window)
frame_right = tk.Frame(window)
frame_mid = tk.Frame(window, width = 200)
frame_bot = tk.Frame(window)
window.resizable(width=False, height=False)

window.rowconfigure(0, weight=1)
window.columnconfigure(1, weight=1)

frame_left.grid(row = 0, column=0, sticky="ew")
frame_mid.grid(row=0, column=1)
frame_right.grid(row = 0,column=2, sticky="ew")
frame_bot.grid(row = 1, column=0, sticky="ew")

btn_benchmark=tk.Button(master=frame_left,text="Run Benchmark Test", command=loop)
btn_gen_map = tk.Button(master=frame_left, text = "Generate Map", command = generate_map)
btn_export = tk.Button(master=frame_left, text = "Export Map", command = export_map)
btn_import = tk.Button(master=frame_left, text = "Import Map", command = import_map)
btn_endpnts = tk.Button(master=frame_left, text = "Generate Endpoints", command = generate_endpnts)
btn_run = tk.Button(master=frame_left, text = "Run Algorithm", command = run_algo_parent)
btn_reset = tk.Button(master=frame_left, text = "Reset Map", command = reset_map)
btn_cell_vals = tk.Button(master = frame_left, text = "Get Cell Values", command = run_get_cell_vals)

weight_entry = tk.Entry(master=frame_bot)
weight_lab = tk.Label(master=frame_bot, text= "Input Weight:")
def update_weight():
    global weight
    weight = float(weight_entry.get())
btn_update_weight = tk.Button(master=frame_bot, text = "Update Weight", command = update_weight)

h_select_lst = tk.Listbox(master= frame_right)
h_val = tk.Entry(master=frame_right)
h_label = tk.Label(master = frame_right,text = "Selected Heuristic:")
h_val.insert(0,heuristic)
Listvalues = ["*Sequential H Algo*","Manhattan","Manhattan_min","Euclidean","Euclidean_min","Diagonal","Diagonal_min"]
for item in Listvalues:
    h_select_lst.insert(0,item)
def update_selection():
    global heuristic
    new_h = h_select_lst.curselection()
    heuristic = h_select_lst.get(new_h)
    h_val.delete(0,tk.END)
    h_val.insert(0,heuristic)
btn_update_selection = tk.Button(master=frame_right, text="Update Heuristic Selection", command = update_selection)

cost_select_lst = tk.Listbox(master = frame_mid)
c_val = tk.Entry(master=frame_mid)
c_label = tk.Label(master=frame_mid, text = "Selected Cost Variant")
c_val.insert(0,cost_type)
cost_values = ["Uniform Cost", "Variable"]
for item in cost_values:
    cost_select_lst.insert(0,item)
def update_cost():
    global cost_type
    new_c = cost_select_lst.curselection()
    cost_type = cost_select_lst.get(new_c)
    c_val.delete(0,tk.END)
    c_val.insert(0,cost_type)
btn_update_cost = tk.Button(master=frame_mid, text = "Update Cost Type", command = update_cost)
# h_select_lst.insert(1,"Manhattan")
# h_select_lst.insert(2,"Manhattan_min")
# h_select_lst.insert(3,"Euclidean")
# h_select_lst.insert(4,"Euclidean_min")
# h_select_lst.insert(5,"Diagonal")
# h_select_lst.insert(6,"Diagonal_min")



btn_gen_map.grid(row=0, column=1, pady=10)
btn_export.grid(row=1, column=1, pady=10)
btn_import.grid(row = 2, column=1, pady = 10)
btn_endpnts.grid(row = 3, column=1, pady=10)
btn_run.grid(row=4, column=1, pady = 10)
btn_reset.grid(row=5, column=1, pady = 10)
btn_cell_vals.grid(row = 6, column=1, pady = 10)
h_select_lst.grid(row=0, column = 2, pady = 1)
h_label.grid(row=2, column=2)
h_val.grid(row=3,column=2,pady=1)
btn_update_selection.grid(row=1,column=2,pady=1)
weight_lab.grid(row=0,column=0, pady = 1)
weight_entry.grid(row=1, column=0, pady = 1)
btn_update_weight.grid(row=1, column=2, pady = 1)

btn_benchmark.grid(row=7,column=1,pady=1)
cost_select_lst.grid(row=0)
c_label.grid(row=1)
c_val.grid(row=2)
btn_update_cost.grid(row=3)
window.mainloop()
