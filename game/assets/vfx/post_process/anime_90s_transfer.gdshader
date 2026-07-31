// Bentosaur adaptation of the purchased "Godot 4 Project - Shader Studies v1".
// Creator: OrdinaryCicada
// Source: https://oddpotatodev.itch.io/godot-46-shader-studies-v1
// Preset 3 (Heavy transfer) approved for the home menu on 2026-07-31.

shader_type canvas_item;
render_mode blend_disabled, unshaded;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap, repeat_disable;


// ─────────────────────────────────────────────
//  LENS DISTORTION
// ─────────────────────────────────────────────

group_uniforms Lens_Distortion;
uniform float curvature          : hint_range(0.0, 1.0) = 0.15;
uniform float vignette_intensity : hint_range(0.0, 1.0) = 0.4;


// ─────────────────────────────────────────────
//  ANALOG GLITCH
// ─────────────────────────────────────────────

group_uniforms Analog_Glitch;
uniform float scanline_opacity : hint_range(0.0, 1.0)    = 0.15;
uniform float scanline_count   : hint_range(0.0, 1080.0) = 540.0;
uniform float noise_intensity  : hint_range(0.0, 1.0)    = 0.08;
uniform float aberration       : hint_range(0.0, 0.1)    = 0.003;


// ─────────────────────────────────────────────
//  GLOW & COLOR
// ─────────────────────────────────────────────

group_uniforms Glow_and_Color;
uniform float brightness : hint_range(0.0, 2.0) = 1.1;
uniform float saturation : hint_range(0.0, 2.0) = 1.2;
uniform float glow_bleed : hint_range(0.0, 2.0) = 0.5;


// ─────────────────────────────────────────────
//  COLOR GRADING
// ─────────────────────────────────────────────

group_uniforms Color_Grading;
uniform float temperature : hint_range(-1.0, 1.0) = 0.0;
uniform float tint        : hint_range(-1.0, 1.0) = 0.0;


// ─────────────────────────────────────────────
//  SHARPENING
// ─────────────────────────────────────────────

group_uniforms Sharpening;
uniform float sharpen_amount     : hint_range(0.0, 3.0) = 0.0;
uniform float highlights_sharpen : hint_range(0.0, 3.0) = 0.0;


// ─────────────────────────────────────────────
//  LUMA CURVES
// ─────────────────────────────────────────────

group_uniforms LUMA_Curves;
uniform sampler2D luma_curve     : hint_default_white, filter_linear, repeat_disable;
uniform float     curve_strength : hint_range(0.0, 1.0) = 1.0;


// ─────────────────────────────────────────────
//  UTILITY
// ─────────────────────────────────────────────

vec2 curve_uv(vec2 uv) {
	uv = uv * 2.0 - 1.0;
	vec2 offset = abs(uv.yx) / vec2(6.0, 4.0);
	uv = uv + uv * offset * offset * curvature;
	return uv * 0.5 + 0.5;
}

float random(vec2 uv) {
	return fract(sin(dot(uv.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

float transfer_grain(vec2 uv, float luma) {
	float transfer_frame = floor(TIME * 12.0);
	vec2 screen_pixel_size = 1.0 / vec2(textureSize(screen_texture, 0));
	vec2 pixel = floor((uv / screen_pixel_size) / 1.25);
	float fine_grain = random(pixel + vec2(transfer_frame * 17.0, transfer_frame * 31.0));
	float grain_mask = smoothstep(0.025, 0.16, luma);
	grain_mask *= 1.0 - 0.32 * smoothstep(0.72, 1.0, luma);
	return (fine_grain - 0.5) * grain_mask;
}

vec3 safe_sample(sampler2D tex, vec2 uv) {
	return texture(tex, clamp(uv, vec2(0.0), vec2(1.0))).rgb;
}

vec3 apply_sharpen(vec2 uv, float amount, vec2 texel_size) {
	if (amount <= 0.0) {
		return safe_sample(screen_texture, uv);
	}
	amount = clamp(amount, 0.0, 1.0);

	vec3 color = safe_sample(screen_texture, uv) * (1.0 + 8.0 * amount);
	color -= safe_sample(screen_texture, uv + vec2(-texel_size.x,  0.0))          * amount;
	color -= safe_sample(screen_texture, uv + vec2( texel_size.x,  0.0))          * amount;
	color -= safe_sample(screen_texture, uv + vec2( 0.0, -texel_size.y))          * amount;
	color -= safe_sample(screen_texture, uv + vec2( 0.0,  texel_size.y))          * amount;
	color -= safe_sample(screen_texture, uv + vec2(-texel_size.x, -texel_size.y)) * amount;
	color -= safe_sample(screen_texture, uv + vec2( texel_size.x, -texel_size.y)) * amount;
	color -= safe_sample(screen_texture, uv + vec2(-texel_size.x,  texel_size.y)) * amount;
	color -= safe_sample(screen_texture, uv + vec2( texel_size.x,  texel_size.y)) * amount;

	return clamp(color, vec3(0.0), vec3(1.0));
}

vec3 apply_temp_tint(vec3 color, float temp, float tint_amount) {
	temp = clamp(temp, -1.0, 1.0);
	tint_amount = clamp(tint_amount, -1.0, 1.0);

	color.r += temp * 0.3;
	color.b -= temp * 0.3;
	color.g -= tint_amount * 0.3;
	color.r += tint_amount * 0.15;
	color.b += tint_amount * 0.15;

	return clamp(color, vec3(0.0), vec3(1.0));
}

vec3 apply_luma_curve(vec3 color, sampler2D curve_tex, float strength) {
	if (strength <= 0.0) {
		return color;
	}
	strength = clamp(strength, 0.0, 1.0);

	float luma = clamp(dot(color, vec3(0.299, 0.587, 0.114)), 0.0, 1.0);
	float adjusted_luma = clamp(texture(curve_tex, vec2(luma, 0.5)).r, 0.0, 1.0);
	adjusted_luma = mix(luma, adjusted_luma, strength);

	return clamp(color * (adjusted_luma / max(luma, 0.001)), vec3(0.0), vec3(1.0));
}


// ─────────────────────────────────────────────
//  FRAGMENT
// ─────────────────────────────────────────────

void fragment() {
	vec2 uv = curve_uv(SCREEN_UV);

	if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0) {
		COLOR = vec4(0.0, 0.0, 0.0, 1.0);
	} else {
		vec2 texel_size = 1.0 / vec2(textureSize(screen_texture, 0));

		vec3 color = clamp(vec3(
			safe_sample(screen_texture, uv + vec2(aberration, 0.0)).r,
			safe_sample(screen_texture, uv).g,
			safe_sample(screen_texture, uv - vec2(aberration, 0.0)).b
		), vec3(0.0), vec3(1.0));

		color = clamp(
			color
				+ textureLod(screen_texture, uv, 2.0).rgb
				* clamp(glow_bleed, 0.0, 2.0)
				* 0.2,
			vec3(0.0),
			vec3(1.0)
		);

		if (sharpen_amount > 0.0) {
			color = apply_sharpen(uv, sharpen_amount, texel_size);
		}

		color = max(
			color
				- (sin(uv.y * scanline_count * 3.14159) * 0.5 + 0.5)
				* clamp(scanline_opacity, 0.0, 1.0),
			vec3(0.0)
		);

		float pre_grain_luma = dot(color, vec3(0.299, 0.587, 0.114));
		color = clamp(
			color
				+ transfer_grain(uv, pre_grain_luma)
				* clamp(noise_intensity, 0.0, 1.0),
			vec3(0.0),
			vec3(1.0)
		);

		color = clamp(
			color * clamp(brightness, 0.0, 2.0),
			vec3(0.0),
			vec3(1.0)
		);

		color = apply_temp_tint(color, temperature, tint);
		color = clamp(
			mix(
				vec3(dot(color, vec3(0.299, 0.587, 0.114))),
				color,
				clamp(saturation, 0.0, 2.0)
			),
			vec3(0.0),
			vec3(1.0)
		);

		color = apply_luma_curve(color, luma_curve, curve_strength);

		if (highlights_sharpen > 0.0) {
			float luma = clamp(
				dot(color, vec3(0.299, 0.587, 0.114)),
				0.0,
				1.0
			);
			if (luma > 0.5) {
				color = clamp(
					mix(
						color,
						apply_sharpen(uv, highlights_sharpen, texel_size),
						smoothstep(0.5, 1.0, luma)
					),
					vec3(0.0),
					vec3(1.0)
				);
			}
		}

		float vignette_edge = smoothstep(
			0.35,
			0.72,
			distance(SCREEN_UV, vec2(0.5))
		);
		color *= 1.0 - clamp(vignette_intensity, 0.0, 1.0) * vignette_edge;

		COLOR = vec4(clamp(color, vec3(0.0), vec3(1.0)), 1.0);
	}
}
