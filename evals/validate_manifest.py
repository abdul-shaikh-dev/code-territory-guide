from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "manifest.json"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_TYPES = {"behavioral", "trigger"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(data.get("schema_version") == 1, "schema_version must be 1")
    require(data.get("skill") == "code-territory-guide", "unexpected skill name")

    cases = data.get("cases")
    require(isinstance(cases, list) and cases, "cases must be a non-empty list")

    seen: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        case_id = case.get("id")
        require(isinstance(case_id, str) and ID_PATTERN.fullmatch(case_id) is not None, f"{prefix}.id must be kebab-case")
        require(case_id not in seen, f"duplicate case id: {case_id}")
        seen.add(case_id)

        require(case.get("type") in VALID_TYPES, f"{case_id}: invalid type")
        require(isinstance(case.get("query"), str) and case["query"].strip(), f"{case_id}: query is required")

        context_files = case.get("context_files")
        require(isinstance(context_files, list), f"{case_id}: context_files must be a list")
        for relative in context_files:
            require(isinstance(relative, str) and relative, f"{case_id}: invalid context path")
            path = (ROOT / relative).resolve()
            require(ROOT in path.parents, f"{case_id}: context path escapes evals root")
            require(path.is_file(), f"{case_id}: missing context file {relative}")

        expected = case.get("expected_behavior")
        require(isinstance(expected, list) and expected, f"{case_id}: expected_behavior is required")
        require(any(item.get("critical") is True for item in expected if isinstance(item, dict)), f"{case_id}: at least one critical expectation is required")
        expected_ids: set[str] = set()
        for item in expected:
            require(isinstance(item, dict), f"{case_id}: expected behavior must be an object")
            item_id = item.get("id")
            require(isinstance(item_id, str) and ID_PATTERN.fullmatch(item_id) is not None, f"{case_id}: invalid expected behavior id")
            require(item_id not in expected_ids, f"{case_id}: duplicate expected behavior id {item_id}")
            expected_ids.add(item_id)
            require(isinstance(item.get("description"), str) and item["description"].strip(), f"{case_id}: expected behavior description is required")
            require(isinstance(item.get("critical"), bool), f"{case_id}: critical must be boolean")

        forbidden = case.get("forbidden_behavior")
        require(isinstance(forbidden, list) and forbidden, f"{case_id}: forbidden_behavior is required")
        require(all(isinstance(item, str) and item.strip() for item in forbidden), f"{case_id}: forbidden behavior entries must be strings")

    print(f"Validated {len(cases)} behavioral eval cases for {data['skill']}.")


if __name__ == "__main__":
    main()
