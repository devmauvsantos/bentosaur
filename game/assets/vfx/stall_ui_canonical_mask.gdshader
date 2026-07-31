shader_type canvas_item;

// State plates were generated independently and their alpha silhouettes differ
// by a fraction of a pixel. Keep one canonical texture as the geometry source
// and take only the painted state color from this secondary sampler.
uniform sampler2D state_texture : source_color, filter_linear_mipmap;
uniform float pregrade_gamma : hint_range(0.05, 1.0) = 0.09;
uniform float pregrade_gain : hint_range(1.0, 1.4) = 1.06;


void fragment() {
	vec4 canonical = texture(TEXTURE, UV);
	vec4 state = texture(state_texture, UV);
	float state_coverage = smoothstep(0.02, 0.18, state.a);
	vec3 state_color = mix(canonical.rgb, state.rgb, state_coverage);
	// The approved anime transfer compresses dark painted wood. Pre-lift only
	// detachable UI plates so their final device values match the registered
	// proof while near-black outlines remain near black.
	state_color = pow(
		clamp(state_color, vec3(0.0), vec3(1.0)),
		vec3(pregrade_gamma)
	);
	state_color = clamp(
		state_color * pregrade_gain,
		vec3(0.0),
		vec3(1.0)
	);
	COLOR = vec4(state_color, canonical.a) * COLOR;
}
