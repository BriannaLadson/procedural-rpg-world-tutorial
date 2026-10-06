from tkinter import *
from tkinter import ttk

import widgets

class Screen(ttk.Frame):
	def __init__(self, root):
		super().__init__(root)
		self.root = root
		
	def display(self):
		self.pack(fill=BOTH, expand=1)
		
	def hide(self):
		self.pack_forget()
		
class PlayScreen(Screen):
	def __init__(self, root):
		super().__init__(root)
		
		self.game = game = root.game
		self.player = game.player
		
		self.location_var = StringVar(value=f"Location: {game.get_player_location()}")
		
		location_lbl = ttk.Label(self, textvariable=self.location_var, anchor="center")
		location_lbl.pack(fill=X)
		
		self.tile_map = tile_map = widgets.TileMap(self, game)
		self.tile_map.pack(fill=BOTH, expand=1)
		
		root.bind("<+>", tile_map.zoom_in)
		root.bind("<minus>", tile_map.zoom_out)
		
		for key, direction in root.bindings.items():
			root.bind(key, lambda event, direction=direction: self.move(direction))
			
	def move(self, direction):
		self.game.move_player(direction)
		
		self.update_screen()
		
	def update_screen(self):
		self.location_var.set(f"Location: {self.game.get_player_location()}")
		
		self.tile_map.update_map()