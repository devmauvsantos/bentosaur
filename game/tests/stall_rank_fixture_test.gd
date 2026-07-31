extends SceneTree

const COMPONENT_PATH := "res://scenes/home/components/stall_rank_fixture.tscn"
const DESIGN_SIZE := Vector2(228.0, 48.0)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(COMPONENT_PATH) as PackedScene
	_expect(packed != null, "Stall rank fixture scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var fixture := packed.instantiate() as StallRankFixture
	_expect(fixture != null, "Scene root must be StallRankFixture.", errors)
	if fixture == null:
		_finish(errors)
		return
	root.add_child(fixture)
	await process_frame

	var content := fixture.get_node_or_null("ContentRoot") as Control
	var plaque := fixture.get_node_or_null("ContentRoot/Plaque") as TextureRect
	_expect(fixture.size == DESIGN_SIZE, "Rank fixture logical size changed.", errors)
	_expect(fixture.mouse_filter == Control.MOUSE_FILTER_IGNORE, "Rank fixture must not consume input.", errors)
	_expect(plaque != null and plaque.texture != null, "Rank plaque texture must load.", errors)
	if plaque != null and plaque.texture != null:
		_expect(plaque.texture.get_size() == Vector2(456.0, 96.0), "Promoted rank plaque must remain 456x96.", errors)
		_expect(plaque.size == Vector2(456.0, 96.0), "Plaque must use its complete promoted plate.", errors)
		_expect(plaque.scale == Vector2(0.5, 0.5), "Plaque must render uniformly at half scale.", errors)

	_expect(fixture.get_rank() == 3, "Default rank must show all three stars.", errors)
	_validate_star_slots(fixture, errors)
	for index: int in range(3):
		_expect(_filled(fixture, index).visible, "Default filled star %d is hidden." % index, errors)

	fixture.set_rank(0, false)
	_expect(fixture.get_rank() == 0, "Rank did not update to zero.", errors)
	for index: int in range(3):
		_expect(not _filled(fixture, index).visible, "Rank zero must hide filled star %d." % index, errors)
		_expect(_empty(fixture, index).visible, "Empty star geometry must always remain present.", errors)

	fixture.set_rank(2, true)
	_expect(
		is_equal_approx(StallRankFixture.FILL_SECONDS, 0.180),
		"Rank fill duration must remain 180 ms.",
		errors
	)
	for index: int in range(2):
		_expect(
			is_zero_approx(_filled(fixture, index).modulate.a),
			"Animated fill must begin from the empty endpoint.",
			errors
		)
	await create_timer(0.210).timeout
	for index: int in range(2):
		_expect(_filled(fixture, index).visible, "Filled star %d must finish visible." % index, errors)
		_expect(is_equal_approx(_filled(fixture, index).modulate.a, 1.0), "Filled star %d must finish opaque." % index, errors)
		_expect(_filled(fixture, index).scale.is_equal_approx(Vector2.ONE), "Filled star %d must finish at rest scale." % index, errors)
		_expect(not _shine(fixture, index).visible, "Shine must finish inside the 180 ms transition.", errors)
	_expect(not _filled(fixture, 2).visible, "Third star must remain empty at rank two.", errors)

	fixture.shine_enabled = false
	fixture.set_rank(3, true)
	await create_timer(0.20).timeout
	_expect(_filled(fixture, 2).visible, "Third star must fill without shine.", errors)
	_expect(not _shine(fixture, 2).visible, "Disabled shine may never appear.", errors)

	fixture.set_rank(0, false)
	fixture.set_reduced_motion(true)
	fixture.set_rank(3, true)
	for index: int in range(3):
		_expect(_filled(fixture, index).visible, "Reduced motion must preserve filled endpoint.", errors)
		_expect(_filled(fixture, index).modulate.a == 1.0, "Reduced motion fill must be immediate.", errors)
		_expect(_filled(fixture, index).scale == Vector2.ONE, "Reduced motion may not leave transient scale.", errors)
		_expect(not _shine(fixture, index).visible, "Reduced motion must suppress shine motion.", errors)

	fixture.size = Vector2(456.0, 96.0)
	await process_frame
	_expect(content.scale == Vector2(2.0, 2.0), "Rank contents must scale uniformly with the root.", errors)
	_expect(content.position.is_zero_approx(), "Equal-aspect rank resize must stay centered.", errors)

	fixture.queue_free()
	await process_frame
	_finish(errors)


func _validate_star_slots(fixture: StallRankFixture, errors: PackedStringArray) -> void:
	var expected := [Vector2(33.0, 9.0), Vector2(93.0, 9.0), Vector2(153.0, 9.0)]
	for index: int in range(3):
		var slot := fixture.get_node("ContentRoot/Star%d" % (index + 1)) as Control
		_expect(slot.position == expected[index], "Star %d registration changed." % index, errors)
		_expect(slot.size == Vector2(42.0, 34.0), "Star %d logical size changed." % index, errors)
		_expect(_empty(fixture, index).texture.get_size() == Vector2(84.0, 68.0), "Empty star runtime density changed.", errors)
		_expect(_filled(fixture, index).texture.get_size() == Vector2(84.0, 68.0), "Filled star runtime density changed.", errors)


func _empty(fixture: StallRankFixture, index: int) -> TextureRect:
	return fixture.get_node("ContentRoot/Star%d/Empty" % (index + 1)) as TextureRect


func _filled(fixture: StallRankFixture, index: int) -> TextureRect:
	return fixture.get_node("ContentRoot/Star%d/Filled" % (index + 1)) as TextureRect


func _shine(fixture: StallRankFixture, index: int) -> TextureRect:
	return fixture.get_node("ContentRoot/Star%d/Shine" % (index + 1)) as TextureRect


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Stall rank fixture contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
