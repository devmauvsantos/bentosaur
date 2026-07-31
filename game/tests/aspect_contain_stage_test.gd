extends SceneTree

const ASPECT_CONTAIN := preload("res://scripts/layout/aspect_contain_stage.gd")
const ASPECT_FILL := preload("res://scripts/layout/aspect_fill_canvas.gd")
const DESIGN_SIZE := Vector2(720.0, 1280.0)
const IPHONE_NATIVE_SIZE := Vector2(1320.0, 2868.0)
const STALL_VISIBLE_BOUNDS := Rect2(77.0, 197.0, 566.0, 874.0)
const STALL_FRAMING_SCALE := 0.86
const STALL_FRAMING_PIVOT := Vector2(360.0, 634.0)


func _initialize() -> void:
	var errors := PackedStringArray()
	var iphone_logical_size := Vector2(
		DESIGN_SIZE.x,
		IPHONE_NATIVE_SIZE.y / (IPHONE_NATIVE_SIZE.x / DESIGN_SIZE.x)
	)
	var fill_scale: float = ASPECT_FILL.calculate_fill_scale(
		iphone_logical_size,
		DESIGN_SIZE
	)
	var fill_position: Vector2 = ASPECT_FILL.calculate_centered_position(
		iphone_logical_size,
		DESIGN_SIZE,
		fill_scale
	)
	var local_scale: float = ASPECT_CONTAIN.calculate_local_scale(
		iphone_logical_size,
		DESIGN_SIZE,
		STALL_FRAMING_SCALE
	)
	var local_position: Vector2 = ASPECT_CONTAIN.calculate_local_position(
		iphone_logical_size,
		DESIGN_SIZE,
		Vector2(0.5, 0.5),
		STALL_FRAMING_PIVOT,
		STALL_FRAMING_SCALE
	)
	var resulting_screen_scale := fill_scale * local_scale
	var resulting_screen_position := (
		fill_position + local_position * fill_scale
	)
	var screen_bounds := Rect2(
		resulting_screen_position + STALL_VISIBLE_BOUNDS.position * resulting_screen_scale,
		STALL_VISIBLE_BOUNDS.size * resulting_screen_scale
	)

	_expect(
		absf(resulting_screen_scale - STALL_FRAMING_SCALE) < 0.0001,
		"The Pro Max stall stage must counter cover and retain its founder-approved framing scale.",
		errors
	)
	_expect(
		absf(screen_bounds.get_center().x - iphone_logical_size.x * 0.5) < 0.001,
		"The receded stall must remain horizontally centered.",
		errors
	)
	_expect(
		absf(
			screen_bounds.get_center().y - iphone_logical_size.y * 0.5
		) < 6.01,
		"The stall must remain visually centered on ultratall phones.",
		errors
	)
	_expect(
		absf(screen_bounds.size.x / iphone_logical_size.x - 0.67594) < 0.001,
		"The stall must occupy about 67.6% of the screen width like the approved concept.",
		errors
	)
	_expect(
		absf(screen_bounds.position.x - 116.62) < 0.01
			and absf(screen_bounds.size.x - 486.76) < 0.01,
		"The approved stall must have generous, symmetrical side margins.",
		errors
	)
	_expect(
		absf(
			ASPECT_CONTAIN.calculate_local_scale(
				DESIGN_SIZE,
				DESIGN_SIZE,
				STALL_FRAMING_SCALE
			) - STALL_FRAMING_SCALE
		) < 0.0001,
		"The same founder framing must also apply on the original 9:16 canvas.",
		errors
	)

	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Aspect-contain stall stage contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
