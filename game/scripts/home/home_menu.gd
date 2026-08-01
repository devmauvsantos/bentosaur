class_name BentosaurHomeMenu
extends Node2D

signal open_stall_requested
signal guestbook_requested
signal decorations_requested
signal pantry_requested
signal settings_requested

@onready var attachment_kit: StallAttachmentKit = (
	$WorldCanvas/ApprovedStallComposition/StallStage/StallAttachmentKit
)
@onready var main_character: BentosaurProprietorIdle = (
	$WorldCanvas/ApprovedStallComposition/StallStage/MainCharacter
)
@onready var foreground_relight: StallForegroundRelight = (
	$WorldCanvas/ApprovedStallComposition/StallStage/ForegroundRelight
)
@onready var stall_lantern_left: StallLanternFixture = (
	$WorldCanvas/ApprovedStallComposition/StallStage/StallLanternLeft
)
@onready var stall_lantern_right: StallLanternFixture = (
	$WorldCanvas/ApprovedStallComposition/StallStage/StallLanternRight
)


func _ready() -> void:
	attachment_kit.open_stall_requested.connect(open_stall_requested.emit)
	attachment_kit.guestbook_requested.connect(guestbook_requested.emit)
	attachment_kit.decorations_requested.connect(decorations_requested.emit)
	attachment_kit.pantry_requested.connect(pantry_requested.emit)
	attachment_kit.settings_requested.connect(settings_requested.emit)
	if OS.get_cmdline_user_args().has("--lantern-tap-proof"):
		call_deferred("_run_lantern_tap_proof")


func set_reduced_motion(enabled: bool) -> void:
	attachment_kit.set_reduced_motion(enabled)
	main_character.set_reduced_motion(enabled)


func set_rank(value: int, animate: bool = true) -> void:
	attachment_kit.set_rank(value, animate)


func set_stockpot_active(enabled: bool) -> void:
	attachment_kit.set_stockpot_active(enabled)


func set_foreground_relight_enabled(enabled: bool) -> void:
	foreground_relight.set_enabled(enabled)


func is_foreground_relight_enabled() -> bool:
	return foreground_relight.is_enabled()


func set_practical_lights_powered(
	enabled: bool,
	immediate: bool = false
) -> void:
	attachment_kit.set_all_practical_lights_powered(enabled, immediate)


func _run_lantern_tap_proof() -> void:
	# Capture-only choreography; production interaction remains touch-driven.
	await get_tree().create_timer(0.75).timeout
	stall_lantern_left.try_tap_interaction()
	await get_tree().create_timer(1.75).timeout
	stall_lantern_right.try_tap_interaction()
	await get_tree().create_timer(1.75).timeout
	stall_lantern_left.try_tap_interaction()
