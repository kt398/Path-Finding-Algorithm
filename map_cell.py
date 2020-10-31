import pygame
from memory_profiler import profile
from memory_profiler import memory_usage
#import math

WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)
BLUE = (52, 158, 235)
GRBLUE = (46, 86, 115)
RED = (255, 0, 0)
GREEN = (34, 255, 0)

# class MapCell:
#
# 	def __init__(self):
# 		self.blockage = 0 #0 is unblocked, 1 is partially blocked, 2 is blocked
# 		self.river = False

class Cell:
	def __init__(self, col, row, size, tot_cols, tot_rows):
		self.col = col
		self.row = row
		self.x = col * size # Position of the cell based on dimensions of cell (used for drawing)
		self.y = row * size
		self.size = size # dimensions of square cell
		self.color = WHITE # initial state of all cells
		self.tot_cols = tot_cols
		self.tot_rows = tot_rows
		self.successors = []
		self.parent = None
		self.g_val=10000000
		self.h_val=-1
		self.f_val=-1
		self.type=.5#.5=normal,1=hard to traverse,.125=highway,.25=hardtotraversehighway,-1=block
		self.sequential_g_val=[10000000]*5
		self.sequential_f_val=[-1]*5
		self.sequential_h_val=[-1]*5
		self.sequential_parent=[None]*5

	def reset_vals(self):
		self.g_val=10000000
		self.h_val=-1
		self.f_val=-1
		self.parent=None
		self.sequential_g_val=[10000000]*5
		self.sequential_f_val=[-1]*5
		self.sequential_h_val=[-1]*5
		self.sequential_parent=[None]*5
	def __eq__(self,other):
		return not other==None and self.col==other.col and self.row==other.row
	def get_rows(self):
		return self.tot_rows
	def __lt__(self, other):
		return self
	def __str__(self):
		return '[%d,%d]'%(self.col,self.row)
	def __repr__(self):
		return '[%d,%d]'%(self.col,self.row)
	def get_cols(self):
		return self.tot_cols

	def get_successors(self):
		return self.successors

	def set_successors(self, succs):
		self.successors = succs

	def set_parent(self, cell):
		self.parent = cell

	def get_position(self):
		return self.col, self.row

	def set_position(self, c, r):
		self.col = c
		self.row = r

	def get_color(self):
		return self.color

	def set_color(self, clr):

		self.color = clr
		if clr==BLACK:
			self.type=-1
		elif clr==WHITE:
			self.type=.5
		elif clr==GREY:
			self.type=1
		elif clr==BLUE:
			self.type=.125
		elif clr==GRBLUE:
			self.type=.25

	def is_blocked(self):
		if self.color == BLACK:
			return True
		else: return False

	def is_partial_blocked(self):
		if self.color == GREY:
			return True
		else: return False

	def is_highway(self):
		if self.color == BLUE:
			return True
		else: return False

	def is_pb_highway(self):
		if self.color == GRBLUE:
			return True
		else: return False

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))
