#WIDTH = 1000
#HEIGHT = 800
GRAVITY = 900.0
FPS = 40

PLAYER_DEF_V = 200.0
JUMP_AMOUNT = -550.0
FLAP_AMOUNT = -300
AMMO = 5 #Initial ammo

NEW_LIFE = 15000 #Player gets a new life every x many points.

VERT_BUFFER = 80 #Both of these are used for scrolling / viewport management
HOR_BUFFER  = 40

CREATURE_DEBUG = False
RELATIVE_DEBUG = False
COLLISION_DEBUG = False
DEBUG = CREATURE_DEBUG or RELATIVE_DEBUG or COLLISION_DEBUG

