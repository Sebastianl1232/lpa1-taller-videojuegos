"""Configuracion global del juego."""

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60

TITLE = "Aventura 2D - Prototipo"

PLAYER_SPEED = 230
ENEMY_SPEED = 120
PROJECTILE_SPEED = 420
PROJECTILE_COOLDOWN = 0.22
CONTACT_INVULN_TIME = 0.6
KNOCKBACK_DISTANCE = 26
PLAYER_BLINK_INTERVAL_MS = 90
GROUND_CHASE_RANGE = 200
FLYING_CHASE_RANGE = 260
BOSS_CHASE_RANGE = 340

BACKGROUND_COLOR = (22, 28, 35)
WALL_COLOR = (64, 78, 91)
PLAYER_COLOR = (70, 200, 120)
ENEMY_COLOR = (218, 80, 80)
TREASURE_COLOR = (238, 196, 72)
TRAP_COLOR = (225, 114, 51)
SHOP_COLOR = (90, 135, 220)
PROJECTILE_COLOR = (153, 229, 255)
BOSS_COLOR = (154, 70, 214)
PARTICLE_FIRE_COLOR = (173, 232, 255)
PARTICLE_HIT_COLOR = (255, 214, 102)
PARTICLE_PICKUP_COLOR = (124, 240, 184)
PARTICLE_DAMAGE_COLOR = (255, 128, 128)
PARTICLE_ZONE_COLOR = (182, 135, 255)
ENEMY_HP_BG_COLOR = (40, 40, 40)
ENEMY_HP_COLOR = (112, 224, 112)
TEXT_COLOR = (240, 244, 248)

OBJECTIVE_SCORE = 150

DIFFICULTY_PROFILES = {
	"easy": {
		"label": "Facil",
		"enemy_hp_multiplier": 0.8,
		"enemy_attack_multiplier": 0.8,
		"enemy_speed_multiplier": 0.9,
		"treasure_multiplier": 1.2,
		"trap_multiplier": 0.8,
		"objective_score": 130,
	},
	"normal": {
		"label": "Normal",
		"enemy_hp_multiplier": 1.0,
		"enemy_attack_multiplier": 1.0,
		"enemy_speed_multiplier": 1.0,
		"treasure_multiplier": 1.0,
		"trap_multiplier": 1.0,
		"objective_score": 150,
	},
	"hard": {
		"label": "Dificil",
		"enemy_hp_multiplier": 1.25,
		"enemy_attack_multiplier": 1.2,
		"enemy_speed_multiplier": 1.1,
		"treasure_multiplier": 0.9,
		"trap_multiplier": 1.2,
		"objective_score": 180,
	},
}
