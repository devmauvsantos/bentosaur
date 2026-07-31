class_name AspectFillCanvas
extends CanvasLayer

@export var design_size := Vector2(720.0, 1280.0)


func _enter_tree() -> void:
	_apply_aspect_fill()


func _ready() -> void:
	var viewport := get_viewport()
	if viewport != null and not viewport.size_changed.is_connected(
		_on_viewport_size_changed
	):
		viewport.size_changed.connect(_on_viewport_size_changed)
	_apply_aspect_fill.call_deferred()


func _on_viewport_size_changed() -> void:
	_apply_aspect_fill()


func _apply_aspect_fill() -> void:
	var viewport := get_viewport()
	if viewport == null:
		return
	var viewport_size := viewport.get_visible_rect().size
	if (
		viewport_size.x <= 0.0
		or viewport_size.y <= 0.0
		or design_size.x <= 0.0
		or design_size.y <= 0.0
	):
		return

	var fill_scale := calculate_fill_scale(viewport_size, design_size)
	var centered_position := calculate_centered_position(
		viewport_size,
		design_size,
		fill_scale
	)
	transform = Transform2D(
		Vector2(fill_scale, 0.0),
		Vector2(0.0, fill_scale),
		centered_position
	)


static func calculate_fill_scale(
	viewport_size: Vector2,
	source_design_size: Vector2
) -> float:
	return maxf(
		viewport_size.x / source_design_size.x,
		viewport_size.y / source_design_size.y
	)


static func calculate_centered_position(
	viewport_size: Vector2,
	source_design_size: Vector2,
	fill_scale: float
) -> Vector2:
	return (viewport_size - source_design_size * fill_scale) * 0.5
