extends SceneTree


func _initialize() -> void:
	var errors := PackedStringArray()
	_expect_setting(
		"display/window/size/viewport_width",
		720,
		"Portrait design width must remain 720 logical units.",
		errors
	)
	_expect_setting(
		"display/window/size/viewport_height",
		1280,
		"Portrait design height must remain 1280 logical units.",
		errors
	)
	_expect_setting(
		"display/window/stretch/mode",
		"canvas_items",
		"2D must render directly at the target display resolution.",
		errors
	)
	_expect_setting(
		"display/window/stretch/aspect",
		"expand",
		"Tall phones must reveal an expanded canvas without distortion.",
		errors
	)
	_expect_setting(
		"display/window/stretch/scale_mode",
		"fractional",
		"Flat-cel art must fill arbitrary mobile resolutions.",
		errors
	)
	_expect_setting(
		"display/window/handheld/orientation",
		1,
		"The game must remain portrait.",
		errors
	)
	_expect_setting(
		"display/window/ios/allow_high_refresh_rate",
		true,
		"iOS must be allowed to use ProMotion refresh rates.",
		errors
	)
	_expect_setting(
		"display/window/vsync/vsync_mode",
		1,
		"VSync must remain enabled.",
		errors
	)
	_expect_setting(
		"application/run/max_fps",
		0,
		"The engine must not impose a fixed frame-rate ceiling.",
		errors
	)
	_expect_setting(
		"rendering/renderer/rendering_method",
		"mobile",
		"The primary renderer must remain Mobile.",
		errors
	)
	_expect_setting(
		"rendering/renderer/rendering_method.mobile",
		"mobile",
		"Mobile overrides must remain on the Mobile renderer.",
		errors
	)
	_expect_setting(
		"rendering/rendering_device/driver.ios",
		"metal",
		"iOS must use the Metal rendering driver.",
		errors
	)
	_finish(errors)


func _expect_setting(
	path: String,
	expected: Variant,
	message: String,
	errors: PackedStringArray
) -> void:
	var actual: Variant = ProjectSettings.get_setting(path)
	if actual != expected:
		errors.append("%s Expected %s, got %s." % [message, expected, actual])


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Mobile display quality contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
