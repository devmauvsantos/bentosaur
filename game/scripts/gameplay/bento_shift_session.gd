class_name BentoShiftSession
extends RefCounted

var shift_id: String = ""
var selection_size: int = 3
var wrong_order_reward: int = 2
var ingredients: Array[Dictionary] = []
var customers: Array[Dictionary] = []

var selected_ingredients: Array[String] = []
var customer_index: int = -1
var customers_served: int = 0
var correct_orders: int = 0
var first_try_orders: int = 0
var shift_coins: int = 0
var lifetime_coins: int = 0
var shift_active: bool = false
var current_attempt_is_first: bool = true

var _ingredient_by_id: Dictionary = {}


func configure(contract: Dictionary, initial_lifetime_coins: int = 0) -> PackedStringArray:
	var errors := PackedStringArray()
	shift_id = String(contract.get("shift_id", ""))
	selection_size = int(contract.get("selection_size", 0))
	wrong_order_reward = int(contract.get("wrong_order_reward", 0))
	lifetime_coins = maxi(initial_lifetime_coins, 0)
	ingredients.clear()
	customers.clear()
	_ingredient_by_id.clear()

	if int(contract.get("schema_version", 0)) != 1:
		errors.append("Unsupported or missing shift schema_version.")
	if shift_id.is_empty():
		errors.append("shift_id must not be empty.")
	if selection_size <= 0:
		errors.append("selection_size must be greater than zero.")
	if wrong_order_reward < 0:
		errors.append("wrong_order_reward must not be negative.")

	var raw_ingredients: Array = contract.get("ingredients", [])
	for raw_ingredient: Variant in raw_ingredients:
		if not raw_ingredient is Dictionary:
			errors.append("Every ingredient must be an object.")
			continue
		var ingredient: Dictionary = raw_ingredient
		var ingredient_id := String(ingredient.get("id", ""))
		var display_name := String(ingredient.get("display_name", ""))
		if ingredient_id.is_empty() or display_name.is_empty():
			errors.append("Every ingredient needs id and display_name.")
			continue
		if _ingredient_by_id.has(ingredient_id):
			errors.append("Duplicate ingredient id: %s" % ingredient_id)
			continue
		ingredients.append(ingredient.duplicate(true))
		_ingredient_by_id[ingredient_id] = ingredient.duplicate(true)

	var raw_customers: Array = contract.get("customers", [])
	for raw_customer: Variant in raw_customers:
		if not raw_customer is Dictionary:
			errors.append("Every customer must be an object.")
			continue
		var customer: Dictionary = raw_customer
		var customer_id := String(customer.get("id", ""))
		var display_name := String(customer.get("display_name", ""))
		var order: Array = customer.get("order", [])
		if customer_id.is_empty() or display_name.is_empty():
			errors.append("Every customer needs id and display_name.")
			continue
		if order.size() != selection_size:
			errors.append(
				"Customer %s must request exactly %d ingredients."
				% [customer_id, selection_size]
			)
			continue
		var order_is_valid := true
		for ingredient_id: Variant in order:
			if not _ingredient_by_id.has(String(ingredient_id)):
				errors.append(
					"Customer %s references unknown ingredient %s."
					% [customer_id, String(ingredient_id)]
				)
				order_is_valid = false
		if order_is_valid:
			customers.append(customer.duplicate(true))

	if ingredients.size() < selection_size:
		errors.append("The shift needs at least selection_size ingredients.")
	if customers.is_empty():
		errors.append("The shift needs at least one valid customer.")
	return errors


func start_shift() -> void:
	assert(not customers.is_empty(), "Configure a valid shift before starting it.")
	selected_ingredients.clear()
	customer_index = 0
	customers_served = 0
	correct_orders = 0
	first_try_orders = 0
	shift_coins = 0
	shift_active = true
	current_attempt_is_first = true


func current_customer() -> Dictionary:
	if not shift_active or customer_index < 0 or customer_index >= customers.size():
		return {}
	return customers[customer_index]


func ingredient_ids() -> Array[String]:
	var result: Array[String] = []
	for ingredient: Dictionary in ingredients:
		result.append(String(ingredient.get("id", "")))
	return result


func ingredient_definition(ingredient_id: String) -> Dictionary:
	return _ingredient_by_id.get(ingredient_id, {})


func ingredient_display_name(ingredient_id: String) -> String:
	var ingredient := ingredient_definition(ingredient_id)
	return String(ingredient.get("display_name", ingredient_id.capitalize()))


func toggle_ingredient(ingredient_id: String) -> bool:
	if not shift_active or not _ingredient_by_id.has(ingredient_id):
		return false
	if selected_ingredients.has(ingredient_id):
		selected_ingredients.erase(ingredient_id)
		return true
	if selected_ingredients.size() >= selection_size:
		return false
	selected_ingredients.append(ingredient_id)
	return true


func can_serve() -> bool:
	return shift_active and selected_ingredients.size() == selection_size


func serve() -> Dictionary:
	if not can_serve():
		return {
			"accepted": false,
			"reason": "Select exactly %d ingredients." % selection_size,
		}

	var customer := current_customer()
	var requested: Array = customer.get("order", [])
	var is_correct := _same_ingredient_sequence(selected_ingredients, requested)
	var reward := (
		int(customer.get("reward", 0))
		if is_correct
		else wrong_order_reward
	)
	var result: Dictionary = {
		"accepted": true,
		"customer_id": String(customer.get("id", "")),
		"customer_name": String(customer.get("display_name", "")),
		"correct": is_correct,
		"reward": reward,
		"served": selected_ingredients.duplicate(),
		"requested": requested.duplicate(),
		"first_try": current_attempt_is_first,
	}

	if not is_correct:
		current_attempt_is_first = false
		result["shift_complete"] = false
		result["stars"] = star_rating()
		return result

	customers_served += 1
	correct_orders += 1
	if current_attempt_is_first:
		first_try_orders += 1
	shift_coins += reward
	lifetime_coins += reward
	selected_ingredients.clear()
	customer_index += 1
	var complete := customer_index >= customers.size()
	if complete:
		shift_active = false
	else:
		current_attempt_is_first = true
	result["shift_complete"] = complete
	result["stars"] = star_rating()
	return result


func star_rating() -> int:
	if customers.is_empty():
		return 0
	return clampi(first_try_orders, 0, 3)


func summary() -> Dictionary:
	return {
		"shift_id": shift_id,
		"served": customers_served,
		"total_customers": customers.size(),
		"correct": correct_orders,
		"first_try": first_try_orders,
		"stars": star_rating(),
		"shift_coins": shift_coins,
		"lifetime_coins": lifetime_coins,
	}


func _same_ingredient_sequence(left: Array[String], right: Array) -> bool:
	if left.size() != right.size():
		return false
	for index: int in range(left.size()):
		if left[index] != String(right[index]):
			return false
	return true
