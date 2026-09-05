# External instruction patches

These focused patches record the global, personal, and installed-vendor changes
from this audit. Full replacement manifests and protected backups remain local.
The paths in each patch are relative to the corresponding installation/source
root; no script should infer a destination from the current working directory.

| Patch | Target root |
| --- | --- |
| [codex-guidance.patch](codex-guidance.patch) | User's `.codex` directory |
| [personal-skills.patch](personal-skills.patch) | User's `.agents/skills` directory |
| [codex-system-skills.patch](codex-system-skills.patch) | User's `.codex/skills/.system` directory |
| [vendor-cache.patch](vendor-cache.patch) | User's `.codex/plugins/cache` directory, at the versions named in the patch |
| [controlled-coding-source.patch](controlled-coding-source.patch) | `controlled-coding-workflow-plugin` source checkout |
| [ghost-source.patch](ghost-source.patch) | `copilot-ghost-implementer` source directory |

[index.json](index.json) records original file hashes; a null hash indicates a
new file. All six patches were checked and applied to isolated copies of their
original files, and every resulting file matched the installed change.

For reuse, review the target root, source hashes, and desired behavior first.
The patches omit unchanged context to keep the record compact.
Run `git apply --unidiff-zero --check <absolute-patch-path>` from the verified target root.
Back up the targets before applying with `git apply --unidiff-zero`. These are version-specific changes, not
an automatic vendor-update mechanism. The controlled-coding and ghost skills
were already inactive and are superseded by Code Territory Guide for this user.
