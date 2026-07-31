class_name StallRankFixture
extends Control

signal rank_changed(value: int)

const DESIGN_SIZE := Vector2(228.0, 48.0)
const SOURCE_PLAQUE_SIZE := Vector2(456.0, 96.0)
const RUNTIME_ASSET_SCALE := 0.5
const FILL_SECONDS := 0.180
const FILLED_START_SCALE := Vector2(0.96, 0.96)
const SHINE_START_SCALE := Vector2(0.90, 0.90)
const STAR_POSITIONS: Array[Vector2] = [
	Vector2(33.0, 9.0),
	Vector2(93.0, 9.0),
	Vector2(153.0, 9.0),
]

var _rank := 3

@export_range(0, 3, 1) var rank: int:
	set(value):
		_rank = clampi(value, 0, 3)
		if is_node_ready():
			_apply_rank(false)
	get:
		return _rank

@export var shine_enabled := true

@export var reduced_motion := false:
	set(value):
		reduced_motion = value
		if is_node_ready():
			_cancel_tweens()
			_apply_rank(false)

@onready var content_root: Control = $ContentRoot
@onready var plaque: TextureRect = $ContentRoot/Plaque

var _star_slots: Array[Control] = []
var _filled_stars: Array[TextureRect] = []
var _shine_stars: Array[TextureRect] = []
var _active_tweens: Array[Tween] = []
var _displayed_rank := -1


func _ready() -> void:
	for index: int in range(3):
		var slot := get_node("ContentRoot/Star%d" % (index + 1)) as Control
		var filled := slot.get_node("Filled") as TextureRect
		var shine := slot.get_node("Shine") as TextureRect
		_star_slots.append(slot)
		_filled_stars.append(filled)
		_shine_stars.append(shine)
		filled.pivot_offset = Vector2(21.0, 17.0)
		shine.pivot_offset = shine.size * 0.5
	resized.connect(_layout_content)
	_layout_content()
	_apply_rank(false)


func set_rank(value: int, animate: bool = true) -> void:
	var next_rank := clampi(value, 0, 3)
	if next_rank == _rank and _displayed_rank == _rank:
		return
	_rank = next_rank
	_apply_rank(animate and not reduced_motion)
	rank_changed.emit(_rank)


func get_rank() -> int:
	return _rank


func set_reduced_motion(enabled: bool) -> void:
	reduced_motion = enabled


func is_reduced_motion() -> bool:
	return reduced_motion


func _layout_content() -> void:
	if content_root == null or size.x <= 0.0 or size.y <= 0.0:
		return
	var content_scale := minf(size.x / DESIGN_SIZE.x, size.y / DESIGN_SIZE.y)
	content_root.size = DESIGN_SIZE
	content_root.scale = Vector2.ONE * content_scale
	content_root.position = (size - DESIGN_SIZE * content_scale) * 0.5

	var plaque_scale := RUNTIME_ASSET_SCALE
	plaque.position = Vector2.ZERO
	plaque.size = SOURCE_PLAQUE_SIZE
	plaque.scale = Vector2.ONE * plaque_scale

	for index: int in range(_star_slots.size()):
		_star_slots[index].position = STAR_POSITIONS[index]


func _apply_rank(animate: bool) -> void:
	if _filled_stars.is_empty():
		return
	var previous_rank := maxi(_displayed_rank, 0)
	_cancel_tweens()
	for index: int in range(3):
		var should_be_filled := index < _rank
		var was_filled := index < previous_rank
		if not animate or should_be_filled == was_filled:
			_apply_star_endpoint(index, should_be_filled)
			continue
		_animate_star(index, should_be_filled)
	_displayed_rank = _rank


func _animate_star(index: int, filled_endpoint: bool) -> void:
	var filled := _filled_stars[index]
	var shine := _shine_stars[index]
	shine.visible = false
	if filled_endpoint:
		filled.visible = true
		filled.modulate.a = 0.0
		filled.scale = FILLED_START_SCALE
	else:
		filled.visible = true
		filled.modulate.a = 1.0
		filled.scale = Vector2.ONE

	var fill_tween := create_tween().set_parallel(true)
	_active_tweens.append(fill_tween)
	fill_tween.tween_property(
		filled,
		"modulate:a",
		1.0 if filled_endpoint else 0.0,
		FILL_SECONDS
	).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	fill_tween.tween_property(
		filled,
		"scale",
		Vector2.ONE if filled_endpoint else FILLED_START_SCALE,
		FILL_SECONDS
	).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	if not filled_endpoint:
		fill_tween.finished.connect(filled.hide)

	if filled_endpoint and shine_enabled:
		shine.visible = true
		shine.modulate.a = 0.0
		shine.scale = SHINE_START_SCALE
		var shine_tween := create_tween().set_parallel(true)
		_active_tweens.append(shine_tween)
		shine_tween.tween_property(
			shine,
			"scale",
			Vector2.ONE,
			FILL_SECONDS
		).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
		var alpha_tween := create_tween()
		_active_tweens.append(alpha_tween)
		alpha_tween.tween_property(
			shine,
			"modulate:a",
			0.72,
			FILL_SECONDS * 0.5
		).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
		alpha_tween.tween_property(
			shine,
			"modulate:a",
			0.0,
			FILL_SECONDS * 0.5
		).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_IN)
		alpha_tween.finished.connect(shine.hide)


func _apply_star_endpoint(index: int, filled_endpoint: bool) -> void:
	var filled := _filled_stars[index]
	var shine := _shine_stars[index]
	filled.visible = filled_endpoint
	filled.modulate.a = 1.0 if filled_endpoint else 0.0
	filled.scale = Vector2.ONE
	shine.visible = false
	shine.modulate.a = 0.0
	shine.scale = Vector2.ONE


func _cancel_tweens() -> void:
	for tween: Tween in _active_tweens:
		if tween != null and tween.is_valid():
			tween.kill()
	_active_tweens.clear()
	for shine: TextureRect in _shine_stars:
		shine.visible = false
