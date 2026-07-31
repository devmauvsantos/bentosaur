extends SceneTree

const MOTION := preload("res://scripts/vfx/cozy_light_motion.gd")
const TEST_SECONDS := 240.0


func _initialize() -> void:
	var errors := PackedStringArray()
	var reference := _sample_motion(60, errors)
	var at_30_hz := _sample_motion(30, errors)
	var at_120_hz := _sample_motion(120, errors)

	_expect(
		reference["flick_times"] == at_30_hz["flick_times"]
			and reference["flick_times"] == at_120_hz["flick_times"],
		"Rare flick scheduling must be frame-rate independent.",
		errors
	)
	_expect(
		reference["flick_targets"] == at_30_hz["flick_targets"]
			and reference["flick_targets"] == at_120_hz["flick_targets"],
		"The same seed must select the same local fixtures at every frame rate.",
		errors
	)

	_finish(errors)


func _sample_motion(frame_rate: int, errors: PackedStringArray) -> Dictionary:
	var motion := MOTION.new()
	motion.reset(771901, 10)
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
	for frame: int in range(sample_count):
		motion.advance(frame_delta)
		core_min = minf(core_min, motion.core_level)
		core_max = maxf(core_max, motion.core_level)
		halo_min = minf(halo_min, motion.halo_level)
		halo_max = maxf(halo_max, motion.halo_level)
		local_flick_min = minf(local_flick_min, motion.flick_level)
		local_flick_max = maxf(local_flick_max, motion.flick_level)
		if motion.flick_started_this_step:
			flick_times.append(motion.last_flick_started_at)
			flick_targets.append(motion.flick_target_index)

	_expect(
		core_min >= 0.992 and core_max <= 1.006,
		"Global core breathing must remain below a one-percent swing.",
		errors
	)
	_expect(
		halo_min >= 0.995 and halo_max <= 1.004,
		"Global halo breathing must be quieter than the cores.",
		errors
	)
	_expect(
		local_flick_min >= 0.955 and local_flick_min < 0.99,
		"The rare local fixture flick must be brief and restrained.",
		errors
	)
	_expect(
		local_flick_max <= 1.003
			and MOTION.PULSE_LEVEL_RANGE.y * local_flick_max * 0.99 < 1.0,
		"Local rebound must not clip the core light alpha.",
		errors
	)
	_expect(
		flick_times.size() >= 2 and flick_times.size() <= 4,
		"A four-minute session should contain only two to four rare flicks.",
		errors
	)
	for index: int in range(1, flick_times.size()):
		_expect(
			flick_times[index] - flick_times[index - 1] >= 60.0,
			"Rare light flicks must never occur more than once per minute.",
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
		print("Cozy randomized light-motion contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
