extends SceneTree

const LAB_PATH := "res://scenes/labs/bentosaur_skeleton_animation_lab.tscn"
const TEST_SEED := 48_043
const SAMPLE_FPS := 60
const SAMPLE_SECONDS_PER_GESTURE := 2.5
const POSITION_LIMITS := {
	&"TorsoBone": 16.0,
	&"HeadBone": 36.0,
	&"LeftArmBone": 56.0,
	&"RightArmBone": 56.0,
}
const ROTATION_LIMITS_DEGREES := {
	&"TorsoBone": 10.0,
	&"HeadBone": 22.0,
	&"LeftArmBone": 48.0,
	&"RightArmBone": 48.0,
}
const MIN_SCALE_RATIO := 0.84
const MAX_SCALE_RATIO := 1.16
const REDUCED_MOTION_TOLERANCE := 0.001

const REQUIRED_METHODS: Array[StringName] = [
	&"trigger_gesture",
	&"trigger_random_gesture",
	&"reset_pose",
	&"step_motion",
	&"set_auto_mode",
	&"set_show_bones",
	&"set_reduced_motion",
	&"set_deterministic_test_mode",
	&"get_current_gesture",
]

const SUPPORTED_GESTURES: Array[StringName] = [
	&"nod",
	&"look",
	&"hands",
	&"chew",
	&"delight",
]

const REQUIRED_BONE_PATHS: Array[NodePath] = [
	^"CharacterStage/GuestPuppet/Skeleton2D/TorsoBone",
	^"CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/HeadBone",
	^"CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/LeftArmBone",
	^"CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/RightArmBone",
]

const REQUIRED_SPRITE_TEXTURES := {
	^"Skeleton2D/TorsoBone/TorsoSprite": (
		"res://assets/characters/bentosaur_proprietor/skeleton_lab_v001/"
		+ "proprietor_torso_central_v001.png"
	),
	^"Skeleton2D/TorsoBone/HeadBone/HeadNeutral": (
		"res://assets/characters/bentosaur_proprietor/skeleton_lab_v001/"
		+ "proprietor_head_neutral_v001.png"
	),
	^"Skeleton2D/TorsoBone/HeadBone/HeadBlink": (
		"res://assets/characters/bentosaur_proprietor/skeleton_lab_v001/"
		+ "proprietor_head_blink_v001.png"
	),
	^"Skeleton2D/TorsoBone/LeftArmBone/LeftArmSprite": (
		"res://assets/characters/bentosaur_proprietor/skeleton_lab_v001/"
		+ "proprietor_arm_hand_screen_left_v001.png"
	),
	^"Skeleton2D/TorsoBone/RightArmBone/RightArmSprite": (
		"res://assets/characters/bentosaur_proprietor/skeleton_lab_v001/"
		+ "proprietor_arm_hand_screen_right_v001.png"
	),
}


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	_expect(
		ResourceLoader.exists(LAB_PATH),
		"Skeleton animation lab scene is missing.",
		errors
	)
	if not ResourceLoader.exists(LAB_PATH):
		_finish(errors)
		return

	var packed := load(LAB_PATH) as PackedScene
	_expect(packed != null, "Skeleton animation lab must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var lab := packed.instantiate()
	_expect(lab != null, "Skeleton animation lab must instantiate.", errors)
	if lab == null:
		_finish(errors)
		return
	root.add_child(lab)
	for frame: int in range(4):
		await process_frame
	_expect(
		is_instance_valid(lab) and lab.is_inside_tree(),
		"Skeleton animation lab must survive headless frame advancement.",
		errors
	)

	for method_name: StringName in REQUIRED_METHODS:
		_expect(
			lab.has_method(method_name),
			"Lab controller is missing public method %s()." % method_name,
			errors
		)
	if not _has_required_methods(lab):
		lab.queue_free()
		await process_frame
		_finish(errors)
		return

	var skeleton := lab.get_node_or_null(
		"CharacterStage/GuestPuppet/Skeleton2D"
	) as Skeleton2D
	_expect(skeleton != null, "Missing puppet Skeleton2D.", errors)
	var bones: Array[Bone2D] = []
	for bone_path: NodePath in REQUIRED_BONE_PATHS:
		var bone := lab.get_node_or_null(bone_path) as Bone2D
		_expect(
			bone != null,
			"Missing required Bone2D at %s." % bone_path,
			errors
		)
		if bone != null:
			bones.append(bone)
	_expect(
		bones.size() == REQUIRED_BONE_PATHS.size(),
		"The puppet must expose all four stable Bone2D nodes.",
		errors
	)
	if skeleton != null:
		var discovered_bones := skeleton.find_children(
			"*", "Bone2D", true, false
		)
		_expect(
			discovered_bones.size() == REQUIRED_BONE_PATHS.size(),
			"Skeleton2D must contain exactly the documented four-bone lab rig.",
			errors
		)
	if bones.size() != REQUIRED_BONE_PATHS.size():
		lab.queue_free()
		await process_frame
		_finish(errors)
		return

	_validate_bone_parentage(bones, skeleton, errors)
	_validate_puppet_assets(
		lab.get_node_or_null("CharacterStage/GuestPuppet"),
		errors
	)

	lab.call("set_auto_mode", false)
	lab.call("set_show_bones", false)
	lab.call("set_reduced_motion", true)
	lab.call("reset_pose")
	var baseline := _capture_pose(bones)
	lab.call("reset_pose")
	_expect(
		_pose_matches(bones, baseline),
		"Repeated reset_pose() calls must be stable and drift-free.",
		errors
	)
	lab.call("set_reduced_motion", false)

	var seeded_gesture := _seeded_random_gesture(lab, TEST_SEED)
	_expect(
		seeded_gesture != &"",
		"Seeded random trigger must select a named gesture.",
		errors
	)
	var repeated_seeded_gesture := _seeded_random_gesture(lab, TEST_SEED)
	_expect(
		repeated_seeded_gesture == seeded_gesture,
		"The same deterministic seed must select the same random gesture.",
		errors
	)
	if seeded_gesture != &"":
		lab.call("reset_pose")
		lab.call("trigger_gesture", seeded_gesture)
		_expect(
			_current_gesture(lab) == seeded_gesture,
			"trigger_gesture() must accept a gesture returned by the lab itself.",
			errors
		)
		for frame: int in range(6):
			lab.call("step_motion", 1.0 / float(SAMPLE_FPS))
			await process_frame
		_expect(
			is_instance_valid(lab),
			"A manually triggered gesture must advance headlessly.",
			errors
		)
	_expect(
		not bool(lab.call("trigger_gesture", &"not_a_real_gesture")),
		"Unknown gesture names must be rejected without changing the rig.",
		errors
	)

	lab.call("set_reduced_motion", true)
	lab.call("reset_pose")
	_expect(
		_pose_matches(bones, baseline),
		"A gesture must restore the exact authored pose in reduced motion.",
		errors
	)
	lab.call("set_reduced_motion", false)
	var normal_probe := _sample_motion(lab, bones, baseline, false, errors)
	var reduced_probe := _sample_motion(lab, bones, baseline, true, errors)
	_validate_motion_bounds(normal_probe, errors)
	_validate_motion_bounds(reduced_probe, errors)
	_expect(
		float(reduced_probe["score"])
			<= float(normal_probe["score"]) + REDUCED_MOTION_TOLERANCE,
		"Reduced motion must never amplify the skeletal motion envelope.",
		errors
	)
	_expect(
		float(normal_probe["score"]) > 0.0001,
		"The normal animation proof must visibly move at least one Bone2D.",
		errors
	)

	lab.call("set_reduced_motion", true)
	lab.call("reset_pose")
	_expect(
		_pose_matches(bones, baseline),
		"Reduced-motion reset must settle on the same authored baseline.",
		errors
	)
	lab.call("set_auto_mode", true)
	for frame: int in range(8):
		await process_frame
	lab.call("set_auto_mode", false)
	_expect(
		is_instance_valid(lab) and lab.is_inside_tree(),
		"Automatic mode must remain valid while real SceneTree frames advance.",
		errors
	)

	lab.queue_free()
	await process_frame
	_expect(
		not is_instance_valid(lab),
		"Skeleton animation lab must free cleanly after the headless probe.",
		errors
	)
	_finish(errors)


func _has_required_methods(lab: Node) -> bool:
	for method_name: StringName in REQUIRED_METHODS:
		if not lab.has_method(method_name):
			return false
	return true


func _validate_bone_parentage(
	bones: Array[Bone2D],
	skeleton: Skeleton2D,
	errors: PackedStringArray
) -> void:
	var torso := bones[0]
	_expect(
		torso.get_parent() == skeleton,
		"TorsoBone must be the Skeleton2D root bone.",
		errors
	)
	for index: int in range(1, bones.size()):
		_expect(
			bones[index].get_parent() == torso,
			"%s must be a direct child of TorsoBone." % bones[index].name,
			errors
		)


func _validate_puppet_assets(puppet: Node, errors: PackedStringArray) -> void:
	_expect(puppet != null, "Missing GuestPuppet visual root.", errors)
	if puppet == null:
		return
	for relative_path: NodePath in REQUIRED_SPRITE_TEXTURES:
		var sprite := puppet.get_node_or_null(relative_path) as Sprite2D
		_expect(
			sprite != null,
			"Missing required puppet sprite %s." % relative_path,
			errors
		)
		if sprite == null:
			continue
		_expect(
			sprite.texture != null,
			"Required puppet sprite %s has no texture." % relative_path,
			errors
		)
		if sprite.texture == null:
			continue
		var expected_path: String = REQUIRED_SPRITE_TEXTURES[relative_path]
		_expect(
			ResourceLoader.exists(expected_path)
				and sprite.texture.resource_path == expected_path,
			"Puppet sprite %s must use canonical texture %s."
				% [relative_path, expected_path],
			errors
		)

	# Optional face-swap placeholders are allowed to be empty in V001. Any
	# texture that is assigned anywhere in the puppet must still be loadable.
	var sprites: Array[Node] = puppet.find_children("*", "Sprite2D", true, false)
	for sprite_node: Node in sprites:
		var sprite := sprite_node as Sprite2D
		if sprite.texture == null or sprite.texture.resource_path.is_empty():
			continue
		_expect(
			ResourceLoader.exists(sprite.texture.resource_path),
			"Puppet sprite %s references a missing texture." % sprite.get_path(),
			errors
		)


func _seeded_random_gesture(lab: Node, seed_value: int) -> StringName:
	lab.call("reset_pose")
	lab.call("set_deterministic_test_mode", true, seed_value)
	lab.call("trigger_random_gesture")
	return _current_gesture(lab)


func _current_gesture(lab: Node) -> StringName:
	return StringName(str(lab.call("get_current_gesture")))


func _capture_pose(bones: Array[Bone2D]) -> Dictionary:
	var pose := {}
	for bone: Bone2D in bones:
		pose[StringName(bone.name)] = {
			"position": bone.position,
			"rotation": bone.rotation,
			"scale": bone.scale,
		}
	return pose


func _pose_matches(bones: Array[Bone2D], expected_pose: Dictionary) -> bool:
	for bone: Bone2D in bones:
		var expected: Dictionary = expected_pose[StringName(bone.name)]
		if not bone.position.is_equal_approx(expected["position"] as Vector2):
			return false
		if not is_equal_approx(bone.rotation, float(expected["rotation"])):
			return false
		if not bone.scale.is_equal_approx(expected["scale"] as Vector2):
			return false
	return true


func _sample_motion(
	lab: Node,
	bones: Array[Bone2D],
	baseline: Dictionary,
	reduced_motion: bool,
	errors: PackedStringArray
) -> Dictionary:
	var probe := {
		"finite": true,
		"score": 0.0,
		"bones": {},
	}
	for bone: Bone2D in bones:
		probe["bones"][StringName(bone.name)] = {
			"translation": 0.0,
			"rotation": 0.0,
			"minimum_scale_ratio": 1.0,
			"maximum_scale_ratio": 1.0,
		}
	lab.call("set_auto_mode", false)
	lab.call("set_reduced_motion", reduced_motion)
	lab.call("set_deterministic_test_mode", true, TEST_SEED)
	lab.call("reset_pose")
	for gesture_name: StringName in SUPPORTED_GESTURES:
		var accepted := bool(lab.call("trigger_gesture", gesture_name))
		_expect(
			accepted and _current_gesture(lab) == gesture_name,
			"Manual gesture %s must be accepted and reported." % gesture_name,
			errors
		)
		for frame: int in range(
			int(SAMPLE_SECONDS_PER_GESTURE * float(SAMPLE_FPS))
		):
			lab.call("step_motion", 1.0 / float(SAMPLE_FPS))
			_observe_pose(bones, baseline, probe)
		if not reduced_motion:
			lab.call("set_reduced_motion", true)
		lab.call("reset_pose")
		_expect(
			_pose_matches(bones, baseline),
			"Gesture %s left cumulative bone drift after reset." % gesture_name,
			errors
		)
		if not reduced_motion:
			lab.call("set_reduced_motion", false)
	return probe


func _observe_pose(
	bones: Array[Bone2D],
	baseline: Dictionary,
	probe: Dictionary
) -> void:
	for bone: Bone2D in bones:
		var bone_name := StringName(bone.name)
		var expected: Dictionary = baseline[bone_name]
		var result: Dictionary = probe["bones"][bone_name]
		var baseline_position := expected["position"] as Vector2
		var baseline_rotation := float(expected["rotation"])
		var baseline_scale := expected["scale"] as Vector2
		var translation := bone.position.distance_to(baseline_position)
		var rotation := absf(
			wrapf(bone.rotation - baseline_rotation, -PI, PI)
		)
		var scale_x_ratio := _safe_scale_ratio(bone.scale.x, baseline_scale.x)
		var scale_y_ratio := _safe_scale_ratio(bone.scale.y, baseline_scale.y)
		result["translation"] = maxf(float(result["translation"]), translation)
		result["rotation"] = maxf(float(result["rotation"]), rotation)
		result["minimum_scale_ratio"] = minf(
			float(result["minimum_scale_ratio"]),
			minf(scale_x_ratio, scale_y_ratio)
		)
		result["maximum_scale_ratio"] = maxf(
			float(result["maximum_scale_ratio"]),
			maxf(scale_x_ratio, scale_y_ratio)
		)
		probe["score"] = maxf(
			float(probe["score"]),
			translation / 16.0
				+ rotation / deg_to_rad(8.0)
				+ absf(scale_x_ratio - 1.0) * 10.0
				+ absf(scale_y_ratio - 1.0) * 10.0
		)
		if (
			not is_finite(translation)
			or not is_finite(rotation)
			or not is_finite(scale_x_ratio)
			or not is_finite(scale_y_ratio)
		):
			probe["finite"] = false


func _safe_scale_ratio(value: float, baseline: float) -> float:
	if is_zero_approx(baseline):
		return 1.0 if is_zero_approx(value) else INF
	return value / baseline


func _validate_motion_bounds(probe: Dictionary, errors: PackedStringArray) -> void:
	_expect(bool(probe["finite"]), "All sampled bone transforms must be finite.", errors)
	var bone_results: Dictionary = probe["bones"]
	for bone_name: StringName in POSITION_LIMITS:
		var result: Dictionary = bone_results[bone_name]
		_expect(
			float(result["translation"]) <= float(POSITION_LIMITS[bone_name]),
			"%s exceeded its %.1f px translation budget."
				% [bone_name, float(POSITION_LIMITS[bone_name])],
			errors
		)
		_expect(
			rad_to_deg(float(result["rotation"]))
				<= float(ROTATION_LIMITS_DEGREES[bone_name]),
			"%s exceeded its %.1f degree rotation budget."
				% [bone_name, float(ROTATION_LIMITS_DEGREES[bone_name])],
			errors
		)
		_expect(
			float(result["minimum_scale_ratio"]) >= MIN_SCALE_RATIO
				and float(result["maximum_scale_ratio"]) <= MAX_SCALE_RATIO,
			"%s exceeded the %.2f-%.2f scale budget."
				% [bone_name, MIN_SCALE_RATIO, MAX_SCALE_RATIO],
			errors
		)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Bentosaur skeleton animation lab contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
