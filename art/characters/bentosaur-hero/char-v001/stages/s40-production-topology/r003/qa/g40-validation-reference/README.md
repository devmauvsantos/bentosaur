# G40 validation reference snapshot

This directory is a compact, immutable review snapshot of the completed run:

```text
.tmp/subagents/g40_validation_harness/runs/bentosaur_r003_reference_final_20260729
```

It preserves the run inputs, machine-readable reports and metrics, evidence
boards, and logs. The full numbered `.blend` checkpoints and individual pose
renders remain in the original local Tier C archive and were intentionally not
duplicated here.

The copied `reports/hash_manifest.json` is the manifest of the complete
original run. It therefore names the omitted checkpoint and render files too;
use the preserved Tier C run when verifying that complete manifest.

Result: the harness reproduces the known R003 diagnostic. Neutral and tail bend
pass. Reach/tray hold, squat, and extreme walk fail. This is diagnostic evidence,
not topology, rig, animation, visual, or user approval.
