extends SceneTree

const FIRST_PLAYABLE_PATH := "res://scenes/vertical_slice/first_playable.tscn"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(FIRST_PLAYABLE_PATH) as PackedScene
	_expect(packed != null, "First playable scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var first_playable := packed.instantiate()
	root.add_child(first_playable)
	await process_frame
	await process_frame

	var home := first_playable.get_node_or_null("Home") as Control
	var service := first_playable.get_node_or_null("Service") as Control
	var summary := first_playable.get_node_or_null("Summary") as Control
	_expect(home != null and home.visible, "Home should be the boot view.", errors)
	_expect(service != null and not service.visible, "Service should start hidden.", errors)
	_expect(summary != null and not summary.visible, "Summary should start hidden.", errors)
	var session: Variant = first_playable.get("session")
	var initial_coins := int(session.lifetime_coins)

	var open_button := first_playable.get_node_or_null(
		"Home/OpenStallButton"
	) as Button
	_expect(open_button != null, "Home needs a live Open Stall button.", errors)
	if open_button == null:
		_finish(errors)
		return
	open_button.emit_signal("pressed")
	await create_timer(0.45).timeout
	_expect(service.visible, "Open Stall should reveal Service.", errors)
	_expect(not home.visible, "Open Stall should hide Home.", errors)

	for button_name: String in ["RiceButton", "LeafButton", "TofuButton"]:
		var ingredient_button := first_playable.get_node_or_null(
			"Service/%s" % button_name
		) as Button
		_expect(ingredient_button != null, "Missing %s." % button_name, errors)
		if ingredient_button != null:
			ingredient_button.emit_signal("pressed")
	await process_frame

	var serve_button := first_playable.get_node_or_null(
		"Service/ServeButton"
	) as Button
	_expect(serve_button != null, "Service needs a live Serve button.", errors)
	if serve_button != null:
		_expect(not serve_button.disabled, "Three selections should enable serving.", errors)
		serve_button.emit_signal("pressed")
		await create_timer(0.70).timeout

	_expect(
		String(session.current_customer().get("id", "")) == "nori",
		"A wrong order should keep the current customer waiting.",
		errors
	)
	_expect(
		session.lifetime_coins == initial_coins,
		"The wrong-order UI path must not award or save coins.",
		errors
	)
	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("First playable UI contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
