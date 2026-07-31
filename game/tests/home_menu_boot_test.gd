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
			home_menu is BentosaurHomeMenu,
			"The production home menu must own typed request signals.",
			errors
		)
		_expect(
			home_menu.get_node_or_null(
				"WorldCanvas/ApprovedStallComposition/StallStage/StallStructure"
			) != null,
			"The promoted scene must contain the approved empty stall.",
			errors
		)
		_expect(
			home_menu.get_node_or_null(
				"WorldCanvas/ApprovedStallComposition/StallStage"
			) is AspectContainStage,
			"The stall must preserve its authored distance on ultratall displays.",
			errors
		)
		_expect(
			home_menu.get_node_or_null(
				"WorldCanvas/ApprovedStallComposition/StallStage/StallLanternLeft"
			) is StallLanternFixture,
			"The promoted home menu must contain the approved left stall lantern.",
			errors
		)
		_expect(
			home_menu.get_node_or_null(
				"WorldCanvas/ApprovedStallComposition/StallStage/StallLanternRight"
			) is StallLanternFixture,
			"The promoted home menu must contain the approved right stall lantern.",
			errors
		)
		var attachment_kit := home_menu.get_node_or_null(
			"WorldCanvas/ApprovedStallComposition/StallStage/StallAttachmentKit"
		) as StallAttachmentKit
		_expect(
			attachment_kit != null,
			"The promoted menu must contain the founder-approved V004 kit.",
			errors
		)
		if attachment_kit != null:
			var open_button := attachment_kit.get_node("OpenStallButton") as StallMenuButton
			var guestbook_button := attachment_kit.get_node("GuestbookButton") as StallMenuButton
			var decorations_button := attachment_kit.get_node("DecorationsButton") as StallMenuButton
			var pantry_button := attachment_kit.get_node("PantryButton") as StallMenuButton
			_expect(
				open_button.label_text == "Open Stall"
					and guestbook_button.label_text == "Guestbook"
					and decorations_button.label_text == "Decorations"
					and pantry_button.label_text == "Pantry",
				"The four approved live menu labels must survive promotion.",
				errors
			)
		_expect(
			home_menu.get_node_or_null(
				"WorldCanvas/ApprovedStallComposition/HomeVillageRainLab"
			) != null,
			"The promoted scene must retain the living rainy village.",
			errors
		)
		var world_canvas := home_menu.get_node_or_null(
			"WorldCanvas"
		) as CanvasLayer
		_expect(
			world_canvas != null,
			"The registered world must use one native-resolution cover canvas.",
			errors
		)
		var post_process := home_menu.get_node_or_null(
			"Anime90sPostProcess"
		) as CanvasLayer
		var anime_filter := home_menu.get_node_or_null(
			"Anime90sPostProcess/Filter"
		) as ColorRect
		_expect(
			post_process != null and post_process.layer == 100,
			"The approved anime transfer must render above the complete world.",
			errors
		)
		_expect(anime_filter != null, "Missing approved preset 3 filter.", errors)
		if post_process != null:
			_expect(
				post_process.get_meta("preset_number", -1) == 3,
				"The home menu must identify the approved preset as number 3.",
				errors
			)
		if anime_filter != null:
			var shader_material := anime_filter.material as ShaderMaterial
			_expect(shader_material != null, "Preset 3 must use its shader material.", errors)
			if shader_material != null:
				_expect(
					is_equal_approx(
						float(shader_material.get_shader_parameter("noise_intensity")),
						0.085
					),
					"Preset 3 transfer grain must remain enabled.",
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
