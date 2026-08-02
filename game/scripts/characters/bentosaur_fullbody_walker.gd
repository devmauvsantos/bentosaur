class_name BentosaurFullBodyWalker
extends Node2D

signal motion_started(motion: StringName)
signal motion_finished(motion: StringName)
signal footstep(side: StringName)
signal landed()

const MOTION_IDLE := &"idle"
const MOTION_WALK := &"walk"
const MOTION_WAVE := &"wave"
const MOTION_LOOK := &"look"
const MOTION_HOP := &"hop"
const SUPPORTED_MOTIONS: Array[StringName] = [
	MOTION_IDLE,
	MOTION_WALK,
	MOTION_WAVE,
	MOTION_LOOK,
	MOTION_HOP,
]

const DETERMINISTIC_SEED := 28_071
const WALK_CYCLE_SECONDS := 0.92
const IDLE_BREATH_SECONDS := 3.6
const AUTO_QUIET_MIN_SECONDS := 1.4
const AUTO_QUIET_MAX_SECONDS := 3.2
const AUTO_WALK_MIN_SECONDS := 3.2
const AUTO_WALK_MAX_SECONDS := 6.4

@export var motion_on_ready: StringName = MOTION_IDLE
@export var auto_mode_on_ready := false
@export var reduced_motion_on_ready := false
@export var show_bones_on_ready := false
@export var motion_seed := -1
@export var locomotion_speed_px_s := 42.0
@export var patrol_enabled := false
@export var patrol_min_x := -240.0
@export var patrol_max_x := 240.0
@export_range(0.5, 1.5, 0.05) var motion_speed_scale := 1.0

@onready var facing_root: Node2D = $FacingRoot
@onready var visual_root: Node2D = $FacingRoot/VisualRoot
@onready var skeleton: Skeleton2D = $FacingRoot/VisualRoot/Skeleton2D
@onready var debug_overlay: Node2D = $FacingRoot/VisualRoot/BoneDebugOverlay

@onready var hip_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone
@onready var torso_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone
@onready var neck_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/NeckBone
@onready var head_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/NeckBone/HeadBone
@onready var arm_far_upper_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone
@onready var arm_far_lower_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmFarUpperBone/ArmFarLowerBone
@onready var arm_near_upper_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone
@onready var arm_near_lower_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TorsoBone/ArmNearUpperBone/ArmNearLowerBone
@onready var leg_far_upper_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone
@onready var leg_far_lower_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/LegFarLowerBone
@onready var foot_far_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/LegFarUpperBone/LegFarLowerBone/FootFarBone
@onready var leg_near_upper_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone
@onready var leg_near_lower_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/LegNearLowerBone
@onready var foot_near_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/LegNearUpperBone/LegNearLowerBone/FootNearBone
@onready var tail_base_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone
@onready var tail_mid_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone
@onready var tail_tip_bone: Bone2D = $FacingRoot/VisualRoot/Skeleton2D/HipBone/TailBaseBone/TailMidBone/TailTipBone

var _rng := RandomNumberGenerator.new()
var _bones: Array[Bone2D] = []
var _rest_pose: Dictionary = {}
var _visual_rest_position := Vector2.ZERO
var _visual_rest_scale := Vector2.ONE
var _current_motion := MOTION_IDLE
var _previous_motion := MOTION_IDLE
var _motion_elapsed := 0.0
var _motion_duration := INF
var _elapsed := 0.0
var _auto_mode := false
var _reduced_motion := false
var _show_bones := false
var _deterministic_test_mode := false
var _next_auto_motion_at := INF
var _locomotion_direction := 0.0
var _facing_direction := 1.0
var _last_contact_side := &""
var _hop_landed_emitted := false


func _ready() -> void:
	_bones = [
		hip_bone,
		torso_bone,
		neck_bone,
		head_bone,
		arm_far_upper_bone,
		arm_far_lower_bone,
		arm_near_upper_bone,
		arm_near_lower_bone,
		leg_far_upper_bone,
		leg_far_lower_bone,
		foot_far_bone,
		leg_near_upper_bone,
		leg_near_lower_bone,
		foot_near_bone,
		tail_base_bone,
		tail_mid_bone,
		tail_tip_bone,
	]
	_cache_rest_pose()
	var args := OS.get_cmdline_user_args()
	_auto_mode = auto_mode_on_ready
	_reduced_motion = reduced_motion_on_ready or args.has("--reduced-motion")
	_show_bones = show_bones_on_ready or args.has("--show-bones")
	debug_overlay.visible = _show_bones
	_reset_rng(DETERMINISTIC_SEED if args.has("--deterministic-capture") else motion_seed)
	play_motion(motion_on_ready, true)
	if _auto_mode:
		_schedule_next_auto_motion(0.4)
	_apply_pose()


func _process(delta: float) -> void:
	step_motion(delta)


func step_motion(delta: float) -> void:
	var safe_delta := maxf(delta, 0.0) * motion_speed_scale
	_elapsed += safe_delta
	_motion_elapsed += safe_delta

	if _reduced_motion:
		_apply_pose()
		return

	if _current_motion == MOTION_WALK and absf(_locomotion_direction) > 0.001:
		position.x += _locomotion_direction * locomotion_speed_px_s * safe_delta
		_apply_patrol_bounds()

	if _motion_elapsed >= _motion_duration:
		_finish_current_motion()

	if _auto_mode and _current_motion == MOTION_IDLE and _elapsed >= _next_auto_motion_at:
		trigger_random_motion()

	_apply_pose()


func play_motion(motion: StringName, restart := false) -> bool:
	var normalized := StringName(String(motion).to_lower())
	if normalized not in SUPPORTED_MOTIONS:
		return false
	if normalized == _current_motion and not restart:
		return true

	if _current_motion != MOTION_IDLE:
		motion_finished.emit(_current_motion)
	_previous_motion = _current_motion
	_current_motion = normalized
	_motion_elapsed = 0.0
	_motion_duration = _duration_for(normalized)
	_hop_landed_emitted = false
	_last_contact_side = &""
	motion_started.emit(normalized)
	_apply_pose()
	return true


func trigger_random_motion() -> StringName:
	var choices: Array[StringName] = [MOTION_WALK, MOTION_WAVE, MOTION_LOOK, MOTION_HOP]
	choices.erase(_previous_motion)
	if choices.is_empty():
		choices = [MOTION_WALK, MOTION_WAVE, MOTION_LOOK, MOTION_HOP]
	var selected: StringName = choices[_rng.randi_range(0, choices.size() - 1)]
	if selected == MOTION_WALK:
		_locomotion_direction = -1.0 if _rng.randf() < 0.5 else 1.0
		set_facing(_locomotion_direction)
	play_motion(selected, true)
	return selected


func set_facing(direction: float) -> void:
	if absf(direction) < 0.001:
		return
	_facing_direction = -1.0 if direction < 0.0 else 1.0
	facing_root.scale.x = absf(facing_root.scale.x) * _facing_direction


func set_locomotion(direction: float, speed_px_s: float = -1.0) -> void:
	_locomotion_direction = clampf(direction, -1.0, 1.0)
	if speed_px_s >= 0.0:
		locomotion_speed_px_s = speed_px_s
	if absf(_locomotion_direction) > 0.001:
		set_facing(_locomotion_direction)
		play_motion(MOTION_WALK, true)
	else:
		play_motion(MOTION_IDLE, true)


func stop_locomotion() -> void:
	_locomotion_direction = 0.0
	play_motion(MOTION_IDLE, true)


func set_auto_mode(enabled: bool) -> void:
	_auto_mode = enabled
	if enabled:
		_schedule_next_auto_motion(0.35)
	else:
		_next_auto_motion_at = INF


func is_auto_mode() -> bool:
	return _auto_mode


func set_reduced_motion(enabled: bool) -> void:
	_reduced_motion = enabled
	if enabled:
		_locomotion_direction = 0.0
		_current_motion = MOTION_IDLE
		_motion_elapsed = 0.0
		_motion_duration = INF
		_next_auto_motion_at = INF
	elif _auto_mode:
		_schedule_next_auto_motion(0.5)
	_apply_pose()


func is_reduced_motion() -> bool:
	return _reduced_motion


func set_show_bones(enabled: bool) -> void:
	_show_bones = enabled
	debug_overlay.visible = enabled


func is_showing_bones() -> bool:
	return _show_bones


func set_deterministic_test_mode(enabled: bool, seed: int = DETERMINISTIC_SEED) -> void:
	_deterministic_test_mode = enabled
	set_process(not enabled)
	_reset_rng(seed if enabled else motion_seed)
	reset_pose()


func reset_pose() -> void:
	_current_motion = MOTION_IDLE
	_previous_motion = MOTION_IDLE
	_motion_elapsed = 0.0
	_motion_duration = INF
	_elapsed = 0.0
	_locomotion_direction = 0.0
	_last_contact_side = &""
	_hop_landed_emitted = false
	if _auto_mode and not _reduced_motion:
		_schedule_next_auto_motion(0.5)
	_apply_pose()


func get_motion_state() -> StringName:
	return _current_motion


func get_walk_phase() -> float:
	return fmod(_motion_elapsed / WALK_CYCLE_SECONDS, 1.0)


func get_facing_direction() -> float:
	return _facing_direction


func get_ground_contacts() -> Dictionary:
	if _current_motion != MOTION_WALK:
		return {"near": true, "far": true}
	var phase := get_walk_phase()
	return {
		"near": phase < 0.12 or phase >= 0.5,
		"far": phase >= 0.0 and phase < 0.62,
	}


func get_pose_snapshot() -> Dictionary:
	var rotations := {}
	for bone in _bones:
		rotations[bone.name] = bone.rotation
	return {
		"motion": _current_motion,
		"phase": get_walk_phase(),
		"position": position,
		"visual_position": visual_root.position,
		"visual_scale": visual_root.scale,
		"facing": _facing_direction,
		"rotations": rotations,
	}


func get_bone_names() -> PackedStringArray:
	var result := PackedStringArray()
	for bone in _bones:
		result.append(String(bone.name))
	return result


func _cache_rest_pose() -> void:
	_visual_rest_position = visual_root.position
	_visual_rest_scale = visual_root.scale
	for bone in _bones:
		_rest_pose[bone] = {
			"position": bone.position,
			"rotation": bone.rotation,
			"scale": bone.scale,
		}


func _restore_rest_pose() -> void:
	visual_root.position = _visual_rest_position
	visual_root.scale = _visual_rest_scale
	for bone in _bones:
		var rest: Dictionary = _rest_pose[bone]
		bone.position = rest["position"]
		bone.rotation = rest["rotation"]
		bone.scale = rest["scale"]


func _apply_pose() -> void:
	_restore_rest_pose()
	if _reduced_motion:
		return

	match _current_motion:
		MOTION_WALK:
			_apply_walk()
		MOTION_WAVE:
			_apply_idle()
			_apply_wave()
		MOTION_LOOK:
			_apply_idle()
			_apply_look()
		MOTION_HOP:
			_apply_hop()
		_:
			_apply_idle()


func _apply_idle() -> void:
	var phase := _elapsed * TAU / IDLE_BREATH_SECONDS
	var breath := (sin(phase) + 1.0) * 0.5
	torso_bone.scale *= Vector2(1.0 - breath * 0.003, 1.0 + breath * 0.008)
	torso_bone.position.y -= breath * 1.7
	neck_bone.position.y -= breath * 1.0
	arm_far_upper_bone.rotation += deg_to_rad(0.8) * breath
	arm_near_upper_bone.rotation -= deg_to_rad(0.8) * breath
	tail_base_bone.rotation += deg_to_rad(1.6) * sin(phase * 0.72)
	tail_mid_bone.rotation += deg_to_rad(1.3) * sin(phase * 0.72 - 0.5)
	tail_tip_bone.rotation += deg_to_rad(1.0) * sin(phase * 0.72 - 0.9)


func _apply_walk() -> void:
	var phase := get_walk_phase() * TAU
	var near_stride := sin(phase)
	var far_stride := sin(phase + PI)
	var near_lift := maxf(0.0, -cos(phase))
	var far_lift := maxf(0.0, -cos(phase + PI))

	hip_bone.position.y -= absf(sin(phase)) * 4.0
	torso_bone.rotation += deg_to_rad(2.2) * sin(phase * 2.0)
	neck_bone.rotation -= deg_to_rad(1.2) * sin(phase * 2.0)
	head_bone.rotation -= deg_to_rad(0.8) * sin(phase * 2.0)

	leg_near_upper_bone.rotation += deg_to_rad(21.0) * near_stride
	leg_far_upper_bone.rotation += deg_to_rad(21.0) * far_stride
	leg_near_lower_bone.rotation += deg_to_rad(25.0) * near_lift
	leg_far_lower_bone.rotation += deg_to_rad(25.0) * far_lift
	foot_near_bone.rotation -= deg_to_rad(10.0) * near_lift
	foot_far_bone.rotation -= deg_to_rad(10.0) * far_lift

	arm_near_upper_bone.rotation -= deg_to_rad(13.0) * near_stride
	arm_far_upper_bone.rotation -= deg_to_rad(13.0) * far_stride
	arm_near_lower_bone.rotation += deg_to_rad(5.0) * near_lift
	arm_far_lower_bone.rotation += deg_to_rad(5.0) * far_lift

	tail_base_bone.rotation += deg_to_rad(4.0) * sin(phase - 0.45)
	tail_mid_bone.rotation += deg_to_rad(4.7) * sin(phase - 0.85)
	tail_tip_bone.rotation += deg_to_rad(5.2) * sin(phase - 1.2)
	_emit_walk_contact(phase)


func _apply_wave() -> void:
	var progress := clampf(_motion_elapsed / maxf(_motion_duration, 0.001), 0.0, 1.0)
	var envelope := sin(progress * PI)
	var wave := sin(progress * TAU * 3.0) * envelope
	arm_near_upper_bone.rotation -= deg_to_rad(54.0) * envelope
	arm_near_lower_bone.rotation -= deg_to_rad(28.0) * envelope
	arm_near_lower_bone.rotation += deg_to_rad(13.0) * wave
	head_bone.rotation += deg_to_rad(3.0) * envelope


func _apply_look() -> void:
	var progress := clampf(_motion_elapsed / maxf(_motion_duration, 0.001), 0.0, 1.0)
	var envelope := sin(progress * PI)
	neck_bone.rotation += deg_to_rad(5.5) * envelope
	head_bone.rotation -= deg_to_rad(2.0) * envelope
	head_bone.position.x += 5.0 * envelope
	tail_tip_bone.rotation -= deg_to_rad(4.0) * envelope


func _apply_hop() -> void:
	var progress := clampf(_motion_elapsed / maxf(_motion_duration, 0.001), 0.0, 1.0)
	var height := 4.0 * 48.0 * progress * (1.0 - progress)
	visual_root.position.y -= height
	var airborne := sin(progress * PI)
	leg_near_upper_bone.rotation -= deg_to_rad(15.0) * airborne
	leg_far_upper_bone.rotation += deg_to_rad(11.0) * airborne
	leg_near_lower_bone.rotation += deg_to_rad(22.0) * airborne
	leg_far_lower_bone.rotation += deg_to_rad(18.0) * airborne
	arm_near_upper_bone.rotation -= deg_to_rad(16.0) * airborne
	arm_far_upper_bone.rotation += deg_to_rad(12.0) * airborne
	tail_base_bone.rotation += deg_to_rad(10.0) * airborne
	if progress >= 0.98 and not _hop_landed_emitted:
		_hop_landed_emitted = true
		landed.emit()


func _emit_walk_contact(phase_radians: float) -> void:
	var normalized := fposmod(phase_radians / TAU, 1.0)
	var side := &"near" if normalized < 0.5 else &"far"
	if side != _last_contact_side:
		_last_contact_side = side
		footstep.emit(side)


func _finish_current_motion() -> void:
	var finished := _current_motion
	if finished != MOTION_IDLE:
		motion_finished.emit(finished)
	_previous_motion = finished
	_current_motion = MOTION_IDLE
	_motion_elapsed = 0.0
	_motion_duration = INF
	_locomotion_direction = 0.0
	if _auto_mode:
		_schedule_next_auto_motion()


func _duration_for(motion: StringName) -> float:
	match motion:
		MOTION_WALK:
			return _rng.randf_range(AUTO_WALK_MIN_SECONDS, AUTO_WALK_MAX_SECONDS) if _auto_mode else INF
		MOTION_WAVE:
			return 1.55
		MOTION_LOOK:
			return 1.75
		MOTION_HOP:
			return 1.05
	return INF


func _schedule_next_auto_motion(delay: float = -1.0) -> void:
	if not _auto_mode or _reduced_motion:
		_next_auto_motion_at = INF
		return
	_next_auto_motion_at = _elapsed + (
		delay if delay >= 0.0 else _rng.randf_range(AUTO_QUIET_MIN_SECONDS, AUTO_QUIET_MAX_SECONDS)
	)


func _apply_patrol_bounds() -> void:
	if not patrol_enabled:
		return
	if position.x > patrol_max_x:
		position.x = patrol_max_x
		_locomotion_direction = -1.0
		set_facing(-1.0)
	elif position.x < patrol_min_x:
		position.x = patrol_min_x
		_locomotion_direction = 1.0
		set_facing(1.0)


func _reset_rng(seed: int) -> void:
	if seed >= 0:
		_rng.seed = seed
	else:
		_rng.randomize()
