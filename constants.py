GRAVITY = 900.0 #Acceleration due to gravity in px/sec/sec.
FPS = 40 #Target fps rate.

PLAYER_DEF_V = 200.0 #Maximum lateral velocity for the player in px/sec.
JUMP_AMOUNT = -550.0 #Initial velocity due to jumping in px/sec
FLAP_AMOUNT = -300 #Acceleration due to flapping in px/sec/sec
AMMO = 5 #Initial ammo

NEW_LIFE = 15000 #Player gets a new life every x many points.

VERT_BUFFER = 80 #Both of these are used for scrolling / viewport management
HOR_BUFFER  = 40

CREATURE_DEBUG = False
RELATIVE_DEBUG = False
COLLISION_DEBUG = False
DEBUG = CREATURE_DEBUG or RELATIVE_DEBUG or COLLISION_DEBUG

