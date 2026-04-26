#!/usr/bin/env python3
"""Script para validar que todos los layouts tienen cámaras accesibles."""

from game.world import World
from game.settings import DIFFICULTY_PROFILES


def test_all_layouts():
    """Prueba que todos los layouts y dificultades permiten acceso al jefe."""
    
    difficulties = ["easy", "normal", "hard"]
    num_layouts = 6  # Ahora con 6 layouts diferentes
    test_floors = [1, 2, 5, 10]  # Pruebar diferentes pisos
    
    print("=" * 70)
    print("VALIDACION DE ACCESIBILIDAD DE CAMARAS")
    print("=" * 70)
    
    all_passed = True
    
    for difficulty in difficulties:
        print(f"\n[DIFICULTAD: {difficulty.upper()}]")
        print("-" * 70)
        
        for floor in test_floors:
            print(f"\n  Piso {floor}:")
            
            for layout_idx in range(num_layouts):
                try:
                    world = World(difficulty=difficulty, floor=floor)
                    
                    # Obtener nombre del layout
                    layout_name = world.layout["name"]
                    
                    # Obtener posición del jefe
                    if world.layout["enemy_specs"]:
                        jefe_x, jefe_y, _, _ = world.layout["enemy_specs"][-1]
                        
                        # Verificar que es accesible
                        is_accessible = world._is_position_reachable((60, 60), (jefe_x, jefe_y))
                        
                        status = "[OK] ACCESIBLE" if is_accessible else "[XX] SELLADO"
                        print(f"    [{layout_idx + 1}] {layout_name:20s} - Jefe en ({jefe_x}, {jefe_y}): {status}")
                        
                        if not is_accessible:
                            all_passed = False
                    else:
                        print(f"    [{layout_idx + 1}] {layout_name:20s} - [WR] SIN JEFE")
                        
                except Exception as e:
                    print(f"    [{layout_idx + 1}] ERROR: {str(e)}")
                    all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("[RESULTADO] TODAS LAS PRUEBAS PASARON - Todos los jefes son accesibles")
    else:
        print("[RESULTADO] ALGUNAS PRUEBAS FALLARON - Revisar layouts sellados")
    print("=" * 70)


if __name__ == "__main__":
    test_all_layouts()
