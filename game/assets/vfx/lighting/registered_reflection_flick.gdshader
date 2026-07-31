shader_type canvas_item;
render_mode blend_add, unshaded;

uniform vec2 reflection_center = vec2(-1.0, -1.0);
uniform vec2 reflection_half_size = vec2(0.01, 0.01);
uniform float reflection_level : hint_range(0.0, 1.0) = 1.0;
uniform float global_intensity : hint_range(0.0, 1.0) = 1.0;


void fragment() {
	vec4 source = COLOR;
	source.rgb *= global_intensity;
	if (abs(reflection_level - 1.0) > 0.0001) {
		vec2 normalized_delta = abs(UV - reflection_center) / max(
			reflection_half_size,
			vec2(0.0001)
		);
		// Reject the rest of the Retina display before evaluating the rounded
		// shape. Constant fourth powers use multiplies and square roots instead
		// of three full-screen pow() calls during each brief flick.
		if (normalized_delta.x <= 1.0 && normalized_delta.y <= 1.0) {
			vec2 squared_delta = normalized_delta * normalized_delta;
			float fourth_sum = dot(squared_delta, squared_delta);
			float mask_distance = sqrt(sqrt(max(fourth_sum, 0.0)));
			float reflection_mask = 1.0 - smoothstep(
				0.78,
				1.0,
				mask_distance
			);
			source.rgb *= mix(1.0, reflection_level, reflection_mask);
		}
	}
	COLOR = source;
}
