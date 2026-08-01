extends SceneTree

const LAB_PATH := "res://scenes/labs/home_menu_stall_lab.tscn"
const LIGHT_POSITIONS: Array[Vector2] = [
	Vector2(134.5, 515.0),
	Vector2(583.5, 515.0),
	Vector2(240.5, 675.0),
]
const LIGHT_ENERGIES: Array[float] = [0.34, 0.34, 0.30]


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(LAB_PATH) as PackedScene
	_expect(packed != null, "Foreground relight lab must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var lab := packed.instantiate()
	root.add_child(lab)
	await process_frame
	await process_frame

	var stage := lab.get_node("StallStage") as AspectContainStage
	var controller := stage.get_node_or_null(
		"ForegroundRelight"
	) as StallForegroundRelight
	var lights_root := stage.get_node_or_null("ForegroundLights") as Node2D
	_expect(controller != null, "Missing reversible foreground relight.", errors)
	_expect(lights_root != null, "Missing foreground practical-light root.", errors)
	if controller == null or lights_root == null:
		lab.queue_free()
		await process_frame
		_finish(errors)
		return

	_expect(controller.is_enabled(), "Relight must be enabled by default.", errors)
	_expect(not controller.is_processing(), "Static gate must not own a process loop.", errors)
	_expect(lights_root.get_child_count() == 3, "Relight must own exactly three pools.", errors)

	var lights: Array[PointLight2D] = []
	for index: int in lights_root.get_child_count():
		var light := lights_root.get_child(index) as PointLight2D
		_expect(light != null, "Every relight child must be PointLight2D.", errors)
		if light == null:
			continue
		lights.append(light)
		_expect(light.enabled, "Approved static pools must be enabled.", errors)
		_expect(light.position == LIGHT_POSITIONS[index], "Light registration changed.", errors)
		_expect(
			is_equal_approx(light.energy, LIGHT_ENERGIES[index]),
			"Static light energy changed without a visual gate.",
			errors
		)
		_expect(light.color.is_equal_approx(
			Color(1.0, 0.74, 0.42, 1.0)
			if index < 2
			else Color(1.0, 0.69, 0.36, 1.0)
		), "Warm-light color changed.", errors)
		_expect(light.blend_mode == Light2D.BLEND_MODE_ADD, "Pools must remain additive.", errors)
		_expect(not light.shadow_enabled, "V014 must not add cast shadows.", errors)
		_expect(
			light.range_z_min == 14 and light.range_z_max == 19,
			"Pools must remain inside the foreground z band.",
			errors
		)
		_expect(
			light.range_layer_min == 0 and light.range_layer_max == 1,
			"Pools must work in both lab and production canvas layers.",
			errors
		)
		_expect(
			light.range_item_cull_mask == 2,
			"Pools must use the isolated foreground receiver mask.",
			errors
		)
		var radial := light.texture as GradientTexture2D
		_expect(radial != null, "Each pool must use a procedural radial texture.", errors)
		if radial != null:
			_expect(
				radial.fill == GradientTexture2D.FILL_RADIAL,
				"Practical-light texture must remain radial.",
				errors
			)
			_expect(
				radial.width == 256 and radial.height == 256,
				"Practical-light texture must remain mobile-bounded.",
				errors
			)

	var stall := stage.get_node("StallStructure") as CanvasItem
	var proprietor := stage.get_node("MainCharacter") as CanvasItem
	var open_button := stage.get_node(
		"StallAttachmentKit/OpenStallButton"
	) as CanvasItem
	var open_label := stage.get_node(
		"StallAttachmentKit/OpenStallButton/VisualRoot/LiveLabel"
	) as CanvasItem
	_expect(stall.modulate.is_equal_approx(
		controller.get_stall_night_modulate()
	), "Stall ambient grade changed.", errors)
	_expect(proprietor.modulate.is_equal_approx(
		controller.get_proprietor_night_modulate()
	), "Proprietor ambient grade changed.", errors)
	_expect(open_button.modulate.is_equal_approx(
		controller.get_button_night_modulate()
	), "Buttons must retain the founder-requested brighter grade.", errors)
	_expect(
		open_button.modulate.get_luminance() > stall.modulate.get_luminance(),
		"Buttons must remain brighter than the lower stall.",
		errors
	)
	_expect(
		open_label.modulate.r > 1.0,
		"Live labels must receive a small readability lift.",
		errors
	)

	var background := lab.get_node(
		"HomeVillageRainLab/BackgroundUnlit"
	) as CanvasItem
	var roof_splashes := stage.get_node("StallRoofSplashes") as CanvasItem
	var left_core := stage.get_node(
		"StallLanternLeft/SwayPivot/Core"
	) as CanvasItem
	_expect(background.light_mask == 1, "Village must remain outside relight mask.", errors)
	_expect(roof_splashes.light_mask == 1, "Roof rain must stay outside cull mask 2.", errors)
	_expect(left_core.light_mask == 1, "Emissive lantern cores must not receive relight.", errors)
	_expect(stall.light_mask == 2, "Stall must receive the practical lights.", errors)

	controller.set_enabled(false)
	_expect(not controller.is_enabled(), "A/B API must disable the relight.", errors)
	_expect(stall.modulate.is_equal_approx(Color.WHITE), "Disable must restore stall grade.", errors)
	_expect(proprietor.modulate.is_equal_approx(Color.WHITE), "Disable must restore character grade.", errors)
	_expect(open_button.modulate.is_equal_approx(Color.WHITE), "Disable must restore button grade.", errors)
	_expect(open_label.modulate.is_equal_approx(Color.WHITE), "Disable must restore label grade.", errors)
	_expect(stall.light_mask == 1, "Disable must restore receiver masks.", errors)
	for light: PointLight2D in lights:
		_expect(not light.enabled, "Disable must turn practical pools off.", errors)

	controller.set_enabled(true)
	_expect(stall.light_mask == 2, "Re-enable must restore receiver masks.", errors)
	_expect(open_button.modulate.is_equal_approx(
		controller.get_button_night_modulate()
	), "Re-enable must restore brighter buttons.", errors)
	for index: int in lights.size():
		_expect(lights[index].enabled, "Re-enable must restore practical pools.", errors)
		_expect(
			is_equal_approx(lights[index].energy, LIGHT_ENERGIES[index]),
			"A/B toggling must never alter static light energy.",
			errors
		)

	var left_fixture := stage.get_node(
		"StallLanternLeft"
	) as StallLanternFixture
	left_fixture.set_deterministic_test_mode(true)
	_expect(left_fixture.try_tap_interaction(), "Left lantern tap must be accepted.", errors)
	_expect(
		lights[0].energy < LIGHT_ENERGIES[0],
		"Tapped lantern must dim its matching foreground light pool.",
		errors
	)
	_expect(
		is_equal_approx(lights[1].energy, LIGHT_ENERGIES[1]),
		"Left lantern tap must not dim the right light pool.",
		errors
	)
	left_fixture.advance_tap_interaction_for_test(1.10)
	_expect(
		is_equal_approx(lights[0].energy, LIGHT_ENERGIES[0]),
		"Foreground light pool must fully recover with the lantern.",
		errors
	)

	lab.queue_free()
	await process_frame
	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Stall foreground relight contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
