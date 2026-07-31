class_name CounterOilLanternFixture
extends Node2D

signal powered_changed(enabled: bool)
signal power_transition_finished(enabled: bool)

const BODY_BOX_SIZE := Vector2(63.0, 115.0)
const SHADOW_BOX_SIZE := Vector2(72.0, 18.0)
const ROOT_PARENT_POSITION := Vector2(240.5, 722.0)
const CORE_BASE_ALPHA := 0.62
const HALO_BASE_ALPHA := 0.48
const HALO_PULSE_COUPLING := 0.72
const HALO_FLICK_COUPLING := 0.78
const POWER_ON_CORE_SECONDS := 0.18
const POWER_ON_HALO_SECONDS := 0.26
const POWER_OFF_CORE_SECONDS := 0.10
const POWER_OFF_HALO_SECONDS := 0.16
const REDUCED_MOTION_POWER_SECONDS := 0.10

@export var powered_on_ready := true

@onready var contact_shadow: Sprite2D = $ContactShadow
@onready var local_halo: Sprite2D = $LocalHalo
@onready var body_off: Sprite2D = $BodyOff
@onready var core: Sprite2D = $Core

var _powered := true
var _reduced_motion := false
var _pulse_level := 1.0
var _flick_level := 1.0
var _core_power := 1.0
var _halo_power := 1.0
var _power_tween: Tween


func _ready() -> void:
	_fit_sprite(body_off, BODY_BOX_SIZE)
	_fit_sprite(core, Vector2(31.0, 58.0))
	_fit_sprite(local_halo, Vector2(110.0, 146.0))
	_fit_sprite(contact_shadow, SHADOW_BOX_SIZE)
	_powered = powered_on_ready
	_core_power = 1.0 if _powered else 0.0
	_halo_power = 1.0 if _powered else 0.0
	_apply_light_visuals()


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

	var core_seconds := POWER_ON_CORE_SECONDS if enabled else POWER_OFF_CORE_SECONDS
	var halo_seconds := POWER_ON_HALO_SECONDS if enabled else POWER_OFF_HALO_SECONDS
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
	_apply_light_visuals()


func is_reduced_motion() -> bool:
	return _reduced_motion


func apply_light_motion(pulse_level: float, flick_level: float = 1.0) -> void:
	_pulse_level = clampf(pulse_level, 0.0, 1.2)
	_flick_level = clampf(flick_level, 0.0, 1.0)
	_apply_light_visuals()


func _set_core_power(level: float) -> void:
	_core_power = clampf(level, 0.0, 1.0)
	_apply_light_visuals()


func _set_halo_power(level: float) -> void:
	_halo_power = clampf(level, 0.0, 1.0)
	_apply_light_visuals()


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
	# Power fades own alpha. Ambient pulse/flick owns RGB so it survives the
	# Retina additive composite used by the current iOS home scene.
	core.modulate = Color(
		core_level,
		core_level,
		core_level,
		CORE_BASE_ALPHA * _core_power
	)
	local_halo.modulate = Color(
		halo_level,
		halo_level,
		halo_level,
		HALO_BASE_ALPHA * _halo_power
	)


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


func _kill_power_tween() -> void:
	if _power_tween != null and _power_tween.is_valid():
		_power_tween.kill()
	_power_tween = null


func _on_power_transition_finished(enabled: bool) -> void:
	_power_tween = null
	power_transition_finished.emit(enabled)
