extends Control

const ShiftSession = preload("res://scripts/gameplay/bento_shift_session.gd")
const SaveStore = preload("res://scripts/services/save_store.gd")
const HOME_TEXTURE: Texture2D = preload(
	"res://assets/vertical_slice/home_classic_stall_v1.png"
)
const SERVICE_TEXTURE: Texture2D = preload(
	"res://assets/vertical_slice/service_counter_flat_cel_v1.png"
)
const SHIFT_CONTRACT_PATH := "res://data/vertical_slice/shift_v1.json"

const INK := Color("#251A19")
const CREAM := Color("#FFF0C7")
const GOLD := Color("#F5C45D")
const GREEN := Color("#607E36")
const GREEN_BRIGHT := Color("#91B84D")
const RED := Color("#9D4139")
const WOOD := Color("#5A2F20")
const NIGHT := Color("#101D35")

var session: BentoShiftSession
var home_layer: Control
var service_layer: Control
var summary_layer: Control
var transition_overlay: ColorRect

var home_coin_label: Label
var service_coin_label: Label
var progress_label: Label
var order_label: Label
var serve_button: Button
var toast_panel: Panel
var toast_label: Label
var summary_stars_label: Label
var summary_stats_label: Label

var ingredient_buttons: Dictionary = {}
var slot_panels: Array[Panel] = []
var slot_labels: Array[Label] = []

var _transitioning := false
var _serving := false
var _toast_tween: Tween


func _ready() -> void:
	var contract_errors := _configure_session()
	if not contract_errors.is_empty():
		_build_fatal_error(contract_errors)
		return
	_build_home()
	_build_service()
	_build_summary()
	_build_transition_overlay()
	_show_only(home_layer)
	_update_home()
	_apply_capture_state()


func _configure_session() -> PackedStringArray:
	var errors := PackedStringArray()
	if not FileAccess.file_exists(SHIFT_CONTRACT_PATH):
		errors.append("Missing shift contract: %s" % SHIFT_CONTRACT_PATH)
		return errors
	var parsed: Variant = JSON.parse_string(
		FileAccess.get_file_as_string(SHIFT_CONTRACT_PATH)
	)
	if not parsed is Dictionary:
		errors.append("The first-playable shift contract is not a JSON object.")
		return errors
	session = ShiftSession.new()
	errors.append_array(
		session.configure(parsed, SaveStore.load_total_coins())
	)
	return errors


func _apply_capture_state() -> void:
	var args := OS.get_cmdline_user_args()
	if args.has("--capture-service"):
		session.start_shift()
		_update_service()
		_show_only(service_layer)
	elif args.has("--capture-summary"):
		session.start_shift()
		while session.shift_active:
			var customer := session.current_customer()
			for ingredient_id: Variant in customer.get("order", []):
				session.toggle_ingredient(String(ingredient_id))
			session.serve()
		_update_summary()
		_show_only(summary_layer)


func _build_home() -> void:
	home_layer = _make_layer("Home")
	home_layer.add_child(_make_background(HOME_TEXTURE))
	home_coin_label = _make_coin_readout(home_layer)

	var open_glow := Panel.new()
	open_glow.name = "OpenStallGlow"
	open_glow.position = Vector2(160, 716)
	open_glow.size = Vector2(400, 112)
	open_glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	open_glow.add_theme_stylebox_override(
		"panel",
		_make_style(Color(0.45, 0.72, 0.20, 0.08), GOLD, 5, 24)
	)
	home_layer.add_child(open_glow)

	var open_button := _make_hotspot(
		home_layer,
		"OpenStallButton",
		Rect2(154, 706, 412, 130),
		"Open the stall"
	)
	open_button.pressed.connect(_on_open_stall_pressed)

	var regulars_button := _make_hotspot(
		home_layer,
		"RegularsButton",
		Rect2(154, 838, 412, 105),
		"Regulars are not in this build yet"
	)
	regulars_button.pressed.connect(
		_show_home_message.bind("The Regulars book comes after the serving loop.")
	)

	var pantry_button := _make_hotspot(
		home_layer,
		"PantryButton",
		Rect2(154, 951, 412, 105),
		"Pantry is not in this build yet"
	)
	pantry_button.pressed.connect(
		_show_home_message.bind("Pantry progression is intentionally locked for now.")
	)

	var decorate_button := _make_hotspot(
		home_layer,
		"DecorateButton",
		Rect2(154, 1065, 412, 105),
		"Decorating is not in this build yet"
	)
	decorate_button.pressed.connect(
		_show_home_message.bind("Decorating comes after the core loop feels good.")
	)

	var hint_panel := _make_panel(
		home_layer,
		"HomeHint",
		Rect2(124, 1192, 472, 58),
		_make_style(Color(0.04, 0.07, 0.12, 0.88), Color(1, 1, 1, 0.12), 2, 20)
	)
	_make_label(
		hint_panel,
		"FIRST PLAYABLE  ·  TAP OPEN STALL",
		Rect2(12, 4, 448, 50),
		20,
		CREAM
	)

	var pulse := create_tween().set_loops()
	pulse.tween_property(open_glow, "modulate:a", 0.28, 1.0).set_trans(
		Tween.TRANS_SINE
	)
	pulse.tween_property(open_glow, "modulate:a", 1.0, 1.0).set_trans(
		Tween.TRANS_SINE
	)


func _build_service() -> void:
	service_layer = _make_layer("Service")
	service_layer.add_child(_make_background(SERVICE_TEXTURE))
	service_coin_label = _make_coin_readout(service_layer)

	progress_label = _make_pill_label(
		service_layer,
		"Progress",
		Rect2(246, 78, 300, 52),
		22
	)

	var order_panel := _make_panel(
		service_layer,
		"OrderPanel",
		Rect2(28, 258, 354, 122),
		_make_style(Color(1.0, 0.93, 0.74, 0.96), WOOD, 4, 24)
	)
	order_label = _make_label(
		order_panel,
		"",
		Rect2(18, 10, 318, 102),
		21,
		INK,
		HORIZONTAL_ALIGNMENT_LEFT
	)

	for index: int in range(session.selection_size):
		var slot := _make_panel(
			service_layer,
			"BentoSlot%d" % (index + 1),
			Rect2(147 + index * 142, 800, 128, 92),
			_make_style(Color(0.15, 0.06, 0.05, 0.72), GOLD, 3, 18)
		)
		var slot_label := _make_label(
			slot,
			"—",
			Rect2(6, 6, 116, 80),
			18,
			CREAM
		)
		var clear_slot_button := Button.new()
		clear_slot_button.name = "ClearSlotButton"
		clear_slot_button.position = Vector2.ZERO
		clear_slot_button.size = slot.size
		clear_slot_button.flat = true
		clear_slot_button.focus_mode = Control.FOCUS_ALL
		clear_slot_button.tooltip_text = "Clear bento compartment %d" % (index + 1)
		clear_slot_button.pressed.connect(_on_slot_pressed.bind(index))
		slot.add_child(clear_slot_button)
		slot_panels.append(slot)
		slot_labels.append(slot_label)

	var ingredient_ids := session.ingredient_ids()
	for index: int in range(ingredient_ids.size()):
		var ingredient_id := ingredient_ids[index]
		var ingredient_button := Button.new()
		ingredient_button.name = "%sButton" % ingredient_id.capitalize()
		ingredient_button.position = Vector2(7 + index * 177, 1010)
		ingredient_button.size = Vector2(170, 258)
		ingredient_button.focus_mode = Control.FOCUS_ALL
		ingredient_button.tooltip_text = "Add %s" % session.ingredient_display_name(
			ingredient_id
		)
		ingredient_button.add_theme_stylebox_override(
			"normal",
			_make_style(Color(0, 0, 0, 0.01), Color(1, 1, 1, 0.05), 2, 18)
		)
		ingredient_button.add_theme_stylebox_override(
			"hover",
			_make_style(Color(1, 0.78, 0.22, 0.10), GOLD, 4, 18)
		)
		ingredient_button.add_theme_stylebox_override(
			"pressed",
			_make_style(Color(0.42, 0.62, 0.20, 0.22), GREEN_BRIGHT, 5, 18)
		)
		ingredient_button.pressed.connect(
			_on_ingredient_pressed.bind(ingredient_id)
		)
		service_layer.add_child(ingredient_button)
		ingredient_buttons[ingredient_id] = ingredient_button

		var ingredient_label := _make_pill_label(
			ingredient_button,
			"%sLabel" % ingredient_id.capitalize(),
			Rect2(14, 204, 142, 42),
			17
		)
		ingredient_label.text = session.ingredient_display_name(
			ingredient_id
		).to_upper()
		ingredient_label.mouse_filter = Control.MOUSE_FILTER_IGNORE

	serve_button = _make_button(
		service_layer,
		"ServeButton",
		"SERVE BENTO",
		Rect2(224, 914, 272, 72),
		GREEN,
		GREEN_BRIGHT
	)
	serve_button.disabled = true
	serve_button.pressed.connect(_on_serve_pressed)

	toast_panel = _make_panel(
		service_layer,
		"Toast",
		Rect2(102, 622, 516, 76),
		_make_style(Color(0.04, 0.07, 0.12, 0.94), GOLD, 3, 22)
	)
	toast_label = _make_label(
		toast_panel,
		"",
		Rect2(14, 8, 488, 60),
		22,
		CREAM
	)
	toast_panel.visible = false


func _build_summary() -> void:
	summary_layer = _make_layer("Summary")
	summary_layer.add_child(_make_background(HOME_TEXTURE))
	var dimmer := ColorRect.new()
	dimmer.name = "Dimmer"
	dimmer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dimmer.color = Color(0.02, 0.03, 0.07, 0.72)
	dimmer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	summary_layer.add_child(dimmer)

	var card := _make_panel(
		summary_layer,
		"SummaryCard",
		Rect2(82, 236, 556, 778),
		_make_style(Color(0.98, 0.87, 0.66, 0.98), WOOD, 7, 34)
	)
	_make_label(
		card,
		"STALL CLOSED",
		Rect2(32, 42, 492, 70),
		38,
		INK
	)
	_make_label(
		card,
		"A tiny rainy-night shift",
		Rect2(32, 105, 492, 46),
		20,
		WOOD
	)
	summary_stars_label = _make_label(
		card,
		"☆☆☆",
		Rect2(32, 162, 492, 94),
		70,
		GREEN
	)
	summary_stats_label = _make_label(
		card,
		"",
		Rect2(58, 250, 440, 300),
		27,
		INK
	)

	var again_button := _make_button(
		card,
		"AgainButton",
		"ANOTHER SHIFT",
		Rect2(62, 585, 432, 72),
		GREEN,
		GREEN_BRIGHT
	)
	again_button.pressed.connect(_on_play_again_pressed)

	var home_button := _make_button(
		card,
		"HomeButton",
		"BACK HOME",
		Rect2(62, 675, 432, 68),
		WOOD,
		GOLD
	)
	home_button.pressed.connect(_on_summary_home_pressed)


func _build_transition_overlay() -> void:
	transition_overlay = ColorRect.new()
	transition_overlay.name = "TransitionOverlay"
	transition_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	transition_overlay.color = Color(NIGHT, 0.0)
	transition_overlay.mouse_filter = Control.MOUSE_FILTER_STOP
	transition_overlay.visible = false
	add_child(transition_overlay)


func _build_fatal_error(errors: PackedStringArray) -> void:
	var background := ColorRect.new()
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.color = NIGHT
	add_child(background)
	var message := "Bentosaur could not load the first shift:\n\n"
	message += "\n".join(errors)
	_make_label(
		background,
		message,
		Rect2(60, 160, 600, 800),
		24,
		CREAM
	)


func _on_open_stall_pressed() -> void:
	if _transitioning:
		return
	session.start_shift()
	_update_service()
	_transition_to(service_layer)


func _on_ingredient_pressed(ingredient_id: String) -> void:
	if _serving:
		return
	if not session.toggle_ingredient(ingredient_id):
		_show_toast("The bento has only three compartments.", false)
		return
	_update_selection()


func _on_slot_pressed(index: int) -> void:
	if _serving or index < 0 or index >= session.selected_ingredients.size():
		return
	session.toggle_ingredient(session.selected_ingredients[index])
	_update_selection()


func _on_serve_pressed() -> void:
	if _serving or not session.can_serve():
		return
	_serving = true
	_set_service_input_enabled(false)
	var result := session.serve()
	if not bool(result.get("correct", false)):
		_show_toast("Not quite — match the order from left to right.", false)
		_shake_bento_slots()
		await get_tree().create_timer(0.62).timeout
		_serving = false
		_set_service_input_enabled(true)
		_update_selection()
		return

	var save_error := SaveStore.save_total_coins(session.lifetime_coins)
	if save_error != OK:
		push_warning("Could not save Bentosaur progress: %s" % error_string(save_error))
	_update_coin_labels()
	_show_toast(
		"%s loved it!  +%d coins"
		% [String(result.get("customer_name", "Customer")), int(result.get("reward", 0))],
		true
	)
	await get_tree().create_timer(0.88).timeout

	if bool(result.get("shift_complete", false)):
		_update_summary()
		_transition_to(summary_layer)
	else:
		_update_service()
		_show_toast(
			"%s is at the counter."
			% String(session.current_customer().get("display_name", "A new neighbor")),
			true
		)
	_serving = false
	_set_service_input_enabled(true)


func _on_play_again_pressed() -> void:
	if _transitioning:
		return
	session.start_shift()
	_update_service()
	_transition_to(service_layer)


func _on_summary_home_pressed() -> void:
	if _transitioning:
		return
	_update_home()
	_transition_to(home_layer)


func _show_home_message(message: String) -> void:
	var existing := home_layer.get_node_or_null("ComingSoon")
	if existing != null:
		existing.queue_free()
	var panel := _make_panel(
		home_layer,
		"ComingSoon",
		Rect2(82, 606, 556, 90),
		_make_style(Color(0.04, 0.07, 0.12, 0.96), GOLD, 3, 22)
	)
	_make_label(panel, message, Rect2(16, 8, 524, 74), 20, CREAM)
	panel.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(panel, "modulate:a", 1.0, 0.14)
	tween.tween_interval(1.7)
	tween.tween_property(panel, "modulate:a", 0.0, 0.20)
	tween.tween_callback(panel.queue_free)


func _update_home() -> void:
	_update_coin_labels()


func _update_service() -> void:
	var customer := session.current_customer()
	if customer.is_empty():
		return
	var order: Array = customer.get("order", [])
	var order_names := PackedStringArray()
	for ingredient_id: Variant in order:
		order_names.append(session.ingredient_display_name(String(ingredient_id)))
	order_label.text = (
		"%s would like:\n%s"
		% [String(customer.get("display_name", "Neighbor")), "  →  ".join(order_names)]
	)
	progress_label.text = "CUSTOMER %d / %d    %s" % [
		session.customer_index + 1,
		session.customers.size(),
		_star_string(session.star_rating()),
	]
	_update_selection()
	_update_coin_labels()


func _update_selection() -> void:
	for index: int in range(slot_labels.size()):
		if index < session.selected_ingredients.size():
			var ingredient_id := session.selected_ingredients[index]
			slot_labels[index].text = "%d\n%s" % [
				index + 1,
				session.ingredient_display_name(ingredient_id).to_upper(),
			]
		else:
			slot_labels[index].text = "%d\n—" % (index + 1)

	for ingredient_id: String in ingredient_buttons:
		var button: Button = ingredient_buttons[ingredient_id]
		var is_selected := session.selected_ingredients.has(ingredient_id)
		button.add_theme_stylebox_override(
			"normal",
			_make_style(
				Color(0.36, 0.58, 0.18, 0.22) if is_selected else Color(0, 0, 0, 0.01),
				GREEN_BRIGHT if is_selected else Color(1, 1, 1, 0.05),
				5 if is_selected else 2,
				18
			)
		)
	serve_button.disabled = not session.can_serve()


func _update_coin_labels() -> void:
	var coin_text := "%02d" % session.lifetime_coins
	if home_coin_label != null:
		home_coin_label.text = coin_text
	if service_coin_label != null:
		service_coin_label.text = coin_text


func _update_summary() -> void:
	var summary := session.summary()
	summary_stars_label.text = _star_string(int(summary.get("stars", 0)))
	summary_stats_label.text = (
		"Neighbors served       %d / %d\n\n"
		+ "First-try orders       %d\n\n"
		+ "Coins earned           +%d\n\n"
		+ "Total coins             %d"
	) % [
		int(summary.get("served", 0)),
		int(summary.get("total_customers", 0)),
		int(summary.get("first_try", 0)),
		int(summary.get("shift_coins", 0)),
		int(summary.get("lifetime_coins", 0)),
	]


func _set_service_input_enabled(enabled: bool) -> void:
	for ingredient_id: String in ingredient_buttons:
		var button: Button = ingredient_buttons[ingredient_id]
		button.disabled = not enabled
	serve_button.disabled = not enabled or not session.can_serve()


func _show_toast(message: String, positive: bool) -> void:
	if _toast_tween != null and _toast_tween.is_valid():
		_toast_tween.kill()
	toast_label.text = message
	toast_panel.add_theme_stylebox_override(
		"panel",
		_make_style(
			Color(0.08, 0.18, 0.10, 0.96) if positive else Color(0.24, 0.07, 0.06, 0.96),
			GREEN_BRIGHT if positive else Color("#E78B72"),
			3,
			22
		)
	)
	toast_panel.visible = true
	toast_panel.modulate.a = 0.0
	toast_panel.scale = Vector2(0.96, 0.96)
	toast_panel.pivot_offset = toast_panel.size * 0.5
	_toast_tween = create_tween()
	_toast_tween.set_parallel(true)
	_toast_tween.tween_property(toast_panel, "modulate:a", 1.0, 0.14)
	_toast_tween.tween_property(toast_panel, "scale", Vector2.ONE, 0.18).set_trans(
		Tween.TRANS_BACK
	).set_ease(Tween.EASE_OUT)
	_toast_tween.set_parallel(false)
	_toast_tween.tween_interval(1.35)
	_toast_tween.tween_property(toast_panel, "modulate:a", 0.0, 0.20)
	_toast_tween.tween_callback(toast_panel.hide)


func _shake_bento_slots() -> void:
	for slot: Panel in slot_panels:
		var origin := slot.position
		var tween := create_tween()
		tween.tween_property(slot, "position:x", origin.x - 8.0, 0.06)
		tween.tween_property(slot, "position:x", origin.x + 8.0, 0.07)
		tween.tween_property(slot, "position:x", origin.x - 5.0, 0.06)
		tween.tween_property(slot, "position:x", origin.x, 0.07)


func _transition_to(target: Control) -> void:
	if _transitioning:
		return
	_transitioning = true
	transition_overlay.visible = true
	transition_overlay.color.a = 0.0
	var fade_out := create_tween()
	fade_out.tween_property(transition_overlay, "color:a", 0.92, 0.16)
	await fade_out.finished
	_show_only(target)
	var fade_in := create_tween()
	fade_in.tween_property(transition_overlay, "color:a", 0.0, 0.22)
	await fade_in.finished
	transition_overlay.visible = false
	_transitioning = false


func _show_only(target: Control) -> void:
	home_layer.visible = target == home_layer
	service_layer.visible = target == service_layer
	summary_layer.visible = target == summary_layer


func _star_string(stars: int) -> String:
	var result := ""
	for index: int in range(3):
		result += "★" if index < stars else "☆"
	return result


func _make_layer(node_name: String) -> Control:
	var layer := Control.new()
	layer.name = node_name
	layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(layer)
	return layer


func _make_background(texture: Texture2D) -> TextureRect:
	var background := TextureRect.new()
	background.name = "Background"
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.texture = texture
	background.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	background.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return background


func _make_coin_readout(parent: Control) -> Label:
	var backing := _make_panel(
		parent,
		"CoinReadoutBacking",
		Rect2(72, 21, 82, 58),
		_make_style(Color(0.035, 0.04, 0.06, 0.96), Color(0, 0, 0, 0), 0, 17)
	)
	return _make_label(backing, "00", Rect2(2, 0, 78, 58), 34, GOLD)


func _make_hotspot(
	parent: Control,
	node_name: String,
	rect: Rect2,
	tooltip: String
) -> Button:
	var button := Button.new()
	button.name = node_name
	button.position = rect.position
	button.size = rect.size
	button.flat = true
	button.focus_mode = Control.FOCUS_ALL
	button.tooltip_text = tooltip
	button.add_theme_stylebox_override(
		"focus",
		_make_style(Color(1, 0.82, 0.25, 0.08), GOLD, 4, 24)
	)
	parent.add_child(button)
	return button


func _make_button(
	parent: Control,
	node_name: String,
	text: String,
	rect: Rect2,
	base_color: Color,
	accent_color: Color
) -> Button:
	var button := Button.new()
	button.name = node_name
	button.text = text
	button.position = rect.position
	button.size = rect.size
	button.focus_mode = Control.FOCUS_ALL
	button.add_theme_font_size_override("font_size", 23)
	button.add_theme_color_override("font_color", CREAM)
	button.add_theme_color_override("font_hover_color", Color.WHITE)
	button.add_theme_color_override("font_pressed_color", Color.WHITE)
	button.add_theme_color_override("font_disabled_color", Color(1, 1, 1, 0.42))
	button.add_theme_stylebox_override(
		"normal",
		_make_style(base_color, GOLD, 4, 22)
	)
	button.add_theme_stylebox_override(
		"hover",
		_make_style(base_color.lightened(0.08), accent_color, 5, 22)
	)
	button.add_theme_stylebox_override(
		"pressed",
		_make_style(base_color.darkened(0.08), accent_color, 6, 22)
	)
	button.add_theme_stylebox_override(
		"disabled",
		_make_style(Color(base_color, 0.55), Color(GOLD, 0.40), 3, 22)
	)
	parent.add_child(button)
	return button


func _make_panel(
	parent: Control,
	node_name: String,
	rect: Rect2,
	style: StyleBoxFlat
) -> Panel:
	var panel := Panel.new()
	panel.name = node_name
	panel.position = rect.position
	panel.size = rect.size
	panel.add_theme_stylebox_override("panel", style)
	parent.add_child(panel)
	return panel


func _make_label(
	parent: Control,
	text: String,
	rect: Rect2,
	font_size: int,
	color: Color,
	alignment: HorizontalAlignment = HORIZONTAL_ALIGNMENT_CENTER
) -> Label:
	var label := Label.new()
	label.text = text
	label.position = rect.position
	label.size = rect.size
	label.horizontal_alignment = alignment
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.add_theme_color_override("font_outline_color", Color(0.04, 0.03, 0.03, 0.72))
	label.add_theme_constant_override("outline_size", 2)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(label)
	return label


func _make_pill_label(
	parent: Control,
	node_name: String,
	rect: Rect2,
	font_size: int
) -> Label:
	var panel := _make_panel(
		parent,
		"%sBacking" % node_name,
		rect,
		_make_style(Color(0.035, 0.04, 0.06, 0.90), GOLD, 3, 18)
	)
	var label := _make_label(
		panel,
		"",
		Rect2(8, 2, rect.size.x - 16, rect.size.y - 4),
		font_size,
		CREAM
	)
	label.name = node_name
	return label


func _make_style(
	background: Color,
	border: Color,
	border_width: int,
	corner_radius: int
) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = border
	style.border_width_left = border_width
	style.border_width_top = border_width
	style.border_width_right = border_width
	style.border_width_bottom = border_width
	style.corner_radius_top_left = corner_radius
	style.corner_radius_top_right = corner_radius
	style.corner_radius_bottom_right = corner_radius
	style.corner_radius_bottom_left = corner_radius
	style.content_margin_left = 8.0
	style.content_margin_top = 6.0
	style.content_margin_right = 8.0
	style.content_margin_bottom = 6.0
	return style
