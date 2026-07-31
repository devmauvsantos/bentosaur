extends SceneTree

const COMPONENT_PATH := "res://scenes/home/components/stall_settings_button.tscn"
const PRESSED_PATH := (
	"res://assets/environments/home_village/v001/stall/attachments/"
	+ "v004/ui/settings/settings-cog-pressed-v001.png"
)


func _initialize() -> void:
	call_deferred("_run")


func _run() -> void:
	var errors := PackedStringArray()
	var packed := load(COMPONENT_PATH) as PackedScene
	_expect(packed != null, "Stall settings button scene must load.", errors)
	if packed == null:
		_finish(errors)
		return

	var button := packed.instantiate() as StallSettingsButton
	_expect(button != null, "Scene root must be StallSettingsButton.", errors)
	if button == null:
		_finish(errors)
		return
	root.add_child(button)
	await process_frame

	var visual_root := button.get_node_or_null("VisualRoot") as Control
	var icon := button.get_node_or_null("VisualRoot/Icon") as TextureRect
	_expect(button is Button, "Settings component must remain a semantic Button.", errors)
	_expect(button.focus_mode == Control.FOCUS_ALL, "Settings must accept keyboard focus.", errors)
	_expect(button.size == Vector2(75.0, 84.0), "Settings logical size changed.", errors)
	_expect(button.text == "Settings", "Settings semantic label mismatch.", errors)
	_expect(button.tooltip_text == "Settings", "Settings tooltip must mirror its label.", errors)
	_expect(is_zero_approx(button.get_theme_color("font_color").a), "Settings built-in text must be visually transparent.", errors)
	_expect(visual_root != null, "Settings needs a stable child visual root.", errors)
	_expect(icon != null and icon.texture != null, "Settings normal icon must load.", errors)
	if icon != null and icon.texture != null:
		_expect(icon.texture.get_size() == Vector2(150.0, 168.0), "Settings runtime plate must remain 150x168.", errors)
		_expect(icon.stretch_mode == TextureRect.STRETCH_KEEP_ASPECT_CENTERED, "Settings art must preserve aspect.", errors)
		_expect(icon.texture == button.get_canonical_mask_texture(), "Normal icon must remain canonical alpha geometry.", errors)
		_expect(icon.material is ShaderMaterial, "Settings states need canonical-mask material.", errors)

	button.accessible_label = "Game Settings"
	_expect(button.text == "Game Settings", "Dynamic settings semantic label failed.", errors)
	_expect(button.tooltip_text == button.text, "Dynamic settings tooltip failed.", errors)

	button.grab_focus()
	await process_frame
	_expect(button.get_visual_state() == StallSettingsButton.VisualState.FOCUSED, "Settings needs visible focus feedback.", errors)
	_expect(visual_root.modulate.r > 1.0, "Focused settings art must brighten without another asset.", errors)

	button.emit_signal("button_down")
	await create_timer(0.085).timeout
	_expect(button.get_visual_state() == StallSettingsButton.VisualState.PRESSED, "Pressed settings state must outrank focus.", errors)
	_expect(button.get_active_state_texture() == load(PRESSED_PATH), "Settings pressed plate mismatch.", errors)
	_expect(visual_root.scale.is_equal_approx(Vector2(0.97, 0.97)), "Settings press scale must settle at .97.", errors)
	_expect(is_equal_approx(visual_root.rotation, deg_to_rad(5.0)), "Settings press rotation must settle at five degrees.", errors)

	button.emit_signal("button_up")
	await create_timer(0.105).timeout
	_expect(button.get_visual_state() == StallSettingsButton.VisualState.FOCUSED, "Settings release must return to focus.", errors)
	_expect(visual_root.scale.is_equal_approx(Vector2.ONE), "Settings release scale must return home.", errors)
	_expect(is_zero_approx(visual_root.rotation), "Settings release rotation must return home.", errors)

	button.disabled = true
	await process_frame
	_expect(button.get_visual_state() == StallSettingsButton.VisualState.DISABLED, "Disabled settings must outrank focus.", errors)
	_expect(is_equal_approx(visual_root.modulate.a, 0.48), "Disabled settings needs visible attenuation.", errors)

	button.disabled = false
	button.release_focus()
	button.set_reduced_motion(true)
	button.emit_signal("button_down")
	_expect(visual_root.scale == Vector2(0.97, 0.97), "Reduced motion must preserve settings pressed endpoint.", errors)
	_expect(
		is_equal_approx(visual_root.rotation, deg_to_rad(5.0)),
		"Reduced motion must snap to settings rotation endpoint.",
		errors
	)
	button.emit_signal("button_up")
	_expect(visual_root.scale == Vector2.ONE, "Reduced motion settings release must snap home.", errors)
	_expect(visual_root.rotation == 0.0, "Reduced motion settings rotation must snap home.", errors)

	button.queue_free()
	await process_frame
	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Stall settings button contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
