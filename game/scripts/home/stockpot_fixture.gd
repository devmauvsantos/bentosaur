class_name StockpotFixture
extends Node2D

signal active_changed(enabled: bool)

const BODY_BOX_SIZE := Vector2(86.0, 92.0)
const LID_BOX_SIZE := Vector2(90.0, 49.0)
const SHADOW_BOX_SIZE := Vector2(94.0, 18.0)
const ROOT_PARENT_POSITION := Vector2(179.0, 727.0)
const LID_TRAVEL_PX := 1.0
const LID_ROTATION_RADIANS := deg_to_rad(0.7)
const RATTLE_INTERVAL_RANGE := Vector2(2.8, 5.2)
const RATTLE_COUNT_RANGE := Vector2i(1, 2)
const RATTLE_UP_SECONDS := 0.060
const RATTLE_DOWN_SECONDS := 0.080
const RATTLE_GAP_SECONDS := 0.060
const WISP_LIFETIME_SECONDS := 1.55
const WISP_RISE_PX := 38.0
const WISP_PHASE_OFFSETS := [0.0, 0.34, 0.68]
const WISP_LANES := [-2.4, 0.8, 3.0]
const USE_CONFIGURED_SEED := -2147483648

@export var active_on_ready := true
@export var reduced_motion_on_ready := false
@export var deterministic_test_mode := false
@export var motion_seed := 48041

@onready var contact_shadow: Sprite2D = $ContactShadow
@onready var body: Sprite2D = $Body
@onready var steam_emitter: Node2D = $SteamEmitter
@onready var lid_pivot: Node2D = $LidPivot
@onready var lid: Sprite2D = $LidPivot/Lid

var _steam_wisps: Array[Sprite2D] = []
var _steam_outlines: Array[Line2D] = []
var _steam_cores: Array[Line2D] = []
var _rng := RandomNumberGenerator.new()
var _active := true
var _reduced_motion := false
var _motion_elapsed := 0.0
var _steam_elapsed := 0.0
var _next_rattle_at := INF
var _event_start := -INF
var _event_end := -INF
var _last_event_started_at := -INF
var _event_count := 0
var _event_direction := 1.0
var _event_serial := 0
var _lid_rest_position := Vector2.ZERO
var _lid_offset_y := 0.0
var _lid_rotation := 0.0


func _ready() -> void:
	_steam_wisps.assign([
		$SteamEmitter/Wisp0 as Sprite2D,
		$SteamEmitter/Wisp1 as Sprite2D,
		$SteamEmitter/Wisp2 as Sprite2D,
	])
	_steam_outlines.assign([
		$SteamEmitter/GraphicOutline0 as Line2D,
		$SteamEmitter/GraphicOutline1 as Line2D,
		$SteamEmitter/GraphicOutline2 as Line2D,
	])
	_steam_cores.assign([
		$SteamEmitter/GraphicCore0 as Line2D,
		$SteamEmitter/GraphicCore1 as Line2D,
		$SteamEmitter/GraphicCore2 as Line2D,
	])
	_lid_rest_position = lid_pivot.position
	_fit_sprite(contact_shadow, SHADOW_BOX_SIZE)
	_fit_sprite(body, BODY_BOX_SIZE)
	_fit_sprite(lid, LID_BOX_SIZE)
	_active = active_on_ready
	_reduced_motion = reduced_motion_on_ready
	reset_motion(motion_seed)
	_apply_visual_state(0.0)


func _process(delta: float) -> void:
	if deterministic_test_mode:
		return
	step_motion(delta)


func set_active(enabled: bool) -> void:
	if _active == enabled:
		return
	_active = enabled
	if enabled:
		_schedule_next_rattle(_motion_elapsed)
	else:
		_event_start = -INF
		_event_end = -INF
		_set_lid_pose(0.0, 0.0)
	_apply_visual_state(0.0)
	active_changed.emit(enabled)


func is_active() -> bool:
	return _active


func set_reduced_motion(enabled: bool) -> void:
	_reduced_motion = enabled
	if enabled:
		_set_lid_pose(0.0, 0.0)
	_apply_visual_state(0.0)


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
	_motion_elapsed = 0.0
	_steam_elapsed = 0.0
	_next_rattle_at = INF
	_event_start = -INF
	_event_end = -INF
	_last_event_started_at = -INF
	_event_count = 0
	_event_direction = 1.0
	_event_serial = 0
	_set_lid_pose(0.0, 0.0)
	if _active:
		_schedule_next_rattle(0.0)
	_apply_visual_state(0.0)


func step_motion(delta: float) -> void:
	delta = maxf(delta, 0.0)
	if not _active:
		_set_lid_pose(0.0, 0.0)
		_apply_visual_state(0.0)
		return
	if _reduced_motion:
		_set_lid_pose(0.0, 0.0)
		_apply_visual_state(0.0)
		return

	_motion_elapsed += delta
	_steam_elapsed += delta
	while _motion_elapsed >= _next_rattle_at:
		_begin_rattle(_next_rattle_at)
		_schedule_next_rattle(_event_end)

	var rattle_amount := 0.0
	var direction := _event_direction
	if _motion_elapsed >= _event_start and _motion_elapsed < _event_end:
		var sample := _sample_rattle(_motion_elapsed - _event_start)
		rattle_amount = sample.x
		direction = sample.y
	_set_lid_pose(-LID_TRAVEL_PX * rattle_amount, direction * LID_ROTATION_RADIANS * rattle_amount)
	_apply_visual_state(rattle_amount)


func get_lid_offset_y() -> float:
	return _lid_offset_y


func get_lid_rotation() -> float:
	return _lid_rotation


func get_event_serial() -> int:
	return _event_serial


func get_last_event_started_at() -> float:
	return _last_event_started_at


func get_current_event_count() -> int:
	return _event_count


func get_visible_steam_wisp_count() -> int:
	var count := 0
	for wisp: Sprite2D in _steam_wisps:
		if wisp.visible and wisp.modulate.a > 0.0001:
			count += 1
	return count


func get_visible_graphic_curl_count() -> int:
	var count := 0
	for core: Line2D in _steam_cores:
		if core.visible and core.default_color.a > 0.0001:
			count += 1
	return count


func _begin_rattle(start_at: float) -> void:
	_event_start = start_at
	_event_count = _rng.randi_range(RATTLE_COUNT_RANGE.x, RATTLE_COUNT_RANGE.y)
	_event_direction = -1.0 if _rng.randi_range(0, 1) == 0 else 1.0
	var pulse_seconds := RATTLE_UP_SECONDS + RATTLE_DOWN_SECONDS
	_event_end = start_at + float(_event_count) * pulse_seconds
	_event_end += float(_event_count - 1) * RATTLE_GAP_SECONDS
	_last_event_started_at = start_at
	_event_serial += 1


func _schedule_next_rattle(after_time: float) -> void:
	_next_rattle_at = after_time + _rng.randf_range(
		RATTLE_INTERVAL_RANGE.x,
		RATTLE_INTERVAL_RANGE.y
	)


func _sample_rattle(local_time: float) -> Vector2:
	var pulse_seconds := RATTLE_UP_SECONDS + RATTLE_DOWN_SECONDS
	var stride := pulse_seconds + RATTLE_GAP_SECONDS
	var pulse_index := mini(int(floor(local_time / stride)), _event_count - 1)
	var pulse_time := local_time - float(pulse_index) * stride
	if pulse_time < 0.0 or pulse_time >= pulse_seconds:
		return Vector2(0.0, _event_direction)

	var amount := 0.0
	if pulse_time < RATTLE_UP_SECONDS:
		amount = _smoother_step(pulse_time / RATTLE_UP_SECONDS)
	else:
		amount = 1.0 - _smoother_step(
			(pulse_time - RATTLE_UP_SECONDS) / RATTLE_DOWN_SECONDS
		)
	var direction := _event_direction
	if pulse_index % 2 == 1:
		direction *= -1.0
	return Vector2(amount, direction)


func _set_lid_pose(offset_y: float, rotation_radians: float) -> void:
	_lid_offset_y = clampf(offset_y, -LID_TRAVEL_PX, 0.0)
	_lid_rotation = clampf(
		rotation_radians,
		-LID_ROTATION_RADIANS,
		LID_ROTATION_RADIANS
	)
	if lid_pivot != null:
		lid_pivot.position = _lid_rest_position + Vector2(0.0, _lid_offset_y)
		lid_pivot.rotation = _lid_rotation


func _apply_visual_state(steam_boost: float) -> void:
	if not _active:
		for wisp: Sprite2D in _steam_wisps:
			wisp.visible = false
		for outline: Line2D in _steam_outlines:
			outline.visible = false
		for core: Line2D in _steam_cores:
			core.visible = false
		return
	if _reduced_motion:
		_apply_reduced_steam()
		return
	for index: int in range(_steam_wisps.size()):
		_apply_animated_wisp(index, steam_boost)


func _apply_reduced_steam() -> void:
	for index: int in range(_steam_wisps.size()):
		var wisp := _steam_wisps[index]
		wisp.visible = index == 0
		if index != 0:
			continue
		wisp.position = Vector2(0.0, -8.0)
		wisp.rotation = 0.0
		wisp.scale = Vector2(0.34, 0.38)
		wisp.modulate = Color(0.84, 0.89, 0.92, 0.12)
	var static_points := PackedVector2Array([
		Vector2(-0.5, 1.0),
		Vector2(2.0, -3.0),
		Vector2(1.5, -7.0),
		Vector2(-1.8, -11.0),
		Vector2(-1.2, -15.0),
		Vector2(1.0, -19.0),
	])
	for index: int in range(_steam_cores.size()):
		var visible := index == 0
		var outline := _steam_outlines[index]
		var core := _steam_cores[index]
		outline.visible = visible
		core.visible = visible
		if not visible:
			continue
		outline.points = static_points
		core.points = static_points
		outline.width = 5.2
		core.width = 2.4
		outline.default_color = Color(0.07, 0.11, 0.14, 0.72)
		core.default_color = Color(0.84, 0.89, 0.84, 0.70)


func _apply_animated_wisp(index: int, steam_boost: float) -> void:
	var wisp := _steam_wisps[index]
	var phase := fposmod(
		_steam_elapsed / WISP_LIFETIME_SECONDS + float(WISP_PHASE_OFFSETS[index]),
		1.0
	)
	var rise := phase * WISP_RISE_PX
	var drift := sin((phase * 1.35 + float(index) * 0.29) * TAU) * 2.2
	var lane := float(WISP_LANES[index])
	var fade_in := smoothstep(0.0, 0.18, phase)
	var fade_out := 1.0 - smoothstep(0.62, 1.0, phase)
	var alpha := 0.34 * fade_in * fade_out * lerpf(1.0, 1.20, steam_boost)
	wisp.visible = alpha > 0.001
	wisp.position = Vector2(lane + drift, -rise - 7.0)
	wisp.rotation = deg_to_rad(sin(phase * TAU + float(index)) * 8.0)
	wisp.scale = Vector2(
		lerpf(0.32, 0.56, phase),
		lerpf(0.30, 0.52, phase)
	)
	wisp.modulate = Color(0.84, 0.89, 0.92, alpha)
	_apply_graphic_curl(index, phase, rise, drift, lane, steam_boost)


func _apply_graphic_curl(
	index: int,
	phase: float,
	rise: float,
	drift: float,
	lane: float,
	steam_boost: float
) -> void:
	var fade_in := smoothstep(0.0, 0.14, phase)
	var fade_out := 1.0 - smoothstep(0.66, 1.0, phase)
	var visibility := fade_in * fade_out * lerpf(1.0, 1.12, steam_boost)
	var outline := _steam_outlines[index]
	var core := _steam_cores[index]
	outline.visible = visibility > 0.015
	core.visible = outline.visible
	var center_x := lane + drift
	var base_y := -rise - 2.0
	var curl := sin(phase * TAU + float(index) * 1.7)
	var points := PackedVector2Array([
		Vector2(center_x - 0.4, base_y + 3.0),
		Vector2(center_x + 2.7 + curl, base_y - 1.0),
		Vector2(center_x + 2.0 + curl, base_y - 6.0),
		Vector2(center_x - 2.5 - curl, base_y - 11.0),
		Vector2(center_x - 1.8 - curl, base_y - 16.0),
		Vector2(center_x + 1.4 + curl * 0.4, base_y - 21.0),
	])
	outline.points = points
	core.points = points
	outline.width = 5.2
	core.width = 2.4
	outline.default_color = Color(0.07, 0.11, 0.14, 0.88 * visibility)
	core.default_color = Color(0.86, 0.91, 0.84, 0.90 * visibility)


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


static func _smoother_step(value: float) -> float:
	value = clampf(value, 0.0, 1.0)
	return value * value * value * (value * (value * 6.0 - 15.0) + 10.0)
