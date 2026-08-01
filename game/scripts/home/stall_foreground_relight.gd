class_name StallForegroundRelight
extends Node

signal enabled_changed(enabled: bool)

const STALL_NIGHT := Color(0.722, 0.733, 0.749, 1.0)
const PROPRIETOR_NIGHT := Color(0.627, 0.636, 0.651, 1.0)
const PROP_NIGHT := Color(0.741, 0.752, 0.769, 1.0)
const RANK_NIGHT := Color(0.779, 0.790, 0.808, 1.0)
const BUTTON_NIGHT := Color(0.855, 0.868, 0.887, 1.0)
const BUTTON_LABEL_BOOST := Color(1.078, 1.078, 1.078, 1.0)
const LANTERN_SHELL_NIGHT := Color(0.741, 0.752, 0.769, 1.0)
const FOREGROUND_LIGHT_MASK := 2

const RECEIVER_PATHS: Array[NodePath] = [
	NodePath("../StallStructure"),
	NodePath("../MainCharacter"),
	NodePath("../StallAttachmentKit/RankFixture"),
	NodePath("../StallAttachmentKit/Stockpot/ContactShadow"),
	NodePath("../StallAttachmentKit/Stockpot/Body"),
	NodePath("../StallAttachmentKit/Stockpot/LidPivot/Lid"),
	NodePath("../StallAttachmentKit/CounterDecor"),
	NodePath("../StallAttachmentKit/OpenStallButton"),
	NodePath("../StallAttachmentKit/GuestbookButton"),
	NodePath("../StallAttachmentKit/DecorationsButton"),
	NodePath("../StallAttachmentKit/PantryButton"),
	NodePath("../StallAttachmentKit/SettingsButton"),
	NodePath("../StallAttachmentKit/OpenStallButton/VisualRoot/LiveLabel"),
	NodePath("../StallAttachmentKit/GuestbookButton/VisualRoot/LiveLabel"),
	NodePath("../StallAttachmentKit/DecorationsButton/VisualRoot/LiveLabel"),
	NodePath("../StallAttachmentKit/PantryButton/VisualRoot/LiveLabel"),
	NodePath("../StallLanternLeft/Anchor"),
	NodePath("../StallLanternLeft/SwayPivot/BodyOff"),
	NodePath("../StallLanternRight/Anchor"),
	NodePath("../StallLanternRight/SwayPivot/BodyOff"),
	NodePath("../StallAttachmentKit/CounterOilLantern/BodyOff"),
]

const RECEIVER_COLORS: Array[Color] = [
	STALL_NIGHT,
	PROPRIETOR_NIGHT,
	RANK_NIGHT,
	PROP_NIGHT,
	PROP_NIGHT,
	PROP_NIGHT,
	PROP_NIGHT,
	BUTTON_NIGHT,
	BUTTON_NIGHT,
	BUTTON_NIGHT,
	BUTTON_NIGHT,
	BUTTON_NIGHT,
	BUTTON_LABEL_BOOST,
	BUTTON_LABEL_BOOST,
	BUTTON_LABEL_BOOST,
	BUTTON_LABEL_BOOST,
	LANTERN_SHELL_NIGHT,
	LANTERN_SHELL_NIGHT,
	LANTERN_SHELL_NIGHT,
	LANTERN_SHELL_NIGHT,
	LANTERN_SHELL_NIGHT,
]

const LIGHT_RECEIVER_PATHS: Array[NodePath] = [
	NodePath("../StallStructure"),
	NodePath("../MainCharacter/VisualRoot/Neutral"),
	NodePath("../MainCharacter/VisualRoot/Blink"),
	NodePath("../MainCharacter/VisualRoot/ForegroundHands"),
	NodePath("../StallLanternLeft/Anchor"),
	NodePath("../StallLanternLeft/SwayPivot/BodyOff"),
	NodePath("../StallLanternRight/Anchor"),
	NodePath("../StallLanternRight/SwayPivot/BodyOff"),
	NodePath("../StallAttachmentKit/Stockpot/ContactShadow"),
	NodePath("../StallAttachmentKit/Stockpot/Body"),
	NodePath("../StallAttachmentKit/Stockpot/LidPivot/Lid"),
	NodePath("../StallAttachmentKit/CounterOilLantern/ContactShadow"),
	NodePath("../StallAttachmentKit/CounterOilLantern/BodyOff"),
	NodePath("../StallAttachmentKit/CounterDecor/FoodBowl"),
	NodePath("../StallAttachmentKit/CounterDecor/Plant/FoliagePivot/Foliage"),
	NodePath("../StallAttachmentKit/CounterDecor/Plant/Pot"),
	NodePath("../StallAttachmentKit/CounterDecor/BottleCrate/Assembled"),
	NodePath("../StallAttachmentKit/CounterDecor/CounterCloth"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Plaque"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star1/Empty"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star1/Filled"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star1/Shine"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star2/Empty"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star2/Filled"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star2/Shine"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star3/Empty"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star3/Filled"),
	NodePath("../StallAttachmentKit/RankFixture/ContentRoot/Star3/Shine"),
]

const LIGHT_PATHS: Array[NodePath] = [
	NodePath("../ForegroundLights/HangingLeft"),
	NodePath("../ForegroundLights/HangingRight"),
	NodePath("../ForegroundLights/Counter"),
]

@export var enabled_on_ready := true

var _enabled := false
var _receivers: Array[CanvasItem] = []
var _original_receiver_modulates: Array[Color] = []
var _light_receivers: Array[CanvasItem] = []
var _original_light_masks: Array[int] = []
var _lights: Array[PointLight2D] = []


func _ready() -> void:
	_cache_nodes()
	var disabled_by_capture := OS.get_cmdline_user_args().has(
		"--foreground-relight-off"
	)
	set_enabled(enabled_on_ready and not disabled_by_capture)


func set_enabled(enabled: bool) -> void:
	if _receivers.is_empty() or _lights.is_empty():
		_cache_nodes()
	_enabled = enabled
	if enabled:
		for index: int in _light_receivers.size():
			_light_receivers[index].light_mask = FOREGROUND_LIGHT_MASK
		for index: int in _receivers.size():
			_receivers[index].modulate = RECEIVER_COLORS[index]
		for light: PointLight2D in _lights:
			light.enabled = true
	else:
		for light: PointLight2D in _lights:
			light.enabled = false
		for index: int in _receivers.size():
			_receivers[index].modulate = _original_receiver_modulates[index]
		for index: int in _light_receivers.size():
			_light_receivers[index].light_mask = _original_light_masks[index]
	enabled_changed.emit(enabled)


func is_enabled() -> bool:
	return _enabled


func get_button_night_modulate() -> Color:
	return BUTTON_NIGHT


func get_stall_night_modulate() -> Color:
	return STALL_NIGHT


func get_proprietor_night_modulate() -> Color:
	return PROPRIETOR_NIGHT


func _cache_nodes() -> void:
	assert(
		RECEIVER_PATHS.size() == RECEIVER_COLORS.size(),
		"Every foreground grade receiver needs exactly one color."
	)
	_receivers.clear()
	_original_receiver_modulates.clear()
	_light_receivers.clear()
	_original_light_masks.clear()
	_lights.clear()
	for path: NodePath in RECEIVER_PATHS:
		var receiver := get_node_or_null(path) as CanvasItem
		assert(receiver != null, "Missing foreground relight receiver: %s" % path)
		if receiver != null:
			_receivers.append(receiver)
			_original_receiver_modulates.append(receiver.modulate)
	for path: NodePath in LIGHT_RECEIVER_PATHS:
		var receiver := get_node_or_null(path) as CanvasItem
		assert(receiver != null, "Missing foreground light receiver: %s" % path)
		if receiver != null:
			_light_receivers.append(receiver)
			_original_light_masks.append(receiver.light_mask)
	for path: NodePath in LIGHT_PATHS:
		var light := get_node_or_null(path) as PointLight2D
		assert(light != null, "Missing foreground practical light: %s" % path)
		if light != null:
			_lights.append(light)
