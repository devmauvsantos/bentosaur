class_name BentosaurFullBodyBoneOverlay
extends Node2D

const BONE_COLOR := Color(1.0, 0.72, 0.22, 0.92)
const JOINT_COLOR := Color(0.24, 0.88, 0.72, 0.97)
const ROOT_COLOR := Color(1.0, 0.34, 0.28, 0.98)

@export var skeleton_path: NodePath = NodePath("../Skeleton2D")

var _skeleton: Skeleton2D
var _bones: Array[Bone2D] = []


func _ready() -> void:
	_skeleton = get_node_or_null(skeleton_path) as Skeleton2D
	if is_instance_valid(_skeleton):
		_collect_bones(_skeleton)
	set_process(true)


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	if not is_instance_valid(_skeleton):
		return
	for bone in _bones:
		var joint := to_local(bone.global_position)
		var parent := bone.get_parent() as Bone2D
		if parent != null:
			draw_line(to_local(parent.global_position), joint, BONE_COLOR, 3.0, true)
		draw_circle(joint, 6.0, ROOT_COLOR if parent == null else JOINT_COLOR)
		var angle := bone.global_rotation
		var tip := joint + Vector2.RIGHT.rotated(angle - global_rotation) * minf(bone.length, 34.0)
		draw_line(joint, tip, BONE_COLOR, 2.0, true)


func _collect_bones(node: Node) -> void:
	for child in node.get_children():
		if child is Bone2D:
			_bones.append(child as Bone2D)
		_collect_bones(child)
