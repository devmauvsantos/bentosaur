extends SceneTree

const FIXTURE_PATH := "res://scenes/home/components/counter_decor_fixture.tscn"
const FIXTURE_SCRIPT := preload("res://scripts/home/counter_decor_fixture.gd")
const ROOT_PARENT_POSITION := Vector2(360.0, 640.0)
const EXPECTED_BOXES := {
	"FoodBowl": Rect2(157.0, 652.0, 66.0, 66.0),
	"Plant/FoliagePivot/Foliage": Rect2(486.0, 500.0, 61.0, 154.0),
	"Plant/Pot": Rect2(481.0, 644.0, 67.0, 75.0),
	"CounterCloth": Rect2(517.0, 684.0, 97.0, 120.0),
}
const CRATE_GROUP_BOX := Rect2(470.0, 618.0, 117.0, 101.0)
const EXPECTED_TEXTURE_SUFFIXES := {
	"FoodBowl": "food_bowl/grape-food-bowl-v001.png",
	"Plant/FoliagePivot/Foliage": "counter_plant/counter_plant_foliage_v001.png",
	"Plant/Pot": "counter_plant/counter_plant_pot_v001.png",
	"BottleCrate/BottleBrown": "bottle_crate/bottle_brown_v001.png",
	"BottleCrate/BottleGreen": "bottle_crate/bottle_green_v001.png",
	"BottleCrate/BottleCreamBlue": "bottle_crate/bottle_cream_blue_cap_v001.png",
	"BottleCrate/EmptyCrate": "bottle_crate/bottle_crate_empty_v001.png",
	"BottleCrate/FrontWallOverlay": "bottle_crate/bottle_crate_empty_v001.png",
	"CounterCloth": "counter_cloth/counter_cloth_red_draped_v001.png",
}
const TEST_SEED := 24680


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(FIXTURE_PATH) as PackedScene
	_expect(packed != null, "Counter decor fixture must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var fixture := packed.instantiate() as CounterDecorFixture
	_expect(fixture != null, "Fixture root must be CounterDecorFixture.", errors)
	if fixture == null:
		_finish(errors)
		return
	fixture.set_deterministic_test_mode(true)
	root.add_child(fixture)
	await process_frame

	_expect(fixture.get_script() == FIXTURE_SCRIPT, "Fixture script mismatch.", errors)
	_expect(
		CounterDecorFixture.ROOT_PARENT_POSITION == ROOT_PARENT_POSITION,
		"Counter decor parent registration changed.",
		errors
	)
	_expect(
		fixture.get_node("BottleCrate").position == Vector2(168.5, 28.5),
		"Bottle-crate root must stay at its approved envelope center.",
		errors
	)
	_expect(
		fixture.get_node("Plant/FoliagePivot").position == Vector2(2.0, -65.0),
		"Foliage pivot must remain at the stem base.",
		errors
	)
	_validate_registered_sprites(fixture, errors)
	_validate_crate_envelope(fixture, errors)
	_validate_crate_seating(fixture, errors)
	_validate_modular_texture_sources(fixture, errors)
	_validate_no_forbidden_nodes(fixture, errors)

	var samples: Array[Dictionary] = []
	for rate: int in [30, 60, 120]:
		samples.append(_sample_plant_motion(packed, rate))
	_compare_samples(samples[0], samples[1], "30/60 fps", errors)
	_compare_samples(samples[1], samples[2], "60/120 fps", errors)

	fixture.reset_motion(TEST_SEED)
	_expect(
		fixture.get_foliage_period() >= 4.5 and fixture.get_foliage_period() <= 8.0,
		"Foliage period must remain in the approved 4.5-8.0 second range.",
		errors
	)
	for frame: int in range(1200):
		fixture.step_motion(1.0 / 60.0)
		_expect(
			absf(fixture.get_foliage_rotation()) <= deg_to_rad(0.35) + 0.000001,
			"Foliage rotation exceeded its 0.35-degree hard limit.",
			errors
		)

	fixture.set_reduced_motion(true)
	fixture.step_motion(8.0)
	_expect(fixture.is_reduced_motion(), "Reduced-motion state must be observable.", errors)
	_expect(is_zero_approx(fixture.get_foliage_rotation()), "Reduced motion must neutralize foliage.", errors)
	fixture.set_reduced_motion(false)
	fixture.set_active(false)
	fixture.step_motion(8.0)
	_expect(not fixture.is_active(), "Inactive state must be observable.", errors)
	_expect(is_zero_approx(fixture.get_foliage_rotation()), "Inactive decor must neutralize foliage.", errors)

	fixture.queue_free()
	await process_frame
	_finish(errors)


func _sample_plant_motion(packed: PackedScene, rate: int) -> Dictionary:
	var fixture := packed.instantiate() as CounterDecorFixture
	fixture.set_deterministic_test_mode(true)
	root.add_child(fixture)
	fixture.reset_motion(TEST_SEED)
	for frame: int in range(rate * 16):
		fixture.step_motion(1.0 / float(rate))
	var result := {
		"rotation": fixture.get_foliage_rotation(),
		"period": fixture.get_foliage_period(),
	}
	fixture.free()
	return result


func _compare_samples(
	left: Dictionary,
	right: Dictionary,
	label: String,
	errors: PackedStringArray
) -> void:
	_expect(
		is_equal_approx(float(left["period"]), float(right["period"])),
		"%s deterministic period diverged." % label,
		errors
	)
	_expect(
		is_equal_approx(float(left["rotation"]), float(right["rotation"])),
		"%s deterministic foliage endpoint diverged." % label,
		errors
	)


func _validate_registered_sprites(
	fixture: CounterDecorFixture,
	errors: PackedStringArray
) -> void:
	for path: String in EXPECTED_BOXES:
		var sprite := fixture.get_node_or_null(path) as Sprite2D
		_expect(sprite != null, "Missing counter decor sprite %s." % path, errors)
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


func _validate_crate_envelope(
	fixture: CounterDecorFixture,
	errors: PackedStringArray
) -> void:
	var paths := [
		"BottleCrate/BottleBrown",
		"BottleCrate/BottleGreen",
		"BottleCrate/BottleCreamBlue",
		"BottleCrate/EmptyCrate",
		"BottleCrate/FrontWallOverlay",
	]
	var union_rect := Rect2()
	var has_rect := false
	for path: String in paths:
		var sprite := fixture.get_node_or_null(path) as Sprite2D
		_expect(sprite != null, "Missing modular crate sprite %s." % path, errors)
		if sprite == null:
			continue
		_expect(
			is_equal_approx(sprite.scale.x, sprite.scale.y),
			"%s must use uniform scaling." % path,
			errors
		)
		var actual := _sprite_rect_in_parent_space(sprite, fixture)
		actual.position += ROOT_PARENT_POSITION
		union_rect = actual if not has_rect else union_rect.merge(actual)
		has_rect = true
	if has_rect:
		_expect(
			_rect_encloses_with_epsilon(CRATE_GROUP_BOX, union_rect, 0.01),
			"Modular bottle crate escaped its 117x101 registration: %s." % union_rect,
			errors
		)
		_expect(
			absf(union_rect.position.y - CRATE_GROUP_BOX.position.y) <= 0.01,
			"Bottle caps must register to the approved crate envelope top.",
			errors
		)


func _validate_crate_seating(
	fixture: CounterDecorFixture,
	errors: PackedStringArray
) -> void:
	var empty_crate := fixture.get_node_or_null("BottleCrate/EmptyCrate") as Sprite2D
	var front_wall := fixture.get_node_or_null(
		"BottleCrate/FrontWallOverlay"
	) as Sprite2D
	_expect(front_wall != null, "Modular crate requires a front-wall overlay.", errors)
	if empty_crate == null or front_wall == null:
		return
	_expect(
		front_wall.texture == empty_crate.texture,
		"Front wall must reuse the independent empty-crate texture.",
		errors
	)
	_expect(front_wall.region_enabled, "Front wall must be a cropped Sprite2D region.", errors)
	_expect(
		front_wall.region_rect == CounterDecorFixture.CRATE_FRONT_REGION_PIXELS,
		"Front-wall crop changed.",
		errors
	)
	_expect(empty_crate.z_index < 1, "Full crate must render behind bottles.", errors)
	_expect(front_wall.z_index > 1, "Front wall must render above bottle bottoms.", errors)
	var front_rect := _sprite_rect_in_parent_space(front_wall, fixture)
	front_rect.position += ROOT_PARENT_POSITION
	for path: String in [
		"BottleCrate/BottleBrown",
		"BottleCrate/BottleGreen",
		"BottleCrate/BottleCreamBlue",
	]:
		var bottle := fixture.get_node_or_null(path) as Sprite2D
		if bottle == null:
			continue
		_expect(bottle.z_index == 1, "%s must sit between crate layers." % path, errors)
		var bottle_rect := _sprite_rect_in_parent_space(bottle, fixture)
		bottle_rect.position += ROOT_PARENT_POSITION
		var visible_height := front_rect.position.y - bottle_rect.position.y
		_expect(
			visible_height >= bottle_rect.size.y * 0.70,
			"%s needs meaningful visible body area above the front lip." % path,
			errors
		)
		_expect(
			bottle_rect.end.y > front_rect.position.y,
			"%s must overlap the front lip so it reads as seated." % path,
			errors
		)


func _validate_modular_texture_sources(
	fixture: CounterDecorFixture,
	errors: PackedStringArray
) -> void:
	for path: String in EXPECTED_TEXTURE_SUFFIXES:
		var sprite := fixture.get_node_or_null(path) as Sprite2D
		if sprite == null or sprite.texture == null:
			continue
		var texture_path := sprite.texture.resource_path
		_expect(
			texture_path.ends_with(EXPECTED_TEXTURE_SUFFIXES[path]),
			"%s must use its canonical independent component." % path,
			errors
		)
		_expect(
			not texture_path.to_lower().contains("assembled"),
			"Runtime decor must never use an assembled preview.",
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


func _rect_encloses_with_epsilon(
	outer: Rect2,
	inner: Rect2,
	epsilon: float
) -> bool:
	return inner.position.x >= outer.position.x - epsilon \
		and inner.position.y >= outer.position.y - epsilon \
		and inner.end.x <= outer.end.x + epsilon \
		and inner.end.y <= outer.end.y + epsilon


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
		print("Counter decor fixture contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
