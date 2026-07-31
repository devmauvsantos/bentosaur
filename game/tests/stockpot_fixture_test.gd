extends SceneTree

const FIXTURE_PATH := "res://scenes/home/components/stockpot_fixture.tscn"
const FIXTURE_SCRIPT := preload("res://scripts/home/stockpot_fixture.gd")
const ROOT_PARENT_POSITION := Vector2(179.0, 727.0)
const EXPECTED_BOXES := {
	"ContactShadow": Rect2(132.0, 709.0, 94.0, 18.0),
	"Body": Rect2(136.0, 626.0, 86.0, 92.0),
	"LidPivot/Lid": Rect2(133.0, 609.0, 90.0, 49.0),
}
const TEST_SEED := 13579
const TEST_DURATION_SECONDS := 20.0


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(FIXTURE_PATH) as PackedScene
	_expect(packed != null, "Stockpot fixture must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var fixture := packed.instantiate() as StockpotFixture
	_expect(fixture != null, "Fixture root must be StockpotFixture.", errors)
	if fixture == null:
		_finish(errors)
		return
	fixture.set_deterministic_test_mode(true)
	root.add_child(fixture)
	await process_frame

	_expect(fixture.get_script() == FIXTURE_SCRIPT, "Fixture script mismatch.", errors)
	_expect(
		StockpotFixture.ROOT_PARENT_POSITION == ROOT_PARENT_POSITION,
		"Stockpot parent registration changed.",
		errors
	)
	_expect(
		fixture.get_node("SteamEmitter").position == Vector2(18.0, -117.0),
		"Steam emitter must register at optical source point (197, 610).",
		errors
	)
	_expect(
		fixture.get_node("LidPivot").position == Vector2(-1.0, -82.0),
		"Lid pivot must register at optical contact point (178, 645).",
		errors
	)
	_expect(fixture.get_node("ContactShadow").z_index == 0, "Shadow z-order changed.", errors)
	_expect(fixture.get_node("Body").z_index == 1, "Body z-order changed.", errors)
	_expect(fixture.get_node("SteamEmitter").z_index == 2, "Steam z-order changed.", errors)
	_expect(fixture.get_node("LidPivot").z_index == 3, "Lid z-order changed.", errors)
	_validate_registered_sprites(fixture, errors)
	_validate_procedural_steam(fixture, errors)
	_validate_no_forbidden_nodes(fixture, errors)

	var samples: Array[Dictionary] = []
	for rate: int in [30, 60, 120]:
		samples.append(_sample_motion(packed, rate, errors))
	_compare_samples(samples[0], samples[1], "30/60 fps", errors)
	_compare_samples(samples[1], samples[2], "60/120 fps", errors)

	fixture.reset_motion(TEST_SEED)
	for frame: int in range(600):
		fixture.step_motion(1.0 / 60.0)
		_expect(
			fixture.get_lid_offset_y() >= -1.000001
			and fixture.get_lid_offset_y() <= 0.000001,
			"Lid translation exceeded its one-pixel hard limit.",
			errors
		)
		_expect(
			absf(fixture.get_lid_rotation()) <= deg_to_rad(0.7) + 0.000001,
			"Lid rotation exceeded its 0.7-degree hard limit.",
			errors
		)

	fixture.set_reduced_motion(true)
	fixture.step_motion(4.0)
	_expect(is_zero_approx(fixture.get_lid_offset_y()), "Reduced motion must settle the lid.", errors)
	_expect(is_zero_approx(fixture.get_lid_rotation()), "Reduced motion must remove lid rotation.", errors)
	_expect(
		fixture.get_visible_steam_wisp_count() == 1,
		"Reduced motion must keep one quiet static steam cue.",
		errors
	)
	_expect(
		fixture.get_visible_graphic_curl_count() == 1,
		"Reduced motion must keep one static illustrated curl.",
		errors
	)

	fixture.set_active(false)
	fixture.step_motion(4.0)
	_expect(not fixture.is_active(), "Inactive state must be observable.", errors)
	_expect(is_zero_approx(fixture.get_lid_offset_y()), "Inactive stockpot must settle the lid.", errors)
	_expect(
		fixture.get_visible_steam_wisp_count() == 0,
		"Inactive stockpot must hide procedural steam.",
		errors
	)
	_expect(
		fixture.get_visible_graphic_curl_count() == 0,
		"Inactive stockpot must hide illustrated steam curls.",
		errors
	)
	await _validate_integrated_steam(errors)

	fixture.queue_free()
	await process_frame
	_finish(errors)


func _validate_integrated_steam(errors: PackedStringArray) -> void:
	var packed_home := load("res://scenes/home/home_menu.tscn") as PackedScene
	_expect(packed_home != null, "Integrated home scene must load for steam QA.", errors)
	if packed_home == null:
		return
	var home := packed_home.instantiate()
	root.add_child(home)
	await process_frame
	await process_frame
	var integrated := home.get_node_or_null(
		"WorldCanvas/ApprovedStallComposition/StallStage/StallAttachmentKit/Stockpot"
	) as StockpotFixture
	_expect(integrated != null, "Integrated home must contain StockpotFixture.", errors)
	if integrated != null:
		_expect(integrated.is_active(), "Integrated stockpot must start active.", errors)
		_expect(
			not integrated.is_reduced_motion(),
			"Default integrated capture must not force reduced motion.",
			errors
		)
		_expect(
			integrated.get_visible_steam_wisp_count() >= 1,
			"Integrated stockpot must have a live visible steam wisp.",
			errors
		)
		var visible_in_tree := 0
		var maximum_alpha := 0.0
		var graphic_visible := 0
		var maximum_core_alpha := 0.0
		for index: int in range(3):
			var wisp := integrated.get_node("SteamEmitter/Wisp%d" % index) as Sprite2D
			if wisp.is_visible_in_tree() and wisp.visible:
				visible_in_tree += 1
			maximum_alpha = maxf(maximum_alpha, wisp.modulate.a)
			var core := integrated.get_node(
				"SteamEmitter/GraphicCore%d" % index
			) as Line2D
			if core.is_visible_in_tree() and core.visible:
				graphic_visible += 1
			maximum_core_alpha = maxf(maximum_core_alpha, core.default_color.a)
		_expect(visible_in_tree >= 1, "Integrated wisp must be visible in the scene tree.", errors)
		_expect(maximum_alpha >= 0.10, "Integrated steam alpha is below mobile visibility floor.", errors)
		_expect(graphic_visible >= 1, "Integrated graphic curl must be visible in the scene tree.", errors)
		_expect(maximum_core_alpha >= 0.50, "Graphic steam core lacks transfer-safe opacity.", errors)
		print(
			"Integrated steam runtime: active=%s reduced=%s soft=%d graphic=%d core_alpha=%.3f"
			% [
				integrated.is_active(),
				integrated.is_reduced_motion(),
				visible_in_tree,
				graphic_visible,
				maximum_core_alpha,
			]
		)
	home.free()


func _sample_motion(
	packed: PackedScene,
	rate: int,
	errors: PackedStringArray
) -> Dictionary:
	var fixture := packed.instantiate() as StockpotFixture
	fixture.set_deterministic_test_mode(true)
	root.add_child(fixture)
	fixture.reset_motion(TEST_SEED)
	var event_times := PackedFloat64Array()
	var event_counts := PackedInt32Array()
	var last_serial := fixture.get_event_serial()
	var total_frames := int(TEST_DURATION_SECONDS * float(rate))
	for frame: int in range(total_frames):
		fixture.step_motion(1.0 / float(rate))
		var serial := fixture.get_event_serial()
		if serial != last_serial:
			_expect(serial == last_serial + 1, "A deterministic rattle event was skipped.", errors)
			event_times.append(fixture.get_last_event_started_at())
			event_counts.append(fixture.get_current_event_count())
			last_serial = serial
	var result := {
		"times": event_times,
		"counts": event_counts,
		"offset": fixture.get_lid_offset_y(),
		"rotation": fixture.get_lid_rotation(),
	}
	_expect(event_times.size() >= 3, "Deterministic sample must include several rattles.", errors)
	for count: int in event_counts:
		_expect(count >= 1 and count <= 2, "Rattle count must stay in the approved 1-2 range.", errors)
	fixture.free()
	return result


func _compare_samples(
	left: Dictionary,
	right: Dictionary,
	label: String,
	errors: PackedStringArray
) -> void:
	var left_times: PackedFloat64Array = left["times"]
	var right_times: PackedFloat64Array = right["times"]
	_expect(left_times.size() == right_times.size(), "%s event count diverged." % label, errors)
	for index: int in range(mini(left_times.size(), right_times.size())):
		_expect(
			is_equal_approx(left_times[index], right_times[index]),
			"%s event timing diverged at event %d." % [label, index],
			errors
		)
	_expect(left["counts"] == right["counts"], "%s rattle pattern diverged." % label, errors)
	_expect(
		is_equal_approx(float(left["offset"]), float(right["offset"])),
		"%s final lid offset diverged." % label,
		errors
	)
	_expect(
		is_equal_approx(float(left["rotation"]), float(right["rotation"])),
		"%s final lid rotation diverged." % label,
		errors
	)


func _validate_registered_sprites(
	fixture: StockpotFixture,
	errors: PackedStringArray
) -> void:
	for path: String in EXPECTED_BOXES:
		var sprite := fixture.get_node_or_null(path) as Sprite2D
		_expect(sprite != null, "Missing stockpot sprite %s." % path, errors)
		if sprite == null:
			continue
		_expect(sprite.texture != null, "%s texture must load." % path, errors)
		_expect(
			is_equal_approx(sprite.scale.x, sprite.scale.y),
			"%s must use uniform scaling." % path,
			errors
		)
		var actual := _sprite_rect_in_parent_space(sprite, fixture)
		actual.position += ROOT_PARENT_POSITION
		_expect(
			_rect_is_approx(actual, EXPECTED_BOXES[path]),
			"%s registration changed: %s." % [path, actual],
			errors
		)


func _validate_procedural_steam(
	fixture: StockpotFixture,
	errors: PackedStringArray
) -> void:
	fixture.reset_motion(TEST_SEED)
	fixture.step_motion(0.40)
	_expect(
		fixture.get_visible_steam_wisp_count() >= 1,
		"Active stockpot must expose at least one visible steam wisp.",
		errors
	)
	for index: int in range(3):
		var wisp := fixture.get_node_or_null("SteamEmitter/Wisp%d" % index) as Sprite2D
		_expect(wisp != null, "Missing pooled procedural steam wisp %d." % index, errors)
		if wisp == null:
			continue
		_expect(
			wisp.texture is GradientTexture2D,
			"Steam wisp %d must use the procedural soft-gradient texture." % index,
			errors
		)
		_expect(
			not wisp.texture.resource_path.to_lower().ends_with(".png"),
			"Steam wisp %d must not depend on external raster art." % index,
			errors
		)
		var material := wisp.material as CanvasItemMaterial
		_expect(material != null, "Steam wisp %d requires CanvasItemMaterial." % index, errors)
		if material != null:
			_expect(
				material.blend_mode == CanvasItemMaterial.BLEND_MODE_ADD,
				"Steam wisp %d must use additive blending." % index,
				errors
			)
			_expect(
				material.light_mode == CanvasItemMaterial.LIGHT_MODE_UNSHADED,
					"Steam wisp %d must remain unshaded." % index,
					errors
				)
	_expect(
		fixture.get_visible_graphic_curl_count() >= 1,
		"Active stockpot must expose an illustrated steam curl.",
		errors
	)
	for index: int in range(3):
		var outline := fixture.get_node_or_null(
			"SteamEmitter/GraphicOutline%d" % index
		) as Line2D
		var core := fixture.get_node_or_null(
			"SteamEmitter/GraphicCore%d" % index
		) as Line2D
		_expect(outline != null, "Missing graphic steam outline %d." % index, errors)
		_expect(core != null, "Missing graphic steam core %d." % index, errors)
		if outline == null or core == null:
			continue
		_expect(outline.points.size() == 6, "Steam outline %d requires six curl points." % index, errors)
		_expect(core.points == outline.points, "Steam core %d must follow its outline." % index, errors)
		_expect(outline.width >= 5.0, "Steam outline %d is below mobile ink width." % index, errors)
		_expect(core.width >= 2.0, "Steam core %d is below mobile highlight width." % index, errors)
		_expect(outline.width > core.width, "Steam outline %d must frame its light core." % index, errors)
		var graphic_material := core.material as CanvasItemMaterial
		_expect(graphic_material != null, "Steam curl %d requires CanvasItemMaterial." % index, errors)
		if graphic_material != null:
			_expect(
				graphic_material.blend_mode == CanvasItemMaterial.BLEND_MODE_MIX,
				"Steam curl %d must retain opaque ink contrast." % index,
				errors
			)
			_expect(
				graphic_material.light_mode == CanvasItemMaterial.LIGHT_MODE_UNSHADED,
				"Steam curl %d must remain unshaded." % index,
				errors
			)


func _sprite_rect_in_parent_space(sprite: Sprite2D, parent: Node2D) -> Rect2:
	var source := sprite.get_rect()
	var corners := [
		source.position,
		source.position + Vector2(source.size.x, 0.0),
		source.end,
		source.position + Vector2(0.0, source.size.y),
	]
	var first := parent.to_local(sprite.to_global(corners[0]))
	var result := Rect2(first, Vector2.ZERO)
	for corner: Vector2 in corners.slice(1):
		result = result.expand(parent.to_local(sprite.to_global(corner)))
	return result


func _rect_is_approx(left: Rect2, right: Rect2, epsilon: float = 0.01) -> bool:
	return left.position.distance_to(right.position) <= epsilon \
		and left.size.distance_to(right.size) <= epsilon


func _validate_no_forbidden_nodes(node: Node, errors: PackedStringArray) -> void:
	_expect(not node is PointLight2D, "Fixture must not contain PointLight2D.", errors)
	_expect(not node is PhysicsBody2D, "Fixture must not contain PhysicsBody2D.", errors)
	_expect(not node is Joint2D, "Fixture must not contain Joint2D.", errors)
	_expect(not node is GPUParticles2D, "Fixture must not contain GPU particles.", errors)
	_expect(not node is CPUParticles2D, "Fixture must not contain CPU particles.", errors)
	for child: Node in node.get_children():
		_validate_no_forbidden_nodes(child, errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Stockpot fixture contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
