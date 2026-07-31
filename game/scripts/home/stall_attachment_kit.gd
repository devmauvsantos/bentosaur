class_name StallAttachmentKit
extends Node2D

signal open_stall_requested
signal guestbook_requested
signal decorations_requested
signal pantry_requested
signal settings_requested

const COZY_LIGHT_MOTION := preload("res://scripts/vfx/cozy_light_motion.gd")
const DETERMINISTIC_LIGHT_SEED := 93013

@onready var stockpot: StockpotFixture = $Stockpot
@onready var counter_lantern: CounterOilLanternFixture = $CounterOilLantern
@onready var counter_decor: CounterDecorFixture = $CounterDecor
@onready var rank_fixture: StallRankFixture = $RankFixture
@onready var open_stall_button: StallMenuButton = $OpenStallButton
@onready var guestbook_button: StallMenuButton = $GuestbookButton
@onready var decorations_button: StallMenuButton = $DecorationsButton
@onready var pantry_button: StallMenuButton = $PantryButton
@onready var settings_button: StallSettingsButton = $SettingsButton

var _reduced_motion := false
var _practical_light_motion: RefCounted = COZY_LIGHT_MOTION.new()
var _practical_lights: Array[Node] = []


func _ready() -> void:
	open_stall_button.pressed.connect(open_stall_requested.emit)
	guestbook_button.pressed.connect(guestbook_requested.emit)
	decorations_button.pressed.connect(decorations_requested.emit)
	pantry_button.pressed.connect(pantry_requested.emit)
	settings_button.pressed.connect(settings_requested.emit)

	_practical_lights.assign([
		_get_stage_fixture("StallLanternLeft"),
		_get_stage_fixture("StallLanternRight"),
		counter_lantern,
	])
	var args := OS.get_cmdline_user_args()
	var seed := DETERMINISTIC_LIGHT_SEED if args.has(
		"--deterministic-capture"
	) else -1
	_practical_light_motion.reset(seed, _practical_lights.size())
	set_reduced_motion(args.has("--reduced-motion"))
	_apply_practical_light_motion()


func _process(delta: float) -> void:
	if _reduced_motion:
		return
	_practical_light_motion.advance(maxf(delta, 0.0))
	_apply_practical_light_motion()


func set_reduced_motion(enabled: bool) -> void:
	_reduced_motion = enabled
	stockpot.set_reduced_motion(enabled)
	counter_decor.set_reduced_motion(enabled)
	rank_fixture.set_reduced_motion(enabled)
	open_stall_button.set_reduced_motion(enabled)
	guestbook_button.set_reduced_motion(enabled)
	decorations_button.set_reduced_motion(enabled)
	pantry_button.set_reduced_motion(enabled)
	settings_button.set_reduced_motion(enabled)
	for practical: Node in _practical_lights:
		if practical != null and practical.has_method("set_reduced_motion"):
			practical.call("set_reduced_motion", enabled)
	_apply_practical_light_motion()


func is_reduced_motion() -> bool:
	return _reduced_motion


func set_stockpot_active(enabled: bool) -> void:
	stockpot.set_active(enabled)


func set_counter_lantern_powered(
	enabled: bool,
	immediate: bool = false
) -> void:
	counter_lantern.set_powered(enabled, immediate)


func set_all_practical_lights_powered(
	enabled: bool,
	immediate: bool = false
) -> void:
	for practical: Node in _practical_lights:
		if practical != null and practical.has_method("set_powered"):
			practical.call("set_powered", enabled, immediate)


func set_rank(value: int, animate: bool = true) -> void:
	rank_fixture.set_rank(value, animate)


func _get_stage_fixture(node_name: String) -> Node:
	var stage := get_parent()
	if stage == null:
		return null
	return stage.get_node_or_null(node_name)


func _apply_practical_light_motion() -> void:
	if _practical_lights.is_empty():
		return
	for index: int in range(_practical_lights.size()):
		var practical := _practical_lights[index]
		if practical == null or not practical.has_method("apply_light_motion"):
			continue
		var pulse_level: float = (
			1.0
			if _reduced_motion
			else float(_practical_light_motion.core_level)
		)
		var flick_level: float = 1.0
		if (
			not _reduced_motion
			and index == _practical_light_motion.flick_target_index
		):
			flick_level = float(_practical_light_motion.flick_level)
		practical.call("apply_light_motion", pulse_level, flick_level)
