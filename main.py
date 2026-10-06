from tkinter import *

import screens
import entities

class Root(Tk):
	def __init__(self):
		super().__init__()
		self.title("Procedural Game World")
		self.state("zoomed")
		
		self.game = entities.Game()
		
		self.bindings = {
			"<Up>": "north",
			"<Down>": "south",
			"<Left>": "west",
			"<Right>": "east",
			"8": "north",
			"7": "northwest",
			"9": "northeast",
			"4": "west",
			"6": "east",
			"1": "southwest",
			"2": "south",
			"3": "southeast",
			"5": "in",
		}
		
if __name__ == "__main__":
	root = Root()
	
	root.play_screen = screens.PlayScreen(root)
	root.play_screen.display()
	
	root.mainloop()