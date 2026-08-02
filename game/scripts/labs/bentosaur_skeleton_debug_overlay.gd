class_name BentosaurSkeletonDebugOverlay
extends Node2D

const BONE_COLOR := Color(0.98, 0.74, 0.31, 0.92)
const JOINT_COLOR := Color(0.28, 0.86, 0.72, 0.96)
const PIVOT_COLOR := Color(1.0, 0.38, 0.30, 0.98)

var _torso_bone: Bone2D
var _head_bone: Bone2D
var _left_arm_bone: Bone2D
var _right_arm_bone: Bone2D


func _ready() -> void:
	_torso_bone = get_node_or_null(
		"../GuestPuppet/Skeleton2D/TorsoBone"
	) as Bone2D
	_head_bone = get_node_or_null(
		"../GuestPuppet/Skeleton2D/TorsoBone/HeadBone"
	) as Bone2D
	_left_arm_bone = get_node_or_null(
		"../GuestPuppet/Skeleton2D/TorsoBone/LeftArmBone"
	) as Bone2D
	_right_arm_bone = get_node_or_null(
		"../GuestPuppet/Skeleton2D/TorsoBone/RightArmBone"
	) as Bone2D
	set_process(true)


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	if not _all_bones_are_ready():
		return
	var torso := to_local(_torso_bone.global_position)
	var head := to_local(_head_bone.global_position)
	var left_arm := to_local(_left_arm_bone.global_position)
	var right_arm := to_local(_right_arm_bone.global_position)

	draw_line(torso, head, BONE_COLOR, 4.0, true)
	draw_line(torso, left_arm, BONE_COLOR, 4.0, true)
	draw_line(torso, right_arm, BONE_COLOR, 4.0, true)
	draw_circle(torso, 9.0, PIVOT_COLOR)
	draw_circle(head, 8.0, JOINT_COLOR)
	draw_circle(left_arm, 8.0, JOINT_COLOR)
	draw_circle(right_arm, 8.0, JOINT_COLOR)
	draw_arc(torso, 20.0, 0.0, TAU, 32, BONE_COLOR, 2.0, true)


func _all_bones_are_ready() -> bool:
	return (
		is_instance_valid(_torso_bone)
		and is_instance_valid(_head_bone)
		and is_instance_valid(_left_arm_bone)
		and is_instance_valid(_right_arm_bone)
	)
