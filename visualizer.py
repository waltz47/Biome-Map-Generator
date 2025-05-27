import pygame
import sys
import noise # Import the noise library
# Import necessary components and noise parameters from biome_generator
from biome_generator import (
    generate_world_data, get_biome, BIOMES,
    WIDTH, HEIGHT, # Corrected: Use WIDTH and HEIGHT from biome_generator
    LAND_WATER_SCALE, LAND_WATER_OCTAVES, LAND_WATER_PERSISTENCE, LAND_WATER_LACUNARITY,
    MOISTURE_SCALE, MOISTURE_OCTAVES, MOISTURE_PERSISTENCE, MOISTURE_LACUNARITY,
    TEMPERATURE_SCALE, TEMPERATURE_OCTAVES, TEMPERATURE_PERSISTENCE, TEMPERATURE_LACUNARITY,
    LW_OFFSET_X, LW_OFFSET_Y, MOIST_OFFSET_X, MOIST_OFFSET_Y, TEMP_OFFSET_X, TEMP_OFFSET_Y,
    LAND_WATER_THRESHOLD, BEACH_THRESHOLD_LOWER, BEACH_THRESHOLD_UPPER
)

# --- Pygame Setup ---
pygame.init()

# --- Display Configuration ---
CELL_SIZE = 10  # You can adjust this; smaller means more pixels, potentially smoother but slower initial draw
SCREEN_WIDTH = WIDTH * CELL_SIZE
SCREEN_HEIGHT = HEIGHT * CELL_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Smoothed Biome Map Visualizer")

# --- Helper function to sample noise and determine biome for a continuous world coordinate ---
# This replicates the core noise sampling logic from biome_generator.py for a specific point
def get_biome_at_continuous_coord(world_x, world_y):
    # Normalized coordinates for noise sampling, adjusted for aspect ratio
    # These are equivalent to nx, ny in biome_generator's loop but derived from continuous world_x, world_y
    nx = (world_x / WIDTH - 0.5) * 2.0 * (WIDTH / HEIGHT) 
    ny = (world_y / HEIGHT - 0.5) * 2.0

    # 1. Sample Land/Water noise
    raw_land_water = noise.pnoise2(nx * LAND_WATER_SCALE + LW_OFFSET_X,
                                   ny * LAND_WATER_SCALE + LW_OFFSET_Y,
                                   octaves=LAND_WATER_OCTAVES,
                                   persistence=LAND_WATER_PERSISTENCE,
                                   lacunarity=LAND_WATER_LACUNARITY,
                                   base=0)
    land_water_value = (raw_land_water + 1.0) / 2.0 # Normalize to 0-1

    # 2. Sample Moisture noise
    raw_moisture = noise.pnoise2(nx * MOISTURE_SCALE + MOIST_OFFSET_X,
                                 ny * MOISTURE_SCALE + MOIST_OFFSET_Y,
                                 octaves=MOISTURE_OCTAVES,
                                 persistence=MOISTURE_PERSISTENCE,
                                 lacunarity=MOISTURE_LACUNARITY,
                                 base=1)
    moisture = (raw_moisture + 1.0) / 2.0 # Normalize to 0-1

    # 3. Sample Temperature noise
    raw_temperature_noise = noise.pnoise2(nx * TEMPERATURE_SCALE + TEMP_OFFSET_X,
                                          ny * TEMPERATURE_SCALE + TEMP_OFFSET_Y,
                                          octaves=TEMPERATURE_OCTAVES,
                                          persistence=TEMPERATURE_PERSISTENCE,
                                          lacunarity=TEMPERATURE_LACUNARITY,
                                          base=2)
    temperature_noise_normalized = (raw_temperature_noise + 1.0) / 2.0
    # Apply y-gradient for temperature (cooler towards top of map, y=0)
    # Note: in Pygame, y=0 is top. If world_y is 0-HEIGHT with 0 at top:
    temperature_y_gradient = 1.0 - (world_y / HEIGHT) 
    temperature = (temperature_y_gradient * 0.7) + (temperature_noise_normalized * 0.3)
    temperature = max(0.0, min(1.0, temperature))

    return get_biome(land_water_value, moisture, temperature)

# --- Function to draw the map per pixel ---
def draw_map_per_pixel():
    print("Starting per-pixel map generation...")
    screen.fill((0,0,0)) # Optional: fill black before starting
    for py in range(SCREEN_HEIGHT):
        for px in range(SCREEN_WIDTH):
            world_x = px / CELL_SIZE
            world_y = py / CELL_SIZE
            
            biome = get_biome_at_continuous_coord(world_x, world_y)
            if biome:
                screen.set_at((px, py), biome.pygame_color)
        if py % (SCREEN_HEIGHT // 20) == 0 and py > 0: # Print progress
            print(f"Progress: {int((py/SCREEN_HEIGHT)*100)}%")
            pygame.display.flip() # Update screen periodically during generation to show progress
    
    pygame.display.flip() # Final update
    print("Map generation complete.")

# --- Initial Drawing --- 
draw_map_per_pixel()

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r: # Press 'R' to regenerate and redraw
                # For a truly new map on 'R', biome_generator's global offsets 
                # (LW_OFFSET_X etc.) would need to be re-randomized and re-imported, 
                # or visualizer.py would need to manage its own offsets passed to pnoise2.
                # Currently, this just re-renders using the existing imported offsets.
                print("Re-rendering map (using existing noise offsets)...")
                draw_map_per_pixel()

pygame.quit()
sys.exit() 