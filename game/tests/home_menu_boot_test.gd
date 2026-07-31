extends SceneTree

const HOME_MENU_PATH := "res://scenes/home/home_menu.tscn"


func _initialize() -> void:
	var errors := PackedStringArray()
	_expect(
		ProjectSettings.get_setting("application/run/main_scene", "") == HOME_MENU_PATH,
		"The approved home menu must remain the project boot scene.",
		errors
	)

	var packed_scene := load(HOME_MENU_PATH) as PackedScene
	_expect(packed_scene != null, "The promoted home menu scene must load.", errors)
	if packed_scene != null:
		var home_menu := packed_scene.instantiate()
		root.add_child(home_menu)
		_expect(
			home_menu.get_node_or_null(
				"ApprovedStallComposition/StallStructure"
			) != null,
			"The promoted scene must contain the approved empty stall.",
			errors
		)
		_expect(
			home_menu.get_node_or_null(
				"ApprovedStallComposition/HomeVillageRainLab"
			) != null,
			"The promoted scene must retain the living rainy village.",
			errors
		)
		home_menu.free()

	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Home menu boot contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
