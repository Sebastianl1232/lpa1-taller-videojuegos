#!/usr/bin/env python3
import sys
import os

# Import settings first to avoid circular import
from game.settings import DIFFICULTY_PROFILES
from game.world import World, Decoration
import pygame

pygame.init()

def debug_chamber_detailed():
    # Test Templo Perdido on floor 5
    world = World(difficulty="Normal", floor=5)
    
    print(f"\n=== {world.layout['name']} (Piso 5) ===")
    
    # Get jefe position (last enemy spec)
    jefe_x, jefe_y, _, _ = world.layout["enemy_specs"][-1]
    print(f"Jefe position: ({jefe_x}, {jefe_y})")
    print(f"Player start: (60, 60)")
    print(f"Jefe tile: ({jefe_x // 20}, {jefe_y // 20})")
    print(f"Player tile: (3, 3)")
    
    # List all walls
    print(f"\nWalls ({len(world.walls)} total):")
    for i, wall in enumerate(world.walls):
        tile_x = wall.x // 20
        tile_y = wall.y // 20
        tile_w = wall.width // 20
        tile_h = wall.height // 20
        print(f"  {i}: Rect({wall.x}, {wall.y}, {wall.width}, {wall.height}) -> Tile({tile_x}, {tile_y}, {tile_w}, {tile_h})")
    
    # Test reachability
    is_reachable = world._is_position_reachable((60, 60), (jefe_x, jefe_y))
    print(f"\nReachable: {is_reachable}")
    
    # Manual flood-fill debug
    print("\n=== Manual Flood Fill ===")
    TILE_SIZE = 20
    MAP_WIDTH = 960
    MAP_HEIGHT = 640
    grid_width = MAP_WIDTH // TILE_SIZE
    grid_height = MAP_HEIGHT // TILE_SIZE
    
    print(f"Grid: {grid_width}x{grid_height}")
    
    # Build collision grid
    collision = [[False] * grid_width for _ in range(grid_height)]
    for wall in world.walls:
        for ty in range(grid_height):
            for tx in range(grid_width):
                pixel_x = tx * TILE_SIZE
                pixel_y = ty * TILE_SIZE
                if wall.collidepoint(pixel_x, pixel_y):
                    collision[ty][tx] = True
    
    # Check player start
    player_tile_x, player_tile_y = 3, 3
    jefe_tile_x = jefe_x // TILE_SIZE
    jefe_tile_y = jefe_y // TILE_SIZE
    
    print(f"Player tile collision: {collision[player_tile_y][player_tile_x]}")
    print(f"Jefe tile collision: {collision[jefe_tile_y][jefe_tile_x]}")
    
    # Show collision map around player
    print("\nCollision map around player (0 = open, 1 = blocked):")
    for y in range(max(0, player_tile_y - 5), min(grid_height, player_tile_y + 6)):
        row = ""
        for x in range(max(0, player_tile_x - 5), min(grid_width, player_tile_x + 6)):
            if x == player_tile_x and y == player_tile_y:
                row += "P"
            elif x == jefe_tile_x and y == jefe_tile_y:
                row += "J"
            else:
                row += "1" if collision[y][x] else "0"
        print(f"  y={y}: {row}")

if __name__ == "__main__":
    debug_chamber_detailed()


