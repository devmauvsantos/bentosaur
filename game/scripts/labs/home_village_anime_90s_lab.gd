extends Node2D

const PRESETS := [
	{
		"name": "Clean",
		"noise_intensity": 0.0,
		"aberration": 0.0,
		"brightness": 1.0,
		"saturation": 1.0,
		"glow_bleed": 0.0,
		"curve_strength": 0.0,
	},
	{
		"name": "Soft transfer",
		"noise_intensity": 0.022,
		"aberration": 0.00045,
		"brightness": 1.015,
		"saturation": 1.0,
		"glow_bleed": 0.08,
		"curve_strength": 0.08,
	},
	{
		"name": "90s broadcast",
		"noise_intensity": 0.05,
		"aberration": 0.00085,
		"brightness": 1.03,
		"saturation": 0.96,
		"glow_bleed": 0.18,
		"curve_strength": 0.10,
	},
	{
		"name": "Heavy transfer",
		"noise_intensity": 0.085,
		"aberration": 0.0013,
		"brightness": 1.025,
		"saturation": 0.92,
		"glow_bleed": 0.28,
		"curve_strength": 0.16,
	},
]

@onready var anime_filter: ColorRect = $PostProcessing/Anime90sFilter

var _active_preset := 3
var _filter_was_visible := true


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.has("--anime-clean"):
		_active_preset = 0
	elif args.has("--anime-soft"):
		_active_preset = 1
	elif args.has("--anime-heavy"):
		_active_preset = 3
	_apply_preset(_active_preset)
	if args.has("--deterministic-capture"):
		call_deferred("_settle_lights_for_capture")


func _unhandled_key_input(event: InputEvent) -> void:
	if not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_0:
			_apply_preset(0)
		KEY_1:
			_apply_preset(1)
		KEY_2:
			_apply_preset(2)
		KEY_3:
			_apply_preset(3)
		KEY_P:
			_filter_was_visible = anime_filter.visible
			anime_filter.visible = not _filter_was_visible


func _apply_preset(index: int) -> void:
	_active_preset = clampi(index, 0, PRESETS.size() - 1)
	var preset: Dictionary = PRESETS[_active_preset]
	var shader_material := anime_filter.material as ShaderMaterial
	for parameter: String in [
		"noise_intensity",
		"aberration",
		"brightness",
		"saturation",
		"glow_bleed",
		"curve_strength",
	]:
		shader_material.set_shader_parameter(parameter, preset[parameter])
	anime_filter.visible = _active_preset != 0
	_filter_was_visible = anime_filter.visible
	print("Anime 90s trial preset: ", preset["name"])


func _settle_lights_for_capture() -> void:
	await get_tree().process_frame
	$HomeMenuStallLab/HomeVillageRainLab.set_lights_enabled(true)
