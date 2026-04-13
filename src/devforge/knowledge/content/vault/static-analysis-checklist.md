# Static Analysis Checklist

> Localized governance audit checklist derived from the myskills meta-skill/code-tuner compliance and duplication protocols.

Use this checklist when a node claims completion and the orchestrator needs to decide whether the result is structurally acceptable or must be sent to refactor.

## Required Checks

1. Boundary integrity
- Domain and transport layers are not collapsed into a single implementation blob.
- Cross-module dependencies move through declared contracts instead of ad-hoc imports.

2. Change safety
- New behavior is covered by tests or explicit verification artifacts.
- Refactors preserve or strengthen deterministic validation seams.

3. Duplication and leakage
- Business rules are not duplicated across handlers/controllers/services.
- Infrastructure details do not leak into core decision logic.

4. Failure handling
- Error paths are explicit and observable.
- Recovery or diagnosis hooks exist for non-happy paths.

## Refactor Triggers

Mark the node as `needs_refactor` when any artifact reports one of these:

- `architectural_smells`
- `audit_findings`
- `violations`
- `cross_layer_duplication`
- `missing_tests`

## Expected Audit Output

The audit result written to `.allforai/devforge/audits/<node-id>.json` should contain:

```json
{
  "node_id": "example-node",
  "status": "pass | needs_refactor",
  "summary": "one line conclusion",
  "violations": [
    {
      "code": "BOUNDARY_LEAK",
      "severity": "high",
      "evidence": "artifact path or short finding"
    }
  ]
}
```
