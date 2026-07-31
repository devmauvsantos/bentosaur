extends SceneTree

const LAB_PATH := "res://scenes/labs/home_menu_stall_lab.tscn"
const STALL_DEPTH_SHADER := preload(
	"res://assets/vfx/lighting/stall_depth_falloff.gdshader"
)
const STALL_DEPTH_MATERIAL_PATH := (
	"res://assets/vfx/lighting/stall_depth_falloff_material.tres"
)
const COUNTER_OCCLUDER_PATH := (
	"res://assets/environments/home_village/v001/stall/"
	+ "stall_counter_occluder_720x1280.png"
)
const CANVAS_SIZE := Vector2(720.0, 1280.0)
const APPROVED_VISIBLE_BOUNDS := Rect2i(77, 197, 566, 874)
const SOURCE_VISIBLE_ASPECT := 862.0 / 1333.0


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
	_expect(village != null, "Approved village lab must remain instanced.", errors)
	_expect(stall_stage != null, "Missing responsive stall stage.", errors)
	_expect(stall != null, "Missing registered empty stall.", errors)

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
