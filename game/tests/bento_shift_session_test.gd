extends SceneTree

const SHIFT_PATH := "res://data/vertical_slice/shift_v1.json"
const ShiftSession = preload("res://scripts/gameplay/bento_shift_session.gd")


func _initialize() -> void:
	var errors := PackedStringArray()
	var contract := _load_contract(errors)
	if not errors.is_empty():
		_finish(errors)
		return

	var session := ShiftSession.new()
	errors.append_array(session.configure(contract, 10))
	if not errors.is_empty():
		_finish(errors)
		return

	_expect(session.ingredient_ids().size() == 4, "Expected four ingredients.", errors)
	_expect(session.customers.size() == 3, "Expected three customers.", errors)
	session.start_shift()
	_expect(session.current_customer().get("id") == "nori", "First customer is Nori.", errors)

	for ingredient_id: String in ["rice", "berry", "leaf"]:
		_expect(session.toggle_ingredient(ingredient_id), "Select %s." % ingredient_id, errors)
	_expect(session.can_serve(), "Three ingredients should enable serving.", errors)
	var first_result: Dictionary = session.serve()
	_expect(bool(first_result.get("correct")), "Nori's matching order should be correct.", errors)
	_expect(int(first_result.get("reward")) == 10, "Nori should reward ten coins.", errors)

	for ingredient_id: String in ["tofu", "leaf", "rice"]:
		session.toggle_ingredient(ingredient_id)
	var second_result: Dictionary = session.serve()
	_expect(not bool(second_result.get("correct")), "Momo's mismatched order should fail.", errors)
	_expect(int(second_result.get("reward")) == 0, "A mismatch should not award coins.", errors)
	_expect(session.current_customer().get("id") == "momo", "Momo should wait for a correction.", errors)
	for ingredient_id: String in ["tofu", "leaf", "rice"]:
		session.toggle_ingredient(ingredient_id)
	for ingredient_id: String in ["leaf", "tofu", "rice"]:
		session.toggle_ingredient(ingredient_id)
	var corrected_result: Dictionary = session.serve()
	_expect(bool(corrected_result.get("correct")), "Momo's corrected order should pass.", errors)
	_expect(not bool(corrected_result.get("first_try")), "Momo should no longer count as first try.", errors)

	for ingredient_id: String in ["berry", "rice", "tofu"]:
		session.toggle_ingredient(ingredient_id)
	var final_result: Dictionary = session.serve()
	_expect(bool(final_result.get("shift_complete")), "Third service should complete the shift.", errors)
	_expect(session.star_rating() == 2, "Two correct orders should earn two stars.", errors)
	_expect(session.shift_coins == 30, "Shift should earn thirty coins.", errors)
	_expect(session.lifetime_coins == 40, "Lifetime coins should include initial balance.", errors)

	_finish(errors)


func _load_contract(errors: PackedStringArray) -> Dictionary:
	if not FileAccess.file_exists(SHIFT_PATH):
		errors.append("Missing shift contract: %s" % SHIFT_PATH)
		return {}
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(SHIFT_PATH))
	if not parsed is Dictionary:
		errors.append("Shift contract is not a JSON object.")
		return {}
	return parsed


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Bento shift session contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
