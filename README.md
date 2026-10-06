# Procedural RPG World in Python + Tkinter

This repository contains the complete source code for my **Procedural RPG World** tutorial.

In this project, we use Python and Tkinter to build a procedurally generated RPG world with multiple interconnected map types, including an overworld, local wilderness maps, towns, and multi-level dungeons.

## Features

- Procedurally generated overworld
- Local wilderness maps
- Procedurally generated towns
- Procedurally generated dungeons
- Multiple dungeon levels
- Player movement
- Player-centered map view
- Overworld travel
- Entering and exiting locations
- Direction-based map entry
- Wraparound local map movement
- Seed-based procedural generation

## Tutorial

You can follow the complete tutorial on YouTube:

**[Watch the Procedural RPG World Tutorial](https://www.youtube.com/watch?v=K4of-8WRbTA)**

The tutorial walks through how the different map systems work and how they are connected together into a single RPG world.

## Requirements

- Python
- Tkinter
- TerraForge
- TownForge
- DungeonForge
- noise
- numpy
- pillow

Additional dependencies may be required by the procedural generation libraries.

## Running the Project

Navigate to the project folder and run:

python main.py

## Project Structure

The project is separated into multiple files responsible for different parts of the RPG world.

- `main.py` - Starts the application
- `entities.py` - Game entities and player-related logic
- `screens.py` - Game screens and map transitions
- `widgets.py` - Tkinter widgets and interface components
