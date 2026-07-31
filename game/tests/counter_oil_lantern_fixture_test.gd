extends SceneTree

const FIXTURE_PATH := "res://scenes/home/components/counter_oil_lantern_fixture.tscn"
const FIXTURE_SCRIPT := preload("res://scripts/home/counter_oil_lantern_fixture.gd")
const ROOT_PARENT_POSITION := Vector2(240.5, 722.0)
const CORE_BASE_ALPHA := 0.62
const HALO_BASE_ALPHA := 0.48
const EXPECTED_BOXES := {
	"ContactShadow": Rect2(205.0, 704.0, 72.0, 18.0),
	"LocalHalo": Rect2(186.0, 581.0, 110.0, 146.0),
	"BodyOff": Rect2(209.0, 604.0, 63.0, 115.0),
	"Core": Rect2(225.0, 646.0, 31.0, 58.0),
}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(FIXTURE_PATH) as PackedScene
	_expect(packed != null, "Counter oil lantern fixture must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var fixture := packed.instantiate() as CounterOilLanternFixture
	_expect(fixture != null, "Fixture root must be CounterOilLanternFixture.", errors)
	if fixture == null:
		_finish(errors)
		return
	root.add_child(fixture)
	await process_frame

	var shadow := fixture.get_node_or_null("ContactShadow") as Sprite2D
	var halo := fixture.get_node_or_null("LocalHalo") as Sprite2D
	var body := fixture.get_node_or_null("BodyOff") as Sprite2D
	var core := fixture.get_node_or_null("Core") as Sprite2D
	_expect(fixture.get_script() == FIXTURE_SCRIPT, "Fixture script mismatch.", errors)
	_expect(
		CounterOilLanternFixture.ROOT_PARENT_POSITION == ROOT_PARENT_POSITION,
		"Counter lantern parent registration changed.",
		errors
	)
	_validate_registered_sprites(fixture, errors)
	_validate_additive(core, "Core", errors)
	_validate_additive(halo, "LocalHalo", errors)
	_validate_no_forbidden_nodes(fixture, errors)
	_expect(fixture.get_node_or_null("SwayPivot") == null, "Counter lantern must not sway.", errors)

	var body_texture := body.texture if body != null else null
	var body_transform := body.transform if body != null else Transform2D.IDENTITY
	fixture.set_powered(false, true)
	_expect(not fixture.is_powered(), "Immediate OFF state must be observable.", errors)
	_expect(is_zero_approx(core.modulate.a), "Immediate OFF must hide Core.", errors)
	_expect(is_zero_approx(halo.modulate.a), "Immediate OFF must hide LocalHalo.", errors)
	_expect(body.texture == body_texture, "Power state must not replace the OFF shell.", errors)
	_expect(body.transform == body_transform, "Power state must not move the shell.", errors)

	fixture.set_powered(true, true)
	_expect(fixture.is_powered(), "Immediate ON state must be observable.", errors)
	_expect(is_equal_approx(core.modulate.a, CORE_BASE_ALPHA), "Immediate ON core alpha changed.", errors)
	_expect(is_equal_approx(halo.modulate.a, HALO_BASE_ALPHA), "Immediate ON halo alpha changed.", errors)

	fixture.apply_light_motion(0.80, 0.45)
	_expect(core.modulate.r < 0.40, "Core must respond to ambient pulse/flick.", errors)
	_expect(halo.modulate.r < 1.0, "Halo must respond to ambient pulse/flick.", errors)
	_expect(halo.modulate.r > core.modulate.r, "Halo flick must stay softer than core flick.", errors)
	_expect(is_equal_approx(core.modulate.a, CORE_BASE_ALPHA), "Motion must not mutate core power alpha.", errors)
	_expect(is_equal_approx(halo.modulate.a, HALO_BASE_ALPHA), "Motion must not mutate halo power alpha.", errors)
	_expect(is_zero_approx(fixture.rotation), "Light motion must never rotate the counter lantern.", errors)

	fixture.set_reduced_motion(true)
	fixture.apply_light_motion(0.10, 0.10)
	_expect(fixture.is_reduced_motion(), "Reduced-motion state must be observable.", errors)
	_expect(is_equal_approx(core.modulate.r, 1.0), "Reduced motion must neutralize core flick.", errors)
	_expect(is_equal_approx(halo.modulate.r, 1.0), "Reduced motion must neutralize halo flick.", errors)
	_expect(is_equal_approx(core.modulate.a, CORE_BASE_ALPHA), "Reduced motion must preserve core power.", errors)
	_expect(is_equal_approx(halo.modulate.a, HALO_BASE_ALPHA), "Reduced motion must preserve halo power.", errors)

	fixture.set_reduced_motion(false)
	fixture.apply_light_motion(1.0, 1.0)
	fixture.set_powered(false)
	await create_timer(0.22).timeout
	_expect(is_zero_approx(core.modulate.a), "Animated OFF must finish with Core hidden.", errors)
	_expect(is_zero_approx(halo.modulate.a), "Animated OFF must finish with LocalHalo hidden.", errors)
	fixture.set_powered(true)
	await create_timer(0.32).timeout
	_expect(is_equal_approx(core.modulate.a, CORE_BASE_ALPHA), "Animated ON core endpoint changed.", errors)
	_expect(is_equal_approx(halo.modulate.a, HALO_BASE_ALPHA), "Animated ON halo endpoint changed.", errors)
	_expect(body.texture == body_texture, "Animated power state must preserve shell texture.", errors)
	_expect(body.transform == body_transform, "Animated power state must preserve shell transform.", errors)

	fixture.queue_free()
	await process_frame
	_finish(errors)


func _validate_registered_sprites(
	fixture: CounterOilLanternFixture,
	errors: PackedStringArray
) -> void:
	for path: String in EXPECTED_BOXES:
		var sprite := fixture.get_node_or_null(path) as Sprite2D
		_expect(sprite != null, "Missing counter lantern sprite %s." % path, errors)
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


func _validate_additive(
	sprite: Sprite2D,
	node_name: String,
	errors: PackedStringArray
) -> void:
	if sprite == null:
		return
	var material := sprite.material as CanvasItemMaterial
	_expect(material != null, "%s requires CanvasItemMaterial." % node_name, errors)
	if material != null:
		_expect(
			material.blend_mode == CanvasItemMaterial.BLEND_MODE_ADD,
			"%s must use additive blending." % node_name,
			errors
		)
		_expect(
			material.light_mode == CanvasItemMaterial.LIGHT_MODE_UNSHADED,
			"%s must remain unshaded." % node_name,
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
		print("Counter oil lantern fixture contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
