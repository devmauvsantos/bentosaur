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
	var music := lab.get_node_or_null("Audio/LateNightRadio") as AudioStreamPlayer
	var rain_audio := lab.get_node_or_null("Audio/GentleRain") as AudioStreamPlayer
	var lighting := lab.get_node_or_null("Lighting") as Node2D
	var weather := lab.get_node_or_null("Weather") as Node2D
	var audio_off := OS.get_cmdline_user_args().has("--audio-off")
	_expect(background != null, "Missing immutable unlit background.", errors)
	_expect(music != null, "Missing Late Night Radio music channel.", errors)
	_expect(rain_audio != null, "Missing synchronized rain-audio channel.", errors)
	_expect(lighting != null, "Missing registered lighting group.", errors)
	_expect(weather != null, "Missing weather group.", errors)
	if background != null:
		_expect(
			background.texture.get_size() == Vector2(720.0, 1280.0),
			"Runtime background must be exactly 720x1280.",
			errors
		)

	if music != null:
		_expect(music.stream is AudioStreamMP3, "Music must load as MP3.", errors)
		_expect(
			(music.stream as AudioStreamMP3).loop,
			"Late Night Radio must loop.",
			errors
		)
		_expect(music.bus == "Music", "Music must use the Music bus.", errors)
		_expect(
			is_equal_approx(music.volume_db, -19.0),
			"Music must use the device-tuned -19 dB balance.",
			errors
		)
		_expect(
			music.playing == not audio_off,
			"Music playback must follow the audio-off runtime option.",
			errors
		)

	if rain_audio != null:
		_expect(rain_audio.stream is AudioStreamMP3, "Rain ambience must load as MP3.", errors)
		_expect(
			(rain_audio.stream as AudioStreamMP3).loop,
			"Rain ambience must loop.",
			errors
		)
		_expect(rain_audio.bus == "Weather", "Rain ambience must use the Weather bus.", errors)
		_expect(
			is_equal_approx(rain_audio.volume_db, -19.0),
			"Rain ambience must remain a quiet bed at -19 dB.",
			errors
		)
		_expect(
			rain_audio.playing == not audio_off,
			"Rain playback must follow the audio-off runtime option.",
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
	var roof_splash_layer := lab.get_node_or_null(
		"Weather/RoofSplashes"
	) as Node2D
	var roof_drop_timer := lab.get_node_or_null(
		"Weather/RoofDropTimer"
	) as Timer
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
			and rain_back.modulate.a >= 0.20
			and rain_back.modulate.a <= 0.26,
		"Back rain must be softly blended from frame one.",
		errors
	)
	_expect(
		rain_front != null
			and rain_front.amount == expected_front
			and rain_front.texture != null
			and rain_front.emitting
			and rain_front.modulate.a >= 0.34
			and rain_front.modulate.a <= 0.40,
		"Front rain must remain readable without glowing over the village.",
		errors
	)
	for rain_layer: GPUParticles2D in [rain_back, rain_front]:
		if rain_layer == null:
			continue
		var rain_material := rain_layer.material as CanvasItemMaterial
		_expect(
			rain_material != null
				and rain_material.blend_mode == CanvasItemMaterial.BLEND_MODE_MIX,
			"%s must use normal alpha blending." % rain_layer.name,
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
	_expect(roof_splash_layer != null, "Missing sparse roof-splash layer.", errors)
	_expect(
		roof_drop_timer != null
			and roof_drop_timer.one_shot
			and not roof_drop_timer.is_stopped(),
		"Roof drops must use one sparse randomized one-shot timer.",
		errors
	)
	if roof_splash_layer != null:
		lab.call("_spawn_roof_splash")
		await process_frame
		_expect(
			roof_splash_layer.get_child_count() == 1,
			"A requested roof impact must create exactly one splash.",
			errors
		)
		if roof_splash_layer.get_child_count() == 1:
			var roof_splash := roof_splash_layer.get_child(0) as Sprite2D
			_expect(roof_splash != null, "Roof impact must be a sprite.", errors)
			if roof_splash != null:
				_expect(
					roof_splash.hframes == 8,
					"Roof impact must use the 8-frame splash atlas.",
					errors
				)
				_expect(
					roof_splash.scale.x <= 0.47
						and roof_splash.modulate.a <= 0.54,
					"Roof impacts must remain smaller and dimmer than pavement splashes.",
					errors
				)

	if rain_audio != null and not audio_off:
		lab.set_rain_enabled(false)
		await create_timer(0.30).timeout
		_expect(
			rain_audio.stream_paused,
			"Turning rain off must pause its audio channel after the short fade.",
			errors
		)
		if roof_splash_layer != null and roof_drop_timer != null:
			_expect(
				roof_drop_timer.is_stopped()
					and roof_splash_layer.get_child_count() == 0,
				"Turning rain off must stop and clear roof impacts.",
				errors
			)
		lab.set_rain_enabled(true)
		await create_timer(0.30).timeout
		_expect(
			rain_audio.playing and not rain_audio.stream_paused,
			"Turning rain on must resume its audio channel.",
			errors
		)
		if roof_drop_timer != null:
			_expect(
				not roof_drop_timer.is_stopped(),
				"Turning rain on must resume sparse roof impacts.",
				errors
			)
	elif rain_audio != null:
		_expect(
			not rain_audio.playing,
			"Silent captures must keep the rain channel stopped.",
			errors
		)

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
			_expect(
				flipbook.blend_mode == CanvasItemMaterial.BLEND_MODE_MIX,
				"Splash particles must use normal alpha blending.",
				errors
			)
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
	if music != null:
		music.stop()
		music.stream = null
	if rain_audio != null:
		rain_audio.stop()
		rain_audio.stream = null
	lab.queue_free()
	await process_frame
	await create_timer(0.10).timeout
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
