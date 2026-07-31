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


func _ready() -> void:
	attachment_kit.open_stall_requested.connect(open_stall_requested.emit)
	attachment_kit.guestbook_requested.connect(guestbook_requested.emit)
	attachment_kit.decorations_requested.connect(decorations_requested.emit)
	attachment_kit.pantry_requested.connect(pantry_requested.emit)
	attachment_kit.settings_requested.connect(settings_requested.emit)


func set_reduced_motion(enabled: bool) -> void:
	attachment_kit.set_reduced_motion(enabled)


func set_rank(value: int, animate: bool = true) -> void:
	attachment_kit.set_rank(value, animate)


func set_stockpot_active(enabled: bool) -> void:
	attachment_kit.set_stockpot_active(enabled)


func set_practical_lights_powered(
	enabled: bool,
	immediate: bool = false
) -> void:
	attachment_kit.set_all_practical_lights_powered(enabled, immediate)
