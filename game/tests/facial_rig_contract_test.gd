extends SceneTree

const MODEL_PATH := "res://assets/characters/bentosaur_hero/v002/bentosaur_hero_facial_mobile_proof_v002.glb"
const REQUIRED_SHAPES: Array[StringName] = [
	&"Mouth_DelightedOpen",
	&"Mouth_CloseCorrective",
	&"Chew_Compress",
	&"Blink_L",
	&"Blink_R",
	&"HappyEyes",
	&"Tongue_Retract",
	&"Tongue_Chew",
]
const REQUIRED_BONES: Array[StringName] = [&"root", &"jaw", &"tongue"]
const MAXIMUM_TRIANGLES := 35_000


func _initialize() -> void:
	var errors: PackedStringArray = []
	var report: Dictionary = {
		"engine": Engine.get_version_info(),
		"renderer": ProjectSettings.get_setting("rendering/renderer/rendering_method", ""),
		"model": MODEL_PATH,
	}

	if not ResourceLoader.exists(MODEL_PATH):
		errors.append("Missing imported GLB: %s" % MODEL_PATH)
		_finish(errors, report)
		return

	var packed: PackedScene = load(MODEL_PATH) as PackedScene
	if packed == null:
		errors.append("GLB did not import as PackedScene.")
		_finish(errors, report)
		return

	var character: Node = packed.instantiate()
	root.add_child(character)
	var meshes: Array[MeshInstance3D] = []
	var skeletons: Array[Skeleton3D] = []
	_collect_nodes(character, meshes, skeletons)

	var shape_counts: Dictionary = {}
	for shape_name: StringName in REQUIRED_SHAPES:
		var matches: int = 0
		for mesh_instance: MeshInstance3D in meshes:
			var index: int = mesh_instance.find_blend_shape_by_name(shape_name)
			if index < 0:
				continue
			matches += 1
			mesh_instance.set_blend_shape_value(index, 0.5)
			if not is_equal_approx(mesh_instance.get_blend_shape_value(index), 0.5):
				errors.append("Blend shape cannot be set/read: %s" % shape_name)
			mesh_instance.set_blend_shape_value(index, 0.0)
		shape_counts[String(shape_name)] = matches
		if matches == 0:
			errors.append("Missing blend shape: %s" % shape_name)

	var skeleton: Skeleton3D = skeletons.front() if not skeletons.is_empty() else null
	var bone_report: Dictionary = {}
	if skeleton == null:
		errors.append("No Skeleton3D found.")
	else:
		for bone_name: StringName in REQUIRED_BONES:
			var index: int = skeleton.find_bone(String(bone_name))
			bone_report[String(bone_name)] = index
			if index < 0:
				errors.append("Missing bone: %s" % bone_name)

	var triangles: int = _triangle_count(meshes)
	if triangles > MAXIMUM_TRIANGLES:
		errors.append("Triangle count %d exceeds %d." % [triangles, MAXIMUM_TRIANGLES])
	if report["renderer"] != "mobile":
		errors.append("Project renderer is not Mobile.")

	var controller := BentosaurFacialRigController.new()
	root.add_child(controller)
	var controller_errors: PackedStringArray = controller.bind(character)
	errors.append_array(controller_errors)
	for mode: BentosaurFacialRigController.MouthMode in [
		BentosaurFacialRigController.MouthMode.MORPH_ONLY,
		BentosaurFacialRigController.MouthMode.BONE_ONLY,
		BentosaurFacialRigController.MouthMode.HYBRID,
	]:
		controller.set_mouth_mode(mode)
		controller.set_mouth_open(0.5)
	controller.set_happy_eyes(1.0)
	controller.set_blink_left(1.0)
	controller.set_blink_right(1.0)
	controller.set_chew_enabled(true)
	controller.apply_controls()

	report["mesh_count"] = meshes.size()
	report["triangles"] = triangles
	var mesh_report: Dictionary = {}
	for mesh_instance: MeshInstance3D in meshes:
		var bounds: AABB = mesh_instance.get_aabb()
		mesh_report[String(mesh_instance.name)] = {
			"aabb_position": bounds.position,
			"aabb_size": bounds.size,
			"blend_shape_count": mesh_instance.get_blend_shape_count(),
		}
	report["meshes"] = mesh_report
	report["shape_bindings"] = shape_counts
	report["skeleton_count"] = skeletons.size()
	report["bones"] = bone_report
	report["controller"] = controller.get_contract_report()
	report["locked_engine_target"] = "4.7.1"
	report["engine_version_note"] = (
		"Validated with installed 4.7-stable; upgrade to locked 4.7.1 before production gate."
	)
	_finish(errors, report)


func _collect_nodes(
	node: Node,
	meshes: Array[MeshInstance3D],
	skeletons: Array[Skeleton3D]
) -> void:
	if node is MeshInstance3D:
		meshes.append(node as MeshInstance3D)
	elif node is Skeleton3D:
		skeletons.append(node as Skeleton3D)
	for child: Node in node.get_children():
		_collect_nodes(child, meshes, skeletons)


func _triangle_count(meshes: Array[MeshInstance3D]) -> int:
	var total: int = 0
	for mesh_instance: MeshInstance3D in meshes:
		if mesh_instance.mesh == null:
			continue
		for surface_index: int in range(mesh_instance.mesh.get_surface_count()):
			var arrays: Array = mesh_instance.mesh.surface_get_arrays(surface_index)
			var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
			if not indices.is_empty():
				total += indices.size() / 3
			else:
				var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
				total += vertices.size() / 3
	return total


func _finish(errors: PackedStringArray, report: Dictionary) -> void:
	report["errors"] = errors
	report["passed"] = errors.is_empty()
	var serialized: String = JSON.stringify(report, "\t") + "\n"
	var report_file := FileAccess.open(
		"res://docs/facial_rig_contract_report.json",
		FileAccess.WRITE
	)
	if report_file != null:
		report_file.store_string(serialized)
	print(serialized)
	quit(0 if errors.is_empty() else 1)
