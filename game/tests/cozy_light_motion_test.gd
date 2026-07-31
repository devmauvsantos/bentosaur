extends SceneTree

const MOTION := preload("res://scripts/vfx/cozy_light_motion.gd")
const TEST_SECONDS := 360.0
const TARGET_COUNT := 18
const TEST_SEED := 771901


func _initialize() -> void:
	var errors := PackedStringArray()
	_assert_production_constants(errors)
	var at_30_hz := _sample_motion(30, errors)
	var reference := _sample_motion(60, errors)
	var at_120_hz := _sample_motion(120, errors)

	_expect(
		reference["flick_times"] == at_30_hz["flick_times"]
			and reference["flick_times"] == at_120_hz["flick_times"],
		"Rare flick timing must be frame-rate independent.",
		errors
	)
	_expect(
		reference["flick_targets"] == at_30_hz["flick_targets"]
			and reference["flick_targets"] == at_120_hz["flick_targets"],
		"Every frame rate must select the same seeded fixture sequence.",
		errors
	)
	_expect(
		reference["flick_counts"] == at_30_hz["flick_counts"]
			and reference["flick_counts"] == at_120_hz["flick_counts"],
		"Every frame rate must select the same seeded 1-3 flick bursts.",
		errors
	)

	_finish(errors)


func _assert_production_constants(errors: PackedStringArray) -> void:
	_expect(
		MOTION.PULSE_LOW_LEVEL_RANGE == Vector2(0.78, 0.86)
			and MOTION.PULSE_HIGH_LEVEL_RANGE == Vector2(0.94, 1.0)
			and MOTION.PULSE_LOW_DURATION_RANGE == Vector2(4.8, 8.6)
			and MOTION.PULSE_HIGH_DURATION_RANGE == Vector2(5.4, 11.5),
		"Living light must alternate visibly separated low and high bands.",
		errors
	)
	_expect(
		is_equal_approx(MOTION.HALO_PULSE_COUPLING, 0.72),
		"Halos must inherit 72 percent of the core breathing trajectory.",
		errors
	)
	_expect(
		MOTION.FIRST_FLICK_DELAY_RANGE == Vector2(6.0, 12.0)
			and MOTION.FLICK_INTERVAL_RANGE == Vector2(14.0, 28.0),
		(
			"Fixture flicks must begin promptly, then recur at an irregular "
			+ "cozy cadence."
		),
		errors
	)
	_expect(
		MOTION.FLICK_COUNT_RANGE == Vector2i(1, 3)
			and MOTION.FLICK_DIP_LEVEL_RANGE == Vector2(0.36, 0.56),
		"Each event must choose one, two, or three readable dips.",
		errors
	)


func _sample_motion(frame_rate: int, errors: PackedStringArray) -> Dictionary:
	var motion := MOTION.new()
	motion.reset(TEST_SEED, TARGET_COUNT)
	var frame_delta := 1.0 / float(frame_rate)
	var sample_count := int(TEST_SECONDS * frame_rate)
	var flick_times := PackedFloat32Array()
	var flick_targets := PackedInt32Array()
	var flick_counts := PackedInt32Array()
	var core_min := INF
	var core_max := -INF
	var halo_min := INF
	var halo_max := -INF
	var local_flick_min := 1.0
	var halo_coupling_error := 0.0
	for _frame: int in range(sample_count):
		motion.advance(frame_delta)
		core_min = minf(core_min, motion.core_level)
		core_max = maxf(core_max, motion.core_level)
		halo_min = minf(halo_min, motion.halo_level)
		halo_max = maxf(halo_max, motion.halo_level)
		local_flick_min = minf(local_flick_min, motion.flick_level)
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
			flick_counts.append(motion.flick_pulse_count)

	_expect(
		core_min >= MOTION.PULSE_LOW_LEVEL_RANGE.x - 0.0001
			and core_min <= MOTION.PULSE_LOW_LEVEL_RANGE.y + 0.0001
			and core_max <= 1.0001
			and core_max >= 0.99,
		"Core RGB must visit the production low band without overshooting one.",
		errors
	)
	_expect(
		halo_min >= 0.8415
			and halo_max <= 1.0001
			and halo_coupling_error <= 0.000001,
		"Halo RGB must follow its attenuated, unclipped breathing formula.",
		errors
	)
	_expect(
		local_flick_min >= MOTION.FLICK_DIP_LEVEL_RANGE.x - 0.0001
			and local_flick_min < 0.70,
		"The sampled local RGB flick must remain bounded and readable.",
		errors
	)
	_expect(
		flick_times.size() >= 15 and flick_times.size() <= 19,
		"Six minutes should contain a restrained but visibly living event cadence.",
		errors
	)
	if not flick_times.is_empty():
		_expect(
			flick_times[0] >= MOTION.FIRST_FLICK_DELAY_RANGE.x
				and flick_times[0] <= MOTION.FIRST_FLICK_DELAY_RANGE.y,
			"The first fixture flick must begin within the production wake-up window.",
			errors
		)
	for event_index: int in range(flick_times.size()):
		_expect(
			flick_targets[event_index] >= 0
				and flick_targets[event_index] < TARGET_COUNT,
			"Every flick must target one of the registered visible fixtures.",
			errors
		)
		_expect(
			flick_counts[event_index] >= MOTION.FLICK_COUNT_RANGE.x
				and flick_counts[event_index] <= MOTION.FLICK_COUNT_RANGE.y,
			"Every event must contain between one and three flicks.",
			errors
		)
		if event_index == 0:
			continue
		_expect(
			flick_targets[event_index] != flick_targets[event_index - 1],
			"The same visible fixture must not flick twice in succession.",
			errors
		)
		var start_gap := flick_times[event_index] - flick_times[event_index - 1]
		_expect(
			start_gap >= MOTION.FLICK_INTERVAL_RANGE.x
				and start_gap <= MOTION.FLICK_INTERVAL_RANGE.y + 1.6,
			"Flick starts must preserve the configured irregular cadence.",
			errors
		)

	return {
		"flick_times": flick_times,
		"flick_targets": flick_targets,
		"flick_counts": flick_counts,
	}


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition and not errors.has(message):
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Production living-light motion contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
