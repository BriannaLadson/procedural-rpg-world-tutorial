from tkinter import *
from terraforge import *

import entities

class TileMap(Canvas):
	def __init__(self, parent, game):
		super().__init__(parent, highlightthickness=2, highlightbackground="black")
		
		self.game = game
		self.player = game.player
		
		self.generator = game.current_map_generator
		
		self.min_tiles = 11
		self.max_tiles = 51
		
		self.map_size = 11
		
		self.tiles = []
		
		self.location_items = []
		
		self.building_items = []
		
		self.bind("<Configure>", self.update_map)
		
	def update_map(self, event=None):
		self.update_idletasks()
		
		self.generator = self.game.current_map_generator
		
		self.draw_tiles()
		
		self.draw_buildings()
		
		self.draw_locations()
		
		self.draw_player()
		
	def draw_tiles(self):
		width = self.winfo_width()
		height = self.winfo_height()
		
		tile_width = width / self.map_size
		tile_height = height / self.map_size
		
		if not self.tiles:
			self.delete("tile")
			
			for sy in range(self.map_size):
				row = []
				
				for sx in range(self.map_size):
					tile = self.create_rectangle(
						0, 0,
						0, 0,
						tags="tile",
						outline="black",
						width=2,
					)
					
					row.append(tile)
					
				self.tiles.append(row)
				
		half = self.map_size // 2
		
		px, py = self.game.get_player_coordinates()
		
		for sy in range(self.map_size):
			for sx in range(self.map_size):
				wx = px - half + sx
				wy = py - half + sy
				
				if isinstance(self.generator, TerraForge):
					wx %= self.generator.map_size
					wy %= self.generator.map_size
					
					color = self.generator.tile_color(wx, wy)
					
				else:
					if (
						0 <= wx < self.generator.map_size
						and 0 <= wy < self.generator.map_size
					):
						color = self.generator.tile_color(wx, wy)
						
					else:
						color = "black"
				
				x0 = sx * tile_width
				y0 = sy * tile_height
				
				rect = self.tiles[sy][sx]
				
				self.coords(
					rect,
					x0, y0,
					x0 + tile_width, y0 + tile_height,
				)
				
				self.itemconfigure(rect, fill=color)
				
	def draw_player(self):
		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size
		
		center = self.map_size // 2
		
		cx = (center + 0.5) * tile_width
		cy = (center + 0.5) * tile_height
		
		font = (
			"TkDefaultFont",
			int(min(tile_width, tile_height) * 0.5),
			"bold"
		)
		
		if not hasattr(self, "player_item"):
			self.player_item = self.create_text(
				cx, cy,
				text="@",
				font=font,
			)
			
		else:
			self.coords(self.player_item, cx, cy)
			
			self.itemconfig(self.player_item, font=font)
			
		self.tag_raise(self.player_item)
		
	def draw_locations(self):
		for item in self.location_items:
			self.delete(item)
			
		self.location_items = []
		
		if not isinstance(self.generator, TerraForge):
			return
			
		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size
		
		half = self.map_size // 2
		
		px, py = self.game.get_player_coordinates()
		
		for sy in range(self.map_size):
			for sx in range(self.map_size):
				wx = (px - half + sx) % self.generator.map_size
				wy = (py - half + sy) % self.generator.map_size
				
				location = self.game.location_map[wy][wx]
				
				if location is None:
					continue
					
				item = self.create_text(
					(sx + 0.5) * tile_width,
					(sy + 0.5) * tile_height,
					text=location.char,
					fill=location.char_color,
					font=(
						"TkDefaultFont",
						int(min(tile_width, tile_height) * 0.5),
						"bold"
					),
				)
				
				self.location_items.append(item)
				
				self.tag_raise(item)
				
	def draw_buildings(self):
		for item in self.building_items:
			self.delete(item)
			
		self.building_items = []
		
		if not hasattr(self.generator, "buildings"):
			return
			
		tile_width = self.winfo_width() / self.map_size
		tile_height = self.winfo_height() / self.map_size
		
		half = self.map_size // 2
		
		px, py = self.game.get_player_coordinates()
		
		for building in self.generator.buildings:
			screen_x = building["x"] - px + half
			screen_y = building["y"] - py + half
			
			width = building["width"]
			height = building["height"]
			
			right_edge = screen_x + width
			bottom_edge = screen_y + height
			
			if (
				right_edge <= 0
				or bottom_edge <= 0
				or screen_x >= self.map_size
				or screen_y >= self.map_size
			):
				continue
				
			building_item = self.create_rectangle(
				screen_x * tile_width,
				screen_y * tile_height,
				(screen_x + width) * tile_width,
				(screen_y + height) * tile_height,
				fill=building["color"],
				outline="black",
				width=2,
			)
			
			self.building_items.append(building_item)
			door_x, door_y = building["door"]
		
			door_screen_x = door_x - px + half
			door_screen_y = door_y - py + half
			
			if (
				0 <= door_screen_x < self.map_size
				and 0 <= door_screen_y < self.map_size
			):
				door_item = self.create_rectangle(
					door_screen_x * tile_width,
					door_screen_y * tile_height,
					(door_screen_x + 1) * tile_width,
					(door_screen_y + 1) * tile_height,
					fill=self.generator.door_color,
					outline="black",
					width=1,
				)
				
				self.building_items.append(door_item)
		
			
	def zoom_in(self, event=None):
		self.map_size = max(self.min_tiles, self.map_size - 2)
		
		self.tiles = []
		
		self.update_map()
		
	def zoom_out(self, event=None):
		self.map_size = min(self.max_tiles, self.map_size + 2)
		
		self.tiles = []
		
		self.update_map()