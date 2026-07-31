extends SceneTree

const RUNTIME_ROOT := (
	"res://assets/environments/home_village/v001/stall/attachments/v004"
)
const MANIFEST_PATH := RUNTIME_ROOT + "/runtime_manifest.json"
const MANIFEST_OUTPUT_PREFIX := (
	"game/assets/environments/home_village/v001/stall/attachments/v004/"
)
const EXPECTED_ASSET_COUNT := 31
const EXPECTED_PNGS := [
	"bottle_crate/bottle_brown_v001.png",
	"bottle_crate/bottle_crate_empty_v001.png",
	"bottle_crate/bottle_cream_blue_cap_v001.png",
	"bottle_crate/bottle_green_v001.png",
	"counter_cloth/counter_cloth_red_draped_v001.png",
	"counter_lantern/counter-oil-lantern-body-off-v001.png",
	"counter_lantern/counter-oil-lantern-contact-shadow-v001.png",
	"counter_lantern/counter-oil-lantern-core-add-v001.png",
	"counter_lantern/counter-oil-lantern-halo-add-v001.png",
	"counter_plant/counter_plant_foliage_v001.png",
	"counter_plant/counter_plant_pot_v001.png",
	"food_bowl/grape-food-bowl-v001.png",
	"stockpot/stall_stockpot_body_open_v001.png",
	"stockpot/stall_stockpot_contact_shadow_v001.png",
	"stockpot/stall_stockpot_lid_v001.png",
	"ui/buttons/menu-button-leaf-left-v001.png",
	"ui/buttons/menu-button-leaf-right-v001.png",
	"ui/buttons/menu-button-primary-disabled-v001.png",
	"ui/buttons/menu-button-primary-normal-v001.png",
	"ui/buttons/menu-button-primary-pressed-v001.png",
	"ui/buttons/menu-button-primary-selected-v001.png",
	"ui/buttons/menu-button-secondary-disabled-v001.png",
	"ui/buttons/menu-button-secondary-normal-v001.png",
	"ui/buttons/menu-button-secondary-pressed-v001.png",
	"ui/buttons/menu-button-secondary-selected-v001.png",
	"ui/rank/rank-plaque-empty-sockets-v001.png",
	"ui/rank/rank-star-empty-v001.png",
	"ui/rank/rank-star-filled-v001.png",
	"ui/rank/rank-star-shine-v001.png",
	"ui/settings/settings-cog-normal-v001.png",
	"ui/settings/settings-cog-pressed-v001.png",
]
const FORBIDDEN_RUNTIME_PATHS := [
	"stockpot/stall_stockpot_assembled_preview_v001.png",
	"bottle_crate/bottle_crate_assembled_preview_v001.png",
	"ui/rank/rank-plaque-empty-sockets-v002.png",
	"ui/rank/rank-plaque-kit-v002.png",
	"ui/rank/rank-plaque-face-recolor-mask-v002.png",
]
const EXPECTED_TEXTURE_SIZES := {
	"stockpot/stall_stockpot_body_open_v001.png": Vector2i(172, 184),
	"stockpot/stall_stockpot_lid_v001.png": Vector2i(180, 98),
	"counter_lantern/counter-oil-lantern-body-off-v001.png": Vector2i(126, 230),
	"counter_lantern/counter-oil-lantern-core-add-v001.png": Vector2i(62, 116),
	"counter_lantern/counter-oil-lantern-halo-add-v001.png": Vector2i(220, 292),
	"food_bowl/grape-food-bowl-v001.png": Vector2i(132, 132),
	"counter_plant/counter_plant_foliage_v001.png": Vector2i(122, 308),
	"bottle_crate/bottle_crate_empty_v001.png": Vector2i(234, 177),
	"counter_cloth/counter_cloth_red_draped_v001.png": Vector2i(194, 240),
	"ui/rank/rank-plaque-empty-sockets-v001.png": Vector2i(456, 96),
	"ui/buttons/menu-button-primary-normal-v001.png": Vector2i(692, 410),
	"ui/buttons/menu-button-primary-pressed-v001.png": Vector2i(692, 410),
	"ui/buttons/menu-button-secondary-normal-v001.png": Vector2i(692, 410),
	"ui/settings/settings-cog-normal-v001.png": Vector2i(150, 168),
	"ui/settings/settings-cog-pressed-v001.png": Vector2i(150, 168),
}

const FONT_ROOT := "res://assets/fonts/lilita_one"
const FONT_PATH := FONT_ROOT + "/LilitaOne-Regular.ttf"
const FONT_LICENSE_PATH := FONT_ROOT + "/OFL.txt"
const FONT_METADATA_PATH := FONT_ROOT + "/METADATA.pb"
const FONT_README_PATH := FONT_ROOT + "/README.md"
const FONT_SHA256 := (
	"f5b641c45c69d772ee4eda687bc9fda411d5cad6b0b45371491da4580cbc8d59"
)


func _initialize() -> void:
	var errors := PackedStringArray()
	_validate_manifest(errors)
	_validate_runtime_inventory(errors)
	_validate_key_texture_dimensions(errors)
	_validate_separately_licensed_font(errors)
	_finish(errors)


func _validate_manifest(errors: PackedStringArray) -> void:
	_expect(FileAccess.file_exists(MANIFEST_PATH), "V004 runtime manifest is missing.", errors)
	if not FileAccess.file_exists(MANIFEST_PATH):
		return

	var manifest_text := FileAccess.get_file_as_string(MANIFEST_PATH)
	var parsed: Variant = JSON.parse_string(manifest_text)
	_expect(typeof(parsed) == TYPE_DICTIONARY, "V004 runtime manifest must parse as JSON.", errors)
	if typeof(parsed) != TYPE_DICTIONARY:
		return

	var manifest: Dictionary = parsed
	_expect(
		manifest.get("status", "") == "founder_approved_runtime_derivatives",
		"V004 runtime manifest must retain founder-approved status.",
		errors
	)
	_expect(
		int(manifest.get("asset_count", -1)) == EXPECTED_ASSET_COUNT,
		"V004 runtime manifest must declare exactly 31 assets.",
		errors
	)
	var asset_entries: Array = manifest.get("assets", [])
	_expect(
		asset_entries.size() == EXPECTED_ASSET_COUNT,
		"V004 runtime manifest asset list must contain exactly 31 entries.",
		errors
	)

	var manifest_outputs := PackedStringArray()
	for asset_variant: Variant in asset_entries:
		_expect(
			typeof(asset_variant) == TYPE_DICTIONARY,
			"Every V004 runtime manifest asset entry must be an object.",
			errors
		)
		if typeof(asset_variant) != TYPE_DICTIONARY:
			continue
		var asset: Dictionary = asset_variant
		manifest_outputs.append(String(asset.get("output", "")))

	var expected_outputs := PackedStringArray()
	for relative_path: String in EXPECTED_PNGS:
		expected_outputs.append(MANIFEST_OUTPUT_PREFIX + relative_path)
	_validate_exact_paths(
		manifest_outputs,
		expected_outputs,
		"runtime manifest outputs",
		errors
	)


func _validate_runtime_inventory(errors: PackedStringArray) -> void:
	var actual_pngs := _collect_pngs(RUNTIME_ROOT)
	var expected_pngs := PackedStringArray(EXPECTED_PNGS)
	_validate_exact_paths(actual_pngs, expected_pngs, "runtime PNG inventory", errors)

	for relative_path: String in actual_pngs:
		_expect(
			not relative_path.contains("assembled_preview"),
			"Review-only assembled preview entered runtime: %s" % relative_path,
			errors
		)
		_expect(
			not relative_path.contains("v002"),
			"Rejected V002 art entered runtime: %s" % relative_path,
			errors
		)
	for relative_path: String in FORBIDDEN_RUNTIME_PATHS:
		_expect(
			not FileAccess.file_exists(RUNTIME_ROOT.path_join(relative_path)),
			"Forbidden source-review asset entered runtime: %s" % relative_path,
			errors
		)

	for relative_path: String in _collect_files(RUNTIME_ROOT):
		var extension := relative_path.get_extension().to_lower()
		_expect(
			not extension in ["ttf", "otf", "woff", "woff2"],
			"Font binaries must remain outside the V004 attachment pack.",
			errors
		)


func _validate_key_texture_dimensions(errors: PackedStringArray) -> void:
	for relative_path: String in EXPECTED_TEXTURE_SIZES:
		var texture_path := RUNTIME_ROOT.path_join(relative_path)
		var texture := load(texture_path) as Texture2D
		_expect(texture != null, "Runtime texture must load: %s" % relative_path, errors)
		if texture != null:
			var expected_size: Vector2i = EXPECTED_TEXTURE_SIZES[relative_path]
			_expect(
				texture.get_size() == Vector2(expected_size),
				"Runtime texture dimensions changed for %s. Expected %s, got %s."
					% [relative_path, expected_size, texture.get_size()],
				errors
			)


func _validate_separately_licensed_font(errors: PackedStringArray) -> void:
	_expect(
		not FONT_ROOT.begins_with(RUNTIME_ROOT),
		"Live label font must remain separate from the attachment pack.",
		errors
	)
	for required_path: String in [
		FONT_PATH,
		FONT_LICENSE_PATH,
		FONT_METADATA_PATH,
		FONT_README_PATH,
	]:
		_expect(FileAccess.file_exists(required_path), "Missing licensed font file: %s" % required_path, errors)

	if FileAccess.file_exists(FONT_PATH):
		_expect(
			FileAccess.get_sha256(FONT_PATH) == FONT_SHA256,
			"Lilita One font binary hash changed without a license review.",
			errors
		)
		_expect(load(FONT_PATH) is FontFile, "Lilita One runtime font must load.", errors)
	if FileAccess.file_exists(FONT_LICENSE_PATH):
		var license_text := FileAccess.get_file_as_string(FONT_LICENSE_PATH)
		_expect(
			license_text.contains("SIL OPEN FONT LICENSE Version 1.1"),
			"Lilita One must retain its SIL Open Font License 1.1 text.",
			errors
		)
	if FileAccess.file_exists(FONT_README_PATH):
		var readme := FileAccess.get_file_as_string(FONT_README_PATH)
		_expect(readme.contains("OFL.txt"), "Font README must link its license file.", errors)
		_expect(readme.contains(FONT_SHA256), "Font README must record the binary hash.", errors)
		_expect(
			readme.contains("github.com/google/fonts/tree/main/ofl/lilitaone"),
			"Font README must preserve the official upstream source.",
			errors
		)


func _collect_pngs(root_path: String) -> PackedStringArray:
	var files := _collect_files(root_path)
	var pngs := PackedStringArray()
	for relative_path: String in files:
		if relative_path.get_extension().to_lower() == "png":
			pngs.append(relative_path)
	return pngs


func _collect_files(root_path: String, relative_path := "") -> PackedStringArray:
	var results := PackedStringArray()
	var directory_path := root_path
	if not relative_path.is_empty():
		directory_path = root_path.path_join(relative_path)
	var directory := DirAccess.open(directory_path)
	if directory == null:
		return results

	directory.list_dir_begin()
	var entry := directory.get_next()
	while not entry.is_empty():
		if entry == "." or entry == "..":
			entry = directory.get_next()
			continue
		var child_relative := entry
		if not relative_path.is_empty():
			child_relative = relative_path.path_join(entry)
		if directory.current_is_dir():
			results.append_array(_collect_files(root_path, child_relative))
		else:
			results.append(child_relative)
		entry = directory.get_next()
	directory.list_dir_end()
	results.sort()
	return results


func _validate_exact_paths(
	actual: PackedStringArray,
	expected: PackedStringArray,
	label: String,
	errors: PackedStringArray
) -> void:
	actual.sort()
	expected.sort()
	_expect(
		actual.size() == expected.size(),
		"Expected %d %s, found %d."
			% [expected.size(), label, actual.size()],
		errors
	)
	var shared_count := mini(actual.size(), expected.size())
	for index: int in range(shared_count):
		_expect(
			actual[index] == expected[index],
			"Unexpected %s entry at %d. Expected %s, got %s."
				% [label, index, expected[index], actual[index]],
			errors
		)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("Stall attachment asset contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
