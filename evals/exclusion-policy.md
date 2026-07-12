# Preregistered Exclusion Policy

A run is excluded from scoring when it produces no evaluable agent response because of harness startup failure, model unavailability, authentication failure, hard timeout, or corrupted output. A treatment run is also excluded from comparison when the installed treatment payload changes during execution, because it no longer represents the preregistered treatment.

Preserve every excluded record. Do not exclude a run for poor reasoning, refusal, failure to invoke the skill, tool errors after an agent response begins, or an unfavorable score. Record treatment mutation as contamination rather than model failure. Reruns receive a new seed or attempt identifier and never replace the original record.
