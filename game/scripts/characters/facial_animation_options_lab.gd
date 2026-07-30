extends Node3D

const MODEL_PATH := "res://assets/characters/bentosaur_hero/v002/bentosaur_hero_facial_mobile_proof_v002.glb"
const PANEL_COLOR := Color(0.075, 0.094, 0.118, 0.96)
const ACCENT_COLOR := Color(0.945, 0.710, 0.330, 1.0)

var _character: Node3D
var _controller: BentosaurFacialRigController
var _camera: Camera3D
var _status_label: Label
var _mode_option: OptionButton
var _mouth_slider: HSlider
var _happy_slider: HSlider
var _demo_enabled: bool = true
var _demo_time: float = 0.0
var _last_demo_state: int = -1


func _ready() -> void:
	_build_world()
	var errors: PackedStringArray = _load_character()
	_build_interface()
	if errors.is_empty():
		_status_label.text = "HYBRID READY • 21.3K TRIANGLES • MOBILE"
		_apply_cli_capture_state()
	else:
		_status_label.text = "CONTRACT FAILED • %s" % " | ".join(errors)
		_status_label.modulate = Color(1.0, 0.48, 0.42)


func _process(delta: float) -> void:
	if not _demo_enabled or _controller == null:
		return
	_demo_time = fmod(_demo_time + delta, 12.0)
	var state: int = int(_demo_time / 2.0)
	if state != _last_demo_state:
		_last_demo_state = state
		_apply_demo_state(state)


func _build_world() -> void:
	var environment_node := WorldEnvironment.new()
	environment_node.name = "WorldEnvironment"
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.035, 0.047, 0.063)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.51, 0.64, 0.74)
	environment.ambient_light_energy = 0.72
	environment.tonemap_mode = Environment.TONE_MAPPER_AGX
	environment_node.environment = environment
	add_child(environment_node)

	var key := DirectionalLight3D.new()
	key.name = "WarmKey"
	key.light_color = Color(1.0, 0.78, 0.62)
	key.light_energy = 2.1
	key.shadow_enabled = true
	key.rotation_degrees = Vector3(-38.0, -28.0, 0.0)
	add_child(key)

	var rim := DirectionalLight3D.new()
	rim.name = "CoolRim"
	rim.light_color = Color(0.56, 0.76, 1.0)
	rim.light_energy = 1.15
	rim.rotation_degrees = Vector3(28.0, 142.0, 0.0)
	add_child(rim)

	var floor_mesh := CylinderMesh.new()
	floor_mesh.top_radius = 0.62
	floor_mesh.bottom_radius = 0.66
	floor_mesh.height = 0.035
	floor_mesh.radial_segments = 64
	var floor := MeshInstance3D.new()
	floor.name = "DioramaFloor"
	floor.mesh = floor_mesh
	floor.position = Vector3(0.0, -0.025, 0.0)
	var floor_material := StandardMaterial3D.new()
	floor_material.albedo_color = Color(0.12, 0.15, 0.17)
	floor_material.roughness = 0.92
	floor.material_override = floor_material
	add_child(floor)

	_camera = Camera3D.new()
	_camera.name = "GameplayCamera"
	_camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	_camera.size = 1.22
	_camera.position = Vector3(0.28, 0.53, 1.75)
	_camera.look_at_from_position(_camera.position, Vector3(0.0, 0.52, 0.0))
	add_child(_camera)


func _load_character() -> PackedStringArray:
	var packed: PackedScene = load(MODEL_PATH) as PackedScene
	if packed == null:
		return PackedStringArray(["Could not load %s" % MODEL_PATH])
	_character = packed.instantiate() as Node3D
	_character.name = "BentosaurHeroFacialProof"
	add_child(_character)
	_apply_proof_render_contract(_character)

	_controller = BentosaurFacialRigController.new()
	_controller.name = "FacialRigController"
	add_child(_controller)
	return _controller.bind(_character)


func _apply_proof_render_contract(node: Node) -> void:
	if node is MeshInstance3D:
		var upper_name: String = String(node.name).to_upper()
		if (
			"UPPER_LIP" in upper_name
			or "LOWER_LIP" in upper_name
			or "ICOSPHERE" in upper_name
		):
			(node as MeshInstance3D).visible = false
		elif "MOUTH_APERTURE" in upper_name:
			(node as MeshInstance3D).material_override = _unshaded_material(
				Color(0.055, 0.020, 0.035)
			)
		elif "EYE_" in upper_name:
			(node as MeshInstance3D).material_override = _unshaded_material(
				Color(0.19, 0.055, 0.070)
			)
		elif "BLUSH_" in upper_name:
			(node as MeshInstance3D).material_override = _unshaded_material(
				Color(0.95, 0.40, 0.42)
			)
		elif "TONGUE_" in upper_name:
			(node as MeshInstance3D).material_override = _unshaded_material(
				Color(0.95, 0.30, 0.43)
			)
	for child: Node in node.get_children():
		_apply_proof_render_contract(child)


func _unshaded_material(color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_color = color
	return material


func _build_interface() -> void:
	var canvas := CanvasLayer.new()
	canvas.name = "Interface"
	add_child(canvas)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 28)
	margin.add_theme_constant_override("margin_right", 28)
	margin.add_theme_constant_override("margin_top", 28)
	margin.add_theme_constant_override("margin_bottom", 28)
	canvas.add_child(margin)

	var layout := VBoxContainer.new()
	layout.add_theme_constant_override("separation", 12)
	margin.add_child(layout)

	var title := Label.new()
	title.text = "BENTOSAUR • FACE LAB"
	title.add_theme_font_size_override("font_size", 24)
	title.modulate = Color(0.96, 0.89, 0.76)
	layout.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "One character. Bones + morphs. No regenerated poses."
	subtitle.add_theme_font_size_override("font_size", 15)
	subtitle.modulate = Color(0.70, 0.78, 0.82)
	layout.add_child(subtitle)

	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	layout.add_child(spacer)

	var panel := PanelContainer.new()
	var panel_style := StyleBoxFlat.new()
	panel_style.bg_color = PANEL_COLOR
	panel_style.corner_radius_top_left = 22
	panel_style.corner_radius_top_right = 22
	panel_style.corner_radius_bottom_left = 22
	panel_style.corner_radius_bottom_right = 22
	panel_style.content_margin_left = 22
	panel_style.content_margin_right = 22
	panel_style.content_margin_top = 18
	panel_style.content_margin_bottom = 20
	panel.add_theme_stylebox_override("panel", panel_style)
	layout.add_child(panel)

	var controls := VBoxContainer.new()
	controls.add_theme_constant_override("separation", 9)
	panel.add_child(controls)

	_status_label = Label.new()
	_status_label.text = "IMPORTING…"
	_status_label.add_theme_font_size_override("font_size", 13)
	_status_label.modulate = ACCENT_COLOR
	controls.add_child(_status_label)

	_mode_option = OptionButton.new()
	_mode_option.add_item(
		"Hybrid — jaw + corrective",
		BentosaurFacialRigController.MouthMode.HYBRID
	)
	_mode_option.add_item(
		"Morph only",
		BentosaurFacialRigController.MouthMode.MORPH_ONLY
	)
	_mode_option.add_item(
		"Bone only — comparison",
		BentosaurFacialRigController.MouthMode.BONE_ONLY
	)
	_mode_option.selected = 0
	_mode_option.item_selected.connect(_on_mode_selected)
	controls.add_child(_mode_option)

	var mouth_group := _make_labeled_slider("Mouth open", _on_mouth_changed)
	_mouth_slider = mouth_group.get_child(1) as HSlider
	controls.add_child(mouth_group)
	var happy_group := _make_labeled_slider("Happy eyes", _on_happy_changed)
	_happy_slider = happy_group.get_child(1) as HSlider
	controls.add_child(happy_group)

	var buttons := HBoxContainer.new()
	buttons.add_theme_constant_override("separation", 8)
	var blink_left := Button.new()
	blink_left.text = "Blink L"
	blink_left.pressed.connect(func() -> void: _pulse_manual_blink(true, false))
	buttons.add_child(blink_left)
	var blink_both := Button.new()
	blink_both.text = "Blink both"
	blink_both.pressed.connect(func() -> void: _pulse_manual_blink(true, true))
	buttons.add_child(blink_both)
	var blink_right := Button.new()
	blink_right.text = "Blink R"
	blink_right.pressed.connect(func() -> void: _pulse_manual_blink(false, true))
	buttons.add_child(blink_right)
	controls.add_child(buttons)

	var toggles := HBoxContainer.new()
	var chew := CheckButton.new()
	chew.text = "Chew loop"
	chew.toggled.connect(_on_chew_toggled)
	toggles.add_child(chew)
	var demo := CheckButton.new()
	demo.text = "Auto demo"
	demo.button_pressed = true
	demo.toggled.connect(_on_demo_toggled)
	toggles.add_child(demo)
	controls.add_child(toggles)


func _make_labeled_slider(label_text: String, callback: Callable) -> VBoxContainer:
	var group := VBoxContainer.new()
	var label := Label.new()
	label.text = label_text
	label.add_theme_font_size_override("font_size", 14)
	group.add_child(label)
	var slider := HSlider.new()
	slider.min_value = 0.0
	slider.max_value = 1.0
	slider.step = 0.01
	slider.custom_minimum_size.y = 36.0
	slider.value_changed.connect(callback)
	group.add_child(slider)
	return group


func _on_mode_selected(index: int) -> void:
	_demo_enabled = false
	if _controller != null:
		var mode_id: int = _mode_option.get_item_id(index)
		_controller.set_mouth_mode(
			mode_id as BentosaurFacialRigController.MouthMode
		)


func _on_mouth_changed(value: float) -> void:
	_demo_enabled = false
	if _controller != null:
		_controller.set_mouth_open(value)


func _on_happy_changed(value: float) -> void:
	_demo_enabled = false
	if _controller != null:
		_controller.set_happy_eyes(value)


func _on_chew_toggled(enabled: bool) -> void:
	_demo_enabled = false
	if _controller != null:
		_controller.set_chew_enabled(enabled)


func _on_demo_toggled(enabled: bool) -> void:
	_demo_enabled = enabled
	_demo_time = 0.0
	_last_demo_state = -1


func _pulse_manual_blink(left: bool, right: bool) -> void:
	_demo_enabled = false
	if _controller == null:
		return
	_controller.trigger_blink(left, right)
	await get_tree().create_timer(0.12).timeout
	_controller.release_manual_blinks()


func _apply_demo_state(state: int) -> void:
	_controller.set_chew_enabled(false)
	_controller.release_manual_blinks()
	match state:
		0:
			_controller.set_mouth_open(0.0)
			_controller.set_happy_eyes(0.0)
		1:
			_controller.set_mouth_open(0.5)
			_controller.set_happy_eyes(0.0)
		2:
			_controller.set_mouth_open(1.0)
			_controller.set_happy_eyes(0.0)
		3:
			_controller.set_mouth_open(1.0)
			_controller.set_happy_eyes(1.0)
		4:
			_controller.set_mouth_open(0.0)
			_controller.set_happy_eyes(0.0)
			_controller.trigger_blink(true, true)
		5:
			_controller.set_mouth_open(0.0)
			_controller.set_happy_eyes(0.0)
			_controller.set_chew_enabled(true)
	if _mouth_slider != null:
		_mouth_slider.set_value_no_signal(
			[0.0, 0.5, 1.0, 1.0, 0.0, 0.0][state]
		)
	if _happy_slider != null:
		_happy_slider.set_value_no_signal(1.0 if state == 3 else 0.0)


func _apply_cli_capture_state() -> void:
	var requested_mode: int = -1
	var happy_weight: float = 0.0
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--capture-mouth-mode="):
			var slug: String = argument.trim_prefix("--capture-mouth-mode=")
			match slug:
				"morph":
					requested_mode = BentosaurFacialRigController.MouthMode.MORPH_ONLY
				"bone":
					requested_mode = BentosaurFacialRigController.MouthMode.BONE_ONLY
				"hybrid":
					requested_mode = BentosaurFacialRigController.MouthMode.HYBRID
				_:
					push_error("Unknown capture mouth mode: %s" % slug)
		elif argument == "--capture-happy":
			happy_weight = 1.0

	if requested_mode < 0:
		return

	_demo_enabled = false
	_controller.set_chew_enabled(false)
	_controller.release_manual_blinks()
	_controller.set_mouth_mode(
		requested_mode as BentosaurFacialRigController.MouthMode
	)
	_controller.set_mouth_open(1.0)
	_controller.set_happy_eyes(happy_weight)
	_mouth_slider.set_value_no_signal(1.0)
	_happy_slider.set_value_no_signal(happy_weight)

	for index: int in range(_mode_option.item_count):
		if _mode_option.get_item_id(index) == requested_mode:
			_mode_option.select(index)
			break

	_status_label.text = "CAPTURE • %s • 21.3K TRIANGLES • MOBILE" % (
		BentosaurFacialRigController.MouthMode.keys()[requested_mode]
	)
