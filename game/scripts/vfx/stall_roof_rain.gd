class_name StallRoofRain
extends Node2D

const RAIN_SPLASH_TEXTURE: Texture2D = preload(
	"res://assets/vfx/weather/rain/v001/rain_splash_8x1.png"
)
const SPLASH_TINT := Color(0.66, 0.79, 0.90, 1.0)
const SPLASH_ALPHA_RANGE := Vector2(0.48, 0.60)
const SPLASH_FRAME_SECONDS := 0.036
const ROOF_ANCHORS: Array[Vector3] = [
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

@export var rain_source_path := NodePath("../../HomeVillageRainLab")

var _rain_source: Node
var _rain_enabled := true
var _rng := RandomNumberGenerator.new()
var _last_anchor_index := -1


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.has("--deterministic-capture"):
		_rng.seed = 95013
	else:
		_rng.randomize()

	_rain_source = get_node_or_null(rain_source_path)
	if _rain_source == null:
		_rain_enabled = not args.has("--rain-off")
		return

	_rain_source.stall_roof_impact_requested.connect(
		_on_stall_roof_impact_requested
	)
	_rain_source.rain_enabled_changed.connect(_set_rain_enabled)
	_rain_source.set_stall_roof_receiver_registered(true)
	_set_rain_enabled(_rain_source.is_rain_enabled())


func _exit_tree() -> void:
	if is_instance_valid(_rain_source):
		_rain_source.set_stall_roof_receiver_registered(false)


func _set_rain_enabled(enabled: bool) -> void:
	_rain_enabled = enabled
	if enabled:
		return
	for child: Node in get_children():
		if child is Sprite2D:
			child.queue_free()


func _on_stall_roof_impact_requested() -> void:
	if _rain_enabled:
		_spawn_roof_splash()


func _spawn_roof_splash() -> void:
	if ROOF_ANCHORS.is_empty():
		return
	var anchor_index := _rng.randi_range(0, ROOF_ANCHORS.size() - 1)
	if anchor_index == _last_anchor_index:
		anchor_index = (anchor_index + 1) % ROOF_ANCHORS.size()
	_last_anchor_index = anchor_index
	var anchor := ROOF_ANCHORS[anchor_index]

	var splash := Sprite2D.new()
	splash.name = "StallRoofSplash%04d" % _rng.randi_range(0, 9999)
	splash.texture = RAIN_SPLASH_TEXTURE
	splash.hframes = 8
	splash.frame = 0
	splash.position = Vector2(anchor.x, anchor.y) + Vector2(
		_rng.randf_range(-4.0, 4.0),
		_rng.randf_range(-1.5, 1.5)
	)
	var splash_scale := anchor.z * _rng.randf_range(0.90, 1.10)
	splash.scale = Vector2.ONE * splash_scale
	splash.rotation = _rng.randf_range(-0.05, 0.05)
	splash.modulate = Color(
		SPLASH_TINT.r,
		SPLASH_TINT.g,
		SPLASH_TINT.b,
		_rng.randf_range(SPLASH_ALPHA_RANGE.x, SPLASH_ALPHA_RANGE.y)
	)
	splash.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	add_child(splash)

	var splash_tween := splash.create_tween()
	for frame_index: int in range(8):
		splash_tween.tween_callback(splash.set_frame.bind(frame_index))
		splash_tween.tween_interval(SPLASH_FRAME_SECONDS)
	splash_tween.tween_callback(splash.queue_free)
