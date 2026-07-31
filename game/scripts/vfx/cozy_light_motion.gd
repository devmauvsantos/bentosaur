class_name CozyLightMotion
extends RefCounted

# Production living-light profile. The registered village emission drifts
# between alternating low and high bands, while individual visible fixtures
# receive rare, irregular bursts. Pulse and flick RNGs are deliberately split
# so rendering frame rate cannot change the event schedule.
const PULSE_LOW_LEVEL_RANGE := Vector2(0.78, 0.86)
const PULSE_HIGH_LEVEL_RANGE := Vector2(0.94, 1.0)
const PULSE_LOW_DURATION_RANGE := Vector2(4.8, 8.6)
const PULSE_HIGH_DURATION_RANGE := Vector2(5.4, 11.5)
const HALO_PULSE_COUPLING := 0.72

const FIRST_FLICK_DELAY_RANGE := Vector2(60.0, 105.0)
const FLICK_INTERVAL_RANGE := Vector2(60.0, 105.0)
const FLICK_COUNT_RANGE := Vector2i(1, 3)
const FLICK_DIP_LEVEL_RANGE := Vector2(0.36, 0.56)
const FLICK_DOWN_SECONDS_RANGE := Vector2(0.055, 0.110)
const FLICK_HOLD_SECONDS_RANGE := Vector2(0.035, 0.085)
const FLICK_UP_SECONDS_RANGE := Vector2(0.090, 0.190)
const FLICK_GAP_SECONDS_RANGE := Vector2(0.055, 0.180)
const FLICK_SEED_SALT := 0x5EED71C5

var elapsed := 0.0
var core_level := 1.0
var halo_level := 1.0
var flick_level := 1.0
var flick_target_index := 0
var flick_pulse_count := 0
var flick_started_this_step := false
var last_flick_started_at := -INF

var _pulse_rng := RandomNumberGenerator.new()
var _flick_rng := RandomNumberGenerator.new()
var _pulse_start_at := 0.0
var _pulse_end_at := 0.0
var _pulse_start_level := 1.0
var _pulse_target_level := 1.0
var _next_pulse_is_low := true
var _flick_target_count := 1
var _previous_flick_target_index := -1
var _next_flick_at := INF
var _active_flick_start := -INF
var _active_flick_end := -INF
var _flick_starts := PackedFloat32Array()
var _flick_down_ends := PackedFloat32Array()
var _flick_hold_ends := PackedFloat32Array()
var _flick_up_ends := PackedFloat32Array()
var _flick_dip_levels := PackedFloat32Array()


func reset(seed: int = -1, target_count: int = 1) -> void:
	elapsed = 0.0
	core_level = 1.0
	halo_level = 1.0
	flick_level = 1.0
	flick_target_index = 0
	flick_pulse_count = 0
	flick_started_this_step = false
	last_flick_started_at = -INF
	_flick_target_count = maxi(target_count, 1)
	_previous_flick_target_index = -1
	_active_flick_start = -INF
	_active_flick_end = -INF
	_clear_flick_shape()

	if seed < 0:
		_pulse_rng.randomize()
		_flick_rng.randomize()
	else:
		_pulse_rng.seed = seed
		_flick_rng.seed = seed ^ FLICK_SEED_SALT

	_pulse_start_at = 0.0
	_pulse_start_level = 1.0
	_next_pulse_is_low = true
	_begin_next_pulse_segment()
	_next_flick_at = _flick_rng.randf_range(
		FIRST_FLICK_DELAY_RANGE.x,
		FIRST_FLICK_DELAY_RANGE.y
	)


func advance(delta: float) -> void:
	var previous_elapsed := elapsed
	elapsed += maxf(delta, 0.0)
	flick_started_this_step = false
	_advance_pulse()
	_advance_flick(previous_elapsed)
	halo_level = 1.0 + (
		core_level - 1.0
	) * HALO_PULSE_COUPLING


func _begin_next_pulse_segment() -> void:
	var level_range := (
		PULSE_LOW_LEVEL_RANGE
		if _next_pulse_is_low
		else PULSE_HIGH_LEVEL_RANGE
	)
	var duration_range := (
		PULSE_LOW_DURATION_RANGE
		if _next_pulse_is_low
		else PULSE_HIGH_DURATION_RANGE
	)
	_pulse_target_level = _pulse_rng.randf_range(
		level_range.x,
		level_range.y
	)
	_pulse_end_at = _pulse_start_at + _pulse_rng.randf_range(
		duration_range.x,
		duration_range.y
	)
	_next_pulse_is_low = not _next_pulse_is_low


func _advance_pulse() -> void:
	while elapsed >= _pulse_end_at:
		_pulse_start_level = _pulse_target_level
		_pulse_start_at = _pulse_end_at
		_begin_next_pulse_segment()
	var progress := inverse_lerp(_pulse_start_at, _pulse_end_at, elapsed)
	core_level = lerpf(
		_pulse_start_level,
		_pulse_target_level,
		_smoother_step(progress)
	)


func _advance_flick(previous_elapsed: float) -> void:
	while elapsed >= _next_flick_at:
		var event_start := _next_flick_at
		_start_flick(event_start)
		if event_start > previous_elapsed:
			flick_started_this_step = true
			last_flick_started_at = event_start
		_next_flick_at = _active_flick_end + _flick_rng.randf_range(
			FLICK_INTERVAL_RANGE.x,
			FLICK_INTERVAL_RANGE.y
		)

	if elapsed < _active_flick_start or elapsed >= _active_flick_end:
		flick_level = 1.0
		return
	flick_level = _sample_flick(elapsed - _active_flick_start)


func _start_flick(event_start: float) -> void:
	_active_flick_start = event_start
	flick_target_index = _choose_flick_target()
	_previous_flick_target_index = flick_target_index
	flick_pulse_count = _flick_rng.randi_range(
		FLICK_COUNT_RANGE.x,
		FLICK_COUNT_RANGE.y
	)
	_clear_flick_shape()

	var cursor := 0.0
	for pulse_index: int in range(flick_pulse_count):
		var down_seconds := _flick_rng.randf_range(
			FLICK_DOWN_SECONDS_RANGE.x,
			FLICK_DOWN_SECONDS_RANGE.y
		)
		var hold_seconds := _flick_rng.randf_range(
			FLICK_HOLD_SECONDS_RANGE.x,
			FLICK_HOLD_SECONDS_RANGE.y
		)
		var up_seconds := _flick_rng.randf_range(
			FLICK_UP_SECONDS_RANGE.x,
			FLICK_UP_SECONDS_RANGE.y
		)
		_flick_starts.append(cursor)
		cursor += down_seconds
		_flick_down_ends.append(cursor)
		cursor += hold_seconds
		_flick_hold_ends.append(cursor)
		cursor += up_seconds
		_flick_up_ends.append(cursor)
		_flick_dip_levels.append(
			_flick_rng.randf_range(
				FLICK_DIP_LEVEL_RANGE.x,
				FLICK_DIP_LEVEL_RANGE.y
			)
		)
		if pulse_index < flick_pulse_count - 1:
			cursor += _flick_rng.randf_range(
				FLICK_GAP_SECONDS_RANGE.x,
				FLICK_GAP_SECONDS_RANGE.y
			)
	_active_flick_end = event_start + cursor


func _choose_flick_target() -> int:
	var target := _flick_rng.randi_range(0, _flick_target_count - 1)
	if _flick_target_count > 1 and target == _previous_flick_target_index:
		target = (
			_previous_flick_target_index
			+ _flick_rng.randi_range(1, _flick_target_count - 1)
		) % _flick_target_count
	return target


func _sample_flick(local_time: float) -> float:
	for pulse_index: int in range(flick_pulse_count):
		var start := _flick_starts[pulse_index]
		var down_end := _flick_down_ends[pulse_index]
		var hold_end := _flick_hold_ends[pulse_index]
		var up_end := _flick_up_ends[pulse_index]
		var dip := _flick_dip_levels[pulse_index]
		if local_time < start:
			return 1.0
		if local_time < down_end:
			return lerpf(
				1.0,
				dip,
				_smoother_step(inverse_lerp(start, down_end, local_time))
			)
		if local_time < hold_end:
			return dip
		if local_time < up_end:
			return lerpf(
				dip,
				1.0,
				_smoother_step(inverse_lerp(hold_end, up_end, local_time))
			)
	return 1.0


func _clear_flick_shape() -> void:
	_flick_starts.clear()
	_flick_down_ends.clear()
	_flick_hold_ends.clear()
	_flick_up_ends.clear()
	_flick_dip_levels.clear()


static func _smoother_step(value: float) -> float:
	value = clampf(value, 0.0, 1.0)
	return value * value * value * (value * (value * 6.0 - 15.0) + 10.0)
