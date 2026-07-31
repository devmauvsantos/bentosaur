class_name CozyLightMotion
extends RefCounted

const PULSE_LEVEL_RANGE := Vector2(0.992, 1.006)
const PULSE_DURATION_RANGE := Vector2(3.8, 10.5)
const FLICK_INTERVAL_RANGE := Vector2(60.0, 105.0)
const FLICK_DURATION_RANGE := Vector2(0.18, 0.28)
const FLICK_DIP_RANGE := Vector2(0.955, 0.975)
const FLICK_REBOUND_RANGE := Vector2(1.001, 1.003)
const FLICK_SEED_SALT := 0x5F3759DF

var elapsed := 0.0
var core_level := 1.0
var halo_level := 1.0
var flick_level := 1.0
var flick_target_index := 0
var flick_started_this_step := false
var last_flick_started_at := -INF

var _pulse_rng := RandomNumberGenerator.new()
var _flick_rng := RandomNumberGenerator.new()
var _target_count := 1
var _pulse_elapsed := 0.0
var _pulse_duration := 1.0
var _pulse_from := 1.0
var _pulse_to := 1.0
var _next_flick_at := INF
var _flick_started_at := -INF
var _flick_duration := 0.0
var _flick_dip := 1.0
var _flick_rebound := 1.0
var _flick_active := false


func reset(seed: int = -1, target_count: int = 1) -> void:
	_target_count = maxi(target_count, 1)
	if seed >= 0:
		_pulse_rng.seed = seed
		_flick_rng.seed = seed ^ FLICK_SEED_SALT
	else:
		_pulse_rng.randomize()
		_flick_rng.randomize()
	elapsed = 0.0
	core_level = 1.0
	halo_level = 1.0
	flick_level = 1.0
	flick_target_index = 0
	flick_started_this_step = false
	last_flick_started_at = -INF
	_pulse_elapsed = 0.0
	_pulse_duration = _random_pulse(PULSE_DURATION_RANGE)
	_pulse_from = 1.0
	_pulse_to = _random_pulse(PULSE_LEVEL_RANGE)
	_next_flick_at = _random_flick(FLICK_INTERVAL_RANGE)
	_flick_started_at = -INF
	_flick_duration = 0.0
	_flick_dip = 1.0
	_flick_rebound = 1.0
	_flick_active = false


func advance(delta: float) -> void:
	delta = maxf(delta, 0.0)
	elapsed += delta
	flick_started_this_step = false
	_advance_pulse(delta)
	_advance_flick()


func _advance_pulse(delta: float) -> void:
	_pulse_elapsed += delta
	while _pulse_elapsed >= _pulse_duration:
		_pulse_elapsed -= _pulse_duration
		_pulse_from = _pulse_to
		_pulse_to = _random_pulse(PULSE_LEVEL_RANGE)
		_pulse_duration = _random_pulse(PULSE_DURATION_RANGE)

	var pulse_phase := clampf(_pulse_elapsed / _pulse_duration, 0.0, 1.0)
	core_level = lerpf(
		_pulse_from,
		_pulse_to,
		_smoother_step(pulse_phase)
	)
	halo_level = 1.0 + (core_level - 1.0) * 0.55


func _advance_flick() -> void:
	while true:
		if not _flick_active:
			if elapsed < _next_flick_at:
				flick_level = 1.0
				return
			_flick_active = true
			_flick_started_at = _next_flick_at
			last_flick_started_at = _flick_started_at
			_flick_duration = _random_flick(FLICK_DURATION_RANGE)
			_flick_dip = _random_flick(FLICK_DIP_RANGE)
			_flick_rebound = _random_flick(FLICK_REBOUND_RANGE)
			flick_target_index = _flick_rng.randi_range(0, _target_count - 1)
			flick_started_this_step = true

		var flick_phase := (elapsed - _flick_started_at) / _flick_duration
		if flick_phase < 1.0:
			flick_level = _sample_flick(flick_phase)
			return

		_flick_active = false
		flick_level = 1.0
		_next_flick_at = (
			_flick_started_at
			+ _flick_duration
			+ _random_flick(FLICK_INTERVAL_RANGE)
		)


func _sample_flick(phase: float) -> float:
	phase = clampf(phase, 0.0, 1.0)
	if phase < 0.30:
		return lerpf(1.0, _flick_dip, _smoother_step(phase / 0.30))
	if phase < 0.52:
		return lerpf(
			_flick_dip,
			_flick_rebound,
			_smoother_step((phase - 0.30) / 0.22)
		)
	return lerpf(
		_flick_rebound,
		1.0,
		_smoother_step((phase - 0.52) / 0.48)
	)


func _random_pulse(value_range: Vector2) -> float:
	return _pulse_rng.randf_range(value_range.x, value_range.y)


func _random_flick(value_range: Vector2) -> float:
	return _flick_rng.randf_range(value_range.x, value_range.y)


static func _smoother_step(value: float) -> float:
	value = clampf(value, 0.0, 1.0)
	return value * value * value * (value * (value * 6.0 - 15.0) + 10.0)
