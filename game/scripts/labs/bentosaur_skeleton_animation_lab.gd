class_name BentosaurSkeletonAnimationLab
extends Node2D

signal gesture_started(gesture: StringName)
signal gesture_finished(gesture: StringName)
signal blink_started(blink_number: int)

const ASSET_ROOT := (
	"res://assets/characters/bentosaur_proprietor/skeleton_lab_v001/"
)
const HEAD_NEUTRAL_PATH := ASSET_ROOT + "proprietor_head_neutral_v001.png"
const HEAD_BLINK_PATH := ASSET_ROOT + "proprietor_head_blink_v001.png"
const TORSO_PATH := ASSET_ROOT + "proprietor_torso_central_v001.png"
const ARM_LEFT_PATH := ASSET_ROOT + "proprietor_arm_hand_screen_left_v001.png"
const ARM_RIGHT_PATH := ASSET_ROOT + "proprietor_arm_hand_screen_right_v001.png"
const MOUTH_OPEN_PATH := ASSET_ROOT + "mouth_open.png"
const MOUTH_CHEW_A_PATH := ASSET_ROOT + "mouth_chew_a.png"
const MOUTH_CHEW_B_PATH := ASSET_ROOT + "mouth_chew_b.png"

const REGISTERED_ART_SIZE := Vector2(865.0, 1024.0)
const REGISTERED_ART_CENTER := REGISTERED_ART_SIZE * 0.5
const DETERMINISTIC_SEED := 84_271

const GESTURE_IDLE := &"idle"
const GESTURE_NOD := &"nod"
const GESTURE_LOOK := &"look"
const GESTURE_HANDS := &"hands"
const GESTURE_CHEW := &"chew"
const GESTURE_DELIGHT := &"delight"
const SUPPORTED_GESTURES: Array[StringName] = [
	GESTURE_NOD,
	GESTURE_LOOK,
	GESTURE_HANDS,
	GESTURE_CHEW,
	GESTURE_DELIGHT,
]

const BREATH_PERIOD_SECONDS := 3.7
const BREATH_SCALE_Y := 0.008
const BREATH_SCALE_X := 0.0035
const BLINK_SECONDS := 0.13
const DOUBLE_BLINK_GAP_SECONDS := 0.11
const BLINK_INTERVAL_MIN_SECONDS := 2.1
const BLINK_INTERVAL_MAX_SECONDS := 5.2
const DOUBLE_BLINK_CHANCE := 0.14
const AUTO_GESTURE_MIN_SECONDS := 4.2
const AUTO_GESTURE_MAX_SECONDS := 7.8
const MAX_STATE_TRANSITIONS_PER_STEP := 16

enum BlinkState {
	OPEN,
	CLOSED,
	DOUBLE_BLINK_GAP,
}

@export var auto_mode_on_ready := true
@export var show_bones_on_ready := false
@export var reduced_motion_on_ready := false
@export var motion_seed := -1

@onready var guest_puppet: Node2D = $CharacterStage/GuestPuppet
@onready var skeleton: Skeleton2D = (
	$CharacterStage/GuestPuppet/Skeleton2D
)
@onready var torso_bone: Bone2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone
)
@onready var head_bone: Bone2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/HeadBone
)
@onready var left_arm_bone: Bone2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/LeftArmBone
)
@onready var right_arm_bone: Bone2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/RightArmBone
)

@onready var torso_sprite: Sprite2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/TorsoSprite
)
@onready var head_neutral_sprite: Sprite2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/HeadBone/HeadNeutral
)
@onready var head_blink_sprite: Sprite2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/HeadBone/HeadBlink
)
@onready var mouth_open_sprite: Sprite2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/HeadBone/MouthOpen
)
@onready var mouth_chew_a_sprite: Sprite2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/HeadBone/MouthChewA
)
@onready var mouth_chew_b_sprite: Sprite2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/HeadBone/MouthChewB
)
@onready var left_arm_sprite: Sprite2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/LeftArmBone/LeftArmSprite
)
@onready var right_arm_sprite: Sprite2D = (
	$CharacterStage/GuestPuppet/Skeleton2D/TorsoBone/RightArmBone/RightArmSprite
)

@onready var debug_overlay: Node2D = $CharacterStage/SkeletonDebugOverlay
@onready var current_state_label: Label = (
	$Interface/SafeArea/Layout/StatusPanel/StatusMargin/StatusRows/CurrentStateLabel
)
@onready var asset_state_label: Label = (
	$Interface/SafeArea/Layout/StatusPanel/StatusMargin/StatusRows/AssetStateLabel
)
@onready var bones_toggle: CheckButton = (
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/SystemRow/BonesToggle
)
@onready var auto_toggle: CheckButton = (
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/SystemRow/AutoToggle
)
@onready var reduced_motion_toggle: CheckButton = (
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/SystemRow/ReducedMotionToggle
)

var _rng := RandomNumberGenerator.new()
var _auto_mode := true
var _show_bones := false
var _reduced_motion := false
var _deterministic_test_mode := false
var _active_seed := DETERMINISTIC_SEED
var _elapsed_seconds := 0.0
var _next_auto_gesture_at := INF
var _current_gesture := GESTURE_IDLE
var _previous_gesture := GESTURE_IDLE
var _gesture_elapsed_seconds := 0.0
var _gesture_duration_seconds := 0.0
var _look_direction := 1.0

var _blink_state := BlinkState.OPEN
var _next_blink_transition_at := INF
var _double_blink_pending := false
var _blink_count := 0

var _torso_base_position := Vector2.ZERO
var _torso_base_rotation := 0.0
var _torso_base_scale := Vector2.ONE
var _head_base_position := Vector2.ZERO
var _head_base_rotation := 0.0
var _head_base_scale := Vector2.ONE
var _left_arm_base_position := Vector2.ZERO
var _left_arm_base_rotation := 0.0
var _left_arm_base_scale := Vector2.ONE
var _right_arm_base_position := Vector2.ZERO
var _right_arm_base_rotation := 0.0
var _right_arm_base_scale := Vector2.ONE


func _ready() -> void:
	_cache_rest_pose()
	var missing_required := _load_character_layers()
	_connect_controls()
	var user_args := OS.get_cmdline_user_args()
	var deterministic_capture := user_args.has("--deterministic-capture")
	_auto_mode = auto_mode_on_ready
	_show_bones = show_bones_on_ready or user_args.has("--show-bones")
	_reduced_motion = (
		reduced_motion_on_ready or user_args.has("--reduced-motion")
	)
	bones_toggle.set_pressed_no_signal(_show_bones)
	auto_toggle.set_pressed_no_signal(_auto_mode)
	reduced_motion_toggle.set_pressed_no_signal(_reduced_motion)
	debug_overlay.visible = _show_bones
	asset_state_label.text = _asset_status_text(missing_required)
	asset_state_label.modulate = (
		Color(0.96, 0.72, 0.34)
		if missing_required.is_empty()
		else Color(1.0, 0.48, 0.40)
	)
	_reset_timeline(DETERMINISTIC_SEED if deterministic_capture else motion_seed)
	_apply_pose()


func _process(delta: float) -> void:
	step_motion(delta)


func step_motion(delta: float) -> void:
	var safe_delta := maxf(delta, 0.0)
	_elapsed_seconds += safe_delta
	_advance_blink_state()

	if _current_gesture != GESTURE_IDLE:
		_gesture_elapsed_seconds += safe_delta
		if _gesture_elapsed_seconds >= _gesture_duration_seconds:
			_finish_current_gesture()
	elif (
		_auto_mode
		and not _reduced_motion
		and _elapsed_seconds >= _next_auto_gesture_at
	):
		trigger_random_gesture()

	_apply_pose()
	_update_status_label()


func trigger_gesture(gesture: StringName) -> bool:
	var normalized := StringName(String(gesture).to_lower())
	if normalized == GESTURE_IDLE:
		reset_pose()
		return true
	if normalized not in SUPPORTED_GESTURES:
		return false

	if _current_gesture != GESTURE_IDLE:
		gesture_finished.emit(_current_gesture)
	_previous_gesture = _current_gesture
	_current_gesture = normalized
	_gesture_elapsed_seconds = 0.0
	_gesture_duration_seconds = _gesture_duration(normalized)
	if normalized == GESTURE_LOOK:
		_look_direction = -1.0 if _rng.randf() < 0.5 else 1.0
	gesture_started.emit(normalized)
	_apply_pose()
	_update_status_label()
	return true


func trigger_random_gesture() -> StringName:
	var choices := SUPPORTED_GESTURES.duplicate()
	if choices.size() > 1:
		choices.erase(_previous_gesture)
		choices.erase(_current_gesture)
	if choices.is_empty():
		choices = SUPPORTED_GESTURES.duplicate()
	var selected: StringName = choices[_rng.randi_range(0, choices.size() - 1)]
	trigger_gesture(selected)
	return selected


func reset_pose() -> void:
	if _current_gesture != GESTURE_IDLE:
		gesture_finished.emit(_current_gesture)
	_current_gesture = GESTURE_IDLE
	_gesture_elapsed_seconds = 0.0
	_gesture_duration_seconds = 0.0
	_blink_state = BlinkState.OPEN
	_double_blink_pending = false
	_next_blink_transition_at = _elapsed_seconds + _random_blink_interval()
	_schedule_next_auto_gesture()
	_apply_pose()
	_update_status_label()


func set_auto_mode(enabled: bool) -> void:
	_auto_mode = enabled
	if is_instance_valid(auto_toggle):
		auto_toggle.set_pressed_no_signal(enabled)
	_schedule_next_auto_gesture()
	_update_status_label()


func is_auto_mode() -> bool:
	return _auto_mode


func set_show_bones(enabled: bool) -> void:
	_show_bones = enabled
	if is_instance_valid(debug_overlay):
		debug_overlay.visible = enabled
	if is_instance_valid(bones_toggle):
		bones_toggle.set_pressed_no_signal(enabled)


func is_showing_bones() -> bool:
	return _show_bones


func set_reduced_motion(enabled: bool) -> void:
	_reduced_motion = enabled
	if is_instance_valid(reduced_motion_toggle):
		reduced_motion_toggle.set_pressed_no_signal(enabled)
	if enabled and _current_gesture != GESTURE_IDLE:
		_finish_current_gesture()
	_schedule_next_auto_gesture()
	_apply_pose()
	_update_status_label()


func is_reduced_motion() -> bool:
	return _reduced_motion


func set_deterministic_test_mode(
	enabled: bool,
	seed: int = DETERMINISTIC_SEED
) -> void:
	_deterministic_test_mode = enabled
	set_process(not enabled)
	_reset_timeline(seed if enabled else motion_seed)
	_apply_pose()
	_update_status_label()


func get_current_gesture() -> StringName:
	return _current_gesture


func get_elapsed_seconds() -> float:
	return _elapsed_seconds


func get_blink_count() -> int:
	return _blink_count


func is_blinking() -> bool:
	return _blink_state == BlinkState.CLOSED


func get_pose_snapshot() -> Dictionary:
	return {
		"gesture": _current_gesture,
		"torso_position": torso_bone.position,
		"torso_rotation": torso_bone.rotation,
		"torso_scale": torso_bone.scale,
		"head_position": head_bone.position,
		"head_rotation": head_bone.rotation,
		"left_arm_rotation": left_arm_bone.rotation,
		"right_arm_rotation": right_arm_bone.rotation,
		"blink_count": _blink_count,
		"blinking": is_blinking(),
	}


func _cache_rest_pose() -> void:
	_torso_base_position = torso_bone.position
	_torso_base_rotation = torso_bone.rotation
	_torso_base_scale = torso_bone.scale
	_head_base_position = head_bone.position
	_head_base_rotation = head_bone.rotation
	_head_base_scale = head_bone.scale
	_left_arm_base_position = left_arm_bone.position
	_left_arm_base_rotation = left_arm_bone.rotation
	_left_arm_base_scale = left_arm_bone.scale
	_right_arm_base_position = right_arm_bone.position
	_right_arm_base_rotation = right_arm_bone.rotation
	_right_arm_base_scale = right_arm_bone.scale


func _load_character_layers() -> PackedStringArray:
	var missing_required := PackedStringArray()
	_load_layer(head_neutral_sprite, HEAD_NEUTRAL_PATH, true, missing_required)
	_load_layer(head_blink_sprite, HEAD_BLINK_PATH, true, missing_required)
	_load_layer(torso_sprite, TORSO_PATH, true, missing_required)
	_load_layer(left_arm_sprite, ARM_LEFT_PATH, true, missing_required)
	_load_layer(right_arm_sprite, ARM_RIGHT_PATH, true, missing_required)
	_load_layer(mouth_open_sprite, MOUTH_OPEN_PATH, false, missing_required)
	_load_layer(mouth_chew_a_sprite, MOUTH_CHEW_A_PATH, false, missing_required)
	_load_layer(mouth_chew_b_sprite, MOUTH_CHEW_B_PATH, false, missing_required)
	return missing_required


func _load_layer(
	sprite: Sprite2D,
	path: String,
	required: bool,
	missing_required: PackedStringArray
) -> void:
	if not ResourceLoader.exists(path):
		if required:
			missing_required.append(path.get_file())
		return
	var texture := load(path) as Texture2D
	if texture == null:
		if required:
			missing_required.append(path.get_file())
		return
	sprite.texture = texture


func _connect_controls() -> void:
	bones_toggle.toggled.connect(set_show_bones)
	auto_toggle.toggled.connect(set_auto_mode)
	reduced_motion_toggle.toggled.connect(set_reduced_motion)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/SystemRow/ResetButton.pressed.connect(
		reset_pose
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/GestureRowOne/NodButton.pressed.connect(
		func() -> void: trigger_gesture(GESTURE_NOD)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/GestureRowOne/LookButton.pressed.connect(
		func() -> void: trigger_gesture(GESTURE_LOOK)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/GestureRowOne/HandsButton.pressed.connect(
		func() -> void: trigger_gesture(GESTURE_HANDS)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/GestureRowTwo/ChewButton.pressed.connect(
		func() -> void: trigger_gesture(GESTURE_CHEW)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/GestureRowTwo/DelightButton.pressed.connect(
		func() -> void: trigger_gesture(GESTURE_DELIGHT)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/ControlRows/GestureRowTwo/RandomButton.pressed.connect(
		trigger_random_gesture
	)


func _reset_timeline(seed: int) -> void:
	_active_seed = seed
	if seed >= 0:
		_rng.seed = seed
	else:
		_rng.randomize()
		_active_seed = int(_rng.seed)
	_elapsed_seconds = 0.0
	_current_gesture = GESTURE_IDLE
	_previous_gesture = GESTURE_IDLE
	_gesture_elapsed_seconds = 0.0
	_gesture_duration_seconds = 0.0
	_blink_state = BlinkState.OPEN
	_double_blink_pending = false
	_blink_count = 0
	_next_blink_transition_at = _random_blink_interval()
	_schedule_next_auto_gesture()


func _advance_blink_state() -> void:
	var transition_count := 0
	while (
		_elapsed_seconds >= _next_blink_transition_at
		and transition_count < MAX_STATE_TRANSITIONS_PER_STEP
	):
		transition_count += 1
		match _blink_state:
			BlinkState.OPEN:
				_blink_state = BlinkState.CLOSED
				_double_blink_pending = _rng.randf() < DOUBLE_BLINK_CHANCE
				_blink_count += 1
				blink_started.emit(_blink_count)
				_next_blink_transition_at += BLINK_SECONDS
			BlinkState.CLOSED:
				if _double_blink_pending:
					_blink_state = BlinkState.DOUBLE_BLINK_GAP
					_double_blink_pending = false
					_next_blink_transition_at += DOUBLE_BLINK_GAP_SECONDS
				else:
					_blink_state = BlinkState.OPEN
					_next_blink_transition_at += _random_blink_interval()
			BlinkState.DOUBLE_BLINK_GAP:
				_blink_state = BlinkState.CLOSED
				_blink_count += 1
				blink_started.emit(_blink_count)
				_next_blink_transition_at += BLINK_SECONDS


func _finish_current_gesture() -> void:
	var finished := _current_gesture
	_previous_gesture = finished
	_current_gesture = GESTURE_IDLE
	_gesture_elapsed_seconds = 0.0
	_gesture_duration_seconds = 0.0
	_schedule_next_auto_gesture()
	gesture_finished.emit(finished)


func _schedule_next_auto_gesture() -> void:
	if not _auto_mode or _reduced_motion:
		_next_auto_gesture_at = INF
		return
	_next_auto_gesture_at = _elapsed_seconds + _rng.randf_range(
		AUTO_GESTURE_MIN_SECONDS,
		AUTO_GESTURE_MAX_SECONDS
	)


func _random_blink_interval() -> float:
	return _rng.randf_range(
		BLINK_INTERVAL_MIN_SECONDS,
		BLINK_INTERVAL_MAX_SECONDS
	)


func _gesture_duration(gesture: StringName) -> float:
	match gesture:
		GESTURE_NOD:
			return 1.35
		GESTURE_LOOK:
			return 1.75
		GESTURE_HANDS:
			return 1.55
		GESTURE_CHEW:
			return 2.25
		GESTURE_DELIGHT:
			return 1.85
	return 0.0


func _apply_pose() -> void:
	_restore_rest_pose()
	_apply_expression_layers()
	if _reduced_motion:
		return

	var breath_phase := _elapsed_seconds * TAU / BREATH_PERIOD_SECONDS
	var breath := (sin(breath_phase) + 1.0) * 0.5
	torso_bone.scale = _torso_base_scale * Vector2(
		1.0 - breath * BREATH_SCALE_X,
		1.0 + breath * BREATH_SCALE_Y
	)
	torso_bone.position.y = _torso_base_position.y - breath * 1.8
	head_bone.position.y = _head_base_position.y - breath * 1.25
	left_arm_bone.rotation = _left_arm_base_rotation + deg_to_rad(0.45) * breath
	right_arm_bone.rotation = _right_arm_base_rotation - deg_to_rad(0.45) * breath

	if _current_gesture == GESTURE_IDLE:
		return
	var progress := clampf(
		_gesture_elapsed_seconds / maxf(_gesture_duration_seconds, 0.001),
		0.0,
		1.0
	)
	var envelope := sin(progress * PI)
	match _current_gesture:
		GESTURE_NOD:
			_apply_nod(progress, envelope)
		GESTURE_LOOK:
			_apply_look(progress, envelope)
		GESTURE_HANDS:
			_apply_hands(progress, envelope)
		GESTURE_CHEW:
			_apply_chew(progress, envelope)
		GESTURE_DELIGHT:
			_apply_delight(progress, envelope)


func _restore_rest_pose() -> void:
	torso_bone.position = _torso_base_position
	torso_bone.rotation = _torso_base_rotation
	torso_bone.scale = _torso_base_scale
	head_bone.position = _head_base_position
	head_bone.rotation = _head_base_rotation
	head_bone.scale = _head_base_scale
	left_arm_bone.position = _left_arm_base_position
	left_arm_bone.rotation = _left_arm_base_rotation
	left_arm_bone.scale = _left_arm_base_scale
	right_arm_bone.position = _right_arm_base_position
	right_arm_bone.rotation = _right_arm_base_rotation
	right_arm_bone.scale = _right_arm_base_scale


func _apply_nod(progress: float, envelope: float) -> void:
	var nod_wave := sin(progress * TAU * 2.0) * envelope
	head_bone.rotation += deg_to_rad(6.5) * nod_wave
	head_bone.position.y += 10.0 * maxf(nod_wave, 0.0)


func _apply_look(_progress: float, envelope: float) -> void:
	head_bone.rotation += deg_to_rad(4.4) * _look_direction * envelope
	head_bone.position.x += 9.0 * _look_direction * envelope
	head_bone.scale.x *= 1.0 - 0.018 * envelope


func _apply_hands(progress: float, envelope: float) -> void:
	var settle := _smoothstep(clampf(progress * 3.0, 0.0, 1.0))
	var release := _smoothstep(clampf((1.0 - progress) * 4.0, 0.0, 1.0))
	var lift := minf(settle, release) * envelope
	left_arm_bone.rotation += deg_to_rad(13.0) * lift
	right_arm_bone.rotation -= deg_to_rad(13.0) * lift
	left_arm_bone.position.y -= 8.0 * lift
	right_arm_bone.position.y -= 8.0 * lift
	head_bone.rotation += deg_to_rad(1.5) * sin(progress * TAU) * envelope


func _apply_chew(progress: float, envelope: float) -> void:
	var chew_wave := sin(_gesture_elapsed_seconds * TAU / 0.30)
	head_bone.position.y += 2.6 * chew_wave * envelope
	head_bone.scale.y *= 1.0 - 0.012 * maxf(chew_wave, 0.0) * envelope
	torso_bone.rotation += deg_to_rad(0.55) * chew_wave * envelope
	_apply_chew_frame()


func _apply_delight(progress: float, envelope: float) -> void:
	var lift := _smoothstep(envelope)
	head_bone.position.y -= 14.0 * lift
	head_bone.rotation += deg_to_rad(-3.2) * sin(progress * PI) * lift
	left_arm_bone.rotation += deg_to_rad(24.0) * lift
	right_arm_bone.rotation -= deg_to_rad(24.0) * lift
	torso_bone.position.y -= 8.0 * lift
	var pulse := sin(progress * PI * 3.0) * envelope
	torso_bone.scale *= Vector2(1.0 + 0.012 * pulse, 1.0 - 0.008 * pulse)


func _apply_expression_layers() -> void:
	var blink_texture_available := head_blink_sprite.texture != null
	var blinking := _blink_state == BlinkState.CLOSED and blink_texture_available
	head_neutral_sprite.visible = not blinking
	head_blink_sprite.visible = blinking
	mouth_open_sprite.visible = (
		_current_gesture == GESTURE_DELIGHT
		and mouth_open_sprite.texture != null
	)
	mouth_chew_a_sprite.visible = false
	mouth_chew_b_sprite.visible = false
	if _current_gesture == GESTURE_CHEW:
		_apply_chew_frame()


func _apply_chew_frame() -> void:
	var has_a := mouth_chew_a_sprite.texture != null
	var has_b := mouth_chew_b_sprite.texture != null
	if not has_a and not has_b:
		mouth_open_sprite.visible = mouth_open_sprite.texture != null
		return
	var use_a := int(_gesture_elapsed_seconds / 0.15) % 2 == 0
	mouth_chew_a_sprite.visible = has_a and (use_a or not has_b)
	mouth_chew_b_sprite.visible = has_b and (not use_a or not has_a)


func _update_status_label() -> void:
	if not is_instance_valid(current_state_label):
		return
	var label := String(_current_gesture).capitalize()
	if _current_gesture == GESTURE_IDLE:
		label = "Breathing + listening"
	if _reduced_motion:
		label = "Still pose • reduced motion"
	var auto_suffix := "AUTO" if _auto_mode else "MANUAL"
	current_state_label.text = "NOW  %s  •  %s" % [label, auto_suffix]


func _asset_status_text(missing_required: PackedStringArray) -> String:
	if missing_required.is_empty():
		var optional_count := 0
		for sprite: Sprite2D in [
			mouth_open_sprite,
			mouth_chew_a_sprite,
			mouth_chew_b_sprite,
		]:
			if sprite.texture != null:
				optional_count += 1
		var status := "REAL SKELETON2D • 5 CUTOUTS • BLINK SWAP • BONE CHEW"
		if optional_count > 0:
			status += " • %d MOUTH SWAPS" % optional_count
		return status
	return "MISSING  %s" % " · ".join(missing_required)


func _smoothstep(value: float) -> float:
	var t := clampf(value, 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)
