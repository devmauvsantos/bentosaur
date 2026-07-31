extends SceneTree

const LAB_PATH := "res://scenes/labs/home_village_rain_lab.tscn"
const REGISTERED_LIGHT_MOTION_SHADER := preload(
	"res://assets/vfx/lighting/registered_light_motion.gdshader"
)
const REGISTERED_REFLECTION_FLICK_SHADER := preload(
	"res://assets/vfx/lighting/registered_reflection_flick.gdshader"
)


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
			is_equal_approx(music.volume_db, -21.0),
			"Music must use the device-tuned -21 dB balance.",
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
			is_equal_approx(rain_audio.volume_db, -22.0),
			"Rain ambience must remain a quiet bed at -22 dB.",
			errors
		)
		_expect(
			rain_audio.playing == not audio_off,
			"Rain playback must follow the audio-off runtime option.",
			errors
		)

	var reflections := lab.get_node_or_null(
		"Lighting/WarmReflections"
	) as TextureRect
	_expect(reflections != null, "Missing lighting layer WarmReflections.", errors)
	var reflection_material: ShaderMaterial = null
	if reflections != null:
		reflection_material = reflections.material as ShaderMaterial
	_expect(
		reflection_material != null,
		"WarmReflections must expose a reflection-flick ShaderMaterial.",
		errors
	)
	if reflection_material != null:
		_expect(
			reflection_material.shader == REGISTERED_REFLECTION_FLICK_SHADER,
			"WarmReflections must use registered_reflection_flick.gdshader.",
			errors
		)

	var lab_script := lab.get_script() as Script
	_expect(lab_script != null, "Rain lab must retain its runtime script.", errors)
	var constants := {} if lab_script == null else lab_script.get_script_constant_map()
	var fixture_centers: Array = constants.get("LIGHT_FLICK_CENTERS", [])
	var reflection_rects: Array = constants.get("LIGHT_REFLECTION_RECTS", [])
	var reflection_weights: Array = constants.get("LIGHT_REFLECTION_WEIGHTS", [])
	var core_flick_radii: Array = constants.get("LIGHT_CORE_FLICK_RADII", [])
	var unique_reflection_rects := {}
	var reflection_weight_sums := {}
	for index: int in range(reflection_rects.size()):
		var reflection_rect: Rect2 = reflection_rects[index]
		if reflection_rect.has_area():
			unique_reflection_rects[reflection_rect] = true
			reflection_weight_sums[reflection_rect] = (
				float(reflection_weight_sums.get(reflection_rect, 0.0))
				+ float(reflection_weights[index])
			)
	_expect(
		fixture_centers.size() == 18
			and reflection_rects.size() == 18
			and reflection_weights.size() == 18
			and core_flick_radii.size() == 18,
		"All 18 fixtures need a reflection record, including the clipped no-band source.",
		errors
	)
	if fixture_centers.size() == 18 and core_flick_radii.size() == 18:
		for fixture_index: int in range(fixture_centers.size()):
			for neighbor_index: int in range(fixture_centers.size()):
				if fixture_index == neighbor_index:
					continue
				var normalized_delta := (
					(Vector2(fixture_centers[fixture_index])
						- Vector2(fixture_centers[neighbor_index]))
					/ Vector2(720.0, 1280.0)
					* Vector2(1.0, 1280.0 / 720.0)
				)
				_expect(
					float(core_flick_radii[fixture_index])
						<= normalized_delta.length() * 0.85,
					"A selected fixture core mask must end before every neighboring core.",
					errors
				)
	_expect(
		unique_reflection_rects.size() == 9,
		"The fixture registry must resolve to exactly nine painted reflection bands.",
		errors
	)
	for reflection_rect: Rect2 in reflection_weight_sums:
		_expect(
			is_equal_approx(float(reflection_weight_sums[reflection_rect]), 1.0),
			"Every shared reflection band must have normalized source weights.",
			errors
		)
	if fixture_centers.size() == 18:
		_expect(
			Vector2(fixture_centers[0]) == Vector2(7.0, 377.0)
				and not Rect2(reflection_rects[0]).has_area()
				and is_zero_approx(float(reflection_weights[0])),
			"Clipped S00 must remain registered without an on-canvas reflection.",
			errors
		)
		var expected_right_centers: Array[Vector2] = [
			Vector2(414.0, 299.0),
			Vector2(433.0, 381.0),
			Vector2(474.0, 384.0),
			Vector2(594.0, 375.0),
			Vector2(642.0, 395.0),
			Vector2(664.0, 214.0),
			Vector2(677.0, 381.0),
		]
		var expected_right_rects: Array[Rect2] = [
			Rect2(398.0, 433.0, 57.0, 401.0),
			Rect2(398.0, 433.0, 57.0, 401.0),
			Rect2(455.0, 478.0, 36.0, 159.0),
			Rect2(552.0, 504.0, 75.0, 461.0),
			Rect2(627.0, 514.0, 83.0, 387.0),
			Rect2(627.0, 514.0, 83.0, 387.0),
			Rect2(627.0, 514.0, 83.0, 387.0),
		]
		var expected_right_weights: Array[float] = [
			0.35,
			0.65,
			1.0,
			1.0,
			0.20,
			0.25,
			0.55,
		]
		for right_offset: int in range(expected_right_centers.size()):
			var registry_index := 11 + right_offset
			_expect(
				Vector2(fixture_centers[registry_index])
					== expected_right_centers[right_offset]
					and Rect2(reflection_rects[registry_index])
						== expected_right_rects[right_offset]
					and is_equal_approx(
						float(reflection_weights[registry_index]),
						expected_right_weights[right_offset]
					),
				"Every right-side source must keep its exact reflection mapping.",
				errors
			)

	for layer_name: String in [
		"IndirectWarmSpill",
		"LightHalos",
		"LightCores",
	]:
		var layer := lab.get_node_or_null("Lighting/%s" % layer_name) as TextureRect
		_expect(layer != null, "Missing lighting layer %s." % layer_name, errors)
		if layer != null:
			var layer_material := layer.material as ShaderMaterial
			_expect(
				layer_material != null
					and layer_material.shader == REGISTERED_LIGHT_MOTION_SHADER,
				"%s must use the localized additive light-motion shader." % layer_name,
				errors
			)
			if layer_material != null:
				var aspect_scale: Vector2 = layer_material.get_shader_parameter(
					"uv_aspect_scale"
				)
				_expect(
					aspect_scale.is_equal_approx(Vector2(1.0, 1280.0 / 720.0)),
					"%s flick mask must stay circular in artwork pixels." % layer_name,
					errors
				)

	var spill := lab.get_node_or_null("Lighting/IndirectWarmSpill") as TextureRect
	var halos := lab.get_node_or_null("Lighting/LightHalos") as TextureRect
	var cores := lab.get_node_or_null("Lighting/LightCores") as TextureRect
	_expect(spill != null, "Missing dynamic layer IndirectWarmSpill.", errors)
	_expect(halos != null, "Missing dynamic layer LightHalos.", errors)
	_expect(cores != null, "Missing dynamic layer LightCores.", errors)
	if spill != null and halos != null and cores != null and reflections != null:
		lab.set_lights_enabled(true)
		var stable_spill_alpha := spill.modulate.a
		var stable_halo_alpha := halos.modulate.a
		var stable_core_alpha := cores.modulate.a
		var stable_reflection_alpha := reflections.modulate.a
		# Stay below the six-second minimum first-flick delay so this assertion
		# never depends on which random production schedule was selected.
		lab.call("_process", 2.0)
		var spill_material := spill.material as ShaderMaterial
		var halo_material := halos.material as ShaderMaterial
		var core_material := cores.material as ShaderMaterial
		_expect(
			spill_material != null
				and halo_material != null
				and core_material != null
				and reflection_material != null,
			"Every dynamic emission and reflection layer must expose explicit RGB intensity.",
			errors
		)
		if (
			spill_material != null
			and halo_material != null
			and core_material != null
			and reflection_material != null
			and reflection_material.shader == REGISTERED_REFLECTION_FLICK_SHADER
		):
			var reduced_motion := OS.get_cmdline_user_args().has("--reduced-motion")
			var motion: RefCounted = lab.get("_light_motion")
			_expect(motion != null, "Living-light state must be available.", errors)
			if motion == null:
				_finish(errors)
				return
			var expected_core := 1.0 if reduced_motion else float(motion.get("core_level"))
			var expected_halo := 1.0 if reduced_motion else float(motion.get("halo_level"))
			var expected_spill := lerpf(1.0, expected_core, 0.42)
			var expected_reflection := lerpf(1.0, expected_core, 0.36)
			_expect(
				is_equal_approx(
					float(core_material.get_shader_parameter("global_intensity")),
					expected_core
				)
					and is_equal_approx(
						float(halo_material.get_shader_parameter("global_intensity")),
						expected_halo
					)
					and is_equal_approx(
						float(spill_material.get_shader_parameter("global_intensity")),
						expected_spill
					)
					and is_equal_approx(
						float(reflection_material.get_shader_parameter("global_intensity")),
						expected_reflection
					),
				"Dynamic RGB layers and reflections must follow the production coupling formulas.",
				errors
			)
			_expect(
				expected_core >= 0.78
					and expected_core <= 1.0
					and expected_halo >= expected_core
					and expected_spill >= expected_halo,
				"Light hierarchy must attenuate motion from core through broad spill.",
				errors
			)
			_expect(
				is_equal_approx(
					float(core_material.get_shader_parameter("flick_level")),
					1.0
				)
					and is_equal_approx(
						float(halo_material.get_shader_parameter("flick_level")),
						1.0
					)
					and is_equal_approx(
						float(spill_material.get_shader_parameter("flick_level")),
						1.0
					)
					and is_equal_approx(
						float(reflection_material.get_shader_parameter("reflection_level")),
						1.0
					),
				"No fixture or reflection may flick before the six-second minimum delay.",
				errors
			)

			if reduced_motion:
				_expect(
					is_equal_approx(expected_core, 1.0)
						and is_equal_approx(expected_halo, 1.0)
						and is_equal_approx(expected_spill, 1.0)
						and is_equal_approx(expected_reflection, 1.0),
					"Reduced motion must leave every light and reflection intensity static.",
					errors
				)
			elif motion != null and reflection_rects.size() == 18:
				# Force source 17, the far-right lantern, rather than waiting for a
				# random event. It owns 55% of the shared rightmost R8 band.
				motion.set("flick_target_index", 17)
				motion.set("flick_level", 0.40)
				lab.call("_apply_local_light_flick")
				var rightmost_rect: Rect2 = reflection_rects[17]
				var expected_center := (
					rightmost_rect.position + rightmost_rect.size * 0.5
				) / Vector2(720.0, 1280.0)
				var expected_half_size := (
					rightmost_rect.size * 0.5 / Vector2(720.0, 1280.0)
				)
				var expected_reflection_flick := lerpf(
					1.0,
					0.40,
					0.62 * 0.55
				)
				var expected_source_center := (
					Vector2(fixture_centers[17]) / Vector2(720.0, 1280.0)
				)
				var actual_source_center: Vector2 = core_material.get_shader_parameter(
					"flick_center"
				)
				var actual_center: Vector2 = reflection_material.get_shader_parameter(
					"reflection_center"
				)
				var actual_half_size: Vector2 = reflection_material.get_shader_parameter(
					"reflection_half_size"
				)
				_expect(
					rightmost_rect.is_equal_approx(
						Rect2(627.0, 514.0, 83.0, 387.0)
					)
						and actual_source_center.is_equal_approx(
							expected_source_center
						)
						and is_equal_approx(
							float(core_material.get_shader_parameter("flick_level")),
							0.40
						)
						and is_equal_approx(
							float(core_material.get_shader_parameter("flick_radius")),
							float(core_flick_radii[17])
						)
						and actual_center.is_equal_approx(expected_center)
						and actual_half_size.is_equal_approx(expected_half_size)
						and is_equal_approx(
							float(
								reflection_material.get_shader_parameter(
									"reflection_level"
								)
							),
							expected_reflection_flick
						),
					"The far-right lantern must drive normalized R8 at 0.62 * 0.55 coupling.",
					errors
				)
		_expect(
			is_equal_approx(spill.modulate.a, stable_spill_alpha)
				and is_equal_approx(halos.modulate.a, stable_halo_alpha)
				and is_equal_approx(cores.modulate.a, stable_core_alpha)
				and is_equal_approx(reflections.modulate.a, stable_reflection_alpha),
			"Every lighting layer alpha must remain stable while RGB intensity moves.",
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
	var expected_roof_interval := (
		Vector2(0.90, 1.80) if reduced_weather else Vector2(0.26, 0.62)
	)
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
			and not roof_drop_timer.is_stopped()
			and roof_drop_timer.wait_time >= expected_roof_interval.x
			and roof_drop_timer.wait_time <= expected_roof_interval.y,
		"Roof drops must use the denser device-test one-shot timer.",
		errors
	)
	_expect(
		lab.has_signal("stall_roof_impact_requested")
			and lab.has_signal("rain_enabled_changed"),
		"The shared roof scheduler must expose stall routing and rain state.",
		errors
	)
	lab.call("set_stall_roof_receiver_registered", true)
	_expect(
		bool(lab.get("_stall_roof_receiver_registered")),
		"A responsive stall-roof receiver must register with the shared scheduler.",
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
