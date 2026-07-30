# P1 mouth-construction prototype

Status: **geometry prototype — not production retopology**

This pass answers one narrow question: can the accepted P1 silhouette support a
real toothless open smile with depth, a dark mouth cavity, and a separate
tongue without altering the raw Tripo GLB?

The generated Blender file contains:

- the original imported source in `00_SOURCE_LOCKED_DO_NOT_EDIT`;
- an untouched neutral reference copy;
- a disposable P1-derived mouth prototype;
- a real Boolean-carved cavity rather than a flat card or painted mouth;
- a separate coral tongue;
- a separate volumetric lip-rim diagnostic.

The Boolean boundary, lip rim, and tongue are construction evidence only. They
do **not** constitute production facial topology. A shippable character still
requires deformation-friendly retopology, concentric lip loops, a connected
mouth bag, jaw weighting, shape keys, and closed/open/chewing deformation QA.

The full-character front and three-quarter renders are visually reviewable for
the proposed toothless smile volume. The magnified close-up intentionally
exposes a thin fitting/seam artifact from mapping the smooth mouth insert onto
P1's irregular triangulated muzzle. It is evidence for why the mouth can be
built and why the lower face must still be retopologized; it is not an
appearance-approval render.

The build script is:

`tools/blender/build_p1_mouth_prototype.py`
