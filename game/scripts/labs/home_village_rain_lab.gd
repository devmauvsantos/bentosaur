extends Node2D

const VIEWPORT_SIZE := Vector2(720.0, 1280.0)

const BACKGROUND_TEXTURE: Texture2D = preload(
	"res://assets/environments/home_village/v001/background_unlit_720x1280.png"
)
const INDIRECT_SPILL_TEXTURE: Texture2D = preload(
	"res://assets/environments/home_village/v001/lighting/"
	+ "indirect_warm_spill_720x1280.png"
)
const LIGHT_HALOS_TEXTURE: Texture2D = preload(
	"res://assets/environments/home_village/v001/lighting/"
	+ "light_halos_720x1280.png"
)
const LIGHT_CORES_TEXTURE: Texture2D = preload(
	"res://assets/environments/home_village/v001/lighting/"
	+ "light_cores_720x1280.png"
)
const WARM_REFLECTIONS_TEXTURE: Texture2D = preload(
	"res://assets/environments/home_village/v001/lighting/"
	+ "warm_reflections_720x1280.png"
)
const RAIN_STREAK_BACK_TEXTURE: Texture2D = preload(
	"res://assets/vfx/weather/rain/v001/rain_streak_back.png"
)
const RAIN_STREAK_FRONT_TEXTURE: Texture2D = preload(
	"res://assets/vfx/weather/rain/v001/rain_streak_front.png"
)
const RAIN_IMPACT_SEED_TEXTURE: Texture2D = preload(
	"res://assets/vfx/weather/rain/v001/rain_impact_seed_transparent.png"
)
const RAIN_SPLASH_TEXTURE: Texture2D = preload(
	"res://assets/vfx/weather/rain/v001/rain_splash_8x1.png"
)

const RAIN_BACK_ALPHA := 0.34
const RAIN_FRONT_ALPHA := 0.54
const LIGHT_CORE_BASE_ALPHA := 0.99
const LIGHT_HALO_BASE_ALPHA := 0.985

var indirect_warm_spill: TextureRect
var light_halos: TextureRect
var light_cores: TextureRect
var warm_reflections: TextureRect
var rain_back: GPUParticles2D
var rain_front: GPUParticles2D
var rain_impact_seeds: GPUParticles2D
var rain_splashes: GPUParticles2D
var pavement_impact_surface: LightOccluder2D

var _elapsed := 0.0
var _lights_awake := false
var _rain_enabled := true
var _reduced_weather := false
var _deterministic_capture := false


func _ready() -> void:
	_read_runtime_options()
	_build_environment()
	_build_weather()
	_begin_wake_sequence()


func _process(delta: float) -> void:
	_elapsed += delta
	if not _lights_awake:
		return
	var core_flicker := (
		1.0
		+ 0.008 * sin(_elapsed * 2.1)
		+ 0.004 * sin(_elapsed * 5.7 + 1.2)
	)
	var halo_flicker := 1.0 + 0.004 * sin(_elapsed * 2.1 + 0.35)
	light_cores.modulate.a = LIGHT_CORE_BASE_ALPHA * core_flicker
	light_halos.modulate.a = LIGHT_HALO_BASE_ALPHA * halo_flicker


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.pressed or event.echo:
		return
	if event.keycode == KEY_R:
		set_rain_enabled(not _rain_enabled)
	elif event.keycode == KEY_L:
		set_lights_enabled(light_cores.modulate.a < 0.05)


func set_rain_enabled(enabled: bool) -> void:
	_rain_enabled = enabled
	for particles: GPUParticles2D in [
		rain_back,
		rain_front,
		rain_impact_seeds,
	]:
		particles.emitting = enabled
	rain_back.visible = enabled
	rain_front.visible = enabled
	rain_splashes.visible = enabled


func set_lights_enabled(enabled: bool) -> void:
	_lights_awake = enabled
	indirect_warm_spill.modulate.a = 1.0 if enabled else 0.0
	light_halos.modulate.a = LIGHT_HALO_BASE_ALPHA if enabled else 0.0
	light_cores.modulate.a = LIGHT_CORE_BASE_ALPHA if enabled else 0.0
	warm_reflections.modulate.a = 1.0 if enabled else 0.0


func _read_runtime_options() -> void:
	var args := OS.get_cmdline_user_args()
	_reduced_weather = args.has("--reduced-weather")
	_rain_enabled = not args.has("--rain-off")
	_deterministic_capture = args.has("--deterministic-capture")


func _build_environment() -> void:
	var background := _make_fullscreen_texture(
		"BackgroundUnlit",
		BACKGROUND_TEXTURE,
		false
	)
	background.z_index = 0
	add_child(background)

	var lighting := Node2D.new()
	lighting.name = "Lighting"
	lighting.z_index = 10
	add_child(lighting)

	indirect_warm_spill = _make_fullscreen_texture(
		"IndirectWarmSpill",
		INDIRECT_SPILL_TEXTURE,
		true
	)
	light_halos = _make_fullscreen_texture(
		"LightHalos",
		LIGHT_HALOS_TEXTURE,
		true
	)
	light_cores = _make_fullscreen_texture(
		"LightCores",
		LIGHT_CORES_TEXTURE,
		true
	)
	warm_reflections = _make_fullscreen_texture(
		"WarmReflections",
		WARM_REFLECTIONS_TEXTURE,
		true
	)

	for layer: TextureRect in [
		indirect_warm_spill,
		light_halos,
		light_cores,
		warm_reflections,
	]:
		layer.modulate.a = 0.0
		lighting.add_child(layer)


func _build_weather() -> void:
	var weather := Node2D.new()
	weather.name = "Weather"
	weather.z_index = 20
	add_child(weather)

	rain_back = _make_rain_field(
		"RainBack",
		RAIN_STREAK_BACK_TEXTURE,
		96 if not _reduced_weather else 48,
		1.95,
		Vector2(600.0, 745.0),
		Vector2(0.48, 0.76),
		RAIN_BACK_ALPHA
	)
	weather.add_child(rain_back)

	rain_front = _make_rain_field(
		"RainFront",
		RAIN_STREAK_FRONT_TEXTURE,
		52 if not _reduced_weather else 24,
		1.48,
		Vector2(900.0, 1080.0),
		Vector2(0.62, 0.96),
		RAIN_FRONT_ALPHA
	)
	rain_front.z_index = 2
	weather.add_child(rain_front)

	rain_splashes = _make_splash_field()
	rain_splashes.z_index = 3
	weather.add_child(rain_splashes)

	rain_impact_seeds = _make_impact_seed_field(
		54 if not _reduced_weather else 28
	)
	rain_impact_seeds.z_index = 1
	weather.add_child(rain_impact_seeds)
	rain_impact_seeds.sub_emitter = rain_impact_seeds.get_path_to(
		rain_splashes
	)

	pavement_impact_surface = _make_pavement_impact_surface()
	weather.add_child(pavement_impact_surface)

	if not _rain_enabled:
		set_rain_enabled(false)


func _begin_wake_sequence() -> void:
	var lights_tween := create_tween().set_parallel(true)
	lights_tween.tween_property(
		indirect_warm_spill,
		"modulate:a",
		1.0,
		1.15
	).set_delay(0.08).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	lights_tween.tween_property(
		warm_reflections,
		"modulate:a",
		1.0,
		1.25
	).set_delay(0.16).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	lights_tween.tween_property(
		light_halos,
		"modulate:a",
		LIGHT_HALO_BASE_ALPHA,
		0.82
	).set_delay(0.24).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	lights_tween.tween_property(
		light_cores,
		"modulate:a",
		LIGHT_CORE_BASE_ALPHA,
		0.66
	).set_delay(0.32).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
	lights_tween.finished.connect(func() -> void: _lights_awake = true)


func _make_fullscreen_texture(
	node_name: String,
	texture: Texture2D,
	additive: bool
) -> TextureRect:
	var layer := TextureRect.new()
	layer.name = node_name
	layer.position = Vector2.ZERO
	layer.size = VIEWPORT_SIZE
	layer.texture = texture
	layer.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	layer.stretch_mode = TextureRect.STRETCH_SCALE
	layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	if additive:
		var additive_material := CanvasItemMaterial.new()
		additive_material.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		additive_material.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
		layer.material = additive_material
	return layer


func _make_rain_field(
	node_name: String,
	texture: Texture2D,
	particle_amount: int,
	particle_lifetime: float,
	velocity_range: Vector2,
	scale_range: Vector2,
	alpha: float
) -> GPUParticles2D:
	var particles := GPUParticles2D.new()
	particles.name = node_name
	particles.position = Vector2(360.0, -70.0)
	particles.texture = texture
	particles.amount = particle_amount
	particles.lifetime = particle_lifetime
	particles.preprocess = particle_lifetime
	particles.randomness = 0.72
	particles.fixed_fps = 30
	particles.use_fixed_seed = _deterministic_capture
	particles.seed = 41017 if node_name == "RainBack" else 88421
	particles.local_coords = false
	particles.visibility_rect = Rect2(-460.0, -170.0, 920.0, 1580.0)
	particles.modulate = Color(0.88, 0.95, 1.0, alpha)

	var display_material := CanvasItemMaterial.new()
	display_material.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	particles.material = display_material

	var process := ParticleProcessMaterial.new()
	process.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	process.emission_box_extents = Vector3(420.0, 90.0, 0.0)
	process.direction = Vector3(-0.055, 1.0, 0.0)
	process.spread = 2.8
	process.initial_velocity_min = velocity_range.x
	process.initial_velocity_max = velocity_range.y
	process.gravity = Vector3(-10.0, 92.0, 0.0)
	process.scale_min = scale_range.x
	process.scale_max = scale_range.y
	process.color = Color(1.0, 1.0, 1.0, 1.0)
	particles.process_material = process
	return particles


func _make_splash_field() -> GPUParticles2D:
	var particles := GPUParticles2D.new()
	particles.name = "RainSplashes"
	particles.texture = RAIN_SPLASH_TEXTURE
	particles.amount = 192 if not _reduced_weather else 96
	particles.lifetime = 0.34
	particles.emitting = false
	particles.fixed_fps = 30
	particles.use_fixed_seed = _deterministic_capture
	particles.seed = 52103
	particles.local_coords = false
	particles.visibility_rect = Rect2(0.0, 380.0, 720.0, 900.0)
	particles.modulate = Color(0.84, 0.94, 1.0, 0.68)

	var flipbook := CanvasItemMaterial.new()
	flipbook.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	flipbook.particles_animation = true
	flipbook.particles_anim_h_frames = 8
	flipbook.particles_anim_v_frames = 1
	flipbook.particles_anim_loop = false
	particles.material = flipbook

	var process := ParticleProcessMaterial.new()
	process.anim_offset_min = 0.0
	process.anim_offset_max = 0.0
	process.anim_speed_min = 1.0
	process.anim_speed_max = 1.0
	process.initial_velocity_min = 0.0
	process.initial_velocity_max = 0.0
	process.gravity = Vector3.ZERO
	process.scale_min = 0.42
	process.scale_max = 0.68
	process.color = Color(1.0, 1.0, 1.0, 1.0)
	particles.process_material = process
	return particles


func _make_impact_seed_field(particle_amount: int) -> GPUParticles2D:
	var particles := GPUParticles2D.new()
	particles.name = "RainImpactSeeds"
	particles.position = Vector2(360.0, 330.0)
	particles.texture = RAIN_IMPACT_SEED_TEXTURE
	particles.amount = particle_amount
	particles.lifetime = 1.65
	particles.preprocess = 1.65
	particles.randomness = 0.8
	particles.fixed_fps = 30
	particles.use_fixed_seed = _deterministic_capture
	particles.seed = 73061
	particles.local_coords = false
	particles.collision_base_size = 0.24
	particles.visibility_rect = Rect2(-430.0, -80.0, 860.0, 1050.0)
	particles.modulate = Color.WHITE

	var process := ParticleProcessMaterial.new()
	process.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	process.emission_box_extents = Vector3(390.0, 26.0, 0.0)
	process.direction = Vector3(-0.035, 1.0, 0.0)
	process.spread = 1.5
	process.initial_velocity_min = 690.0
	process.initial_velocity_max = 860.0
	process.gravity = Vector3(0.0, 60.0, 0.0)
	process.collision_mode = ParticleProcessMaterial.COLLISION_HIDE_ON_CONTACT
	process.sub_emitter_mode = ParticleProcessMaterial.SUB_EMITTER_AT_COLLISION
	process.sub_emitter_amount_at_collision = 1
	process.sub_emitter_keep_velocity = false
	process.scale_min = 0.20
	process.scale_max = 0.28
	particles.process_material = process
	return particles


func _make_pavement_impact_surface() -> LightOccluder2D:
	# A static zig-zag SDF surface spreads collision-triggered flipbook splashes
	# across the deep perspective pavement. The visible streak layers are
	# independent, so this invisible surface never truncates the rainfall.
	var polygon := OccluderPolygon2D.new()
	polygon.closed = true
	polygon.polygon = PackedVector2Array([
		Vector2(-40.0, 1040.0),
		Vector2(25.0, 785.0),
		Vector2(92.0, 1150.0),
		Vector2(158.0, 655.0),
		Vector2(224.0, 935.0),
		Vector2(290.0, 535.0),
		Vector2(356.0, 1080.0),
		Vector2(422.0, 710.0),
		Vector2(488.0, 1205.0),
		Vector2(554.0, 805.0),
		Vector2(620.0, 1015.0),
		Vector2(686.0, 595.0),
		Vector2(760.0, 890.0),
		Vector2(760.0, 1360.0),
		Vector2(-40.0, 1360.0),
	])
	var collider := LightOccluder2D.new()
	collider.name = "PavementImpactSurface"
	collider.sdf_collision = true
	collider.occluder = polygon
	return collider
