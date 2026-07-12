# Repository context

Before the task, all slug-normalizer tests pass because the focused assertion
encodes the old behavior. Updating that assertion to the requested underscore
behavior should fail against the old implementation. This expected Prove red is
different from an unexpected task-caused failure discovered after implementation.
