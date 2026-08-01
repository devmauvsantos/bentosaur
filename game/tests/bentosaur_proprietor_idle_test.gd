extends SceneTree

const CHARACTER_PATH := (
	"res://scenes/home/components/bentosaur_proprietor_idle.tscn"
)
const SCRIPT_PATH := "res://scripts/home/bentosaur_proprietor_idle.gd"
const NEUTRAL_TEXTURE_PATH := (
	"res://assets/characters/bentosaur_proprietor/v002/"
	+ "bentosaur_proprietor_counter_neutral_v002.png"
)
const BLINK_TEXTURE_PATH := (
	"res://assets/characters/bentosaur_proprietor/v002/"
	+ "bentosaur_proprietor_counter_blink_v002.png"
)
const HANDS_TEXTURE_PATH := (
	"res://assets/characters/bentosaur_proprietor/v002/"
	+ "bentosaur_proprietor_counter_hands_v002.png"
)
const EXPECTED_TEXTURE_SIZE := Vector2(865.0, 1024.0)
const EXPECTED_VISUAL_SCALE := Vector2(0.2, 0.2)
const EXPECTED_SPRITE_OFFSET := Vector2(0.0, -512.0)
const TEST_SEED := 48043
const MAX_HEAD_SHIFT_DEGREES := 0.51
const MIN_VISIBLE_HEAD_SHIFT_DEGREES := 0.15


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(CHARACTER_PATH) as PackedScene
	_expect(packed != null, "Proprietor idle scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var character := packed.instantiate() as BentosaurProprietorIdle
	root.add_child(character)
	await process_frame

	_expect(character != null, "Idle scene must expose its typed controller.", errors)
	if character == null:
		_finish(errors)
		return
	_expect(
		character.get_script().resource_path == SCRIPT_PATH,
		"Proprietor must use the reusable idle controller.",
		errors
	)
	_expect(
		character.get_base_visual_scale() == EXPECTED_VISUAL_SCALE,
		"Prototype scale must preserve the approved registered framing.",
		errors
	)
	_expect(
		character.body_motion_root != null
			and character.body_motion_root.get_parent() == character.visual_root,
		"Body motion needs its own bottom-center pivot under VisualRoot.",
		errors
	)
	_expect(
		character.neutral_sprite.get_parent() == character.body_motion_root
			and character.blink_sprite.get_parent() == character.body_motion_root,
		"Only the body and expression sprites may inherit the micro-lean.",
		errors
	)
	_expect(
		character.foreground_hands_sprite.get_parent() == character.visual_root,
		"Foreground hands must stay outside the moving body pivot.",
		errors
	)
	_validate_sprite(
		character.neutral_sprite,
		NEUTRAL_TEXTURE_PATH,
		"Neutral",
		errors
	)
	_validate_sprite(
		character.blink_sprite,
		BLINK_TEXTURE_PATH,
		"Blink",
		errors
	)
	_validate_sprite(
		character.foreground_hands_sprite,
		HANDS_TEXTURE_PATH,
		"Foreground hands",
		errors
	)
	_expect(
		character.foreground_hands_sprite.z_index == 2,
		"Foreground hands must render two levels above the body.",
		errors
	)

	var samples: Array[Dictionary] = []
	for rate: int in [30, 60, 120]:
		character.set_reduced_motion(false)
		character.set_active(true)
		character.set_deterministic_test_mode(true, TEST_SEED)
		for frame: int in range(rate * 24):
			character.step_motion(1.0 / float(rate))
		samples.append({
			"scale": character.get_visual_scale(),
			"blink_count": character.get_blink_count(),
			"blinking": character.is_blinking(),
			"head_rotation": character.get_head_rotation_radians(),
			"head_shift_count": character.get_head_shift_count(),
			"head_shifting": character.is_head_shifting(),
			"breath_speed": character.get_breath_speed(),
			"breath_phase": character.get_breath_phase_offset(),
		})

	var reference: Dictionary = samples[0]
	_expect(
		int(reference["blink_count"]) > 0,
		"Twenty-four deterministic seconds must contain at least one blink.",
		errors
	)
	_expect(
		int(reference["head_shift_count"]) > 0,
		"Twenty-four deterministic seconds must contain a micro-lean.",
		errors
	)
	for sample: Dictionary in samples.slice(1):
		_expect(
			(sample["scale"] as Vector2).is_equal_approx(
				reference["scale"] as Vector2
			),
			"Breathing must be frame-rate independent at 30/60/120 FPS.",
			errors
		)
		_expect(
			int(sample["blink_count"]) == int(reference["blink_count"])
				and bool(sample["blinking"]) == bool(reference["blinking"]),
			"Blink scheduling must be frame-rate independent.",
			errors
		)
		_expect(
			is_equal_approx(
				float(sample["head_rotation"]),
				float(reference["head_rotation"])
			)
				and int(sample["head_shift_count"])
					== int(reference["head_shift_count"])
				and bool(sample["head_shifting"])
					== bool(reference["head_shifting"]),
			"Micro-lean scheduling must be frame-rate independent.",
			errors
		)
		_expect(
			is_equal_approx(
				float(sample["breath_speed"]),
				float(reference["breath_speed"])
			),
			"The deterministic seed must reproduce the session cadence.",
			errors
		)
		_expect(
			is_equal_approx(
				float(sample["breath_phase"]),
				float(reference["breath_phase"])
			),
			"The deterministic seed must reproduce the starting breath phase.",
			errors
		)

	character.set_deterministic_test_mode(true, TEST_SEED)
	var minimum_scale := EXPECTED_VISUAL_SCALE
	var maximum_scale := EXPECTED_VISUAL_SCALE
	var hands_baseline := character.foreground_hands_sprite.global_transform
	var maximum_head_rotation_degrees := 0.0
	var observed_head_shift := false
	var observed_rest_after_shift := false
	var hands_stayed_planted := true
	for frame: int in range(30 * 120 + 1):
		character.step_motion(1.0 / 120.0)
		var value := character.get_visual_scale()
		minimum_scale.x = minf(minimum_scale.x, value.x)
		minimum_scale.y = minf(minimum_scale.y, value.y)
		maximum_scale.x = maxf(maximum_scale.x, value.x)
		maximum_scale.y = maxf(maximum_scale.y, value.y)
		maximum_head_rotation_degrees = maxf(
			maximum_head_rotation_degrees,
			absf(rad_to_deg(character.get_head_rotation_radians()))
		)
		if character.get_head_shift_count() > 0:
			observed_head_shift = true
			if not character.is_head_shifting():
				observed_rest_after_shift = true
		if not character.foreground_hands_sprite.global_transform.is_equal_approx(
			hands_baseline
		):
			hands_stayed_planted = false
	_expect(
		minimum_scale.x >= EXPECTED_VISUAL_SCALE.x * 0.99749
			and maximum_scale.x <= EXPECTED_VISUAL_SCALE.x,
		"Breath compensation must stay within the 0.25% horizontal budget.",
		errors
	)
	_expect(
		minimum_scale.y >= EXPECTED_VISUAL_SCALE.y
			and maximum_scale.y <= EXPECTED_VISUAL_SCALE.y * 1.00501,
		"Breathing must stay within the 0.5% vertical budget.",
		errors
	)
	_expect(
		observed_head_shift and observed_rest_after_shift,
		"The idle must alternate rare micro-leans with genuine stillness.",
		errors
	)
	_expect(
		maximum_head_rotation_degrees >= MIN_VISIBLE_HEAD_SHIFT_DEGREES
			and maximum_head_rotation_degrees <= MAX_HEAD_SHIFT_DEGREES,
		"The head-led lean must remain subtle but visible on the phone.",
		errors
	)
	_expect(
		hands_stayed_planted,
		"Foreground hands must remain planted throughout body motion.",
		errors
	)

	character.set_reduced_motion(false)
	character.set_deterministic_test_mode(true, TEST_SEED)
	var blink_search_steps := 0
	while not character.is_blinking() and blink_search_steps < 600:
		character.step_motion(0.01)
		blink_search_steps += 1
	_expect(
		character.is_blinking(),
		"The deterministic schedule must reach a blink within six seconds.",
		errors
	)
	character.set_active(false)
	var blink_count_before_reactivation := character.get_blink_count()
	character.set_active(true)
	character.step_motion(2.29)
	_expect(
		character.get_blink_count() == blink_count_before_reactivation,
		"Reactivation must schedule a fresh blink at least 2.3 seconds later.",
		errors
	)
	character.step_motion(3.12)
	_expect(
		character.get_blink_count() > blink_count_before_reactivation,
		"A reactivated proprietor must resume blinking within 5.4 seconds.",
		errors
	)
	_expect(
		_has_seeded_double_blink(character),
		"The seeded scheduler must retain the documented double blink.",
		errors
	)

	character.set_reduced_motion(true)
	character.set_active(true)
	character.set_deterministic_test_mode(true, TEST_SEED)
	var reduced_blink_search_steps := 0
	while not character.is_blinking() and reduced_blink_search_steps < 600:
		character.step_motion(0.01)
		reduced_blink_search_steps += 1
	_expect(
		character.is_blinking(),
		"Reduced motion must preserve the discrete blink expression.",
		errors
	)
	_expect(
		character.get_visual_scale() == EXPECTED_VISUAL_SCALE,
		"Reduced motion must stop breathing at the registered baseline.",
		errors
	)
	_expect(
		is_zero_approx(character.get_head_rotation_radians())
			and not character.is_head_shifting(),
		"Reduced motion must stop the micro-lean at its baseline.",
		errors
	)
	character.set_active(false)
	_expect(
		character.neutral_sprite.visible and not character.blink_sprite.visible,
		"An inactive proprietor must settle into the neutral state.",
		errors
	)
	_expect(
		character.get_visual_scale() == EXPECTED_VISUAL_SCALE
			and is_zero_approx(character.get_head_rotation_radians()),
		"An inactive proprietor must settle at the registered transform.",
		errors
	)

	character.queue_free()
	await process_frame
	_finish(errors)


func _has_seeded_double_blink(character: BentosaurProprietorIdle) -> bool:
	character.set_reduced_motion(false)
	character.set_active(true)
	for seed: int in range(64):
		character.set_deterministic_test_mode(true, seed)
		var previous_blink_count := 0
		var previous_blink_time := -1.0
		for step: int in range(3000):
			character.step_motion(0.01)
			var blink_count := character.get_blink_count()
			if blink_count == previous_blink_count:
				continue
			var blink_time := character.get_elapsed_seconds()
			if previous_blink_time >= 0.0 and blink_time - previous_blink_time < 0.5:
				return true
			previous_blink_time = blink_time
			previous_blink_count = blink_count
	return false


func _validate_sprite(
	sprite: Sprite2D,
	expected_path: String,
	label: String,
	errors: PackedStringArray
) -> void:
	_expect(sprite != null, "%s sprite is missing." % label, errors)
	if sprite == null:
		return
	_expect(
		sprite.position == EXPECTED_SPRITE_OFFSET,
		"%s sprite lost bottom-center registration." % label,
		errors
	)
	_expect(sprite.texture != null, "%s texture must load." % label, errors)
	if sprite.texture != null:
		_expect(
			sprite.texture.resource_path == expected_path,
			"%s texture path is not canonical." % label,
			errors
		)
		_expect(
			sprite.texture.get_size() == EXPECTED_TEXTURE_SIZE,
			"%s texture must preserve the shared 865x1024 crop." % label,
			errors
		)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Bentosaur proprietor idle contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
