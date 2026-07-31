class_name StallLanternFixture
extends Node2D

signal powered_changed(enabled: bool)
signal power_transition_finished(enabled: bool)

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

var _powered := true
var _reduced_motion := false
var _sway_elapsed := 0.0
var _sway_rotation := 0.0
var _pulse_level := 1.0
var _flick_level := 1.0
var _core_power := 1.0
var _halo_power := 1.0
var _power_tween: Tween


func _ready() -> void:
	_powered = powered_on_ready
	_core_power = 1.0 if _powered else 0.0
	_halo_power = 1.0 if _powered else 0.0
	_apply_light_visuals()


func _process(delta: float) -> void:
	if self_driven_wind and not deterministic_test_mode:
		_advance_sway(0.0, delta, false)


func _exit_tree() -> void:
	_kill_power_tween()


func set_powered(enabled: bool, immediate: bool = false) -> void:
	var changed := _powered != enabled
	_powered = enabled
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
		_set_sway_rotation(0.0)
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


func _advance_sway(
	wind_level: float,
	delta: float,
	has_external_wind: bool
) -> void:
	delta = maxf(delta, 0.0)
	_sway_elapsed += delta
	if _reduced_motion:
		_set_sway_rotation(0.0)
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
	_set_sway_rotation(lerpf(_sway_rotation, target, response_weight))


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
	_set_sway_rotation(0.0)


func _set_core_power(level: float) -> void:
	_core_power = clampf(level, 0.0, 1.0)
	_apply_light_visuals()


func _set_halo_power(level: float) -> void:
	_halo_power = clampf(level, 0.0, 1.0)
	_apply_light_visuals()


func _set_sway_rotation(value: float) -> void:
	_sway_rotation = clampf(
		value,
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
	var core_level := clampf(pulse * flick, 0.0, 1.0)
	var halo_level := clampf(
		lerpf(1.0, pulse, HALO_PULSE_COUPLING)
		* lerpf(1.0, flick, HALO_FLICK_COUPLING),
		0.0,
		1.0
	)
	core.modulate = Color(1.0, 1.0, 1.0, CORE_BASE_ALPHA * _core_power * core_level)
	local_halo.modulate = Color(
		1.0,
		1.0,
		1.0,
		HALO_BASE_ALPHA * _halo_power * halo_level
	)


func _kill_power_tween() -> void:
	if _power_tween != null and _power_tween.is_valid():
		_power_tween.kill()
	_power_tween = null


func _on_power_transition_finished(enabled: bool) -> void:
	_power_tween = null
	power_transition_finished.emit(enabled)
