shader_type canvas_item;

uniform float shadow_strength : hint_range(0.0, 0.20) = 0.075;
uniform float shadow_start : hint_range(0.0, 1.0) = 0.52;
uniform float shadow_end : hint_range(0.0, 1.0) = 0.88;
uniform vec3 shadow_tint : source_color = vec3(0.64, 0.72, 0.84);


void fragment() {
	vec4 source = COLOR;
	float lower_falloff = smoothstep(shadow_start, shadow_end, UV.y);
	float opaque_surface = smoothstep(0.02, 0.35, source.a);
	float influence = lower_falloff * opaque_surface * shadow_strength;
	source.rgb = mix(source.rgb, source.rgb * shadow_tint, influence);
	COLOR = source;
}
