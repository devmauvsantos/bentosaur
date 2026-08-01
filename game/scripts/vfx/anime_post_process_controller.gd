extends CanvasLayer

const GRAIN_FRAMES_PER_SECOND := 12.0
const GRAIN_FRAME_COUNT := 256
const GRAIN_FRAME_EPSILON := 0.0001
const GRAIN_LOOP_SECONDS := (
	float(GRAIN_FRAME_COUNT) / GRAIN_FRAMES_PER_SECOND
)

# iOS can resize or recreate its drawable surface during launch and lifecycle
# transitions. Keep the opaque screen-reading pass explicitly registered to the
# current visible viewport instead of relying on one initial anchor solve.
@onready var back_buffer: BackBufferCopy = $BackBufferCopy
@onready var filter: ColorRect = $Filter

var _grain_elapsed_seconds := 0.0
var _grain_frame := 0


func _enter_tree() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _ready() -> void:
	var viewport := get_viewport()
	if viewport != null and not viewport.size_changed.is_connected(
		_on_viewport_size_changed
	):
		viewport.size_changed.connect(_on_viewport_size_changed)
	reset_grain_clock()
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


func _process(delta: float) -> void:
	step_grain_clock(delta)
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


func step_grain_clock(delta: float) -> void:
	_grain_elapsed_seconds = fmod(
		_grain_elapsed_seconds + maxf(delta, 0.0),
		GRAIN_LOOP_SECONDS
	)
	var next_frame := _grain_frame_from_elapsed(_grain_elapsed_seconds)
	if next_frame == _grain_frame:
		return
	_grain_frame = next_frame
	_apply_grain_frame()


func reset_grain_clock(elapsed_seconds: float = 0.0) -> void:
	_grain_elapsed_seconds = fmod(
		maxf(elapsed_seconds, 0.0),
		GRAIN_LOOP_SECONDS
	)
	_grain_frame = _grain_frame_from_elapsed(_grain_elapsed_seconds)
	_apply_grain_frame()


func get_grain_frame() -> int:
	return _grain_frame


func get_grain_elapsed_seconds() -> float:
	return _grain_elapsed_seconds


func _grain_frame_from_elapsed(elapsed_seconds: float) -> int:
	return int(floor(
		elapsed_seconds * GRAIN_FRAMES_PER_SECOND + GRAIN_FRAME_EPSILON
	)) % GRAIN_FRAME_COUNT


func _apply_grain_frame() -> void:
	if filter == null:
		return
	var shader_material := filter.material as ShaderMaterial
	if shader_material == null:
		return
	shader_material.set_shader_parameter("grain_frame", float(_grain_frame))


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
