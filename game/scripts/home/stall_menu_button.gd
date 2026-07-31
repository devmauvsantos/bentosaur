class_name StallMenuButton
extends Button

signal visual_state_changed(state: VisualState)

enum ButtonKind {
	PRIMARY,
	SECONDARY,
}

enum VisualState {
	NORMAL,
	FOCUSED,
	PRESSED,
	DISABLED,
}

const PRIMARY_NORMAL := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-primary-normal-v001.png"
)
const PRIMARY_SELECTED := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-primary-selected-v001.png"
)
const PRIMARY_PRESSED := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-primary-pressed-v001.png"
)
const PRIMARY_DISABLED := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-primary-disabled-v001.png"
)
const SECONDARY_NORMAL := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-secondary-normal-v001.png"
)
const SECONDARY_SELECTED := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-secondary-selected-v001.png"
)
const SECONDARY_PRESSED := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-secondary-pressed-v001.png"
)
const SECONDARY_DISABLED := preload(
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-secondary-disabled-v001.png"
)

const PRIMARY_MINIMUM_SIZE := Vector2(292.0, 72.0)
const SECONDARY_MINIMUM_SIZE := Vector2(290.0, 64.0)
const SOURCE_FRAME_HEIGHT := 410.0
const SOURCE_CAP_WIDTH := 144
const PRESS_OFFSET := Vector2(0.0, 2.0)
const PRESS_SCALE := Vector2(0.985, 0.985)
const DOWN_SECONDS := 0.070
const UP_SECONDS := 0.090

@export var button_kind := ButtonKind.PRIMARY:
	set(value):
		button_kind = clampi(value, ButtonKind.PRIMARY, ButtonKind.SECONDARY)
		if is_node_ready():
			_apply_kind()

@export var label_text := "Open Stall":
	set(value):
		label_text = value
		if is_node_ready():
			_apply_label()

@export var label_font: Font:
	set(value):
		label_font = value
		if is_node_ready():
			_apply_label_theme()

@export_range(0, 96, 1) var primary_font_size := 30:
	set(value):
		primary_font_size = maxi(value, 0)
		if is_node_ready():
			_apply_label_theme()

@export_range(0, 96, 1) var secondary_font_size := 26:
	set(value):
		secondary_font_size = maxi(value, 0)
		if is_node_ready():
			_apply_label_theme()

@export var label_color := Color(0.97, 0.85, 0.63, 1.0):
	set(value):
		label_color = value
		if is_node_ready():
			_apply_label_theme()

@export var label_outline_color := Color(0.21, 0.11, 0.055, 0.96):
	set(value):
		label_outline_color = value
		if is_node_ready():
			_apply_label_theme()

@export_range(0, 8, 1) var label_outline_size := 1:
	set(value):
		label_outline_size = maxi(value, 0)
		if is_node_ready():
			_apply_label_theme()

@export var reduced_motion := false:
	set(value):
		reduced_motion = value
		if is_node_ready():
			_snap_motion_endpoint()

@onready var visual_root: Control = $VisualRoot
@onready var frame: NinePatchRect = $VisualRoot/Frame
@onready var left_leaf: TextureRect = $VisualRoot/LeafLeft
@onready var right_leaf: TextureRect = $VisualRoot/LeafRight
@onready var live_label: Label = $VisualRoot/LiveLabel

var _visually_pressed := false
var _current_state := VisualState.NORMAL
var _motion_tween: Tween


func _ready() -> void:
	button_down.connect(_on_button_down)
	button_up.connect(_on_button_up)
	focus_entered.connect(_refresh_visual_state)
	focus_exited.connect(_refresh_visual_state)
	resized.connect(_layout_visuals)
	_apply_kind()
	_apply_label()
	_apply_label_theme()
	_layout_visuals()
	_refresh_visual_state()
	set_process(true)


func _process(_delta: float) -> void:
	# BaseButton has no disabled-changed signal. This is a cheap state comparison
	# and only performs work when disabled/focus/press precedence actually changes.
	_refresh_visual_state()


func set_reduced_motion(enabled: bool) -> void:
	reduced_motion = enabled


func is_reduced_motion() -> bool:
	return reduced_motion


func get_visual_state() -> VisualState:
	_refresh_visual_state()
	return _current_state


func get_active_state_texture() -> Texture2D:
	return _texture_for_state(_current_state)


func get_canonical_mask_texture() -> Texture2D:
	return _normal_texture()


func _apply_kind() -> void:
	custom_minimum_size = (
		PRIMARY_MINIMUM_SIZE
		if button_kind == ButtonKind.PRIMARY
		else SECONDARY_MINIMUM_SIZE
	)
	frame.texture = _normal_texture()
	var material := frame.material as ShaderMaterial
	if material != null:
		material.set_shader_parameter("state_texture", get_active_state_texture())
	_apply_label_theme()
	_layout_visuals()
	_refresh_visual_state(true)


func _apply_label() -> void:
	# The root's live text supplies Button semantics to assistive technology.
	# Its rendered colors are transparent; the child Label moves with the art.
	text = label_text
	tooltip_text = label_text
	live_label.text = label_text


func _apply_label_theme() -> void:
	if live_label == null:
		return
	if label_font == null:
		live_label.remove_theme_font_override("font")
	else:
		live_label.add_theme_font_override("font", label_font)
	var font_size := (
		primary_font_size
		if button_kind == ButtonKind.PRIMARY
		else secondary_font_size
	)
	if font_size <= 0:
		live_label.remove_theme_font_size_override("font_size")
	else:
		live_label.add_theme_font_size_override("font_size", font_size)
	live_label.add_theme_color_override("font_color", label_color)
	live_label.add_theme_color_override("font_outline_color", label_outline_color)
	live_label.add_theme_color_override(
		"font_shadow_color",
		Color(0.12, 0.055, 0.02, 0.78)
	)
	live_label.add_theme_constant_override("outline_size", label_outline_size)
	live_label.add_theme_constant_override("shadow_offset_x", 1)
	live_label.add_theme_constant_override("shadow_offset_y", 2)


func _layout_visuals() -> void:
	if visual_root == null or frame == null or size.x <= 0.0 or size.y <= 0.0:
		return
	visual_root.pivot_offset = size * 0.5
	var frame_scale := size.y / SOURCE_FRAME_HEIGHT
	frame.position = Vector2.ZERO
	frame.size = Vector2(size.x / frame_scale, SOURCE_FRAME_HEIGHT)
	frame.scale = Vector2.ONE * frame_scale
	frame.patch_margin_left = SOURCE_CAP_WIDTH
	frame.patch_margin_right = SOURCE_CAP_WIDTH
	frame.patch_margin_top = 0
	frame.patch_margin_bottom = 0

	var leaf_box := Vector2(size.x * 0.11, size.y * 0.32)
	var leaf_y := (size.y - leaf_box.y) * 0.5
	left_leaf.position = Vector2(size.x * 0.045, leaf_y)
	left_leaf.size = leaf_box
	left_leaf.self_modulate = Color(1.28, 1.22, 1.08, 1.0)
	right_leaf.position = Vector2(
		size.x - leaf_box.x - size.x * 0.045,
		leaf_y
	)
	right_leaf.size = leaf_box
	right_leaf.self_modulate = Color(1.28, 1.22, 1.08, 1.0)

	var label_inset := size.x * 0.15
	live_label.position = Vector2(label_inset, 0.0)
	live_label.size = Vector2(maxf(0.0, size.x - 2.0 * label_inset), size.y)


func _refresh_visual_state(force: bool = false) -> void:
	if not is_node_ready():
		return
	var next_state := _resolve_visual_state()
	if not force and next_state == _current_state:
		return
	_current_state = next_state
	var material := frame.material as ShaderMaterial
	if material != null:
		material.set_shader_parameter("state_texture", _texture_for_state(next_state))
	visual_state_changed.emit(next_state)
	if next_state == VisualState.DISABLED:
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


func _texture_for_state(state: VisualState) -> Texture2D:
	if button_kind == ButtonKind.PRIMARY:
		match state:
			VisualState.FOCUSED:
				return PRIMARY_SELECTED
			VisualState.PRESSED:
				return PRIMARY_PRESSED
			VisualState.DISABLED:
				return PRIMARY_DISABLED
			_:
				return PRIMARY_NORMAL
	match state:
		VisualState.FOCUSED:
			return SECONDARY_SELECTED
		VisualState.PRESSED:
			return SECONDARY_PRESSED
		VisualState.DISABLED:
			return SECONDARY_DISABLED
		_:
			return SECONDARY_NORMAL


func _normal_texture() -> Texture2D:
	return (
		PRIMARY_NORMAL
		if button_kind == ButtonKind.PRIMARY
		else SECONDARY_NORMAL
	)


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
	var target_position := PRESS_OFFSET if pressed_endpoint else Vector2.ZERO
	var target_scale := PRESS_SCALE if pressed_endpoint else Vector2.ONE
	if reduced_motion or not is_inside_tree():
		visual_root.position = target_position
		visual_root.scale = target_scale
		return
	var seconds := DOWN_SECONDS if pressed_endpoint else UP_SECONDS
	_motion_tween = create_tween().set_parallel(true)
	_motion_tween.tween_property(
		visual_root,
		"position",
		target_position,
		seconds
	).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	_motion_tween.tween_property(
		visual_root,
		"scale",
		target_scale,
		seconds
	).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	_motion_tween.finished.connect(_clear_motion_tween)


func _snap_motion_endpoint() -> void:
	if visual_root == null:
		return
	_kill_motion_tween()
	visual_root.position = PRESS_OFFSET if _visually_pressed else Vector2.ZERO
	visual_root.scale = PRESS_SCALE if _visually_pressed else Vector2.ONE


func _kill_motion_tween() -> void:
	if _motion_tween != null and _motion_tween.is_valid():
		_motion_tween.kill()
	_motion_tween = null


func _clear_motion_tween() -> void:
	_motion_tween = null
