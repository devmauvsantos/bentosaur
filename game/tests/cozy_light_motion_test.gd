extends SceneTree

const MOTION := preload("res://scripts/vfx/cozy_light_motion.gd")
const TEST_SECONDS := 16.0
const TARGET_COUNT := 8


func _initialize() -> void:
	var errors := PackedStringArray()
	_assert_diagnostic_constants(errors)
	var reference := _sample_motion(60, errors)
	var at_30_hz := _sample_motion(30, errors)
	var at_120_hz := _sample_motion(120, errors)

	_expect(
		reference["flick_times"] == at_30_hz["flick_times"]
			and reference["flick_times"] == at_120_hz["flick_times"],
		"Diagnostic flick timing must be frame-rate independent.",
		errors
	)
	_expect(
		reference["flick_targets"] == at_30_hz["flick_targets"]
			and reference["flick_targets"] == at_120_hz["flick_targets"],
		"Every frame rate must use the same fixed visible lantern.",
		errors
	)

	_finish(errors)


func _assert_diagnostic_constants(errors: PackedStringArray) -> void:
	_expect(
		is_equal_approx(MOTION.CYCLE_SECONDS, 8.0)
			and is_equal_approx(MOTION.FULL_HOLD_END, 0.80)
			and is_equal_approx(MOTION.BREATHE_DOWN_END, 2.20)
			and is_equal_approx(MOTION.LOW_HOLD_END, 3.00)
			and is_equal_approx(MOTION.BREATHE_RECOVERY_END, 4.40),
		"The diagnostic breath must keep its guaranteed eight-second trajectory.",
		errors
	)
	_expect(
		is_equal_approx(MOTION.CORE_MIN_LEVEL, 0.55)
			and is_equal_approx(MOTION.HALO_PULSE_COUPLING, 0.85),
		"The diagnostic breath minimum must remain unmistakable but unclipped.",
		errors
	)
	_expect(
		is_equal_approx(MOTION.FLICK_START, 5.30)
			and is_equal_approx(MOTION.FLICK_END, 5.85)
			and is_equal_approx(MOTION.FLICK_FIRST_DIP_LEVEL, 0.12)
			and is_equal_approx(MOTION.FLICK_REBOUND_LEVEL, 0.55)
			and is_equal_approx(MOTION.FLICK_SECOND_DIP_LEVEL, 0.20)
			and MOTION.FIXED_FLICK_TARGET_INDEX == 0,
		"The diagnostic must use the fixed double flick on the visible lantern.",
		errors
	)


func _sample_motion(frame_rate: int, errors: PackedStringArray) -> Dictionary:
	var motion := MOTION.new()
	motion.reset(771901, TARGET_COUNT)
	var frame_delta := 1.0 / float(frame_rate)
	var sample_count := int(TEST_SECONDS * frame_rate)
	var flick_times := PackedFloat32Array()
	var flick_targets := PackedInt32Array()
	var core_min := INF
	var core_max := -INF
	var halo_min := INF
	var halo_max := -INF
	var local_flick_min := 1.0
	var local_flick_max := 1.0
	var halo_coupling_error := 0.0
	for frame: int in range(sample_count):
		motion.advance(frame_delta)
		core_min = minf(core_min, motion.core_level)
		core_max = maxf(core_max, motion.core_level)
		halo_min = minf(halo_min, motion.halo_level)
		halo_max = maxf(halo_max, motion.halo_level)
		local_flick_min = minf(local_flick_min, motion.flick_level)
		local_flick_max = maxf(local_flick_max, motion.flick_level)
		halo_coupling_error = maxf(
			halo_coupling_error,
			absf(
				motion.halo_level
				- (
					1.0
					+ (motion.core_level - 1.0)
					* MOTION.HALO_PULSE_COUPLING
				)
			)
		)
		if motion.flick_started_this_step:
			flick_times.append(motion.last_flick_started_at)
			flick_targets.append(motion.flick_target_index)

	_expect(
		is_equal_approx(core_min, 0.55) and is_equal_approx(core_max, 1.0),
		"Every diagnostic cycle must reach full and the 55-percent hold.",
		errors
	)
	_expect(
		is_equal_approx(halo_min, 0.6175)
			and is_equal_approx(halo_max, 1.0)
			and halo_coupling_error <= 0.000001,
		"Halo RGB must inherit exactly 85 percent of the core trajectory.",
		errors
	)
	_expect(
		local_flick_min >= 0.1199
			and local_flick_min <= 0.1201
			and is_equal_approx(local_flick_max, 1.0),
		"The fixed fixture must visibly hold at the 12-percent first dip.",
		errors
	)
	_expect(
		flick_times == PackedFloat32Array([5.3, 13.3]),
		"Two cycles must report fixed flick starts at 5.3 and 13.3 seconds.",
		errors
	)
	_expect(
		flick_targets == PackedInt32Array([0, 0]),
		"Both diagnostic flicks must target the brightest visible lantern.",
		errors
	)

	return {
		"flick_times": flick_times,
		"flick_targets": flick_targets,
	}


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition and not errors.has(message):
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Device light diagnostic contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
