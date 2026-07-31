class_name StallSettingsButton
extends Button

signal visual_state_changed(state: VisualState)

enum VisualState {
	NORMAL,
	FOCUSED,
	PRESSED,
	DISABLED,
}

const NORMAL_TEXTURE := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/settings/settings-cog-normal-v001.png"
)
const PRESSED_TEXTURE := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/settings/settings-cog-pressed-v001.png"
)
const DESIGN_SIZE := Vector2(75.0, 84.0)
const PRESS_SCALE := Vector2(0.97, 0.97)
const PRESS_ROTATION := deg_to_rad(5.0)
const DOWN_SECONDS := 0.070
const UP_SECONDS := 0.090

@export var accessible_label := "Settings":
	set(value):
		accessible_label = value
		if is_node_ready():
			_apply_accessible_label()

@export var reduced_motion := false:
	set(value):
		reduced_motion = value
		if is_node_ready():
			_snap_motion_endpoint()

@onready var visual_root: Control = $VisualRoot
@onready var icon_art: TextureRect = $VisualRoot/Icon

var _visually_pressed := false
var _current_state := VisualState.NORMAL
var _motion_tween: Tween


func _ready() -> void:
	button_down.connect(_on_button_down)
	button_up.connect(_on_button_up)
	focus_entered.connect(_refresh_visual_state)
	focus_exited.connect(_refresh_visual_state)
	resized.connect(_layout_visual)
	_apply_accessible_label()
	_layout_visual()
	_refresh_visual_state(true)
	set_process(true)


func _process(_delta: float) -> void:
	_refresh_visual_state()


func set_reduced_motion(enabled: bool) -> void:
	reduced_motion = enabled


func is_reduced_motion() -> bool:
	return reduced_motion


func get_visual_state() -> VisualState:
	_refresh_visual_state()
	return _current_state


func get_active_state_texture() -> Texture2D:
	return PRESSED_TEXTURE if _current_state == VisualState.PRESSED else NORMAL_TEXTURE


func get_canonical_mask_texture() -> Texture2D:
	return NORMAL_TEXTURE


func _apply_accessible_label() -> void:
	text = accessible_label
	tooltip_text = accessible_label


func _layout_visual() -> void:
	if visual_root == null:
		return
	visual_root.pivot_offset = size * 0.5


func _refresh_visual_state(force: bool = false) -> void:
	if not is_node_ready():
		return
	var next_state := _resolve_visual_state()
	if not force and next_state == _current_state:
		return
	_current_state = next_state
	var material := icon_art.material as ShaderMaterial
	if material != null:
		material.set_shader_parameter("state_texture", get_active_state_texture())
	visual_root.modulate = (
		Color(1.08, 1.04, 0.94, 1.0)
		if next_state == VisualState.FOCUSED
		else Color.WHITE
	)
	if disabled:
		visual_root.modulate.a = 0.48
	visual_state_changed.emit(next_state)
	if disabled:
		_visually_pressed = false
		_animate_visual(false)


func _resolve_visual_state() -> VisualState:
	if disabled:
		return VisualState.DISABLED
	if _visually_pressed:
		return VisualState.PRESSED
	if has_focus():
		return VisualState.FOCUSED
	return VisualState.NORMAL


func _on_button_down() -> void:
	if disabled:
		return
	_visually_pressed = true
	_refresh_visual_state()
	_animate_visual(true)


func _on_button_up() -> void:
	_visually_pressed = false
	_refresh_visual_state()
	_animate_visual(false)


func _animate_visual(pressed_endpoint: bool) -> void:
	_kill_motion_tween()
	var target_scale := PRESS_SCALE if pressed_endpoint else Vector2.ONE
	var target_rotation := PRESS_ROTATION if pressed_endpoint else 0.0
	if reduced_motion or not is_inside_tree():
		visual_root.scale = target_scale
		visual_root.rotation = target_rotation
		return
	var seconds := DOWN_SECONDS if pressed_endpoint else UP_SECONDS
	_motion_tween = create_tween().set_parallel(true)
	_motion_tween.tween_property(
		visual_root,
		"scale",
		target_scale,
		seconds
	).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	_motion_tween.tween_property(
		visual_root,
		"rotation",
		target_rotation,
		seconds
	).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	_motion_tween.finished.connect(_clear_motion_tween)


func _snap_motion_endpoint() -> void:
	if visual_root == null:
		return
	_kill_motion_tween()
	visual_root.scale = PRESS_SCALE if _visually_pressed else Vector2.ONE
	visual_root.rotation = PRESS_ROTATION if _visually_pressed else 0.0


func _kill_motion_tween() -> void:
	if _motion_tween != null and _motion_tween.is_valid():
		_motion_tween.kill()
	_motion_tween = null


func _clear_motion_tween() -> void:
	_motion_tween = null
