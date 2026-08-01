extends SceneTree

const POST_PROCESS_PATH := "res://scenes/vfx/anime_90s_post_process.tscn"
const PORTRAIT_VIEWPORT_SIZES: Array[Vector2i] = [
	Vector2i(720, 1280),
	Vector2i(720, 1564),
	Vector2i(440, 956),
	Vector2i(1024, 1366),
]


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(POST_PROCESS_PATH) as PackedScene
	_expect(packed != null, "Anime post-process scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var viewport := SubViewport.new()
	viewport.name = "AnimePostProcessCoverageViewport"
	viewport.size = PORTRAIT_VIEWPORT_SIZES[0]
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)

	var post_process := packed.instantiate() as CanvasLayer
	_expect(post_process != null, "Anime post-process root must be a CanvasLayer.", errors)
	if post_process == null:
		viewport.queue_free()
		await process_frame
		_finish(errors)
		return

	viewport.add_child(post_process)
	await process_frame
	await process_frame

	var back_buffer := post_process.get_node_or_null("BackBufferCopy") as BackBufferCopy
	var filter := post_process.get_node_or_null("Filter") as ColorRect
	_expect(back_buffer != null, "Post-process must own an explicit BackBufferCopy.", errors)
	_expect(filter != null, "Post-process must own its full-screen Filter.", errors)
	_expect(
		post_process.process_mode == Node.PROCESS_MODE_ALWAYS,
		"Post-process coverage repair must keep running while the scene tree is paused.",
		errors
	)
	_expect(
		post_process.transform.is_equal_approx(Transform2D.IDENTITY),
		"Post-process CanvasLayer must start with an identity transform.",
		errors
	)

	if back_buffer != null and filter != null:
		var shader_material := filter.material as ShaderMaterial
		_expect(
			shader_material != null,
			"Post-process filter must retain its local shader material.",
			errors
		)
		if shader_material != null:
			_expect(
				not shader_material.shader.code.contains("TIME"),
				"Mobile grain must not use an unbounded TIME hash.",
				errors
			)
			_expect(
				not shader_material.shader.code.contains("12.9898")
					and not shader_material.shader.code.contains("78.233"),
				"Mobile grain must not restore the failing sine-hash coefficients.",
				errors
			)
			_validate_long_horizon_grain(
				post_process,
				filter,
				viewport,
				shader_material,
				errors
			)
		_expect(
			back_buffer.get_index() < filter.get_index(),
			"BackBufferCopy must render before the screen-reading Filter.",
			errors
		)
		_expect(
			back_buffer.copy_mode == BackBufferCopy.COPY_MODE_VIEWPORT,
			"BackBufferCopy must refresh the complete viewport.",
			errors
		)

		for viewport_size: Vector2i in PORTRAIT_VIEWPORT_SIZES:
			viewport.size = viewport_size
			await process_frame
			await process_frame
			_expect_filter_covers_viewport(
				post_process,
				filter,
				viewport,
				"after resizing to %dx%d" % [viewport_size.x, viewport_size.y],
				errors
			)

		# Copy-only drift must recover even when the geometry remains correct.
		back_buffer.copy_mode = BackBufferCopy.COPY_MODE_DISABLED
		await process_frame
		_expect(
			back_buffer.copy_mode == BackBufferCopy.COPY_MODE_VIEWPORT,
			"The controller must repair isolated back-buffer copy-mode drift.",
			errors
		)

		# A same-size mobile drawable recreation arrives as a lifecycle event, not
		# necessarily as Viewport.size_changed. Disable processing to prove the
		# notification's deferred re-arm owns this recovery path.
		post_process.process_mode = Node.PROCESS_MODE_DISABLED
		back_buffer.copy_mode = BackBufferCopy.COPY_MODE_DISABLED
		post_process.notification(Node.NOTIFICATION_APPLICATION_RESUMED)
		await process_frame
		await process_frame
		_expect(
			back_buffer.copy_mode == BackBufferCopy.COPY_MODE_VIEWPORT,
			"Application resume must re-arm full-viewport screen copying.",
			errors
		)
		post_process.process_mode = Node.PROCESS_MODE_ALWAYS

		paused = true
		filter.position = Vector2(87.0, 143.0)
		filter.size = Vector2(260.0, 410.0)
		back_buffer.copy_mode = BackBufferCopy.COPY_MODE_DISABLED
		post_process.transform = Transform2D(
			Vector2(0.91, 0.07),
			Vector2(-0.04, 1.08),
			Vector2(31.0, -52.0)
		)
		await process_frame
		await process_frame
		paused = false
		_expect_filter_covers_viewport(
			post_process,
			filter,
			viewport,
			"after injected geometry drift while paused",
			errors
		)
		_expect(
			back_buffer.copy_mode == BackBufferCopy.COPY_MODE_VIEWPORT,
			"Geometry recovery must preserve full-viewport back-buffer copying.",
			errors
		)

	viewport.queue_free()
	await process_frame
	await create_timer(0.05).timeout
	_finish(errors)


func _validate_long_horizon_grain(
	post_process: CanvasLayer,
	filter: ColorRect,
	viewport: Viewport,
	shader_material: ShaderMaterial,
	errors: PackedStringArray
) -> void:
	# This contract validates bounded controller state and viewport coverage. The
	# reported fragment-precision artifact still requires the documented physical
	# iPhone longevity gate because a headless geometry test cannot inspect pixels.
	post_process.set_process(false)
	var cross_rate_frames: Array[int] = []
	for rate: int in [30, 60, 120]:
		post_process.call("reset_grain_clock", 0.0)
		for frame: int in range(rate * 360):
			post_process.call("step_grain_clock", 1.0 / float(rate))
		cross_rate_frames.append(int(post_process.call("get_grain_frame")))
	_expect(
		cross_rate_frames[0] == cross_rate_frames[1]
			and cross_rate_frames[1] == cross_rate_frames[2],
		"Six-minute grain clocks must agree at 30, 60, and 120 FPS.",
		errors
	)
	var grain_frame := int(post_process.call("get_grain_frame"))
	var elapsed := float(post_process.call("get_grain_elapsed_seconds"))
	_expect(
		grain_frame >= 0 and grain_frame < 256,
		"Six-minute grain simulation must remain inside its bounded frame ring.",
		errors
	)
	_expect(
		elapsed >= 0.0 and elapsed < 256.0 / 12.0,
		"Six-minute grain simulation must keep elapsed shader time bounded.",
		errors
	)
	_expect(
		is_equal_approx(
			float(shader_material.get_shader_parameter("grain_frame")),
			float(grain_frame)
		),
		"The shader must receive the controller's bounded grain frame.",
		errors
	)
	_expect_filter_covers_viewport(
		post_process,
		filter,
		viewport,
		"after a simulated six-minute grain lifetime",
		errors
	)
	post_process.set_process(true)


func _expect_filter_covers_viewport(
	post_process: CanvasLayer,
	filter: ColorRect,
	viewport: Viewport,
	context: String,
	errors: PackedStringArray
) -> void:
	var visible_rect := viewport.get_visible_rect()
	_expect(
		filter.position.is_equal_approx(visible_rect.position),
		"Filter position must match the visible viewport %s." % context,
		errors
	)
	_expect(
		filter.size.is_equal_approx(visible_rect.size),
		"Filter size must match the visible viewport %s." % context,
		errors
	)
	_expect(
		post_process.transform.is_equal_approx(Transform2D.IDENTITY),
		"Post-process transform must recover to identity %s." % context,
		errors
	)
	for side: Side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
		_expect(
			is_zero_approx(filter.get_anchor(side)),
			"Filter anchors must remain explicitly top-left %s." % context,
			errors
		)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Anime post-process coverage contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
