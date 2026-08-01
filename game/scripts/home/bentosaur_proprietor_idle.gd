class_name BentosaurProprietorIdle
extends Node2D

signal blink_started(blink_number: int)
signal head_shift_started(shift_number: int, target_degrees: float)

const BREATH_PERIOD_SECONDS := 3.4
const BREATH_VERTICAL_EXPANSION := 0.005
const BREATH_HORIZONTAL_CONTRACTION := 0.0025
const BREATH_SPEED_MIN := 0.94
const BREATH_SPEED_MAX := 1.06
const BLINK_SECONDS := 0.18
const BLINK_INTERVAL_MIN_SECONDS := 2.3
const BLINK_INTERVAL_MAX_SECONDS := 5.4
const DOUBLE_BLINK_CHANCE := 0.12
const DOUBLE_BLINK_GAP_SECONDS := 0.14
const HEAD_SHIFT_INTERVAL_MIN_SECONDS := 6.5
const HEAD_SHIFT_INTERVAL_MAX_SECONDS := 10.0
const HEAD_SHIFT_LEAN_MIN_SECONDS := 0.72
const HEAD_SHIFT_LEAN_MAX_SECONDS := 1.05
const HEAD_SHIFT_HOLD_MIN_SECONDS := 0.28
const HEAD_SHIFT_HOLD_MAX_SECONDS := 0.72
const HEAD_SHIFT_RETURN_MIN_SECONDS := 0.82
const HEAD_SHIFT_RETURN_MAX_SECONDS := 1.18
const HEAD_SHIFT_DEGREES_MIN := 0.35
const HEAD_SHIFT_DEGREES_MAX := 0.50
const HEAD_SHIFT_SEED_SALT := 19793
const DETERMINISTIC_CAPTURE_SEED := 48043
const MAX_TRANSITIONS_PER_STEP := 16

enum BlinkState {
	OPEN,
	CLOSED,
	DOUBLE_BLINK_GAP,
}

enum HeadShiftState {
	REST,
	LEAN,
	HOLD,
	RETURN,
}

@export var active_on_ready := true
@export var reduced_motion_on_ready := false
@export var deterministic_test_mode := false
@export var motion_seed := -1

@onready var visual_root: Node2D = $VisualRoot
@onready var body_motion_root: Node2D = $VisualRoot/BodyMotionRoot
@onready var neutral_sprite: Sprite2D = $VisualRoot/BodyMotionRoot/Neutral
@onready var blink_sprite: Sprite2D = $VisualRoot/BodyMotionRoot/Blink
@onready var foreground_hands_sprite: Sprite2D = $VisualRoot/ForegroundHands

var _rng := RandomNumberGenerator.new()
var _head_rng := RandomNumberGenerator.new()
var _active := true
var _reduced_motion := false
var _base_visual_scale := Vector2.ONE
var _base_body_motion_scale := Vector2.ONE
var _base_body_motion_rotation := 0.0
var _elapsed_seconds := 0.0
var _breath_speed := 1.0
var _breath_phase_offset := 0.0
var _blink_state := BlinkState.OPEN
var _next_transition_at := INF
var _double_blink_pending := false
var _blink_count := 0
var _head_shift_state := HeadShiftState.REST
var _head_state_started_at := 0.0
var _next_head_transition_at := INF
var _head_target_rotation := 0.0
var _head_lean_seconds := 0.0
var _head_hold_seconds := 0.0
var _head_return_seconds := 0.0
var _head_shift_count := 0


func _ready() -> void:
	_base_visual_scale = visual_root.scale
	_base_body_motion_scale = body_motion_root.scale
	_base_body_motion_rotation = body_motion_root.rotation
	_active = active_on_ready
	_reduced_motion = reduced_motion_on_ready
	var args := OS.get_cmdline_user_args()
	var deterministic_capture := args.has("--deterministic-capture")
	if args.has("--reduced-motion"):
		_reduced_motion = true
	var seed := (
		DETERMINISTIC_CAPTURE_SEED
		if deterministic_capture or deterministic_test_mode
		else motion_seed
	)
	reset_motion(seed)
	set_process(not deterministic_test_mode)


func _process(delta: float) -> void:
	step_motion(delta)


func step_motion(delta: float) -> void:
	if not _active:
		return
	_elapsed_seconds += maxf(delta, 0.0)
	_advance_blink_state()
	_advance_head_shift_state()
	_apply_visuals()


func reset_motion(seed: int = -1) -> void:
	if seed >= 0:
		_rng.seed = seed
		_head_rng.seed = seed ^ HEAD_SHIFT_SEED_SALT
	else:
		_rng.randomize()
		_head_rng.randomize()
	_elapsed_seconds = 0.0
	_breath_speed = _rng.randf_range(BREATH_SPEED_MIN, BREATH_SPEED_MAX)
	_breath_phase_offset = _rng.randf()
	_blink_state = BlinkState.OPEN
	_double_blink_pending = false
	_blink_count = 0
	_next_transition_at = _random_blink_interval()
	_head_shift_count = 0
	_reset_head_shift_schedule(0.0)
	_apply_visuals()


func set_active(enabled: bool) -> void:
	if _active == enabled:
		_apply_visuals()
		return
	_active = enabled
	if enabled:
		_next_transition_at = _elapsed_seconds + _random_blink_interval()
		_reset_head_shift_schedule(_elapsed_seconds)
	else:
		_blink_state = BlinkState.OPEN
		_double_blink_pending = false
		_reset_head_shift_schedule(_elapsed_seconds)
	_apply_visuals()


func is_active() -> bool:
	return _active


func set_reduced_motion(enabled: bool) -> void:
	if _reduced_motion == enabled:
		_apply_visuals()
		return
	_reduced_motion = enabled
	_reset_head_shift_schedule(_elapsed_seconds)
	_apply_visuals()


func is_reduced_motion() -> bool:
	return _reduced_motion


func set_deterministic_test_mode(
	enabled: bool,
	seed: int = DETERMINISTIC_CAPTURE_SEED
) -> void:
	deterministic_test_mode = enabled
	set_process(not enabled)
	reset_motion(seed if enabled else motion_seed)


func is_blinking() -> bool:
	return _blink_state == BlinkState.CLOSED


func get_blink_count() -> int:
	return _blink_count


func is_head_shifting() -> bool:
	return _head_shift_state != HeadShiftState.REST


func get_head_shift_count() -> int:
	return _head_shift_count


func get_elapsed_seconds() -> float:
	return _elapsed_seconds


func get_breath_speed() -> float:
	return _breath_speed


func get_breath_phase_offset() -> float:
	return _breath_phase_offset


func get_visual_scale() -> Vector2:
	return visual_root.scale * body_motion_root.scale


func get_base_visual_scale() -> Vector2:
	return _base_visual_scale


func get_head_rotation_radians() -> float:
	return body_motion_root.rotation - _base_body_motion_rotation


func _advance_blink_state() -> void:
	var transition_count := 0
	while (
		_elapsed_seconds >= _next_transition_at
		and transition_count < MAX_TRANSITIONS_PER_STEP
	):
		transition_count += 1
		match _blink_state:
			BlinkState.OPEN:
				_blink_state = BlinkState.CLOSED
				_double_blink_pending = _rng.randf() < DOUBLE_BLINK_CHANCE
				_blink_count += 1
				blink_started.emit(_blink_count)
				_next_transition_at += BLINK_SECONDS
			BlinkState.CLOSED:
				if _double_blink_pending:
					_blink_state = BlinkState.DOUBLE_BLINK_GAP
					_double_blink_pending = false
					_next_transition_at += DOUBLE_BLINK_GAP_SECONDS
				else:
					_blink_state = BlinkState.OPEN
					_next_transition_at += _random_blink_interval()
			BlinkState.DOUBLE_BLINK_GAP:
				_blink_state = BlinkState.CLOSED
				_blink_count += 1
				blink_started.emit(_blink_count)
				_next_transition_at += BLINK_SECONDS


func _advance_head_shift_state() -> void:
	if not _active or _reduced_motion:
		return
	var transition_count := 0
	while (
		_elapsed_seconds >= _next_head_transition_at
		and transition_count < MAX_TRANSITIONS_PER_STEP
	):
		transition_count += 1
		var transition_at := _next_head_transition_at
		match _head_shift_state:
			HeadShiftState.REST:
				_head_shift_state = HeadShiftState.LEAN
				_head_state_started_at = transition_at
				_head_lean_seconds = _head_rng.randf_range(
					HEAD_SHIFT_LEAN_MIN_SECONDS,
					HEAD_SHIFT_LEAN_MAX_SECONDS
				)
				_head_hold_seconds = _head_rng.randf_range(
					HEAD_SHIFT_HOLD_MIN_SECONDS,
					HEAD_SHIFT_HOLD_MAX_SECONDS
				)
				_head_return_seconds = _head_rng.randf_range(
					HEAD_SHIFT_RETURN_MIN_SECONDS,
					HEAD_SHIFT_RETURN_MAX_SECONDS
				)
				var direction := -1.0 if _head_rng.randf() < 0.5 else 1.0
				_head_target_rotation = deg_to_rad(
					_head_rng.randf_range(
						HEAD_SHIFT_DEGREES_MIN,
						HEAD_SHIFT_DEGREES_MAX
					) * direction
				)
				_head_shift_count += 1
				head_shift_started.emit(
					_head_shift_count,
					rad_to_deg(_head_target_rotation)
				)
				_next_head_transition_at = (
					transition_at + _head_lean_seconds
				)
			HeadShiftState.LEAN:
				_head_shift_state = HeadShiftState.HOLD
				_head_state_started_at = transition_at
				_next_head_transition_at = (
					transition_at + _head_hold_seconds
				)
			HeadShiftState.HOLD:
				_head_shift_state = HeadShiftState.RETURN
				_head_state_started_at = transition_at
				_next_head_transition_at = (
					transition_at + _head_return_seconds
				)
			HeadShiftState.RETURN:
				_head_shift_state = HeadShiftState.REST
				_head_state_started_at = transition_at
				_head_target_rotation = 0.0
				_next_head_transition_at = (
					transition_at + _random_head_shift_interval()
				)


func _apply_visuals() -> void:
	if (
		visual_root == null
		or body_motion_root == null
		or neutral_sprite == null
		or blink_sprite == null
	):
		return
	var blinking := _active and _blink_state == BlinkState.CLOSED
	neutral_sprite.visible = not blinking
	blink_sprite.visible = blinking

	var scale_multiplier := Vector2.ONE
	if _active and not _reduced_motion:
		var phase := fmod(
			_breath_phase_offset
			+ _elapsed_seconds * _breath_speed / BREATH_PERIOD_SECONDS,
			1.0
		)
		var breath := 0.5 - 0.5 * cos(TAU * phase)
		scale_multiplier = Vector2(
			1.0 - BREATH_HORIZONTAL_CONTRACTION * breath,
			1.0 + BREATH_VERTICAL_EXPANSION * breath
		)
	body_motion_root.scale = _base_body_motion_scale * scale_multiplier
	body_motion_root.rotation = (
		_base_body_motion_rotation + _sample_head_rotation()
	)


func _sample_head_rotation() -> float:
	if not _active or _reduced_motion:
		return 0.0
	match _head_shift_state:
		HeadShiftState.LEAN:
			return _head_target_rotation * _ease_in_out(
				_state_progress(_head_lean_seconds)
			)
		HeadShiftState.HOLD:
			return _head_target_rotation
		HeadShiftState.RETURN:
			return _head_target_rotation * (
				1.0 - _ease_in_out(_state_progress(_head_return_seconds))
			)
	return 0.0


func _state_progress(duration: float) -> float:
	if duration <= 0.0:
		return 1.0
	return clampf(
		(_elapsed_seconds - _head_state_started_at) / duration,
		0.0,
		1.0
	)


func _ease_in_out(value: float) -> float:
	var t := clampf(value, 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)


func _reset_head_shift_schedule(from_time: float) -> void:
	_head_shift_state = HeadShiftState.REST
	_head_state_started_at = from_time
	_head_target_rotation = 0.0
	if _active and not _reduced_motion:
		_next_head_transition_at = (
			from_time + _random_head_shift_interval()
		)
	else:
		_next_head_transition_at = INF


func _random_blink_interval() -> float:
	return _rng.randf_range(
		BLINK_INTERVAL_MIN_SECONDS,
		BLINK_INTERVAL_MAX_SECONDS
	)


func _random_head_shift_interval() -> float:
	return _head_rng.randf_range(
		HEAD_SHIFT_INTERVAL_MIN_SECONDS,
		HEAD_SHIFT_INTERVAL_MAX_SECONDS
	)
