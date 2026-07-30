# Visual Gate 04 — Textured Hero Candidate

**Candidate:** `bentosaur_vg04_h31_extreme_texture`  
**Tripo task:** `26811821-3e6d-4b62-a695-679275c04f60`  
**Rendered modes:** `basecolor, matte`  
**Geometry matches frozen reference:** `True`

This package separates texture truth from presentation:

- `basecolor`: the actual linked base-colour image goes directly to Emission,
  with Standard view transform, no lights, no floor, no normal/ORM maps, and
  no colour correction.
- `matte`: the same unchanged image goes directly to Principled Base Color,
  with metallic `0`, roughness `.82`, specular IOR level `.18`, no normal/ORM
  maps, soft neutral lights, and AgX.

The source import is locked and hidden. Renderable meshes are deep duplicates.
The evaluator changes material assignments only. It performs **no geometry,
face, mouth, smoothing, retopology, rigging, or animation edits**.

Evidence is in `boards/`, raw renders are in `renders/`, and deterministic
source/reference checks are in `metrics.json`. No `.blend` is saved or packed.

These images are evidence for the user's visual approval. The evaluator does
not approve the character.
