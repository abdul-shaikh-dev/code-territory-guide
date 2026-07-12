# Field Entry: The Missing Empty State

Use this short example to understand the guide's shape. It is illustrative, not a required template.

## Map

User request: "Show a useful state when a filtered dashboard has no results."

## Survey

The request does not specify whether the empty state means no data exists or the active filters exclude existing data. Inspect the dashboard component, current filter state, nearby loading/error states, and relevant UI tests before asking a question.

## Territory

The repository already distinguishes `hasLoaded`, `items.length`, and `activeFilters`. A shared `EmptyPanel` component is used by adjacent views. The relevant test suite renders the dashboard with mocked query results.

## Route

Reuse `EmptyPanel`. Render a filter-specific message only after loading completes and only when results are empty while filters are active. Preserve the existing no-data message for an unfiltered empty list. Add the two narrow rendering tests and run the dashboard test file.

## Field Brief

Files: the dashboard view and its existing test file. Non-goals: changing filter behavior, query APIs, or the shared component. Scope expansion: new filtering semantics or a redesign of all empty states requires confirmation.

## Expedition Result

The smallest patch adds one conditional branch and two tests. The targeted test suite passes. No notes file is needed because the repository convention resolved the only ambiguity.

If the targeted test failed, classify the failure before handoff. A regression introduced by the patch returns to Track and prevents a Complete result; a verified pre-existing or environmental failure is preserved and disclosed with evidence.

## Field Report

Changed the dashboard's post-load empty rendering so filtered and unfiltered empty results have distinct guidance. Verified with the dashboard tests. Review the final copy and whether the clear-filters action belongs in this change.
