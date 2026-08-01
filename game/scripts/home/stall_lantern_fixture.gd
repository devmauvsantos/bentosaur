class_name StallLanternFixture
extends Node2D

signal powered_changed(enabled: bool)
signal power_transition_finished(enabled: bool)
signal tapped
signal interaction_light_level_changed(level: float)

const HARD_MAX_SWAY_DEGREES := 1.4
const HARD_MAX_SWAY_RADIANS := deg_to_rad(HARD_MAX_SWAY_DEGREES)
const CORE_BASE_ALPHA := 0.68
const HALO_BASE_ALPHA := 0.82
const HALO_PULSE_COUPLING := 0.72
const HALO_FLICK_COUPLING := 0.78
const POWER_ON_CORE_SECONDS := 0.18
const POWER_ON_HALO_SECONDS := 0.26
const POWER_OFF_CORE_SECONDS := 0.10
const POWER_OFF_HALO_SECONDS := 0.16
const REDUCED_MOTION_POWER_SECONDS := 0.10
const TAP_COOLDOWN_SECONDS := 1.5
const TAP_SWING_DURATION_SECONDS := 1.10
const TAP_SWING_FREQUENCY_HZ := 2.35
const TAP_SWING_DAMPING := 2.9
const TAP_SWING_PEAK_RADIANS := deg_to_rad(1.15)
const TAP_HALO_COUPLING := 0.84

@export var powered_on_ready := true
@export var deterministic_test_mode := false
@export var self_driven_wind := true
@export_range(0.0, HARD_MAX_SWAY_DEGREES, 0.05) var sway_amplitude_degrees := 0.85
@export_range(2.0, 20.0, 0.1) var sway_period_seconds := 6.4
@export_range(0.0, 1.0, 0.01) var wind_influence := 0.42
@export_range(0.1, 12.0, 0.1) var sway_response := 2.8
@export var phase_offset_radians := 0.0

@onready var anchor: Sprite2D = $Anchor
@onready var sway_pivot: Node2D = $SwayPivot
@onready var body_off: Sprite2D = $SwayPivot/BodyOff
@onready var core: Sprite2D = $SwayPivot/Core
@onready var local_halo: Sprite2D = $SwayPivot/LocalHalo
@onready var tap_target: Area2D = $SwayPivot/TapTarget

var _powered := true
var _reduced_motion := false
var _sway_elapsed := 0.0
var _ambient_sway_rotation := 0.0
var _interaction_swing_rotation := 0.0
var _sway_rotation := 0.0
var _pulse_level := 1.0
var _flick_level := 1.0
var _core_power := 1.0
var _halo_power := 1.0
var _power_tween: Tween
var _tap_cooldown_remaining := 0.0
var _tap_elapsed := 0.0
var _tap_active := false
var _interaction_light_level := 1.0


func _ready() -> void:
	_powered = powered_on_ready
	_core_power = 1.0 if _powered else 0.0
	_halo_power = 1.0 if _powered else 0.0
	tap_target.input_event.connect(_on_tap_target_input_event)
	_apply_light_visuals()


func _process(delta: float) -> void:
	_advance_tap_interaction(maxf(delta, 0.0))
	if self_driven_wind and not deterministic_test_mode:
		_advance_sway(0.0, delta, false)


func _exit_tree() -> void:
	_kill_power_tween()


func set_powered(enabled: bool, immediate: bool = false) -> void:
	var changed := _powered != enabled
	_powered = enabled
	if not enabled:
		_cancel_tap_interaction()
	_kill_power_tween()

	var target := 1.0 if enabled else 0.0
	if immediate or not is_inside_tree():
		_set_core_power(target)
		_set_halo_power(target)
		if changed:
			powered_changed.emit(enabled)
		power_transition_finished.emit(enabled)
		return

	var core_seconds := (
		POWER_ON_CORE_SECONDS if enabled else POWER_OFF_CORE_SECONDS
	)
	var halo_seconds := (
		POWER_ON_HALO_SECONDS if enabled else POWER_OFF_HALO_SECONDS
	)
	if _reduced_motion:
		core_seconds = REDUCED_MOTION_POWER_SECONDS
		halo_seconds = REDUCED_MOTION_POWER_SECONDS

	_power_tween = create_tween().set_parallel(true)
	_power_tween.tween_method(
		_set_core_power,
		_core_power,
		target,
		core_seconds
	).set_trans(Tween.TRANS_QUART).set_ease(
		Tween.EASE_OUT if enabled else Tween.EASE_IN
	)
	_power_tween.tween_method(
		_set_halo_power,
		_halo_power,
		target,
		halo_seconds
	).set_trans(Tween.TRANS_QUART).set_ease(
		Tween.EASE_OUT if enabled else Tween.EASE_IN
	)
	_power_tween.finished.connect(_on_power_transition_finished.bind(enabled))
	if changed:
		powered_changed.emit(enabled)


func is_powered() -> bool:
	return _powered


func set_reduced_motion(enabled: bool) -> void:
	_reduced_motion = enabled
	if enabled:
		_cancel_tap_interaction()
		_apply_composed_sway()
	_apply_light_visuals()


func is_reduced_motion() -> bool:
	return _reduced_motion


func set_self_driven_wind(enabled: bool) -> void:
	self_driven_wind = enabled


func apply_light_motion(pulse_level: float, flick_level: float = 1.0) -> void:
	_pulse_level = clampf(pulse_level, 0.0, 1.2)
	_flick_level = clampf(flick_level, 0.0, 1.0)
	_apply_light_visuals()


func apply_wind(wind_level: float, delta: float) -> void:
	_advance_sway(wind_level, delta, true)


func try_tap_interaction() -> bool:
	if (
		not _powered
		or _reduced_motion
		or _tap_cooldown_remaining > 0.0
	):
		return false
	_tap_cooldown_remaining = TAP_COOLDOWN_SECONDS
	_tap_elapsed = 0.0
	_tap_active = true
	_set_interaction_light_level(_sample_tap_light(0.0))
	_set_interaction_swing_rotation(0.0)
	tapped.emit()
	return true


func is_tap_cooling_down() -> bool:
	return _tap_cooldown_remaining > 0.0


func get_tap_cooldown_remaining() -> float:
	return _tap_cooldown_remaining


func is_tap_interaction_active() -> bool:
	return _tap_active


func get_interaction_light_level() -> float:
	return _interaction_light_level


func get_interaction_swing_rotation() -> float:
	return _interaction_swing_rotation


func advance_tap_interaction_for_test(delta: float) -> void:
	assert(deterministic_test_mode, "Manual tap advance is test-only.")
	_advance_tap_interaction(maxf(delta, 0.0))


func _advance_sway(
	wind_level: float,
	delta: float,
	has_external_wind: bool
) -> void:
	delta = maxf(delta, 0.0)
	_sway_elapsed += delta
	if _reduced_motion:
		_ambient_sway_rotation = 0.0
		_apply_composed_sway()
		return

	var safe_period := maxf(sway_period_seconds, 0.001)
	var ambient_wave := sin(
		TAU * _sway_elapsed / safe_period + phase_offset_radians
	)
	var external_wind := clampf(wind_level, -1.0, 1.0)
	var mixed_wind := ambient_wave
	if has_external_wind:
		mixed_wind = lerpf(ambient_wave, external_wind, wind_influence)
	var target := deg_to_rad(sway_amplitude_degrees) * mixed_wind
	target = clampf(target, -HARD_MAX_SWAY_RADIANS, HARD_MAX_SWAY_RADIANS)

	var response_weight := 1.0 - exp(-sway_response * delta)
	_ambient_sway_rotation = clampf(
		lerpf(_ambient_sway_rotation, target, response_weight),
		-HARD_MAX_SWAY_RADIANS,
		HARD_MAX_SWAY_RADIANS
	)
	_apply_composed_sway()


func get_sway_phase_seconds() -> float:
	return _sway_elapsed


func get_sway_rotation() -> float:
	return _sway_rotation


func set_deterministic_test_mode(
	enabled: bool,
	elapsed_seconds: float = 0.0
) -> void:
	deterministic_test_mode = enabled
	if not enabled:
		return
	_sway_elapsed = maxf(elapsed_seconds, 0.0)
	_ambient_sway_rotation = 0.0
	_set_interaction_swing_rotation(0.0)


func _set_core_power(level: float) -> void:
	_core_power = clampf(level, 0.0, 1.0)
	_apply_light_visuals()


func _set_halo_power(level: float) -> void:
	_halo_power = clampf(level, 0.0, 1.0)
	_apply_light_visuals()


func _set_interaction_swing_rotation(value: float) -> void:
	_interaction_swing_rotation = clampf(
		value,
		-HARD_MAX_SWAY_RADIANS,
		HARD_MAX_SWAY_RADIANS
	)
	_apply_composed_sway()


func _apply_composed_sway() -> void:
	var composed := 0.0
	if not _reduced_motion:
		composed = _ambient_sway_rotation + _interaction_swing_rotation
	_sway_rotation = clampf(
		composed,
		-HARD_MAX_SWAY_RADIANS,
		HARD_MAX_SWAY_RADIANS
	)
	if sway_pivot != null:
		sway_pivot.rotation = _sway_rotation


func _apply_light_visuals() -> void:
	if core == null or local_halo == null:
		return
	var pulse := 1.0 if _reduced_motion else _pulse_level
	var flick := 1.0 if _reduced_motion else _flick_level
	var tap_level := 1.0 if _reduced_motion else _interaction_light_level
	var core_level := clampf(pulse * flick * tap_level, 0.0, 1.0)
	var halo_level := clampf(
		lerpf(1.0, pulse, HALO_PULSE_COUPLING)
		* lerpf(1.0, flick, HALO_FLICK_COUPLING)
		* lerpf(1.0, tap_level, TAP_HALO_COUPLING),
		0.0,
		1.0
	)
	core.modulate = Color(
		1.0,
		1.0,
		1.0,
		CORE_BASE_ALPHA * _core_power * core_level
	)
	local_halo.modulate = Color(
		1.0,
		1.0,
		1.0,
		HALO_BASE_ALPHA * _halo_power * halo_level
	)


func _advance_tap_interaction(delta: float) -> void:
	_tap_cooldown_remaining = maxf(_tap_cooldown_remaining - delta, 0.0)
	if not _tap_active:
		return
	_tap_elapsed += delta
	if _tap_elapsed >= TAP_SWING_DURATION_SECONDS:
		_tap_active = false
		_set_interaction_swing_rotation(0.0)
		_set_interaction_light_level(1.0)
		return

	var envelope := exp(-TAP_SWING_DAMPING * _tap_elapsed)
	var swing := (
		sin(TAU * TAP_SWING_FREQUENCY_HZ * _tap_elapsed)
		* envelope
		* TAP_SWING_PEAK_RADIANS
	)
	_set_interaction_swing_rotation(swing)
	_set_interaction_light_level(_sample_tap_light(_tap_elapsed))


func _sample_tap_light(elapsed: float) -> float:
	# Two soft, irregular dips read as a tactile lantern flick without strobing.
	var first_dip := 0.46 * exp(-pow(elapsed / 0.040, 2.0))
	var second_dip := 0.29 * exp(-pow((elapsed - 0.155) / 0.044, 2.0))
	return clampf(1.0 - first_dip - second_dip, 0.52, 1.0)


func _set_interaction_light_level(level: float) -> void:
	var next_level := clampf(level, 0.0, 1.0)
	if is_equal_approx(_interaction_light_level, next_level):
		return
	_interaction_light_level = next_level
	_apply_light_visuals()
	interaction_light_level_changed.emit(_interaction_light_level)


func _cancel_tap_interaction() -> void:
	_tap_active = false
	_tap_elapsed = 0.0
	_tap_cooldown_remaining = 0.0
	_set_interaction_swing_rotation(0.0)
	_set_interaction_light_level(1.0)


func _on_tap_target_input_event(
	viewport: Node,
	event: InputEvent,
	_shape_index: int
) -> void:
	var pressed := false
	if event is InputEventScreenTouch:
		pressed = (event as InputEventScreenTouch).pressed
	elif event is InputEventMouseButton:
		var mouse_event := event as InputEventMouseButton
		pressed = mouse_event.pressed and mouse_event.button_index == MOUSE_BUTTON_LEFT
	if not pressed or not try_tap_interaction():
		return
	viewport.set_input_as_handled()


func _kill_power_tween() -> void:
	if _power_tween != null and _power_tween.is_valid():
		_power_tween.kill()
	_power_tween = null


func _on_power_transition_finished(enabled: bool) -> void:
	_power_tween = null
	power_transition_finished.emit(enabled)
