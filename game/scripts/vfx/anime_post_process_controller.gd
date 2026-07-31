extends CanvasLayer

# iOS can resize or recreate its drawable surface during launch and lifecycle
# transitions. Keep the opaque screen-reading pass explicitly registered to the
# current visible viewport instead of relying on one initial anchor solve.
@onready var back_buffer: BackBufferCopy = $BackBufferCopy
@onready var filter: ColorRect = $Filter


func _enter_tree() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _ready() -> void:
	var viewport := get_viewport()
	if viewport != null and not viewport.size_changed.is_connected(
		_on_viewport_size_changed
	):
		viewport.size_changed.connect(_on_viewport_size_changed)
	_pin_to_viewport()
	_pin_to_viewport.call_deferred()


func _notification(what: int) -> void:
	if what in [
		NOTIFICATION_APPLICATION_RESUMED,
		NOTIFICATION_APPLICATION_FOCUS_IN,
	]:
		# A mobile drawable can be recreated without changing the logical size.
		# Re-arm the explicit copy after the lifecycle notification has settled.
		_pin_to_viewport.call_deferred()


func _process(_delta: float) -> void:
	var viewport := get_viewport()
	if viewport == null or filter == null or back_buffer == null:
		return
	var visible_rect := viewport.get_visible_rect()
	if (
		not filter.position.is_equal_approx(visible_rect.position)
		or not filter.size.is_equal_approx(visible_rect.size)
		or not transform.is_equal_approx(Transform2D.IDENTITY)
		or back_buffer.copy_mode != BackBufferCopy.COPY_MODE_VIEWPORT
	):
		_pin_to_viewport()


func _on_viewport_size_changed() -> void:
	_pin_to_viewport()
	_pin_to_viewport.call_deferred()


func _pin_to_viewport() -> void:
	var viewport := get_viewport()
	if viewport == null or filter == null or back_buffer == null:
		return
	transform = Transform2D.IDENTITY
	back_buffer.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
	for side: Side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		filter.set_anchor(side, 0.0, false)
	var visible_rect := viewport.get_visible_rect()
	filter.position = visible_rect.position
	filter.size = visible_rect.size
