import random
import noise

class Biome:
    def __init__(self, name, symbol, color_code, pygame_color, min_val=0, max_val=1):
        self.name = name
        self.symbol = symbol
        self.color_code = color_code
        self.pygame_color = pygame_color
        self.min_val = min_val
        self.max_val = max_val

    def __str__(self):
        try:
            return f"{self.color_code}{self.symbol}\033[0m"
        except:
            return self.symbol

# Adjusted Pygame colors to be less saturated / slightly darker
BIOMES = [
    # Water Biomes (differentiated by land_water_noise value)
    Biome('DEEP_WATER',    '~', '\033[34m', (0, 0, 70), 0.0, 0.3),      # Darker Blue, e.g. land_water_noise 0.0-0.3
    Biome('SHALLOW_WATER', 's', '\033[94m', (30, 60, 150), 0.3, 0.45),    # Muted Light Blue, e.g. land_water_noise 0.3-0.45
    
    # Land Biomes (differentiated by temperature and moisture after land_water_noise > threshold)
    Biome('BEACH',         '_', '\033[93m', (210, 190, 110)), # Muted Khaki - Special case, border of land/water
    Biome('PLAINS',        '.', '\033[32m', (50, 110, 50)),   # Muted ForestGreen
    Biome('FOREST',        'F', '\033[92m', (20, 80, 20)),     # Darker Green
    Biome('DESERT',        'D', '\033[33m', (200, 140, 80)),   # Muted SandyBrown
    Biome('SAVANNA',       'S', '\033[92m', (150, 150, 90)), # Muted DarkKhaki
    Biome('JUNGLE',        'J', '\033[32m', (30, 100, 30)),     # Muted Green
    Biome('SNOWY_PLAIN',   '*', '\033[97m', (220, 220, 230))  # Off-white/Light Grayish blue
    # Removed MOUNTAIN_BASE, MOUNTAIN_PEAK, VOLCANIC
]

WIDTH = 100 # This is MAP_WIDTH_CELLS
HEIGHT = 60 # This is MAP_HEIGHT_CELLS

# Noise parameters
LAND_WATER_SCALE = 4.0  # Further reduced for very large land/water features
LAND_WATER_OCTAVES = 4   
LAND_WATER_PERSISTENCE = 0.5
LAND_WATER_LACUNARITY = 2.0
LAND_WATER_THRESHOLD = 0.40 # Reduced to have less water overall
BEACH_THRESHOLD_LOWER = 0.38 # Adjusted around new LAND_WATER_THRESHOLD
BEACH_THRESHOLD_UPPER = 0.42 # Adjusted around new LAND_WATER_THRESHOLD

MOISTURE_SCALE = 7.0  # Drastically reduced for larger moisture zones
MOISTURE_OCTAVES = 3
MOISTURE_PERSISTENCE = 0.5
MOISTURE_LACUNARITY = 2.0

TEMPERATURE_SCALE = 10.0 # Drastically reduced for larger temperature zones
TEMPERATURE_OCTAVES = 2
TEMPERATURE_PERSISTENCE = 0.5
TEMPERATURE_LACUNARITY = 2.0

# Random offsets for variety in noise patterns
LW_OFFSET_X = random.uniform(0, 1000)
LW_OFFSET_Y = random.uniform(0, 1000)
MOIST_OFFSET_X = random.uniform(0, 1000)
MOIST_OFFSET_Y = random.uniform(0, 1000)
TEMP_OFFSET_X = random.uniform(0, 1000)
TEMP_OFFSET_Y = random.uniform(0, 1000)

def get_biome_by_name(name):
    for biome in BIOMES:
        if biome.name == name:
            return biome
    return None # Should not happen if names are correct

def get_biome(land_water_value, moisture, temperature):
    # Determine if it's water, beach, or land based on land_water_value
    if BEACH_THRESHOLD_LOWER <= land_water_value < BEACH_THRESHOLD_UPPER: # Check for Beach first
        return get_biome_by_name('BEACH')
    elif land_water_value < LAND_WATER_THRESHOLD:
        if land_water_value < get_biome_by_name('DEEP_WATER').max_val: # Using max_val from Biome for thresholds
            return get_biome_by_name('DEEP_WATER')
        else:
            return get_biome_by_name('SHALLOW_WATER') # Covers up to LAND_WATER_THRESHOLD
    else: # It's land
        # Define conditions for land biomes based on temperature and moisture
        # This is a simplified example; you might want more nuanced ranges or a priority system
        if temperature < 0.3 and moisture < 0.4: return get_biome_by_name('SNOWY_PLAIN')
        if temperature < 0.3: return get_biome_by_name('SNOWY_PLAIN') # Coldest general

        if moisture < 0.2: return get_biome_by_name('DESERT')
        if moisture < 0.4 and temperature > 0.6: return get_biome_by_name('SAVANNA')
        
        if moisture > 0.7 and temperature > 0.5: return get_biome_by_name('JUNGLE')
        if moisture > 0.5: return get_biome_by_name('FOREST')

        return get_biome_by_name('PLAINS') # Default land biome

def generate_world_data():
    world_map = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
    world_parameters = [[{} for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for y in range(HEIGHT):
        for x in range(WIDTH):
            # Normalized coordinates for noise sampling, adjusted for aspect ratio
            nx = (x / WIDTH - 0.5) * 2.0 * (WIDTH/HEIGHT) # Adjust x for aspect ratio
            ny = (y / HEIGHT - 0.5) * 2.0

            # 1. Generate Land/Water noise
            raw_land_water = noise.pnoise2(nx * LAND_WATER_SCALE + LW_OFFSET_X,
                                           ny * LAND_WATER_SCALE + LW_OFFSET_Y,
                                           octaves=LAND_WATER_OCTAVES,
                                           persistence=LAND_WATER_PERSISTENCE,
                                           lacunarity=LAND_WATER_LACUNARITY,
                                           base=0)
            land_water_value = (raw_land_water + 1.0) / 2.0 # Normalize to 0-1

            # 2. Generate Moisture noise (independent of elevation now)
            raw_moisture = noise.pnoise2(nx * MOISTURE_SCALE + MOIST_OFFSET_X,
                                         ny * MOISTURE_SCALE + MOIST_OFFSET_Y,
                                         octaves=MOISTURE_OCTAVES,
                                         persistence=MOISTURE_PERSISTENCE,
                                         lacunarity=MOISTURE_LACUNARITY,
                                         base=1)
            moisture = (raw_moisture + 1.0) / 2.0 # Normalize to 0-1

            # 3. Generate Temperature noise (independent of elevation now, but with y-gradient)
            raw_temperature_noise = noise.pnoise2(nx * TEMPERATURE_SCALE + TEMP_OFFSET_X,
                                                  ny * TEMPERATURE_SCALE + TEMP_OFFSET_Y,
                                                  octaves=TEMPERATURE_OCTAVES,
                                                  persistence=TEMPERATURE_PERSISTENCE,
                                                  lacunarity=TEMPERATURE_LACUNARITY,
                                                  base=2)
            temperature_noise_normalized = (raw_temperature_noise + 1.0) / 2.0
            temperature_y_gradient = 1.0 - (y / HEIGHT) # Warmer at y=0 (bottom), cooler at y=HEIGHT-1 (top)
            temperature = (temperature_y_gradient * 0.7) + (temperature_noise_normalized * 0.3)
            temperature = max(0.0, min(1.0, temperature))
            
            world_parameters[y][x] = {
                'land_water': land_water_value,
                'm': moisture, 
                't': temperature
            }
            world_map[y][x] = get_biome(land_water_value, moisture, temperature)
            
    return world_map, world_parameters, WIDTH, HEIGHT, BIOMES

if __name__ == "__main__":
    world_map_data, world_params_data, map_width, map_height, biomes_list = generate_world_data()
    
    print('Generated Biome Map (Console Output - Flat World Model):')
    for y_idx in range(map_height):
        for x_idx in range(map_width):
            # Print biome symbol
            if world_map_data[y_idx][x_idx] is not None:
                 print(world_map_data[y_idx][x_idx], end='')
            else:
                 print("?", end='') # Should not happen with current get_biome
        # Optionally print some parameters for the last cell in row for quick check
        # params = world_params_data[y_idx][-1]
        # print(f" | LW: {params['land_water']:.2f} M: {params['m']:.2f} T: {params['t']:.2f}", end='')
        print()

    print('\nBiome Legend:')
    for b in biomes_list:
        # For Biome constructor: name, symbol, color_code, pygame_color, min_val=0, max_val=1
        if b.name in ['DEEP_WATER', 'SHALLOW_WATER']:
            print(f"{b.color_code}{b.symbol}\033[0m: {b.name} (LW Noise: {b.min_val:.2f}-{b.max_val:.2f})")
        else:
            print(f"{b.color_code}{b.symbol}\033[0m: {b.name}")

    print('\nNote: Colors are ANSI escape codes. If you see strange characters, your terminal might not support them.')
    print('Parameters (approximate): land_water (0-1), m=moisture (0-1), t=temperature (0-1)') 