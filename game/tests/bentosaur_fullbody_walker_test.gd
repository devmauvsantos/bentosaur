extends SceneTree

const WALKER_PATH := "res://scenes/characters/bentosaur_fullbody_walker.tscn"
const WALKER_SCRIPT_PATH := "res://scripts/characters/bentosaur_fullbody_walker.gd"
const TEST_SEED := 72_041
const SAMPLE_FPS := 60
const TRANSFORM_EPSILON := 0.0001

const REQUIRED_METHODS: Array[StringName] = [
	&"play_motion",
	&"trigger_random_motion",
	&"set_locomotion",
	&"stop_locomotion",
	&"set_facing",
	&"set_auto_mode",
	&"set_reduced_motion",
	&"set_show_bones",
	&"set_deterministic_test_mode",
	&"reset_pose",
	&"step_motion",
	&"get_motion_state",
	&"get_walk_phase",
	&"get_facing_direction",
	&"get_ground_contacts",
	&"get_pose_snapshot",
	&"get_bone_names",
]

const SUPPORTED_MOTIONS: Array[StringName] = [
	&"idle",
	&"walk",
	&"wave",
	&"look",
	&"hop",
]

const REQUIRED_BONE_PATHS: Array[NodePath] = [
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/NeckBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/NeckBone/HeadBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone/ArmFarLowerBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone/ArmNearLowerBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/LegFarLowerBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/LegFarLowerBone/FootFarBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/LegNearLowerBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/LegNearLowerBone/FootNearBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone/TailTipBone",
]

const EXPECTED_BONE_NAMES: Array[String] = [
	"HipBone",
	"TorsoBone",
	"NeckBone",
	"HeadBone",
	"ArmFarUpperBone",
	"ArmFarLowerBone",
	"ArmNearUpperBone",
	"ArmNearLowerBone",
	"LegFarUpperBone",
	"LegFarLowerBone",
	"FootFarBone",
	"LegNearUpperBone",
	"LegNearLowerBone",
	"FootNearBone",
	"TailBaseBone",
	"TailMidBone",
	"TailTipBone",
]

const EXPECTED_PARENT_PATHS := {
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone": ^"FacingRoot/VisualRoot/Skeleton2D",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/NeckBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/NeckBone/HeadBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/NeckBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone/ArmFarLowerBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone/ArmNearLowerBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/LegFarLowerBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/LegFarLowerBone/FootFarBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/LegFarLowerBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/LegNearLowerBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/LegNearLowerBone/FootNearBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/LegNearLowerBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone/TailTipBone": ^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone",
}

const REQUIRED_TEXTURES := {
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/TorsoSprite": "res://assets/characters/bentosaur_walker/v001/walker_torso_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/NeckBone/HeadBone/HeadSprite": "res://assets/characters/bentosaur_walker/v001/walker_head_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone/UpperArmFarSprite": "res://assets/characters/bentosaur_walker/v001/walker_upper_arm_shared_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone/ArmFarLowerBone/LowerArmFarSprite": "res://assets/characters/bentosaur_walker/v001/walker_lower_arm_far_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone/UpperArmNearSprite": "res://assets/characters/bentosaur_walker/v001/walker_upper_arm_shared_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone/ArmNearLowerBone/LowerArmNearSprite": "res://assets/characters/bentosaur_walker/v001/walker_lower_arm_near_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/ThighFarSprite": "res://assets/characters/bentosaur_walker/v001/walker_thigh_far_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/LegFarLowerBone/LowerLegFarSprite": "res://assets/characters/bentosaur_walker/v001/walker_lower_leg_far_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/ThighNearSprite": "res://assets/characters/bentosaur_walker/v001/walker_thigh_near_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/LegNearLowerBone/LowerLegNearSprite": "res://assets/characters/bentosaur_walker/v001/walker_lower_leg_near_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailBaseSprite": "res://assets/characters/bentosaur_walker/v001/walker_tail_base_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone/TailMidSprite": "res://assets/characters/bentosaur_walker/v001/walker_tail_mid_v001.png",
	^"FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone/TailTipBone/TailTipSprite": "res://assets/characters/bentosaur_walker/v001/walker_tail_tip_v001.png",
}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	_expect(ResourceLoader.exists(WALKER_PATH), "Full-body walker scene is missing.", errors)
	if not ResourceLoader.exists(WALKER_PATH):
		_finish(errors)
		return

	var packed := load(WALKER_PATH) as PackedScene
	_expect(packed != null, "Full-body walker scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var walker := packed.instantiate() as BentosaurFullBodyWalker
	_expect(walker != null, "Full-body walker must expose its typed controller.", errors)
	if walker == null:
		_finish(errors)
		return
	root.add_child(walker)
	for frame: int in range(3):
		await process_frame

	_expect(
		walker.get_script().resource_path == WALKER_SCRIPT_PATH,
		"Walker scene must use the canonical full-body controller.",
		errors
	)
	for method_name: StringName in REQUIRED_METHODS:
		_expect(
			walker.has_method(method_name),
			"Walker controller is missing public method %s()." % method_name,
			errors
		)

	var bones := _validate_hierarchy(walker, errors)
	_validate_textures(walker, errors)
	if bones.size() != REQUIRED_BONE_PATHS.size():
		walker.queue_free()
		await process_frame
		_finish(errors)
		return

	walker.set_auto_mode(false)
	walker.set_deterministic_test_mode(true, TEST_SEED)
	walker.set_reduced_motion(true)
	walker.set_facing(1.0)
	walker.position = Vector2.ZERO
	walker.reset_pose()
	var authored_rest := _capture_pose(walker, bones)

	_validate_supported_motions(walker, bones, authored_rest, errors)
	_validate_walk_cycle(walker, bones, authored_rest, errors)
	_validate_determinism(walker, bones, authored_rest, errors)
	_validate_facing(walker, bones, errors)
	_validate_traversal_and_patrol(walker, errors)
	_validate_reduced_motion(walker, bones, authored_rest, errors)

	walker.queue_free()
	await process_frame
	_expect(
		not is_instance_valid(walker),
		"Full-body walker must free cleanly after the headless contract.",
		errors
	)
	_finish(errors)


func _validate_hierarchy(
	walker: BentosaurFullBodyWalker,
	errors: PackedStringArray
) -> Array[Bone2D]:
	var bones: Array[Bone2D] = []
	var skeleton := walker.get_node_or_null("FacingRoot/VisualRoot/Skeleton2D") as Skeleton2D
	_expect(skeleton != null, "Walker is missing its Skeleton2D.", errors)
	for bone_path: NodePath in REQUIRED_BONE_PATHS:
		var bone := walker.get_node_or_null(bone_path) as Bone2D
		_expect(bone != null, "Missing Bone2D at %s." % bone_path, errors)
		if bone == null:
			continue
		bones.append(bone)
		_expect(bone.length > 0.0, "%s must have a positive bone length." % bone.name, errors)
		_expect(_transform_is_finite(bone.rest), "%s has a non-finite rest transform." % bone.name, errors)
		var expected_parent := walker.get_node_or_null(EXPECTED_PARENT_PATHS[bone_path])
		_expect(
			bone.get_parent() == expected_parent,
			"%s has the wrong parent." % bone.name,
			errors
		)
	if skeleton != null:
		var discovered := skeleton.find_children("*", "Bone2D", true, false)
		_expect(discovered.size() == 17, "Skeleton2D must contain exactly 17 bones.", errors)
	_expect(
		Array(walker.get_bone_names()) == EXPECTED_BONE_NAMES,
		"Controller bone order must match the stable 17-bone contract.",
		errors
	)
	return bones


func _validate_textures(
	walker: BentosaurFullBodyWalker,
	errors: PackedStringArray
) -> void:
	for sprite_path: NodePath in REQUIRED_TEXTURES:
		var sprite := walker.get_node_or_null(sprite_path) as Sprite2D
		var expected_path: String = REQUIRED_TEXTURES[sprite_path]
		_expect(sprite != null, "Missing required sprite %s." % sprite_path, errors)
		_expect(ResourceLoader.exists(expected_path), "Missing texture %s." % expected_path, errors)
		if sprite == null:
			continue
		_expect(sprite.texture != null, "%s has no texture." % sprite.name, errors)
		if sprite.texture != null:
			_expect(
				sprite.texture.resource_path == expected_path,
				"%s must use canonical texture %s." % [sprite.name, expected_path],
				errors
			)


func _validate_supported_motions(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D],
	authored_rest: Dictionary,
	errors: PackedStringArray
) -> void:
	for motion: StringName in SUPPORTED_MOTIONS:
		walker.set_auto_mode(false)
		walker.set_deterministic_test_mode(true, TEST_SEED)
		walker.set_reduced_motion(false)
		walker.position = Vector2.ZERO
		_expect(walker.play_motion(motion, true), "Motion %s must be accepted." % motion, errors)
		var movement_score := 0.0
		for frame: int in range(int(0.70 * SAMPLE_FPS)):
			walker.step_motion(1.0 / float(SAMPLE_FPS))
			movement_score = maxf(
				movement_score,
				_pose_difference_score(walker, bones, authored_rest)
			)
			_validate_pose_bounds(walker, bones, authored_rest, motion, errors)
		_expect(
			movement_score > 0.01,
			"Motion %s must visibly move at least one rig transform." % motion,
			errors
		)
		_expect(
			walker.get_motion_state() == motion,
			"Motion %s ended before its documented sample window." % motion,
			errors
		)
		walker.set_reduced_motion(true)
		walker.reset_pose()
		_expect(
			_pose_matches(walker, bones, authored_rest),
			"Motion %s left cumulative drift after reset." % motion,
			errors
		)

	walker.set_reduced_motion(false)
	walker.reset_pose()
	var state_before := walker.get_motion_state()
	_expect(
		not walker.play_motion(&"not_a_motion", true),
		"Unknown motion names must be rejected.",
		errors
	)
	_expect(
		walker.get_motion_state() == state_before,
		"Rejecting an unknown motion must not alter state.",
		errors
	)

	for finite_motion: StringName in [&"wave", &"look", &"hop"]:
		walker.set_deterministic_test_mode(true, TEST_SEED)
		walker.set_reduced_motion(false)
		walker.play_motion(finite_motion, true)
		for frame: int in range(3 * SAMPLE_FPS):
			walker.step_motion(1.0 / float(SAMPLE_FPS))
		_expect(
			walker.get_motion_state() == &"idle",
			"Finite motion %s must settle back to idle." % finite_motion,
			errors
		)


func _validate_walk_cycle(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D],
	authored_rest: Dictionary,
	errors: PackedStringArray
) -> void:
	var cycle := BentosaurFullBodyWalker.WALK_CYCLE_SECONDS
	walker.set_auto_mode(false)
	walker.set_deterministic_test_mode(true, TEST_SEED)
	walker.set_reduced_motion(false)
	walker.play_motion(&"walk", true)
	var phase_zero := _capture_bone_pose(bones)
	walker.step_motion(cycle * 0.25)
	var quarter := walker.get_pose_snapshot()
	walker.step_motion(cycle * 0.50)
	var three_quarter := walker.get_pose_snapshot()

	_expect(is_equal_approx(float(quarter["phase"]), 0.25), "Quarter-cycle snapshot must report phase 0.25.", errors)
	_expect(is_equal_approx(float(three_quarter["phase"]), 0.75), "Three-quarter snapshot must report phase 0.75.", errors)
	_validate_phase_opposition(quarter, three_quarter, authored_rest, errors)

	walker.set_deterministic_test_mode(true, TEST_SEED)
	walker.set_reduced_motion(false)
	walker.play_motion(&"walk", true)
	walker.step_motion(cycle)
	_expect(
		_bone_pose_matches(bones, phase_zero),
		"One complete walk cycle must close on the same local bone pose.",
		errors
	)
	_expect(absf(walker.get_walk_phase()) <= TRANSFORM_EPSILON, "Walk phase must wrap to zero after one cycle.", errors)

	for rate: int in [30, 60, 120]:
		walker.set_deterministic_test_mode(true, TEST_SEED)
		walker.set_reduced_motion(false)
		walker.play_motion(&"walk", true)
		for frame: int in range(rate * 4):
			walker.step_motion(1.0 / float(rate))
		var sample := walker.get_pose_snapshot()
		if rate == 30:
			walker.set_meta("walk_reference", sample)
		else:
			_expect(
				_snapshots_match(sample, walker.get_meta("walk_reference")),
				"Walk sampling must be frame-rate independent at 30/60/120 FPS.",
				errors
			)

	walker.set_deterministic_test_mode(true, TEST_SEED)
	walker.set_reduced_motion(false)
	walker.play_motion(&"walk", true)
	for frame: int in range(120):
		var contacts: Dictionary = walker.get_ground_contacts()
		_expect(
			bool(contacts["near"]) or bool(contacts["far"]),
			"A walking pose must always report at least one grounded foot.",
			errors
		)
		walker.step_motion(cycle / 120.0)

	walker.set_deterministic_test_mode(true, TEST_SEED)
	walker.set_reduced_motion(false)
	walker.play_motion(&"walk", true)
	for frame: int in range(int(48.0 * cycle * SAMPLE_FPS)):
		walker.step_motion(1.0 / float(SAMPLE_FPS))
	walker.set_reduced_motion(true)
	walker.reset_pose()
	_expect(
		_pose_matches(walker, bones, authored_rest),
		"Repeated walk cycles and resets must not accumulate transform drift.",
		errors
	)


func _validate_phase_opposition(
	quarter: Dictionary,
	three_quarter: Dictionary,
	authored_rest: Dictionary,
	errors: PackedStringArray
) -> void:
	var rest_bones: Dictionary = authored_rest["bones"]
	var q1: Dictionary = quarter["rotations"]
	var q3: Dictionary = three_quarter["rotations"]
	var near_q1 := _rotation_delta(q1, rest_bones, &"LegNearUpperBone")
	var far_q1 := _rotation_delta(q1, rest_bones, &"LegFarUpperBone")
	var near_q3 := _rotation_delta(q3, rest_bones, &"LegNearUpperBone")
	var far_q3 := _rotation_delta(q3, rest_bones, &"LegFarUpperBone")
	_expect(near_q1 * far_q1 < 0.0, "Near and far legs must oppose at quarter cycle.", errors)
	_expect(near_q3 * far_q3 < 0.0, "Near and far legs must oppose at three-quarter cycle.", errors)
	_expect(is_equal_approx(near_q1, -far_q1), "Near/far leg amplitudes must be half-cycle opposites.", errors)
	_expect(is_equal_approx(near_q3, -far_q3), "Near/far leg amplitudes must remain opposed after half a cycle.", errors)
	_expect(is_equal_approx(near_q1, -near_q3), "Near leg must reverse after half a cycle.", errors)
	_expect(is_equal_approx(far_q1, -far_q3), "Far leg must reverse after half a cycle.", errors)
	var near_arm_q1 := _rotation_delta(q1, rest_bones, &"ArmNearUpperBone")
	var far_arm_q1 := _rotation_delta(q1, rest_bones, &"ArmFarUpperBone")
	_expect(near_arm_q1 * near_q1 < 0.0, "Near arm must oppose the near leg.", errors)
	_expect(far_arm_q1 * far_q1 < 0.0, "Far arm must oppose the far leg.", errors)


func _validate_determinism(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D],
	authored_rest: Dictionary,
	errors: PackedStringArray
) -> void:
	var first := _seeded_random_sequence(walker, TEST_SEED, 12)
	var repeated := _seeded_random_sequence(walker, TEST_SEED, 12)
	_expect(first == repeated, "The same seed must reproduce the same random motion sequence.", errors)
	_expect(first.size() == 12, "Seeded random sampling must return every requested motion.", errors)

	walker.set_reduced_motion(true)
	walker.reset_pose()
	var baseline := _capture_pose(walker, bones)
	walker.reset_pose()
	_expect(_pose_matches(walker, bones, baseline), "Repeated reset_pose() calls must be stable.", errors)
	_expect(_pose_matches(walker, bones, authored_rest), "Deterministic reset must return to authored rest.", errors)


func _validate_facing(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D],
	errors: PackedStringArray
) -> void:
	walker.set_reduced_motion(true)
	walker.reset_pose()
	walker.set_facing(1.0)
	var facing_root := walker.get_node("FacingRoot") as Node2D
	var right_pose := _capture_bone_pose(bones)
	var right_scale := facing_root.scale
	walker.set_facing(-1.0)
	_expect(walker.get_facing_direction() == -1.0, "Negative facing input must face left.", errors)
	_expect(facing_root.scale.x < 0.0, "Facing left must mirror FacingRoot on X.", errors)
	_expect(is_equal_approx(absf(facing_root.scale.x), absf(right_scale.x)), "Facing mirror must preserve absolute X scale.", errors)
	_expect(is_equal_approx(facing_root.scale.y, right_scale.y), "Facing mirror must preserve Y scale.", errors)
	_expect(_bone_pose_matches(bones, right_pose), "Facing changes must not rewrite local bone transforms.", errors)
	walker.set_facing(0.0)
	_expect(walker.get_facing_direction() == -1.0, "Zero facing input must preserve the current direction.", errors)
	walker.set_facing(1.0)
	_expect(walker.get_facing_direction() == 1.0 and facing_root.scale.x > 0.0, "Positive facing input must restore right-facing art.", errors)


func _validate_traversal_and_patrol(
	walker: BentosaurFullBodyWalker,
	errors: PackedStringArray
) -> void:
	walker.set_deterministic_test_mode(true, TEST_SEED)
	walker.set_reduced_motion(false)
	walker.set_auto_mode(false)
	walker.patrol_enabled = false
	walker.position = Vector2.ZERO
	walker.set_locomotion(1.0, 40.0)
	walker.step_motion(1.5)
	_expect(is_equal_approx(walker.position.x, 60.0), "Right traversal must honor speed × time.", errors)
	_expect(walker.get_facing_direction() == 1.0, "Right traversal must face right.", errors)
	walker.set_locomotion(-1.0, 20.0)
	walker.step_motion(1.0)
	_expect(is_equal_approx(walker.position.x, 40.0), "Left traversal must honor speed × time.", errors)
	_expect(walker.get_facing_direction() == -1.0, "Left traversal must face left.", errors)
	walker.stop_locomotion()
	_expect(walker.get_motion_state() == &"idle", "Stopping traversal must return to idle.", errors)

	walker.patrol_enabled = true
	walker.patrol_min_x = -10.0
	walker.patrol_max_x = 10.0
	walker.position.x = 9.0
	walker.set_locomotion(1.0, 40.0)
	walker.step_motion(0.10)
	_expect(is_equal_approx(walker.position.x, 10.0), "Upper patrol crossing must clamp to patrol_max_x.", errors)
	_expect(walker.get_facing_direction() == -1.0, "Upper patrol crossing must reverse facing.", errors)
	walker.step_motion(0.25)
	_expect(walker.position.x >= -10.0 and walker.position.x <= 10.0, "Reversed patrol must remain in bounds.", errors)
	walker.position.x = -9.0
	walker.set_locomotion(-1.0, 40.0)
	walker.step_motion(0.10)
	_expect(is_equal_approx(walker.position.x, -10.0), "Lower patrol crossing must clamp to patrol_min_x.", errors)
	_expect(walker.get_facing_direction() == 1.0, "Lower patrol crossing must reverse facing.", errors)
	walker.patrol_enabled = false
	walker.stop_locomotion()


func _validate_reduced_motion(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D],
	authored_rest: Dictionary,
	errors: PackedStringArray
) -> void:
	walker.set_deterministic_test_mode(true, TEST_SEED)
	walker.set_reduced_motion(false)
	walker.set_auto_mode(true)
	walker.position = Vector2(21.0, 8.0)
	walker.set_locomotion(1.0, 35.0)
	walker.step_motion(0.33)
	var settled_position := walker.position
	walker.set_reduced_motion(true)
	_expect(walker.is_reduced_motion(), "Reduced-motion state must be observable.", errors)
	_expect(walker.get_motion_state() == &"idle", "Reduced motion must settle the walker to idle.", errors)
	_expect(_pose_matches(walker, bones, authored_rest, false), "Reduced motion must restore the authored bone pose.", errors)
	walker.step_motion(8.0)
	_expect(walker.position.is_equal_approx(settled_position), "Reduced motion must stop decorative traversal.", errors)
	_expect(walker.get_motion_state() == &"idle", "Reduced motion must suppress automatic random motions.", errors)
	_expect(_pose_matches(walker, bones, authored_rest, false), "Reduced motion must remain visually stable.", errors)
	walker.set_auto_mode(false)
	walker.set_reduced_motion(false)
	walker.reset_pose()
	_expect(not walker.is_reduced_motion(), "Normal motion must be restorable after the reduced-motion gate.", errors)


func _seeded_random_sequence(
	walker: BentosaurFullBodyWalker,
	seed_value: int,
	count: int
) -> PackedStringArray:
	walker.set_auto_mode(false)
	walker.set_reduced_motion(false)
	walker.set_deterministic_test_mode(true, seed_value)
	var result := PackedStringArray()
	for index: int in range(count):
		result.append(String(walker.trigger_random_motion()))
	return result


func _capture_pose(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D]
) -> Dictionary:
	return {
		"bones": _capture_bone_pose(bones),
		"visual_position": walker.visual_root.position,
		"visual_scale": walker.visual_root.scale,
	}


func _capture_bone_pose(bones: Array[Bone2D]) -> Dictionary:
	var result := {}
	for bone: Bone2D in bones:
		result[StringName(bone.name)] = {
			"position": bone.position,
			"rotation": bone.rotation,
			"scale": bone.scale,
		}
	return result


func _pose_matches(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D],
	expected: Dictionary,
	include_visual := true
) -> bool:
	if include_visual:
		if not walker.visual_root.position.is_equal_approx(expected["visual_position"] as Vector2):
			return false
		if not walker.visual_root.scale.is_equal_approx(expected["visual_scale"] as Vector2):
			return false
	return _bone_pose_matches(bones, expected["bones"])


func _bone_pose_matches(bones: Array[Bone2D], expected: Dictionary) -> bool:
	for bone: Bone2D in bones:
		var baseline: Dictionary = expected[StringName(bone.name)]
		if bone.position.distance_to(baseline["position"] as Vector2) > TRANSFORM_EPSILON:
			return false
		if absf(wrapf(bone.rotation - float(baseline["rotation"]), -PI, PI)) > TRANSFORM_EPSILON:
			return false
		if bone.scale.distance_to(baseline["scale"] as Vector2) > TRANSFORM_EPSILON:
			return false
	return true


func _pose_difference_score(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D],
	rest: Dictionary
) -> float:
	var score := walker.visual_root.position.distance_to(rest["visual_position"] as Vector2)
	var rest_bones: Dictionary = rest["bones"]
	for bone: Bone2D in bones:
		var baseline: Dictionary = rest_bones[StringName(bone.name)]
		score += bone.position.distance_to(baseline["position"] as Vector2)
		score += absf(wrapf(bone.rotation - float(baseline["rotation"]), -PI, PI)) * 20.0
		score += bone.scale.distance_to(baseline["scale"] as Vector2) * 20.0
	return score


func _validate_pose_bounds(
	walker: BentosaurFullBodyWalker,
	bones: Array[Bone2D],
	rest: Dictionary,
	motion: StringName,
	errors: PackedStringArray
) -> void:
	var rest_bones: Dictionary = rest["bones"]
	_expect(_vector_is_finite(walker.visual_root.position), "%s produced non-finite visual position." % motion, errors)
	_expect(
		walker.visual_root.position.distance_to(rest["visual_position"] as Vector2) <= 49.0,
		"%s exceeded the 49 px visual-root travel budget." % motion,
		errors
	)
	for bone: Bone2D in bones:
		var baseline: Dictionary = rest_bones[StringName(bone.name)]
		var rotation_delta := absf(wrapf(bone.rotation - float(baseline["rotation"]), -PI, PI))
		_expect(_vector_is_finite(bone.position) and _vector_is_finite(bone.scale) and is_finite(bone.rotation), "%s produced a non-finite %s transform." % [motion, bone.name], errors)
		_expect(
			bone.position.distance_to(baseline["position"] as Vector2) <= 6.1,
			"%s moved %s beyond the 6.1 px joint budget." % [motion, bone.name],
			errors
		)
		_expect(
			rotation_delta <= deg_to_rad(60.1),
			"%s rotated %s beyond the 60.1 degree budget." % [motion, bone.name],
			errors
		)
		var baseline_scale := baseline["scale"] as Vector2
		var ratio_x := bone.scale.x / baseline_scale.x
		var ratio_y := bone.scale.y / baseline_scale.y
		_expect(
			ratio_x >= 0.97 and ratio_x <= 1.03 and ratio_y >= 0.97 and ratio_y <= 1.03,
			"%s scaled %s beyond the 0.97–1.03 budget." % [motion, bone.name],
			errors
		)


func _rotation_delta(
	rotations: Dictionary,
	rest_bones: Dictionary,
	bone_name: StringName
) -> float:
	var baseline: Dictionary = rest_bones[bone_name]
	return wrapf(float(rotations[bone_name]) - float(baseline["rotation"]), -PI, PI)


func _snapshots_match(a: Dictionary, b: Dictionary) -> bool:
	if absf(float(a["phase"]) - float(b["phase"])) > TRANSFORM_EPSILON:
		return false
	var rotations_a: Dictionary = a["rotations"]
	var rotations_b: Dictionary = b["rotations"]
	for bone_name: StringName in rotations_a:
		if absf(wrapf(float(rotations_a[bone_name]) - float(rotations_b[bone_name]), -PI, PI)) > TRANSFORM_EPSILON:
			return false
	return true


func _transform_is_finite(value: Transform2D) -> bool:
	return _vector_is_finite(value.x) and _vector_is_finite(value.y) and _vector_is_finite(value.origin)


func _vector_is_finite(value: Vector2) -> bool:
	return is_finite(value.x) and is_finite(value.y)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition and errors.find(message) == -1:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Bentosaur full-body walker contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
