extends SceneTree

const FIXTURE_PATH := "res://scenes/home/components/stall_lantern_fixture.tscn"
const FIXTURE_SCRIPT := preload("res://scripts/home/stall_lantern_fixture.gd")
const HARD_MAX_RADIANS := deg_to_rad(1.4)
const CORE_BASE_ALPHA := 0.68
const HALO_BASE_ALPHA := 0.82
const EXPECTED_TEXTURE_SIZES := {
	"Anchor": Vector2i(43, 35),
	"BodyOff": Vector2i(75, 175),
	"Core": Vector2i(57, 72),
	"LocalHalo": Vector2i(208, 224),
}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(FIXTURE_PATH) as PackedScene
	_expect(packed != null, "Stall lantern fixture must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var fixture := packed.instantiate() as Node2D
	_expect(fixture != null, "Fixture root must be StallLanternFixture.", errors)
	if fixture == null:
		_finish(errors)
		return
	root.add_child(fixture)
	await process_frame
	var automatic_phase_start := float(fixture.get_sway_phase_seconds())
	await create_timer(0.08).timeout
	_expect(
		fixture.get_sway_phase_seconds() > automatic_phase_start,
		"Production fixture must advance its own ambient sway.",
		errors
	)
	_expect(
		absf(fixture.get_sway_rotation()) > 0.000001,
		"Production fixture must visibly apply its autonomous sway.",
		errors
	)

	var anchor := fixture.get_node_or_null("Anchor") as Sprite2D
	var sway_pivot := fixture.get_node_or_null("SwayPivot") as Node2D
	var body := fixture.get_node_or_null("SwayPivot/BodyOff") as Sprite2D
	var core := fixture.get_node_or_null("SwayPivot/Core") as Sprite2D
	var halo := fixture.get_node_or_null("SwayPivot/LocalHalo") as Sprite2D
	_expect(fixture.get_script() == FIXTURE_SCRIPT, "Fixture script mismatch.", errors)
	_expect(anchor != null, "Fixture requires a static Anchor sprite.", errors)
	_expect(sway_pivot != null, "Fixture requires a SwayPivot.", errors)
	_expect(body != null, "Fixture requires BodyOff inside SwayPivot.", errors)
	_expect(core != null, "Fixture requires Core inside SwayPivot.", errors)
	_expect(halo != null, "Fixture requires LocalHalo inside SwayPivot.", errors)

	if anchor != null and sway_pivot != null:
		_expect(anchor.get_parent() == fixture, "Anchor must remain outside SwayPivot.", errors)
		_expect(anchor.position == Vector2(0.0, -27.5), "Anchor registration changed.", errors)
	if body != null and sway_pivot != null:
		_expect(body.get_parent() == sway_pivot, "BodyOff must sway from SwayPivot.", errors)
		_expect(body.position == Vector2(0.0, 75.5), "BodyOff registration changed.", errors)
	if core != null and sway_pivot != null:
		_expect(core.get_parent() == sway_pivot, "Core must follow the shell.", errors)
		_expect(core.position == Vector2(0.0, 78.0), "Core registration changed.", errors)
	if halo != null and sway_pivot != null:
		_expect(halo.get_parent() == sway_pivot, "LocalHalo must follow the shell.", errors)
		_expect(halo.position == Vector2(-0.5, 79.0), "Halo registration changed.", errors)

	_validate_texture(anchor, "Anchor", errors)
	_validate_texture(body, "BodyOff", errors)
	_validate_texture(core, "Core", errors)
	_validate_texture(halo, "LocalHalo", errors)
	_validate_additive(core, "Core", errors)
	_validate_additive(halo, "LocalHalo", errors)
	_validate_no_forbidden_nodes(fixture, errors)

	fixture.set_powered(false, true)
	_expect(is_zero_approx(core.modulate.a), "Immediate OFF must hide Core.", errors)
	_expect(is_zero_approx(halo.modulate.a), "Immediate OFF must hide LocalHalo.", errors)
	fixture.set_powered(true, true)
	_expect(is_equal_approx(core.modulate.a, CORE_BASE_ALPHA), "Immediate ON core alpha changed.", errors)
	_expect(is_equal_approx(halo.modulate.a, HALO_BASE_ALPHA), "Immediate ON halo alpha changed.", errors)

	fixture.set_deterministic_test_mode(true)
	for step: int in range(120):
		fixture.apply_wind(sin(float(step) * 0.09), 1.0 / 60.0)
	var first_rotation := float(fixture.get_sway_rotation())
	var first_phase := float(fixture.get_sway_phase_seconds())
	_expect(absf(first_rotation) > 0.00001, "Wind must produce restrained sway.", errors)
	fixture.set_powered(false, true)
	fixture.set_powered(true, true)
	_expect(
		is_equal_approx(fixture.get_sway_rotation(), first_rotation),
		"Power toggle must preserve the current sway rotation.",
		errors
	)
	_expect(
		is_equal_approx(fixture.get_sway_phase_seconds(), first_phase),
		"Power toggle must preserve sway phase.",
		errors
	)

	fixture.set_deterministic_test_mode(true)
	for step: int in range(120):
		fixture.apply_wind(sin(float(step) * 0.09), 1.0 / 60.0)
	_expect(
		is_equal_approx(fixture.get_sway_rotation(), first_rotation),
		"Deterministic mode must replay the same wind result.",
		errors
	)
	_expect(
		is_equal_approx(fixture.get_sway_phase_seconds(), first_phase),
		"Deterministic mode must replay the same phase.",
		errors
	)

	for step: int in range(600):
		fixture.apply_wind(100.0, 1.0 / 60.0)
	_expect(
		absf(fixture.get_sway_rotation()) <= HARD_MAX_RADIANS + 0.000001,
		"Sway may never exceed the 1.4-degree hard maximum.",
		errors
	)

	fixture.set_reduced_motion(true)
	_expect(is_zero_approx(sway_pivot.rotation), "Reduced motion must neutralize sway.", errors)
	fixture.apply_light_motion(0.2, 0.2)
	_expect(
		is_equal_approx(core.modulate.a, CORE_BASE_ALPHA),
		"Reduced motion must suppress core pulse and flick.",
		errors
	)
	_expect(
		is_equal_approx(halo.modulate.a, HALO_BASE_ALPHA),
		"Reduced motion must suppress halo pulse and flick.",
		errors
	)
	fixture.apply_wind(1.0, 1.0)
	_expect(is_zero_approx(sway_pivot.rotation), "Reduced motion must keep sway neutral.", errors)

	fixture.set_reduced_motion(false)
	fixture.apply_light_motion(0.80, 0.45)
	_expect(core.modulate.a < CORE_BASE_ALPHA, "Core must respond to pulse/flick.", errors)
	_expect(halo.modulate.a < HALO_BASE_ALPHA, "Halo must respond at lower coupling.", errors)
	_expect(halo.modulate.a > core.modulate.a, "Halo response must remain attenuated.", errors)

	var phase_before_fade := float(fixture.get_sway_phase_seconds())
	var rotation_before_fade := float(fixture.get_sway_rotation())
	fixture.set_powered(false)
	await create_timer(0.30).timeout
	_expect(is_zero_approx(core.modulate.a), "Animated OFF must finish with Core hidden.", errors)
	_expect(is_zero_approx(halo.modulate.a), "Animated OFF must finish with Halo hidden.", errors)
	_expect(
		is_equal_approx(fixture.get_sway_phase_seconds(), phase_before_fade),
		"Power fades must not mutate sway phase.",
		errors
	)
	_expect(
		is_equal_approx(fixture.get_sway_rotation(), rotation_before_fade),
		"Power fades must not mutate sway rotation.",
		errors
	)

	fixture.queue_free()
	await process_frame
	await create_timer(0.05).timeout
	_finish(errors)


func _validate_texture(
	sprite: Sprite2D,
	node_name: String,
	errors: PackedStringArray
) -> void:
	if sprite == null:
		return
	_expect(sprite.texture != null, "%s texture must load." % node_name, errors)
	if sprite.texture != null:
		_expect(
			sprite.texture.get_size() == Vector2(EXPECTED_TEXTURE_SIZES[node_name]),
			"%s texture dimensions changed." % node_name,
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


func _validate_no_forbidden_nodes(node: Node, errors: PackedStringArray) -> void:
	_expect(not node is PointLight2D, "Fixture must not contain PointLight2D.", errors)
	_expect(not node is PhysicsBody2D, "Fixture must not contain PhysicsBody2D.", errors)
	_expect(not node is Joint2D, "Fixture must not contain Joint2D.", errors)
	for child: Node in node.get_children():
		_validate_no_forbidden_nodes(child, errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Stall lantern fixture contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
