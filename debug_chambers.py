#!/usr/bin/env python3
"""Debug script para verificar accesibilidad de layouts."""

from game.world import World

# Probar layouts específicos
layouts_to_test = [
    ("easy", 1),
    ("easy", 5),
    ("easy", 10),
]

for difficulty, floor in layouts_to_test:
    world = World(difficulty=difficulty, floor=floor)
    
    layout_name = world.layout["name"]
    
    if world.layout["enemy_specs"]:
        jefe_x, jefe_y, _, _ = world.layout["enemy_specs"][-1]
        
        print(f"\n{layout_name} (Piso {floor}):")
        print(f"  Jefe en: ({jefe_x}, {jefe_y})")
        print(f"  Muros: {len(world.walls)} total")
        print(f"  Accesible: {world._is_position_reachable((60, 60), (jefe_x, jefe_y))}")
