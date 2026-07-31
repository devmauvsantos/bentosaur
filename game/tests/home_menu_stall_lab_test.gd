extends SceneTree

const LAB_PATH := "res://scenes/labs/home_menu_stall_lab.tscn"
const STALL_DEPTH_SHADER := preload(
	"res://assets/vfx/lighting/stall_depth_falloff.gdshader"
)
const STALL_DEPTH_MATERIAL_PATH := (
	"res://assets/vfx/lighting/stall_depth_falloff_material.tres"
)
const STALL_ROOF_RAIN_SCRIPT := preload(
	"res://scripts/vfx/stall_roof_rain.gd"
)
const COUNTER_OCCLUDER_PATH := (
	"res://assets/environments/home_village/v001/stall/"
	+ "stall_counter_occluder_720x1280.png"
)
const CANVAS_SIZE := Vector2(720.0, 1280.0)
const APPROVED_VISIBLE_BOUNDS := Rect2i(77, 197, 566, 874)
const SOURCE_VISIBLE_ASPECT := 862.0 / 1333.0
const STALL_ROOF_ANCHORS: Array[Vector3] = [
	Vector3(242.0, 211.0, 0.39),
	Vector3(296.0, 211.0, 0.39),
	Vector3(424.0, 211.0, 0.39),
	Vector3(478.0, 211.0, 0.39),
	Vector3(213.0, 249.0, 0.43),
	Vector3(253.0, 251.0, 0.43),
	Vector3(467.0, 251.0, 0.43),
	Vector3(507.0, 249.0, 0.43),
	Vector3(178.0, 269.0, 0.46),
	Vector3(222.0, 269.0, 0.46),
	Vector3(498.0, 269.0, 0.46),
	Vector3(542.0, 269.0, 0.46),
	Vector3(148.0, 327.0, 0.49),
	Vector3(572.0, 327.0, 0.49),
	Vector3(130.0, 359.0, 0.52),
	Vector3(590.0, 359.0, 0.52),
]


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(LAB_PATH) as PackedScene
	_expect(packed != null, "Home-menu stall lab must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var lab := packed.instantiate()
	root.add_child(lab)
	await process_frame
	await process_frame

	var village := lab.get_node_or_null("HomeVillageRainLab") as Node2D
	var stall_stage := lab.get_node_or_null("StallStage") as AspectContainStage
	var stall := lab.get_node_or_null("StallStage/StallStructure") as TextureRect
	var stall_roof_splashes := (
		lab.get_node_or_null("StallStage/StallRoofSplashes") as Node2D
	)
	_expect(village != null, "Approved village lab must remain instanced.", errors)
	_expect(stall_stage != null, "Missing responsive stall stage.", errors)
	_expect(stall != null, "Missing registered empty stall.", errors)
	_expect(
		stall_roof_splashes != null,
		"Stall-roof rain receiver must be a Node2D.",
		errors
	)

	if stall_roof_splashes != null:
		_expect(
			stall_roof_splashes.get_script() == STALL_ROOF_RAIN_SCRIPT,
			"Stall-roof receiver must use the registered rain script.",
			errors
		)
		_expect(
			stall_roof_splashes.get_parent() == stall_stage,
			"Stall-roof rain must inherit the responsive StallStage.",
			errors
		)
		_expect(
			stall_roof_splashes.z_index == 16,
			"Stall-roof rain must render immediately above the shell at z 16.",
			errors
		)

	if stall != null:
		_expect(stall.texture != null, "Stall texture must load.", errors)
		if stall.texture != null:
			_expect(
				stall.texture.get_size() == CANVAS_SIZE,
				"Stall texture must be exactly 720x1280.",
				errors
			)
			var stall_image := stall.texture.get_image()
			_expect(stall_image != null, "Stall texture must expose image data.", errors)
			if stall_image != null:
				var visible_bounds := stall_image.get_used_rect()
				_expect(
					visible_bounds == APPROVED_VISIBLE_BOUNDS,
					"Stall visible bounds must keep the approved V002 registration.",
					errors
				)
				var runtime_aspect := (
					float(visible_bounds.size.x) / float(visible_bounds.size.y)
				)
				_expect(
					absf(runtime_aspect - SOURCE_VISIBLE_ASPECT) < 0.002,
					"Stall silhouette must preserve the immutable cutout aspect ratio.",
					errors
				)
		_expect(stall.position == Vector2.ZERO, "Stall must stay at canvas origin.", errors)
		_expect(stall.size == CANVAS_SIZE, "Stall must cover the registered canvas.", errors)
		_expect(stall.scale == Vector2.ONE, "Stall must not be repositioned by scale.", errors)
		_expect(stall.z_index == 15, "Stall must render at global z 15.", errors)
		var depth_material := stall.material as ShaderMaterial
		_expect(depth_material != null, "Stall must have its subtle depth material.", errors)
		if depth_material != null:
			_expect(
				depth_material.resource_path == STALL_DEPTH_MATERIAL_PATH,
				"Stall depth must come from the reusable shared material.",
				errors
			)
			_expect(
				depth_material.shader == STALL_DEPTH_SHADER,
				"Stall must use the approved depth-falloff shader.",
				errors
			)
			_expect(
				is_equal_approx(
					float(depth_material.get_shader_parameter("shadow_strength")),
					0.075
				),
				"Lower-stall shadow must remain below an 8% influence.",
				errors
			)
			_expect(
				is_equal_approx(
					float(depth_material.get_shader_parameter("shadow_start")),
					0.52
				)
					and is_equal_approx(
						float(depth_material.get_shader_parameter("shadow_end")),
						0.88
					),
				"Stall depth must affect only the lower authored surface.",
				errors
			)
			var shadow_tint: Color = depth_material.get_shader_parameter("shadow_tint")
			_expect(
				shadow_tint.is_equal_approx(Color(0.64, 0.72, 0.84, 1.0)),
				"Stall depth tint must remain a cool scene-derived blue.",
				errors
			)

	if village != null:
		var background := village.get_node_or_null("BackgroundUnlit") as TextureRect
		var lighting := village.get_node_or_null("Lighting") as Node2D
		var weather := village.get_node_or_null("Weather") as Node2D
		_expect(background != null, "Missing approved village background.", errors)
		_expect(lighting != null, "Missing approved village lighting.", errors)
		_expect(weather != null, "Missing existing weather group.", errors)
		if background != null:
			_expect(background.z_index < 15, "Background must render behind stall.", errors)
		if lighting != null:
			_expect(lighting.z_index < 15, "Village lighting must render behind stall.", errors)
		if weather != null:
			_expect(weather.z_index > 15, "Existing weather must render above stall.", errors)

	if village != null and stall_roof_splashes != null:
		var roof_drop_timer := (
			village.get_node_or_null("Weather/RoofDropTimer") as Timer
		)
		_expect(roof_drop_timer != null, "Missing shared roof-impact timer.", errors)
		if roof_drop_timer != null:
			roof_drop_timer.stop()

		village.emit_signal("stall_roof_impact_requested")
		var splash_sprites := _get_splash_sprites(stall_roof_splashes)
		_expect(
			splash_sprites.size() == 1,
			"One shared-scheduler request must create exactly one stall-roof splash.",
			errors
		)
		if splash_sprites.size() == 1:
			_validate_stall_roof_splash(splash_sprites[0], errors)

		village.call("set_rain_enabled", false)
		await process_frame
		_expect(
			_get_splash_sprites(stall_roof_splashes).is_empty(),
			"Disabling rain must clear every active stall-roof splash.",
			errors
		)

	var counter_texture := load(COUNTER_OCCLUDER_PATH) as Texture2D
	_expect(counter_texture != null, "Future-owner counter occluder must load.", errors)
	if counter_texture != null:
		_expect(
			counter_texture.get_size() == CANVAS_SIZE,
			"Counter occluder must preserve full-canvas registration.",
			errors
		)

	lab.queue_free()
	await process_frame
	await create_timer(0.10).timeout
	_finish(errors)


func _get_splash_sprites(parent: Node) -> Array[Sprite2D]:
	var sprites: Array[Sprite2D] = []
	for child: Node in parent.get_children():
		if child is Sprite2D:
			sprites.append(child as Sprite2D)
	return sprites


func _validate_stall_roof_splash(
	splash: Sprite2D,
	errors: PackedStringArray
) -> void:
	_expect(splash.hframes == 8, "Stall-roof splash must use all 8 atlas frames.", errors)
	_expect(splash.texture != null, "Stall-roof splash atlas must load.", errors)
	_expect(
		is_equal_approx(splash.scale.x, splash.scale.y),
		"Stall-roof splash scale must remain uniform.",
		errors
	)
	_expect(
		absf(splash.rotation) <= 0.0501,
		"Stall-roof splash rotation must stay restrained.",
		errors
	)
	_expect(
		splash.modulate.a >= 0.48 and splash.modulate.a <= 0.60,
		"Stall-roof splash alpha must remain within the approved subtle range.",
		errors
	)
	_expect(
		Color(splash.modulate.r, splash.modulate.g, splash.modulate.b).is_equal_approx(
			Color(0.66, 0.79, 0.90)
		),
		"Stall-roof splash must keep the approved cool rain tint.",
		errors
	)

	var matching_anchor := Vector3.ZERO
	var found_anchor := false
	for anchor: Vector3 in STALL_ROOF_ANCHORS:
		var offset := splash.position - Vector2(anchor.x, anchor.y)
		if absf(offset.x) <= 4.001 and absf(offset.y) <= 1.501:
			matching_anchor = anchor
			found_anchor = true
			break
	_expect(
		found_anchor,
		"Stall-roof splash must remain within approved anchor jitter.",
		errors
	)
	if found_anchor:
		_expect(
			splash.scale.x >= matching_anchor.z * 0.90
				and splash.scale.x <= matching_anchor.z * 1.10,
			"Stall-roof splash scale must follow its perspective anchor.",
			errors
		)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Home-menu stall lab contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
