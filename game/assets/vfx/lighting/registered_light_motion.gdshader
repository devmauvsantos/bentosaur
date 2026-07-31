shader_type canvas_item;
render_mode blend_add, unshaded;

uniform vec2 flick_center = vec2(-1.0, -1.0);
uniform float flick_radius : hint_range(0.0, 0.25) = 0.06;
uniform float flick_level : hint_range(0.90, 1.05) = 1.0;
uniform vec2 uv_aspect_scale = vec2(1.0, 1.7777778);


void fragment() {
	vec4 source = COLOR;
	// The expensive mask path is active for only ~0.25 s per minute. This
	// uniform branch keeps ordinary 60/120 Hz frames as cheap as the base layer.
	if (abs(flick_level - 1.0) > 0.0001) {
		vec2 fixture_delta = (UV - flick_center) * uv_aspect_scale;
		float fixture_mask = 1.0 - smoothstep(
			flick_radius * 0.35,
			flick_radius,
			length(fixture_delta)
		);
		source.a *= mix(1.0, flick_level, fixture_mask);
	}
	COLOR = source;
}
