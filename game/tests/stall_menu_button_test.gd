extends SceneTree

const COMPONENT_PATH := "res://scenes/home/components/stall_menu_button.tscn"
const PRIMARY_PRESSED_PATH := (
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-primary-pressed-v001.png"
)
const PRIMARY_DISABLED_PATH := (
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/buttons/menu-button-primary-disabled-v001.png"
)
const SOURCE_SIZE := Vector2(692.0, 410.0)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(COMPONENT_PATH) as PackedScene
	_expect(packed != null, "Stall menu button scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var button := packed.instantiate() as StallMenuButton
	_expect(button != null, "Scene root must be a StallMenuButton.", errors)
	if button == null:
		_finish(errors)
		return
	root.add_child(button)
	await process_frame

	var visual_root := button.get_node_or_null("VisualRoot") as Control
	var frame := button.get_node_or_null("VisualRoot/Frame") as NinePatchRect
	var label := button.get_node_or_null("VisualRoot/LiveLabel") as Label
	var left_leaf := button.get_node_or_null("VisualRoot/LeafLeft") as TextureRect
	var right_leaf := button.get_node_or_null("VisualRoot/LeafRight") as TextureRect
	_expect(button is Button, "Component must remain a semantic Button.", errors)
	_expect(button.focus_mode == Control.FOCUS_ALL, "Button must accept keyboard focus.", errors)
	_expect(visual_root != null, "Button needs a stable child visual root.", errors)
	_expect(frame != null, "Button needs its NinePatch frame.", errors)
	_expect(label != null, "Button needs a live Label.", errors)
	_expect(left_leaf != null and right_leaf != null, "Detached leaves must remain separate.", errors)
	_expect(button.size == Vector2(292.0, 72.0), "Primary logical size changed.", errors)
	_expect(button.text == "Open Stall", "Root Button must retain semantic text.", errors)
	_expect(label != null and label.text == button.text, "Visible live label must mirror Button text.", errors)
	_expect(
		is_zero_approx(button.get_theme_color("font_color").a),
		"Built-in Button text must be visually transparent.",
		errors
	)

	if frame != null:
		_expect(frame.texture != null, "Canonical frame texture must load.", errors)
		if frame.texture != null:
			_expect(frame.texture.get_size() == SOURCE_SIZE, "Button runtime texture must remain 692x410.", errors)
		_expect(frame.patch_margin_left == 144 and frame.patch_margin_right == 144, "2x horizontal caps must remain 144 px.", errors)
		_expect(frame.patch_margin_top == 0 and frame.patch_margin_bottom == 0, "Button must use horizontal-only slicing.", errors)
		_expect(is_equal_approx(frame.size.y, 410.0), "NinePatch source height must remain uncut.", errors)
		_expect(is_equal_approx(frame.scale.y, 72.0 / 410.0), "Primary wrapper scale must preserve vertical aspect.", errors)
		_expect(frame.texture == button.get_canonical_mask_texture(), "Normal texture must remain the canonical alpha mask.", errors)
		_expect(frame.material is ShaderMaterial, "Frame requires canonical-mask shader material.", errors)

	button.label_text = "Collection"
	_expect(button.text == "Collection", "Dynamic semantic label did not update.", errors)
	_expect(label.text == "Collection", "Dynamic visible label did not update.", errors)

	button.grab_focus()
	await process_frame
	_expect(
		button.get_visual_state() == StallMenuButton.VisualState.FOCUSED,
		"Focused state must follow normal state.",
		errors
	)
	_expect(
		frame.texture == button.get_canonical_mask_texture(),
		"Focus may not replace the canonical geometry texture.",
		errors
	)

	button.emit_signal("button_down")
	await create_timer(0.085).timeout
	_expect(
		button.get_visual_state() == StallMenuButton.VisualState.PRESSED,
		"Pressed state must outrank focus.",
		errors
	)
	_expect(
		button.get_active_state_texture() == load(PRIMARY_PRESSED_PATH),
		"Primary pressed plate mismatch.",
		errors
	)
	if visual_root != null:
		_expect(visual_root.position.is_equal_approx(Vector2(0.0, 2.0)), "Press must settle at y +2.", errors)
		_expect(visual_root.scale.is_equal_approx(Vector2(0.985, 0.985)), "Press must settle at scale .985.", errors)

	button.emit_signal("button_up")
	await create_timer(0.105).timeout
	_expect(
		button.get_visual_state() == StallMenuButton.VisualState.FOCUSED,
		"Release must return to focused when focus remains.",
		errors
	)
	if visual_root != null:
		_expect(visual_root.position.is_zero_approx(), "Release must restore visual offset.", errors)
		_expect(visual_root.scale.is_equal_approx(Vector2.ONE), "Release must restore visual scale.", errors)

	button.disabled = true
	await process_frame
	_expect(
		button.get_visual_state() == StallMenuButton.VisualState.DISABLED,
		"Disabled must outrank every other state.",
		errors
	)
	_expect(
		button.get_active_state_texture() == load(PRIMARY_DISABLED_PATH),
		"Primary disabled plate mismatch.",
		errors
	)

	button.disabled = false
	button.release_focus()
	button.set_reduced_motion(true)
	button.emit_signal("button_down")
	_expect(visual_root.position == Vector2(0.0, 2.0), "Reduced motion must jump to pressed offset.", errors)
	_expect(visual_root.scale == Vector2(0.985, 0.985), "Reduced motion must preserve pressed endpoint.", errors)
	button.emit_signal("button_up")
	_expect(visual_root.position == Vector2.ZERO, "Reduced motion release must snap home.", errors)
	_expect(visual_root.scale == Vector2.ONE, "Reduced motion release scale must snap home.", errors)

	button.button_kind = StallMenuButton.ButtonKind.SECONDARY
	button.size = Vector2(290.0, 64.0)
	await process_frame
	_expect(button.custom_minimum_size == Vector2(290.0, 64.0), "Secondary minimum size mismatch.", errors)
	_expect(is_equal_approx(frame.scale.y, 64.0 / 410.0), "Secondary wrapper must use 64/410 scale.", errors)
	_expect(frame.texture == button.get_canonical_mask_texture(), "Secondary normal must become the canonical mask.", errors)

	button.size = Vector2(320.0, 80.0)
	await process_frame
	_expect(is_equal_approx(frame.scale.y, 80.0 / 410.0), "Resized button must preserve frame height aspect.", errors)
	_expect(is_equal_approx(frame.size.x * frame.scale.x, 320.0), "Horizontal-only slice must fill requested width.", errors)

	button.queue_free()
	await process_frame
	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Stall menu button contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
