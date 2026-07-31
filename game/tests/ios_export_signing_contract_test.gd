extends SceneTree

const EXPORT_PRESETS_PATH := "res://export_presets.cfg"
const PERSONAL_TEAM_ID := "53RJ43876F"
const PERSONAL_BUNDLE_ID := "com.mauvsantos.bentosaur"
const DEBUG_ICON_PATH := (
	"res://assets/branding/ios/bentosaur-ios-debug-icon-1024-v004.png"
)
const FORBIDDEN_MARKERS := [
	"274NNU52S8",
	"655H347X58",
	"mauricio@mellow.kids",
	"Mellow Kids",
	"NYMU5SBURP",
	"5FU6XCM55P",
]


func _initialize() -> void:
	var errors := PackedStringArray()
	var config := ConfigFile.new()
	var load_error := config.load(EXPORT_PRESETS_PATH)
	_expect(load_error == OK, "The iOS export preset must load.", errors)
	if load_error != OK:
		_finish(errors)
		return

	_expect(
		config.get_value("preset.0", "name", "") == "iOS",
		"The runnable preset must remain named iOS.",
		errors
	)
	_expect(
		config.get_value("preset.0", "platform", "") == "iOS",
		"The export platform must remain iOS.",
		errors
	)
	_expect(
		config.get_value("preset.0", "export_path", "")
			== "../build/ios/Bentosaur.xcodeproj",
		"The Xcode export must stay outside the Godot project.",
		errors
	)

	var options := "preset.0.options"
	_expect(
		config.get_value(options, "application/app_store_team_id", "")
			== PERSONAL_TEAM_ID,
		"Bentosaur must use the mauvsantos@gmail.com Personal Team.",
		errors
	)
	_expect(
		config.get_value(options, "application/bundle_identifier", "")
			== PERSONAL_BUNDLE_ID,
		"Bentosaur must keep its personal bundle identifier.",
		errors
	)
	_expect(
		config.get_value(options, "application/export_method_debug", -1) == 1,
		"Debug exports must use Apple's Development method.",
		errors
	)
	_expect(
		config.get_value(options, "application/export_project_only", false),
		"The initial export must generate an Xcode project.",
		errors
	)
	_expect(
		config.get_value(options, "application/targeted_device_family", -1) == 0,
		"The current device gate targets iPhone only.",
		errors
	)
	_expect(
		config.get_value(options, "application/min_ios_version", "") == "14.0",
		"The minimum iOS version must remain explicit.",
		errors
	)
	_expect(
		config.get_value(options, "icons/icon_1024x1024", "") == DEBUG_ICON_PATH,
		"The provisional opaque iOS icon must remain configured.",
		errors
	)

	for signing_key: String in [
		"application/code_sign_identity_debug",
		"application/code_sign_identity_release",
		"application/provisioning_profile_specifier_debug",
		"application/provisioning_profile_specifier_release",
	]:
		_expect(
			String(config.get_value(options, signing_key, "")).is_empty(),
			"%s must stay blank for automatic signing." % signing_key,
			errors
		)

	var raw_export_config := FileAccess.get_file_as_string(EXPORT_PRESETS_PATH)
	for marker: String in FORBIDDEN_MARKERS:
		_expect(
			not raw_export_config.contains(marker),
			"Forbidden company signing marker found in export settings.",
			errors
		)

	_expect(
		ProjectSettings.get_setting("application/config/icon", "") == DEBUG_ICON_PATH,
		"The project icon must match the iOS development icon.",
		errors
	)
	_expect(
		ProjectSettings.get_setting(
			"rendering/textures/vram_compression/import_etc2_astc",
			false
		),
		"iOS ETC2/ASTC texture import must remain enabled.",
		errors
	)
	_expect(
		ProjectSettings.get_setting("display/window/handheld/orientation", 0) == 1,
		"The iOS application must remain portrait.",
		errors
	)
	_finish(errors)


func _expect(condition: bool, message: String, errors: PackedStringArray) -> void:
	if not condition:
		errors.append(message)


func _finish(errors: PackedStringArray) -> void:
	if errors.is_empty():
		print("iOS personal-signing contract: PASS")
	else:
		for error: String in errors:
			push_error(error)
	quit(0 if errors.is_empty() else 1)
