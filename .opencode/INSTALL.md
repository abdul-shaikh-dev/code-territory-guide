# Installing Code Territory Guide for OpenCode

Add the Git-backed plugin to the `plugin` array in your global or project-level
`opencode.json`:

```json
{
  "plugin": [
    "code-territory-guide@git+https://github.com/abdul-shaikh-dev/code-territory-guide.git"
  ]
}
```

Restart OpenCode. The adapter registers the repository's `skills/` directory
with OpenCode's native skill loader.

Verify by asking OpenCode to list its skills and load `code-territory-guide`.

To update, refresh the Git-backed package through OpenCode's package manager. If
the resolved commit remains cached, clear the package cache or reinstall the
plugin.
