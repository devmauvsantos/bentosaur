extends SceneTree

const ASPECT_FILL := preload("res://scripts/layout/aspect_fill_canvas.gd")
const DESIGN_SIZE := Vector2(720.0, 1280.0)
const IPHONE_NATIVE_SIZE := Vector2(1320.0, 2868.0)
const STALL_ALPHA_BOUNDS := Rect2(77.0, 197.0, 566.0, 874.0)


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
	var centered_position: Vector2 = ASPECT_FILL.calculate_centered_position(
		iphone_logical_size,
		DESIGN_SIZE,
		fill_scale
	)
	var covered_size := DESIGN_SIZE * fill_scale
	var visible_source_left := -centered_position.x / fill_scale
	var visible_source_right := (
		iphone_logical_size.x - centered_position.x
	) / fill_scale

	_expect(
		is_equal_approx(fill_scale, 1.2221590909),
		"The expanded iPhone canvas must use one uniform cover scale.",
		errors
	)
	_expect(
		absf(centered_position.x + 79.9772727) < 0.01
			and absf(centered_position.y) < 0.01,
		"The registered canvas must crop equally from both horizontal sides.",
		errors
	)
	_expect(
		covered_size.x >= iphone_logical_size.x
			and covered_size.y >= iphone_logical_size.y,
		"Aspect fill must cover every physical pixel without a black band.",
		errors
	)
	_expect(
		visible_source_left <= STALL_ALPHA_BOUNDS.position.x
			and visible_source_right >= STALL_ALPHA_BOUNDS.end.x,
		"The approved stall must remain fully visible after the centered crop.",
		errors
	)
	_expect(
		ASPECT_FILL.calculate_fill_scale(DESIGN_SIZE, DESIGN_SIZE) == 1.0,
		"The original 9:16 design canvas must remain pixel-aligned.",
		errors
	)

	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Aspect-fill canvas contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
