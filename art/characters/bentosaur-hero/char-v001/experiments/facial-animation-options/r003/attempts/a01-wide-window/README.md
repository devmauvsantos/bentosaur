# r003 Attempt 01 — Wide Static Mouth Window

Result: **best r003 attempt; visual gate failed; frozen**.

Parameters:

- outer window: `1.18 × 1.20` relative to the open-mouth boundary;
- four skin-transition loops;
- recessed cavity depth: approximately `0.031`;
- separate static tongue with all transforms applied;
- no new morphs or skinning.

What improved:

- no r002 cyan lower loop;
- tongue is contained by the aperture;
- actual cavity depth exists;
- profile no longer reads as a flat black sticker.

Why it failed:

- the separate skin transition has a visible outer seam;
- the seam is clearest in the three-quarter render;
- the duplicated body comparison also reports one coordinate change outside
  the original narrow audit window, so no strong outside-window preservation
  claim is made.

The exact recipe used is preserved in `recipes/`.
