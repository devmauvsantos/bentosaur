extends SceneTree

const LAB_PATH := "res://scenes/labs/home_village_rain_lab.tscn"


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(LAB_PATH) as PackedScene
	_expect(packed != null, "Rain lab scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var lab := packed.instantiate()
	root.add_child(lab)
	await process_frame
	await process_frame

	var background := lab.get_node_or_null("BackgroundUnlit") as TextureRect
	var lighting := lab.get_node_or_null("Lighting") as Node2D
	var weather := lab.get_node_or_null("Weather") as Node2D
	_expect(background != null, "Missing immutable unlit background.", errors)
	_expect(lighting != null, "Missing registered lighting group.", errors)
	_expect(weather != null, "Missing weather group.", errors)
	if background != null:
		_expect(
			background.texture.get_size() == Vector2(720.0, 1280.0),
			"Runtime background must be exactly 720x1280.",
			errors
		)

	for layer_name: String in [
		"IndirectWarmSpill",
		"LightHalos",
		"LightCores",
		"WarmReflections",
	]:
		var layer := lab.get_node_or_null("Lighting/%s" % layer_name) as TextureRect
		_expect(layer != null, "Missing lighting layer %s." % layer_name, errors)
		if layer != null:
			var layer_material := layer.material as CanvasItemMaterial
			_expect(
				layer_material != null
				and layer_material.blend_mode == CanvasItemMaterial.BLEND_MODE_ADD,
				"%s must use additive blending." % layer_name,
				errors
			)

	var rain_back := lab.get_node_or_null("Weather/RainBack") as GPUParticles2D
	var rain_front := lab.get_node_or_null("Weather/RainFront") as GPUParticles2D
	var impact := lab.get_node_or_null("Weather/RainImpactSeeds") as GPUParticles2D
	var splashes := lab.get_node_or_null("Weather/RainSplashes") as GPUParticles2D
	var surface := lab.get_node_or_null(
		"Weather/PavementImpactSurface"
	) as LightOccluder2D
	var reduced_weather := OS.get_cmdline_user_args().has("--reduced-weather")
	var expected_back := 48 if reduced_weather else 96
	var expected_front := 24 if reduced_weather else 52
	var expected_impact := 28 if reduced_weather else 54
	var expected_splashes := 96 if reduced_weather else 192
	_expect(
		rain_back != null
			and rain_back.amount == expected_back
			and rain_back.texture != null
			and rain_back.emitting
			and rain_back.modulate.a > 0.30,
		"Back rain must be visible from frame one and match its density contract.",
		errors
	)
	_expect(
		rain_front != null
			and rain_front.amount == expected_front
			and rain_front.texture != null
			and rain_front.emitting
			and rain_front.modulate.a > 0.50,
		"Front rain must be visible from frame one and match its density contract.",
		errors
	)
	_expect(
		impact != null
			and impact.amount == expected_impact
			and impact.texture != null
			and impact.emitting,
		"Impact seeds must be active and match their density contract.",
		errors
	)
	_expect(
		splashes != null
			and splashes.amount == expected_splashes
			and splashes.texture != null,
		"Splash field must have its atlas and capacity contract.",
		errors
	)
	_expect(surface != null and surface.sdf_collision, "Missing SDF pavement surface.", errors)

	if OS.get_cmdline_user_args().has("--deterministic-capture"):
		for particles: GPUParticles2D in [
			rain_back,
			rain_front,
			impact,
			splashes,
		]:
			_expect(
				particles != null and particles.use_fixed_seed,
				"Every weather source needs a fixed visual-QA seed.",
				errors
			)

	if impact != null:
		var impact_process := impact.process_material as ParticleProcessMaterial
		_expect(impact_process != null, "Impact rain needs a process material.", errors)
		if impact_process != null:
			_expect(
				impact_process.collision_mode
					== ParticleProcessMaterial.COLLISION_HIDE_ON_CONTACT,
				"Impact rain must hide on contact.",
				errors
			)
			_expect(
				impact_process.sub_emitter_mode
					== ParticleProcessMaterial.SUB_EMITTER_AT_COLLISION,
				"Impact rain must trigger its sub-emitter at collision.",
				errors
			)
			_expect(
				impact_process.sub_emitter_amount_at_collision == 1,
				"Each impact must trigger one splash flipbook.",
				errors
			)
		_expect(
			impact.sub_emitter == NodePath("../RainSplashes"),
			"Impact rain must target the splash particle system.",
			errors
		)

	if splashes != null:
		var flipbook := splashes.material as CanvasItemMaterial
		_expect(flipbook != null, "Splash particles need a flipbook material.", errors)
		if flipbook != null:
			_expect(flipbook.particles_animation, "Splash animation must be enabled.", errors)
			_expect(
				flipbook.particles_anim_h_frames == 8
					and flipbook.particles_anim_v_frames == 1,
				"Splash atlas must remain 8x1.",
				errors
			)
			_expect(
				not flipbook.particles_anim_loop,
				"Splash flipbook must play once.",
				errors
			)

	_expect(
		ProjectSettings.get_setting("rendering/renderer/rendering_method", "")
			== "mobile",
		"Rain sub-emitters require the locked Mobile renderer.",
		errors
	)
	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Home Village rain lab contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
