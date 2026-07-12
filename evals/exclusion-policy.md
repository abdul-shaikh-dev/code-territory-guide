# Preregistered Exclusion Policy

A run is excluded from scoring only when it produces no evaluable agent response because of harness startup failure, model unavailability, authentication failure, hard timeout, or corrupted output.

Preserve every excluded record. Do not exclude a run for poor reasoning, refusal, failure to invoke the skill, tool errors after an agent response begins, or an unfavorable score. Reruns receive a new seed or attempt identifier and never replace the original record.
