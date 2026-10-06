from terraforge import *
import random
import numpy as np

class Game:
	directions = {
		"north": (0, -1),
		"northwest": (-1, -1),
		"northeast": (1, -1),
		"south": (0, 1),
		"southwest": (-1, 1),
		"southeast": (1, 1),
		"west": (-1, 0),
		"east": (1, 0),
	}
	
	def __init__(self):
		self.overworld_generator = TerraForge()
		self.overworld_generator.generate_noise()
		
		self.overworld_map_size = self.overworld_generator.map_size
		
		self.current_map_generator = self.overworld_generator
		
		self.player = Player()
		
		self.randomize_overworld_coordinates()
		
		self.location_map = np.full(
			(self.overworld_map_size, self.overworld_map_size),
			None,
			dtype=object
		)
		
		self.town_quantity = 50
		self.dungeon_quantity = 50
		
		self.generate_locations(Town, self.town_quantity)
		self.generate_locations(Dungeon, self.dungeon_quantity)
		
	def randomize_overworld_coordinates(self):
		self.player.gx = random.randint(0, self.overworld_map_size - 1)
		self.player.gy = random.randint(0, self.overworld_map_size - 1)
		
	def get_player_location(self):
		player = self.player
		
		location = self.location_map[player.gy][player.gx]
		
		name = location.name if location else "Wilderness"
		
		if player.lx == None:
			return f"{name} ({player.gx}, {player.gy})"
			
		else:
			return f"{name} ({player.lx}, {player.ly}, {player.lz})"
			
	def get_player_coordinates(self):
		if isinstance(self.current_map_generator, TerraForge):
			return self.player.gx, self.player.gy
			
		return self.player.lx, self.player.ly
		
	def move_player(self, direction):
		if direction == "in":
			if self.player.lx is None:
				self.enter_local_map()
				
			elif isinstance(self.local_generator, DungeonMapGenerator):
				self.use_dungeon_stairs()
				
			else:
				self.exit_local_map()
				
		elif self.player.lx is None:
			self.move_player_overworld(direction)
			
		else:
			self.move_player_local(direction)
		
	def move_player_overworld(self, direction):
		player = self.player
		
		dx, dy = self.directions[direction]
		
		player.gx += dx
		player.gy += dy
		
		player.gx %= self.overworld_map_size
		player.gy %= self.overworld_map_size
		
		player.last_overworld_direction = direction
		
	def enter_local_map(self):
		player = self.player
		
		seed = player.gy * self.overworld_map_size + player.gx + 1
		
		biome_color = self.overworld_generator.tile_color(player.gx, player.gy)
		
		location = self.location_map[player.gy][player.gx]
		
		if isinstance(location, Town):
			self.local_generator = TownMapGenerator(biome_color, seed)
			
		elif isinstance(location, Dungeon):
			self.local_generator = DungeonMapGenerator(seed)
			
		else:
			self.local_generator = LocalMapGenerator(biome_color, seed)
		
		size = self.local_generator.map_size
		
		mid = size // 2
		
		if isinstance(self.local_generator, DungeonMapGenerator):
			player.lx, player.ly = self.local_generator.entrance
			player.lz = 0
			
		else:
			entrances = {
				"north": (mid, size - 1),
				"northwest": (size - 1, size - 1),
				"northeast": (0, size - 1),
				"south": (mid, 0),
				"southwest": (size - 1, 0),
				"southeast": (0, 0),
				"west": (size - 1, mid),
				"east": (0, mid),
			}
			
			player.lx, player.ly = entrances.get(player.last_overworld_direction, (mid, mid))
			
			player.lx, player.ly = self.local_generator.get_nearest_walkable_tile(
				player.lx,
				player.ly,
			)
			player.lz = 0
		
		self.current_map_generator = self.local_generator
		
	def exit_local_map(self):
		self.current_map_generator = self.overworld_generator
		
		self.player.lx = self.player.ly = self.player.lz = None
		
	def move_player_local(self, direction):
		dx, dy = self.directions[direction]
		
		player = self.player
		
		x = player.lx + dx
		y = player.ly + dy
		
		if not self.local_generator.validate_coordinates(x, y):
			self.exit_local_map()
			
		elif self.local_generator.is_walkable(x, y):
			player.lx = x
			player.ly = y
		
	def generate_locations(self, location_class, quantity):
		for number in range(1, quantity + 1):
			gx = random.randint(0, self.overworld_map_size - 1)
			gy = random.randint(0, self.overworld_map_size - 1)
			
			if self.location_map[gy][gx] is None:
				self.location_map[gy][gx] = location_class(gx, gy, number)
				
	def use_dungeon_stairs(self):
		player = self.player
		
		dungeon = self.local_generator
		
		tile = dungeon.tile_at(player.lx, player.ly)
		
		if tile == DungeonForge.UP:
			if player.lz == 0:
				self.exit_local_map()
				
			else:
				player.lz -= 1
				
				dungeon.set_level(player.lz)
				
		elif (tile == DungeonForge.DOWN and player.lz < len(dungeon.map_array) - 1):
			player.lz += 1
			
			dungeon.set_level(player.lz)
		
class MapGenerator:
	def __init__(self, seed, map_size=100):
		self.seed = seed
		
		self.map_size = map_size
		
	def validate_coordinates(self, x, y):
		if not (0 <= x < self.map_size and 0 <= y < self.map_size):
			return False
			
		else:
			return True
			
	def get_nearest_walkable_tile(self, x, y):
		if self.is_walkable(x, y):
			return x, y
			
		for radius in range(1, self.map_size):
			for dy in range(-radius, radius + 1):
				for dx in range(-radius, radius + 1):
					tx = x + dx
					ty = y + dy
					
					if self.validate_coordinates(tx, ty):
						if self.is_walkable(tx, ty):
							return tx, ty
							
		return x, y

class LocalMapGenerator(MapGenerator):
	def __init__(self, biome_color, seed, map_size=100):
		super().__init__(seed, map_size)
		
		self.main_color = biome_color
		
		self.wraparound = False
		
		self.map_array = np.full(
			(map_size, map_size),
			biome_color,
			dtype=object,
		)
		
	def tile_color(self, x, y):
		return self.map_array[y][x]
		
	def is_walkable(self, x, y):
		return True
	
class TownMapGenerator(MapGenerator, TownForge):
	def __init__(self, ground_color, seed, map_size=100):
		MapGenerator.__init__(self, seed, map_size)
		
		TownForge.__init__(self, seed=seed, map_size=map_size)
		
		self.ground_color = ground_color
		
		self.map_array = self.generate()
		
	def tile_color(self, x, y):
		tile = self.map_array[y][x]
		
		if tile == TownForge.GROUND:
			return self.ground_color
			
		if tile == TownForge.DOOR:
			return self.door_color
			
		building = self.get_building_at(x, y)
		
		return building["color"] if building else "black"
		
	def is_walkable(self, x, y):
		tile = self.map_array[y][x]
		
		return tile in (
			TownForge.GROUND,
			TownForge.DOOR,
		)
	
class DungeonMapGenerator(MapGenerator, DungeonForge):
	def __init__(self, seed, map_size=100):
		MapGenerator.__init__(self, seed, map_size)
		
		DungeonForge.__init__(self, seed=seed, level_size=map_size)
		
		self.map_array = self.generate()
		
		self.map_size = self.level_size
		
		self.current_level = 0
		
	def tile_at(self, x, y):
		return self.map_array[self.current_level][y][x]
		
	def tile_color(self, x, y):
		tile = self.tile_at(x, y)
		
		return {
			DungeonForge.FLOOR: "white",
			DungeonForge.WALL: "black",
			DungeonForge.UP: "green",
			DungeonForge.DOWN: "red"
		}[tile]
		
	def is_walkable(self, x, y):
		return self.tile_at(x, y) != DungeonForge.WALL
		
	def set_level(self, level):
		if not 0 <= level < len(self.map_array):
			raise ValueError(f"Dungeon level {level} is out of range.")
			
		self.current_level = level
	
class Location:
	def __init__(self, gx, gy, name, char, char_color):
		self.gx = gx
		self.gy = gy
		
		self.name = name
		
		self.char = char
		
		self.char_color = char_color
		
class Town(Location):
	def __init__(self, gx, gy, number):
		super().__init__(gx, gy, f"Town {number}", "T", "black")
		
class Dungeon(Location):
	def __init__(self, gx, gy, number):
		super().__init__(gx, gy, f"Dungeon {number}", "D", "black")
		
class Player:
	def __init__(self):
		self.gx = 0
		self.gy = 0
		
		self.lx = None
		self.ly = None
		self.lz = None
		
		self.last_overworld_direction = None