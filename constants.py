'''
Single source of truth - one place to update all constants 
and avoid potential errors if update had to be done on multiple files.
'''


# World size (screen dimensions: width x height)
SCREEN_W = 800 # horizontal axis
SCREEN_H = 600 # vertical axis


# Frame rate
'''
The screen is redrawn 60 times every second. 
Constant ensures that game runs the same on different devices.
So not 120 FPS or 30 FPS but always as the constant FPS says. 

'''
FPS = 60


# Tier mass thresholds 
'''
Mass points at which the player evolves to a new size/level.
New mass tiers can be added later. 
'''
TIER_2_MASS = 50
TIER_3_MASS = 200


# Radius for each tier
'''
A dictionary with int keys which are mass tiers and values as px radius. 
'''
TIER_RADII = {1: 10, 2: 20, 3: 55}


# Main colors in RGB format
'''
Stored as variable for easier use later i.e. typing PLAYER_COLOR instead of COLORS["PLAYER_COLOR"]
if they were stored in a dictionary.
Uses a new type of variable - tuple: values that cant change in parentheses.
'''
OCEAN_BG     = (10, 40, 80)
PLAYER_COLOR = (50, 200, 120) # teal-green
WHITE        = (255, 255, 255)
BLACK        = (0, 0, 0)


# Secondary colors in RGB format
'''
Stored as a dictionary with key: collor name and value: tuple value (RGB code).
'''
COLORS = {
    "RED":    (255, 0, 0),
    "GREEN":  (0, 255, 0),
    "BLUE":   (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "PURPLE": (128, 0, 128),
    "CYAN":   (0, 255, 255),
    "ORANGE": (255, 165, 0),
}


# Zooplankton population constants
ZOOPLANKTON_COUNT  = 30  # number of basic food on screen at all times
RESPAWN_DELAY      = 2.0 # seconds before a food replacement appears - after basic food is eaten. It is a float vriable used in other float calculations)


# Zooplankton properties
'''
Properties of an individual plankton.
'''
ZP_RADIUS     = 4
ZP_MASS_VALUE = 1
ZP_MAX_DRIFT  = 25
ZP_COLOR      = COLORS["CYAN"]


# Small fish population constants
SF_COUNT = 9 # number of small fish population on screen


# Small fish proprerties
'''
Properties of an individual NPC small fish.
'''
SF_RADIUS     = 10               # bigger than zooplankton, but smaller than Tier 1 
SF_MASS_VALUE = 8                # mass value boost after eating, worth more than a zooplankton (ZP gives 1)
SF_SPEED      = 90               # px/s straight-line swim across screen - faster than ZP drift
SF_COLOR      = (255, 180, 50)   # warm orange — distinct from the cyan plankton dots


# Shark properties
SHARK_RADIUS     = 22 # larger than SmallFish (10 px), smaller than Tier 2 player (35 px)
SHARK_MASS_VALUE = 200 # eating the shark = large mass reward
SHARK_SPEED      = 140 # px/s — threatening but slower than player (200 px/s)
SHARK_COLOR      = (160, 160, 180) # cool grey-blue, distinct from everything else


# Heads up display constants
'''
Coordinates for the HUD.
'''
HUD_X          = 16        # left margin for all HUD elements (text and the bar)
MASS_Y         = 16        # top of mass text
BAR_Y          = 44        # top of progress bar (just below mass text)
BAR_W          = 180       # full width of the bar in pixels
BAR_H          = 14        # height of the bar in pixels
BAR_BG_COLOR   = (30, 60, 100)   # dark blue empty portion/background
BAR_FILL_COLOR = COLORS["CYAN"]  # bright fill matching zooplankton color
BAR_BORDER     = WHITE

FONT_SIZE      = 22


# Bubble particles 
BUBBLE_COUNT  = 7              # number of bubbles on screen at all times
BUBBLE_COLOR  = (200, 230, 255)  # pale blue-white
BUBBLE_RADIUS = 3              # px — tiny
BUBBLE_SPEED  = 30             # px/s upward drift (gentle float)