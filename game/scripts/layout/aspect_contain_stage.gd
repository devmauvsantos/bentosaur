class_name AspectContainStage
extends Node2D

const ASPECT_FILL := preload("res://scripts/layout/aspect_fill_canvas.gd")

@export var design_size := Vector2(720.0, 1280.0)
@export var viewport_anchor := Vector2(0.5, 0.5)
@export_range(0.5, 1.5, 0.01) var framing_scale := 1.0
@export var framing_pivot := Vector2(360.0, 640.0)


func _enter_tree() -> void:
	_apply_aspect_contain()


func _ready() -> void:
	var viewport := get_viewport()
	if viewport != null and not viewport.size_changed.is_connected(
		_on_viewport_size_changed
	):
		viewport.size_changed.connect(_on_viewport_size_changed)
	_apply_aspect_contain.call_deferred()


func _on_viewport_size_changed() -> void:
	_apply_aspect_contain()


func _apply_aspect_contain() -> void:
	var viewport := get_viewport()
	if viewport == null:
		return
	var viewport_size := viewport.get_visible_rect().size
	if not _has_valid_sizes(viewport_size, design_size):
		return

	var local_scale := calculate_local_scale(
		viewport_size,
		design_size,
		framing_scale
	)
	position = calculate_local_position(
		viewport_size,
		design_size,
		viewport_anchor,
		framing_pivot,
		framing_scale
	)
	scale = Vector2.ONE * local_scale


static func calculate_fit_scale(
	viewport_size: Vector2,
	source_design_size: Vector2
) -> float:
	return minf(
		viewport_size.x / source_design_size.x,
		viewport_size.y / source_design_size.y
	)


static func calculate_local_scale(
	viewport_size: Vector2,
	source_design_size: Vector2,
	authored_scale: float = 1.0
) -> float:
	var fill_scale: float = ASPECT_FILL.calculate_fill_scale(
		viewport_size,
		source_design_size
	)
	var fit_scale := calculate_fit_scale(viewport_size, source_design_size)
	return fit_scale * authored_scale / fill_scale


static func calculate_local_position(
	viewport_size: Vector2,
	source_design_size: Vector2,
	anchor: Vector2 = Vector2(0.5, 0.5),
	pivot: Vector2 = Vector2(360.0, 640.0),
	authored_scale: float = 1.0
) -> Vector2:
	var fill_scale: float = ASPECT_FILL.calculate_fill_scale(
		viewport_size,
		source_design_size
	)
	var fit_scale := calculate_fit_scale(viewport_size, source_design_size)
	var fill_position: Vector2 = ASPECT_FILL.calculate_centered_position(
		viewport_size,
		source_design_size,
		fill_scale
	)
	var remaining_space := viewport_size - source_design_size * fit_scale
	var target_position := remaining_space * anchor
	var target_pivot := target_position + pivot * fit_scale
	var local_scale := fit_scale * authored_scale / fill_scale
	return (target_pivot - fill_position) / fill_scale - pivot * local_scale


static func _has_valid_sizes(
	viewport_size: Vector2,
	source_design_size: Vector2
) -> bool:
	return (
		viewport_size.x > 0.0
		and viewport_size.y > 0.0
		and source_design_size.x > 0.0
		and source_design_size.y > 0.0
	)
