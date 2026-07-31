class_name CounterDecorFixture
extends Node2D

const ROOT_PARENT_POSITION := Vector2(360.0, 640.0)
const BOWL_BOX_SIZE := Vector2(66.0, 66.0)
const PLANT_POT_BOX_SIZE := Vector2(67.0, 75.0)
const PLANT_FOLIAGE_BOX_SIZE := Vector2(61.0, 154.0)
const CRATE_BOX_SIZE := Vector2(117.0, 88.0)
const BOTTLE_BOX_SIZE := Vector2(38.0, 64.0)
const CLOTH_BOX_SIZE := Vector2(97.0, 120.0)
const CRATE_FRONT_REGION_PIXELS := Rect2(0.0, 82.0, 234.0, 95.0)
const FOLIAGE_MAX_RADIANS := deg_to_rad(0.35)
const FOLIAGE_PERIOD_RANGE := Vector2(4.5, 8.0)
const USE_CONFIGURED_SEED := -2147483648

@export var active_on_ready := true
@export var reduced_motion_on_ready := false
@export var deterministic_test_mode := false
@export var motion_seed := 48042

@onready var food_bowl: Sprite2D = $FoodBowl
@onready var foliage_pivot: Node2D = $Plant/FoliagePivot
@onready var foliage: Sprite2D = $Plant/FoliagePivot/Foliage
@onready var plant_pot: Sprite2D = $Plant/Pot
@onready var bottle_brown: Sprite2D = $BottleCrate/BottleBrown
@onready var bottle_green: Sprite2D = $BottleCrate/BottleGreen
@onready var bottle_cream_blue: Sprite2D = $BottleCrate/BottleCreamBlue
@onready var empty_crate: Sprite2D = $BottleCrate/EmptyCrate
@onready var crate_front_wall: Sprite2D = $BottleCrate/FrontWallOverlay
@onready var counter_cloth: Sprite2D = $CounterCloth

var _rng := RandomNumberGenerator.new()
var _active := true
var _reduced_motion := false
var _elapsed := 0.0
var _foliage_period := 6.0


func _ready() -> void:
	_fit_sprite(food_bowl, BOWL_BOX_SIZE)
	_fit_sprite(plant_pot, PLANT_POT_BOX_SIZE)
	_fit_sprite(foliage, PLANT_FOLIAGE_BOX_SIZE)
	_fit_sprite(empty_crate, CRATE_BOX_SIZE)
	_fit_sprite(bottle_brown, BOTTLE_BOX_SIZE)
	_fit_sprite(bottle_green, BOTTLE_BOX_SIZE)
	_fit_sprite(bottle_cream_blue, BOTTLE_BOX_SIZE)
	_register_crate_front_wall()
	_fit_sprite(counter_cloth, CLOTH_BOX_SIZE)
	_active = active_on_ready
	_reduced_motion = reduced_motion_on_ready
	reset_motion(motion_seed)


func _process(delta: float) -> void:
	if deterministic_test_mode:
		return
	step_motion(delta)


func set_active(enabled: bool) -> void:
	_active = enabled
	if not enabled:
		foliage_pivot.rotation = 0.0


func is_active() -> bool:
	return _active


func set_reduced_motion(enabled: bool) -> void:
	_reduced_motion = enabled
	if enabled:
		foliage_pivot.rotation = 0.0


func is_reduced_motion() -> bool:
	return _reduced_motion


func set_deterministic_test_mode(enabled: bool) -> void:
	deterministic_test_mode = enabled


func reset_motion(seed: int = USE_CONFIGURED_SEED) -> void:
	var resolved_seed := motion_seed if seed == USE_CONFIGURED_SEED else seed
	if resolved_seed < 0:
		_rng.randomize()
	else:
		_rng.seed = resolved_seed
	_elapsed = 0.0
	_foliage_period = _rng.randf_range(
		FOLIAGE_PERIOD_RANGE.x,
		FOLIAGE_PERIOD_RANGE.y
	)
	if foliage_pivot != null:
		foliage_pivot.rotation = 0.0


func step_motion(delta: float) -> void:
	if not _active or _reduced_motion:
		foliage_pivot.rotation = 0.0
		return
	_elapsed += maxf(delta, 0.0)
	var primary := sin(TAU * _elapsed / _foliage_period)
	var secondary := sin(
		TAU * _elapsed / (_foliage_period * 0.61) + 0.83
	)
	var normalized_wave := primary * 0.78 + secondary * 0.22
	foliage_pivot.rotation = clampf(
		FOLIAGE_MAX_RADIANS * normalized_wave,
		-FOLIAGE_MAX_RADIANS,
		FOLIAGE_MAX_RADIANS
	)


func get_foliage_rotation() -> float:
	return foliage_pivot.rotation


func get_foliage_period() -> float:
	return _foliage_period


func _fit_sprite(sprite: Sprite2D, box_size: Vector2) -> void:
	if sprite == null or sprite.texture == null:
		return
	var texture_size := sprite.texture.get_size()
	if texture_size.x <= 0.0 or texture_size.y <= 0.0:
		return
	var uniform_scale := minf(
		box_size.x / texture_size.x,
		box_size.y / texture_size.y
	)
	sprite.scale = Vector2.ONE * uniform_scale


func _register_crate_front_wall() -> void:
	if empty_crate == null or empty_crate.texture == null or crate_front_wall == null:
		return
	crate_front_wall.texture = empty_crate.texture
	crate_front_wall.region_enabled = true
	crate_front_wall.region_rect = CRATE_FRONT_REGION_PIXELS
	crate_front_wall.scale = empty_crate.scale
	var texture_size := empty_crate.texture.get_size()
	var region_center := (
		CRATE_FRONT_REGION_PIXELS.position
		+ CRATE_FRONT_REGION_PIXELS.size * 0.5
	)
	var source_center := texture_size * 0.5
	crate_front_wall.position = empty_crate.position + Vector2(
		(region_center.x - source_center.x) * empty_crate.scale.x,
		(region_center.y - source_center.y) * empty_crate.scale.y
	)
