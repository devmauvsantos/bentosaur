class_name BentosaurFacialRigController
extends Node

signal contract_failed(errors: PackedStringArray)
signal contract_ready(report: Dictionary)

enum MouthMode {
	MORPH_ONLY,
	BONE_ONLY,
	HYBRID,
}

const SHAPE_MOUTH_OPEN: StringName = &"Mouth_DelightedOpen"
const SHAPE_MOUTH_CLOSE: StringName = &"Mouth_CloseCorrective"
const SHAPE_CHEW: StringName = &"Chew_Compress"
const SHAPE_BLINK_LEFT: StringName = &"Blink_L"
const SHAPE_BLINK_RIGHT: StringName = &"Blink_R"
const SHAPE_HAPPY_EYES: StringName = &"HappyEyes"
const SHAPE_TONGUE_RETRACT: StringName = &"Tongue_Retract"
const SHAPE_TONGUE_CHEW: StringName = &"Tongue_Chew"

const REQUIRED_SHAPES: Array[StringName] = [
	SHAPE_MOUTH_OPEN,
	SHAPE_MOUTH_CLOSE,
	SHAPE_CHEW,
	SHAPE_BLINK_LEFT,
	SHAPE_BLINK_RIGHT,
	SHAPE_HAPPY_EYES,
	SHAPE_TONGUE_RETRACT,
	SHAPE_TONGUE_CHEW,
]
const REQUIRED_BONES: Array[StringName] = [
	&"root",
	&"jaw",
	&"tongue",
]

@export var mouth_mode: MouthMode = MouthMode.HYBRID
@export_range(0.0, 20.0, 0.1, "degrees") var maximum_jaw_degrees: float = 10.0
@export var random_blink_enabled: bool = true
@export_range(0.5, 10.0, 0.1) var blink_interval_minimum: float = 2.0
@export_range(0.5, 10.0, 0.1) var blink_interval_maximum: float = 5.0
@export var chew_enabled: bool = false
@export_range(0.5, 4.0, 0.05) var chew_cycles_per_second: float = 1.8
@export var deterministic_seed: int = 20260729

var _character_root: Node
var _meshes: Array[MeshInstance3D] = []
var _tongue_meshes: Array[MeshInstance3D] = []
var _skeleton: Skeleton3D
var _shape_bindings: Dictionary = {}
var _bone_indices: Dictionary = {}
var _random: RandomNumberGenerator = RandomNumberGenerator.new()

var _mouth_open: float = 0.0
var _blink_left_manual: float = 0.0
var _blink_right_manual: float = 0.0
var _blink_automatic: float = 0.0
var _happy_eyes: float = 0.0
var _chew_phase: float = 0.0
var _blink_loop_running: bool = false


func bind(character_root: Node) -> PackedStringArray:
	_character_root = character_root
	_meshes.clear()
	_tongue_meshes.clear()
	_skeleton = null
	_shape_bindings.clear()
	_bone_indices.clear()
	_collect_nodes(character_root)
	_bind_contract()
	var errors: PackedStringArray = validate_contract()
	if errors.is_empty():
		_random.seed = deterministic_seed
		apply_controls()
		contract_ready.emit(get_contract_report())
		if random_blink_enabled and not _blink_loop_running:
			_blink_loop_running = true
			_run_blink_loop()
	else:
		contract_failed.emit(errors)
	return errors


func validate_contract() -> PackedStringArray:
	var errors: PackedStringArray = []
	if _character_root == null:
		errors.append("Character root is not bound.")
	if _skeleton == null:
		errors.append("No Skeleton3D was found.")
	for shape_name: StringName in REQUIRED_SHAPES:
		if not _shape_bindings.has(shape_name):
			errors.append("Missing facial blend shape: %s" % shape_name)
	for bone_name: StringName in REQUIRED_BONES:
		if int(_bone_indices.get(bone_name, -1)) < 0:
			errors.append("Missing facial bone: %s" % bone_name)
	return errors


func get_contract_report() -> Dictionary:
	var shape_counts: Dictionary = {}
	for shape_name: StringName in _shape_bindings:
		shape_counts[String(shape_name)] = (_shape_bindings[shape_name] as Array).size()
	return {
		"mesh_count": _meshes.size(),
		"skeleton": _skeleton.name if _skeleton != null else "",
		"shapes": shape_counts,
		"bones": _bone_indices.duplicate(),
		"mouth_mode": MouthMode.keys()[mouth_mode],
	}


func set_mouth_open(value: float) -> void:
	_mouth_open = clampf(value, 0.0, 1.0)
	apply_controls()


func set_mouth_mode(value: MouthMode) -> void:
	mouth_mode = value
	apply_controls()


func set_blink_left(value: float) -> void:
	_blink_left_manual = clampf(value, 0.0, 1.0)
	apply_controls()


func set_blink_right(value: float) -> void:
	_blink_right_manual = clampf(value, 0.0, 1.0)
	apply_controls()


func set_happy_eyes(value: float) -> void:
	_happy_eyes = clampf(value, 0.0, 1.0)
	apply_controls()


func set_chew_enabled(value: bool) -> void:
	chew_enabled = value
	if not chew_enabled:
		_chew_phase = 0.0
	apply_controls()


func set_random_blink_enabled(value: bool) -> void:
	random_blink_enabled = value
	if random_blink_enabled and not _blink_loop_running:
		_blink_loop_running = true
		_run_blink_loop()


func trigger_blink(left: bool = true, right: bool = true) -> void:
	if left:
		_blink_left_manual = 1.0
	if right:
		_blink_right_manual = 1.0
	apply_controls()


func release_manual_blinks() -> void:
	_blink_left_manual = 0.0
	_blink_right_manual = 0.0
	apply_controls()


func _process(delta: float) -> void:
	if chew_enabled:
		_chew_phase = fmod(_chew_phase + delta * chew_cycles_per_second, 1.0)
		apply_controls()


func apply_controls() -> void:
	if _character_root == null:
		return

	var morph_open: float = (
		_mouth_open
		if mouth_mode == MouthMode.MORPH_ONLY or mouth_mode == MouthMode.HYBRID
		else 0.0
	)
	var jaw_open: float = (
		_mouth_open
		if mouth_mode == MouthMode.BONE_ONLY or mouth_mode == MouthMode.HYBRID
		else 0.0
	)
	var effective_open: float = maxf(morph_open, jaw_open)
	var chew_weight: float = 0.0
	var tongue_chew: float = 0.0
	if chew_enabled:
		var pulse: float = 0.5 - 0.5 * cos(TAU * _chew_phase)
		chew_weight = smoothstep(0.0, 1.0, pulse)
		tongue_chew = chew_weight
		morph_open = 0.0
		jaw_open = lerpf(0.15, 0.55, chew_weight)

	var close_corrective: float = clampf(1.0 - _mouth_open * 5.0, 0.0, 1.0)
	if chew_enabled:
		close_corrective = 0.0

	_set_shape(SHAPE_MOUTH_OPEN, morph_open)
	_set_shape(SHAPE_MOUTH_CLOSE, close_corrective)
	_set_shape(SHAPE_CHEW, chew_weight)
	_set_shape(SHAPE_BLINK_LEFT, maxf(_blink_left_manual, _blink_automatic))
	_set_shape(SHAPE_BLINK_RIGHT, maxf(_blink_right_manual, _blink_automatic))
	_set_shape(SHAPE_HAPPY_EYES, _happy_eyes)
	_set_shape(
		SHAPE_TONGUE_RETRACT,
		clampf(1.0 - effective_open * 2.0, 0.0, 1.0)
	)
	_set_shape(SHAPE_TONGUE_CHEW, tongue_chew)
	for tongue_mesh: MeshInstance3D in _tongue_meshes:
		# The layered proof has no physical mouth aperture to occlude a
		# retracted tongue. Production topology removes this visibility switch.
		tongue_mesh.visible = effective_open > 0.20 or chew_enabled
	_set_jaw_pose(jaw_open)
	_set_tongue_pose(-3.0 * effective_open + 4.0 * tongue_chew)


func _collect_nodes(node: Node) -> void:
	if node is MeshInstance3D:
		var mesh_instance := node as MeshInstance3D
		_meshes.append(mesh_instance)
		if "TONGUE" in String(mesh_instance.name).to_upper():
			_tongue_meshes.append(mesh_instance)
	elif node is Skeleton3D and _skeleton == null:
		_skeleton = node as Skeleton3D
	for child: Node in node.get_children():
		_collect_nodes(child)


func _bind_contract() -> void:
	for shape_name: StringName in [
		SHAPE_MOUTH_OPEN,
		SHAPE_MOUTH_CLOSE,
		SHAPE_CHEW,
		SHAPE_BLINK_LEFT,
		SHAPE_BLINK_RIGHT,
		SHAPE_HAPPY_EYES,
		SHAPE_TONGUE_RETRACT,
		SHAPE_TONGUE_CHEW,
	]:
		var bindings: Array[Dictionary] = []
		for mesh_instance: MeshInstance3D in _meshes:
			var index: int = mesh_instance.find_blend_shape_by_name(shape_name)
			if index >= 0:
				bindings.append({"mesh": mesh_instance, "index": index})
		if not bindings.is_empty():
			_shape_bindings[shape_name] = bindings

	if _skeleton != null:
		for bone_name: StringName in REQUIRED_BONES:
			_bone_indices[bone_name] = _skeleton.find_bone(String(bone_name))


func _set_shape(shape_name: StringName, value: float) -> void:
	var bindings: Array = _shape_bindings.get(shape_name, [])
	for binding_variant: Variant in bindings:
		var binding: Dictionary = binding_variant as Dictionary
		var mesh_instance: MeshInstance3D = binding["mesh"] as MeshInstance3D
		mesh_instance.set_blend_shape_value(
			int(binding["index"]),
			clampf(value, 0.0, 1.0)
		)


func _set_jaw_pose(normalized: float) -> void:
	if _skeleton == null:
		return
	var index: int = int(_bone_indices.get(&"jaw", -1))
	if index < 0:
		return
	_skeleton.set_bone_pose_rotation(
		index,
		Quaternion(Vector3.UP, deg_to_rad(maximum_jaw_degrees * normalized))
	)


func _set_tongue_pose(degrees: float) -> void:
	if _skeleton == null:
		return
	var index: int = int(_bone_indices.get(&"tongue", -1))
	if index < 0:
		return
	_skeleton.set_bone_pose_rotation(
		index,
		Quaternion(Vector3.UP, deg_to_rad(degrees))
	)


func _run_blink_loop() -> void:
	while is_inside_tree() and random_blink_enabled:
		var delay: float = _random.randf_range(
			blink_interval_minimum,
			maxf(blink_interval_minimum, blink_interval_maximum)
		)
		await get_tree().create_timer(delay).timeout
		if not is_inside_tree() or not random_blink_enabled:
			break
		await _play_automatic_blink()
	_blink_loop_running = false


func _play_automatic_blink() -> void:
	var close_tween: Tween = create_tween()
	close_tween.tween_method(_set_automatic_blink, 0.0, 1.0, 0.06)
	await close_tween.finished
	await get_tree().create_timer(0.035).timeout
	var open_tween: Tween = create_tween()
	open_tween.tween_method(_set_automatic_blink, 1.0, 0.0, 0.09)
	await open_tween.finished


func _set_automatic_blink(value: float) -> void:
	_blink_automatic = clampf(value, 0.0, 1.0)
	apply_controls()
