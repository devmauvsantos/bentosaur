class_name CozyLightMotion
extends RefCounted

# Temporary physical-device diagnostic. It repeats one guaranteed, known
# trajectory so visibility can be judged through rain, Retina, and preset 3.
const CYCLE_SECONDS := 8.0
const FULL_HOLD_END := 0.80
const BREATHE_DOWN_END := 2.20
const LOW_HOLD_END := 3.00
const BREATHE_RECOVERY_END := 4.40
const FLICK_START := 5.30
const FLICK_FIRST_DIP_END := 5.38
const FLICK_FIRST_HOLD_END := 5.48
const FLICK_REBOUND_END := 5.56
const FLICK_SECOND_DIP_END := 5.64
const FLICK_END := 5.85
const CORE_MIN_LEVEL := 0.55
const HALO_PULSE_COUPLING := 0.85
const FLICK_FIRST_DIP_LEVEL := 0.12
const FLICK_REBOUND_LEVEL := 0.55
const FLICK_SECOND_DIP_LEVEL := 0.20
const FIXED_FLICK_TARGET_INDEX := 0

var elapsed := 0.0
var core_level := 1.0
var halo_level := 1.0
var flick_level := 1.0
var flick_target_index := FIXED_FLICK_TARGET_INDEX
var flick_started_this_step := false
var last_flick_started_at := -INF


func reset(_seed: int = -1, _target_count: int = 1) -> void:
	elapsed = 0.0
	core_level = 1.0
	halo_level = 1.0
	flick_level = 1.0
	flick_target_index = FIXED_FLICK_TARGET_INDEX
	flick_started_this_step = false
	last_flick_started_at = -INF


func advance(delta: float) -> void:
	delta = maxf(delta, 0.0)
	var previous_elapsed := elapsed
	elapsed += delta
	_update_flick_event(previous_elapsed, elapsed)

	var cycle_time := fmod(elapsed, CYCLE_SECONDS)
	core_level = _sample_breath(cycle_time)
	halo_level = 1.0 + (
		core_level - 1.0
	) * HALO_PULSE_COUPLING
	flick_level = _sample_flick(cycle_time)
	flick_target_index = FIXED_FLICK_TARGET_INDEX


func _sample_breath(cycle_time: float) -> float:
	if cycle_time < FULL_HOLD_END:
		return 1.0
	if cycle_time < BREATHE_DOWN_END:
		return lerpf(
			1.0,
			CORE_MIN_LEVEL,
			_smoother_step(
				(cycle_time - FULL_HOLD_END)
				/ (BREATHE_DOWN_END - FULL_HOLD_END)
			)
		)
	if cycle_time < LOW_HOLD_END:
		return CORE_MIN_LEVEL
	if cycle_time < BREATHE_RECOVERY_END:
		return lerpf(
			CORE_MIN_LEVEL,
			1.0,
			_smoother_step(
				(cycle_time - LOW_HOLD_END)
				/ (BREATHE_RECOVERY_END - LOW_HOLD_END)
			)
		)
	return 1.0


func _sample_flick(cycle_time: float) -> float:
	if cycle_time < FLICK_START or cycle_time >= FLICK_END:
		return 1.0
	if cycle_time < FLICK_FIRST_DIP_END:
		return lerpf(
			1.0,
			FLICK_FIRST_DIP_LEVEL,
			_smoother_step(
				(cycle_time - FLICK_START)
				/ (FLICK_FIRST_DIP_END - FLICK_START)
			)
		)
	if cycle_time < FLICK_FIRST_HOLD_END:
		return FLICK_FIRST_DIP_LEVEL
	if cycle_time < FLICK_REBOUND_END:
		return lerpf(
			FLICK_FIRST_DIP_LEVEL,
			FLICK_REBOUND_LEVEL,
			_smoother_step(
				(cycle_time - FLICK_FIRST_HOLD_END)
				/ (FLICK_REBOUND_END - FLICK_FIRST_HOLD_END)
			)
		)
	if cycle_time < FLICK_SECOND_DIP_END:
		return lerpf(
			FLICK_REBOUND_LEVEL,
			FLICK_SECOND_DIP_LEVEL,
			_smoother_step(
				(cycle_time - FLICK_REBOUND_END)
				/ (FLICK_SECOND_DIP_END - FLICK_REBOUND_END)
			)
		)
	return lerpf(
		FLICK_SECOND_DIP_LEVEL,
		1.0,
		_smoother_step(
			(cycle_time - FLICK_SECOND_DIP_END)
			/ (FLICK_END - FLICK_SECOND_DIP_END)
		)
	)


func _update_flick_event(previous_elapsed: float, current_elapsed: float) -> void:
	flick_started_this_step = false
	var event_cycle := floori(
		(previous_elapsed - FLICK_START) / CYCLE_SECONDS
	) + 1
	var next_event := float(event_cycle) * CYCLE_SECONDS + FLICK_START
	if next_event > previous_elapsed and next_event <= current_elapsed:
		flick_started_this_step = true
		last_flick_started_at = next_event


static func _smoother_step(value: float) -> float:
	value = clampf(value, 0.0, 1.0)
	return value * value * value * (value * (value * 6.0 - 15.0) + 10.0)
