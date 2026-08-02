class_name BentosaurFullBodyWalkLab
extends Node2D

@onready var main_walker: BentosaurFullBodyWalker = $Stage/MainWalker
@onready var crowd: Array[BentosaurFullBodyWalker] = [
	$Stage/CrowdWalkerA,
	$Stage/CrowdWalkerB,
	$Stage/CrowdWalkerC,
]
@onready var state_label: Label = $Interface/SafeArea/Layout/StatusPanel/StatusMargin/Rows/StateLabel
@onready var bones_toggle: CheckButton = $Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/SystemRow/BonesToggle
@onready var auto_toggle: CheckButton = $Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/SystemRow/AutoToggle
@onready var still_toggle: CheckButton = $Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/SystemRow/StillToggle
@onready var crowd_toggle: CheckButton = $Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/SystemRow/CrowdToggle

var _capture_mode := false
var _capture_elapsed := 0.0
var _capture_step := -1


func _ready() -> void:
	_capture_mode = OS.get_cmdline_user_args().has("--deterministic-capture")
	_connect_controls()
	_setup_crowd()
	main_walker.set_auto_mode(not _capture_mode)
	auto_toggle.set_pressed_no_signal(not _capture_mode)
	if OS.get_cmdline_user_args().has("--show-bones"):
		bones_toggle.set_pressed_no_signal(true)
		main_walker.set_show_bones(true)
	_update_status()


func _process(delta: float) -> void:
	if _capture_mode:
		_capture_elapsed += maxf(delta, 0.0)
		_apply_capture_sequence()
	_update_status()


func _setup_crowd() -> void:
	var directions := [1.0, -1.0, 1.0]
	var speeds := [35.0, 29.0, 40.0]
	for index in crowd.size():
		var walker := crowd[index]
		walker.patrol_enabled = true
		walker.patrol_min_x = 65.0
		walker.patrol_max_x = 655.0
		walker.set_locomotion(directions[index], speeds[index])


func _connect_controls() -> void:
	bones_toggle.toggled.connect(main_walker.set_show_bones)
	auto_toggle.toggled.connect(_on_auto_toggled)
	still_toggle.toggled.connect(_on_still_toggled)
	crowd_toggle.toggled.connect(_on_crowd_toggled)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/SystemRow/ResetButton.pressed.connect(_on_reset)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/MotionRow/IdleButton.pressed.connect(
		func() -> void: _play_main(BentosaurFullBodyWalker.MOTION_IDLE)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/MotionRow/WalkButton.pressed.connect(
		func() -> void: _play_main(BentosaurFullBodyWalker.MOTION_WALK)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/MotionRow/WaveButton.pressed.connect(
		func() -> void: _play_main(BentosaurFullBodyWalker.MOTION_WAVE)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/MotionRowTwo/LookButton.pressed.connect(
		func() -> void: _play_main(BentosaurFullBodyWalker.MOTION_LOOK)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/MotionRowTwo/HopButton.pressed.connect(
		func() -> void: _play_main(BentosaurFullBodyWalker.MOTION_HOP)
	)
	$Interface/SafeArea/Layout/ControlPanel/ControlMargin/Rows/MotionRowTwo/RandomButton.pressed.connect(
		_on_random_pressed
	)


func _play_main(motion: StringName) -> void:
	_capture_mode = false
	main_walker.set_auto_mode(false)
	auto_toggle.set_pressed_no_signal(false)
	main_walker.stop_locomotion()
	main_walker.play_motion(motion, true)


func _on_random_pressed() -> void:
	_capture_mode = false
	main_walker.set_auto_mode(false)
	auto_toggle.set_pressed_no_signal(false)
	main_walker.trigger_random_motion()


func _on_auto_toggled(enabled: bool) -> void:
	_capture_mode = false
	main_walker.set_auto_mode(enabled)
	if enabled and main_walker.get_motion_state() == BentosaurFullBodyWalker.MOTION_IDLE:
		main_walker.trigger_random_motion()


func _on_still_toggled(enabled: bool) -> void:
	main_walker.set_reduced_motion(enabled)
	for walker in crowd:
		walker.set_reduced_motion(enabled)


func _on_crowd_toggled(enabled: bool) -> void:
	for walker in crowd:
		walker.visible = enabled


func _on_reset() -> void:
	_capture_mode = false
	main_walker.reset_pose()
	main_walker.set_auto_mode(false)
	auto_toggle.set_pressed_no_signal(false)
	still_toggle.set_pressed_no_signal(false)
	main_walker.set_reduced_motion(false)


func _apply_capture_sequence() -> void:
	var step := 0
	if _capture_elapsed >= 4.0:
		step = 1
	if _capture_elapsed >= 6.1:
		step = 2
	if _capture_elapsed >= 8.4:
		step = 3
	if _capture_elapsed >= 10.2:
		step = 4
	if step == _capture_step:
		return
	_capture_step = step
	match step:
		0:
			main_walker.play_motion(BentosaurFullBodyWalker.MOTION_WALK, true)
		1:
			main_walker.play_motion(BentosaurFullBodyWalker.MOTION_WAVE, true)
		2:
			main_walker.play_motion(BentosaurFullBodyWalker.MOTION_LOOK, true)
		3:
			main_walker.play_motion(BentosaurFullBodyWalker.MOTION_HOP, true)
		_:
			main_walker.set_auto_mode(true)
			main_walker.trigger_random_motion()


func _update_status() -> void:
	if not is_instance_valid(state_label):
		return
	var state := String(main_walker.get_motion_state()).to_upper()
	var mode := "CAPTURE" if _capture_mode else ("AUTO" if main_walker.is_auto_mode() else "MANUAL")
	state_label.text = "%s  •  %s  •  17 BONES" % [state, mode]
