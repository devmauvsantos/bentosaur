extends SceneTree

const LAB_PATH := "res://scenes/labs/home_menu_stall_lab.tscn"
const FONT_PATH := "res://assets/fonts/lilita_one/LilitaOne-Regular.ttf"
const BUTTON_CONTRACT := {
	"OpenStallButton": {
		"position": Vector2(222.0, 770.0),
		"size": Vector2(292.0, 72.0),
		"label": "Open Stall",
	},
	"GuestbookButton": {
		"position": Vector2(223.0, 852.0),
		"size": Vector2(290.0, 64.0),
		"label": "Guestbook",
	},
	"DecorationsButton": {
		"position": Vector2(223.0, 926.0),
		"size": Vector2(290.0, 64.0),
		"label": "Decorations",
	},
	"PantryButton": {
		"position": Vector2(223.0, 1000.0),
		"size": Vector2(290.0, 64.0),
		"label": "Pantry",
	},
}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(LAB_PATH) as PackedScene
	_expect(packed != null, "The integrated stall scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var lab := packed.instantiate()
	root.add_child(lab)
	await process_frame
	await process_frame

	var stage := lab.get_node_or_null("StallStage") as AspectContainStage
	var kit := lab.get_node_or_null(
		"StallStage/StallAttachmentKit"
	) as StallAttachmentKit
	_expect(stage != null, "Missing responsive StallStage.", errors)
	_expect(kit != null, "Missing promoted V004 attachment kit.", errors)
	if kit == null:
		lab.queue_free()
		await process_frame
		_finish(errors)
		return

	_expect(kit.get_parent() == stage, "Every attachment must inherit StallStage.", errors)
	_expect(kit.position == Vector2.ZERO, "Kit registration must remain canvas-local.", errors)
	_expect(kit.scale == Vector2.ONE, "Kit must not compensate the shared stage scale.", errors)
	_expect(kit.z_index == 16, "Kit base z-index must remain below weather.", errors)

	_expect(
		kit.get_node("Stockpot").position == Vector2(179.0, 727.0),
		"Stockpot fixture root registration changed.",
		errors
	)
	_expect(
		kit.get_node("CounterOilLantern").position == Vector2(240.5, 722.0),
		"Counter lantern fixture root registration changed.",
		errors
	)
	_expect(
		kit.get_node("CounterDecor").position == Vector2(360.0, 640.0),
		"Counter decor must remain in the shared canvas coordinate space.",
		errors
	)
	var rank_fixture := kit.get_node("RankFixture") as StallRankFixture
	_expect(rank_fixture.position == Vector2(246.0, 372.0), "Rank plaque moved.", errors)
	_expect(rank_fixture.size == Vector2(228.0, 48.0), "Rank plaque size changed.", errors)
	_expect(rank_fixture.get_rank() == 3, "Approved menu should begin at three stars.", errors)

	for node_name: String in BUTTON_CONTRACT:
		var button := kit.get_node(node_name) as StallMenuButton
		var contract: Dictionary = BUTTON_CONTRACT[node_name]
		_expect(button != null, "Missing %s." % node_name, errors)
		if button == null:
			continue
		_expect(button.position == contract["position"], "%s moved." % node_name, errors)
		_expect(button.size == contract["size"], "%s size changed." % node_name, errors)
		_expect(button.label_text == contract["label"], "%s label changed." % node_name, errors)
		_expect(button.text == contract["label"], "%s accessibility text changed." % node_name, errors)
		_expect(button.label_font != null, "%s needs the licensed live font." % node_name, errors)
		if button.label_font != null:
			_expect(
				button.label_font.resource_path == FONT_PATH,
				"%s must use the vendored Lilita One file." % node_name,
				errors
			)

	var settings := kit.get_node("SettingsButton") as StallSettingsButton
	_expect(settings.position == Vector2(515.0, 1033.0), "Settings control moved.", errors)
	_expect(settings.size == Vector2(75.0, 84.0), "Settings control size changed.", errors)
	_expect(settings.text == "Settings", "Settings needs an accessible label.", errors)

	var request_log: Array[StringName] = []
	kit.open_stall_requested.connect(
		func() -> void: request_log.append(&"open_stall")
	)
	kit.settings_requested.connect(
		func() -> void: request_log.append(&"settings")
	)
	kit.open_stall_button.pressed.emit()
	settings.pressed.emit()
	_expect(
		request_log == [&"open_stall", &"settings"],
		"Buttons must emit navigation-neutral home-menu requests.",
		errors
	)

	kit.set_reduced_motion(true)
	_expect(kit.is_reduced_motion(), "Kit must expose reduced-motion state.", errors)
	_expect(kit.stockpot.is_reduced_motion(), "Reduced motion must reach the stockpot.", errors)
	_expect(kit.counter_decor.is_reduced_motion(), "Reduced motion must reach foliage.", errors)
	_expect(kit.counter_lantern.is_reduced_motion(), "Reduced motion must reach the counter light.", errors)
	_expect(kit.open_stall_button.is_reduced_motion(), "Reduced motion must reach buttons.", errors)
	_expect(settings.is_reduced_motion(), "Reduced motion must reach settings.", errors)
	for lantern_name: String in ["StallLanternLeft", "StallLanternRight"]:
		var lantern := stage.get_node(lantern_name) as StallLanternFixture
		_expect(lantern.is_reduced_motion(), "Reduced motion must stop %s sway." % lantern_name, errors)

	var max_effective_z := _maximum_effective_z(kit, 0)
	_expect(max_effective_z == 19, "Attachments must top out at global z19.", errors)
	var weather := lab.get_node_or_null("HomeVillageRainLab/Weather") as Node2D
	_expect(weather != null and weather.z_index == 20, "Weather must remain above attachments.", errors)

	lab.queue_free()
	await process_frame
	await create_timer(0.05).timeout
	_finish(errors)


func _maximum_effective_z(node: Node, parent_z: int) -> int:
	var effective_z := parent_z
	if node is CanvasItem:
		var item := node as CanvasItem
		effective_z = parent_z + item.z_index if item.z_as_relative else item.z_index
	var maximum := effective_z
	for child: Node in node.get_children():
		maximum = maxi(maximum, _maximum_effective_z(child, effective_z))
	return maximum


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Stall attachment kit integration contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
