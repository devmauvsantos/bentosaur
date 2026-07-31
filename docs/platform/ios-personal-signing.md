# Bentosaur iOS Personal Signing Contract

**Scope:** personal Bentosaur development only

## Allowed identity

- Apple account: `mauvsantos@gmail.com`
- Xcode team: Personal Team
- Team ID: `53RJ43876F`
- Development certificate observed locally:
  `Apple Development: Mauricio Vargas (CRAZV8U43J)`
- Bundle identifier: `com.mauvsantos.bentosaur`
- Provisioning mode: Xcode automatic signing

The certificate name and provisioning-profile UUID are deliberately not pinned
inside `export_presets.cfg`. Godot writes `CODE_SIGN_STYLE=Automatic` when the
identity and provisioning fields are blank. The Team ID is the authoritative
boundary that keeps Xcode on the personal team.

## Forbidden identities

Never sign, provision, archive, upload, or run Bentosaur using:

- Team `274NNU52S8` — Mellow Kids AB
- Team `655H347X58` — Personal Team associated with
  `mauricio@mellow.kids`
- A certificate containing `NYMU5SBURP` or `5FU6XCM55P`
- Any Mellow Kids distribution certificate

`game/tests/ios_export_signing_contract_test.gd` enforces this boundary against
the checked-in Godot export settings.

## Godot export configuration

- Preset: `iOS`, runnable
- Output: `build/ios/Bentosaur.xcodeproj`
- Architecture: ARM64
- Target family: iPhone
- Minimum iOS: 14.0
- Export project only: enabled for the initial Xcode provisioning build
- Debug export method: Development
- Release export method: App Store; no release certificate is selected
- Bundle version: `0.1.0`
- Build number: `1`
- App icon: provisional opaque 1024-square development icon

## First device build

The first personal-team device gate passed on July 31, 2026:

- Godot exported the promoted home-menu scene into the Xcode project.
- The generated project passed `tools/ios/verify_personal_signing.sh`.
- Xcode built with Team `53RJ43876F`, certificate
  `Apple Development: Mauricio Vargas (CRAZV8U43J)`, and the installed
  personal wildcard development profile.
- The signed entitlements resolved to
  `53RJ43876F.com.mauvsantos.bentosaur`.
- Bentosaur installed and launched successfully on Mauricio's iPhone.

For subsequent device builds:

1. Export the `iOS` preset from Godot.
2. Verify the generated project before opening Xcode:

   ```sh
   tools/ios/verify_personal_signing.sh
   ```

3. Open `build/ios/Bentosaur.xcodeproj`.
4. In Signing & Capabilities, verify:
   - Team resolves to the personal team under `mauvsantos@gmail.com`;
   - Development Team is `53RJ43876F`;
   - Automatically manage signing is enabled;
   - bundle identifier is `com.mauvsantos.bentosaur`.
5. Keep the iPhone unlocked and select it as the run destination.
6. Build and run in Xcode, or use the equivalent `xcodebuild` and
   `devicectl` flow.
7. Godot's runnable iOS preset can be used for later one-click deployment.

Stop if Xcode displays either forbidden Team ID or a Mellow identity. Do not
let Xcode "fix" signing by switching teams.
