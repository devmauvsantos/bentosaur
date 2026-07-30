# 3D Diorama Gameplay Exploration 02 — Engine Target

**Status:** Visual target for the Godot proof  
**Date:** July 29, 2026  
**Production approval:** None  
**Character approval:** None  
**Tripo credits used:** 0  
**Generation tool:** built-in ImageGen

## Result

`art/concepts/3d-diorama/bentosaur-gameplay-3d-diorama-engine-target-v2.png`

SHA-256:

`c17b087d84f960040844fca09d0f70d19d9b42ec39f5f7a868b0c1ec3c1505da`

This frame is an art and composition target, not a Godot screenshot. It tests
whether the original service loop can read as a fully 3D mobile diorama:

- a close front-facing customer at the stall;
- a warm wooden counter against a cool rainy street;
- multiple independent background dinosaur walkers;
- chunky, touch-readable bento ingredients;
- physical depth without turning the game into a free-camera adventure;
- a small, readable HUD integrated with the diorama framing.

## What this establishes

- Full 3D can preserve the intimate ramen-stall feeling.
- The customer remains the emotional focal point.
- The street can feel inhabited without redrawing seasonal background frames.
- Separate characters and props can be lit and recombined at runtime.
- The bento can remain tactile and legible on a vertical screen.
- Warm interior light versus cool exterior weather is a strong visual signature.

## What is deliberately not final

- This is not the approved Tripo/Blender character.
- The top-right portrait is generic and not canonical.
- The HUD is a readability placeholder, not the final design system.
- The request bubble and complete order-state UI still need a production pass.
- The exact ingredient set is illustrative.
- Background species, density, and camera depth are not locked.
- This image does not validate mobile performance, topology, rigging, skinning,
  animation, materials, or engine import.

## Reference-aware generation prompt

The generation used the original pixel gameplay composition and the approved
anatomy direction as references.

```text
Create an original full-3D vertical mobile-game screenshot for Bentosaur, a
cozy bento stall run for cute upright biped dinosaurs. Use the supplied
gameplay concept for composition and the supplied Triceratops model sheet only
for the canonical character anatomy and color identity.

Render a miniature handcrafted chibi diorama with rounded toy-like forms,
matte clay and lacquered wood materials, soft ambient occlusion, warm amber
lanterns, and a cool indigo rainy street. The camera is fixed and mostly
frontal with a gentle top-down view of the counter. A delighted sage-green
baby Triceratops customer stands front-facing at the stall. It has a cream
belly, horns, frill knobs and claws, coral cheeks, short biped legs, small
rounded paws, and a readable expressive face. The character wears no clothes
and has no fused prop.

Show several separate dinosaur pedestrians alive in the rainy street behind
the customer, with wet reflections, lantern pools, steam, plants, condiment
bottles, and layered depth. In the foreground show a red three-compartment
bento and four large touch-readable ingredient bins. Include a restrained
cozy HUD at the top: coins, a three-step progress meter, and customer mood.

The image should look achievable in a real-time Godot mobile scene: simple
opaque stylized materials, controlled light count, modest geometry, readable
silhouettes, and depth of field restricted to the far background. Preserve
the heart and intimacy of a rainy neighborhood food stall.

Do not copy any franchise character, logo, UI, icon, asset, or world. Do not
use pixel-art filtering, photorealism, text-heavy menus, extra limbs, clothes,
an umbrella, a tray, a bento fused to the character, or a cropped interface.
```

## Runtime reproduction notes

- Start with an orthographic or very-low-FOV `Camera3D`.
- Use one shadowed warm key light and bake/fake most fill.
- Use opaque stylized materials before adding transparency or outlines.
- Keep distant street actors on cheaper LODs and lower animation update rates.
- Build rain from a bounded particle volume and cheap wetness/reflection fakes.
- Place the HUD and book in Godot's UI layer; keep imported art independent.
- Compare the running result against this frame at the same vertical crop.

