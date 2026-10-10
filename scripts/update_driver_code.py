"""Regenerate the "Driver code" section of the intro example markdown files.

Every examples/intro/example_N directory holds example_N.py and example_N.md.
The "## Driver code" section of example_N.md is a copy of example_N.py; this
script rewrites that section from the current code, or appends it when missing.

Usage:
    python scripts/update_driver_code.py          # update the markdown files
    python scripts/update_driver_code.py --check  # exit with 1 if any is out of date
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples" / "intro"

SECTION_HEADING = "## Driver code"

# the section runs from its heading, past its fenced code block (whose code may itself
# contain lines starting with "## "), to the next level-2 heading or the end of the file
SECTION_PATTERN = re.compile(
    rf"^{re.escape(SECTION_HEADING)}\n(?:.*?^```python\n.*?^```$)?.*?(?=^## |\Z)", re.MULTILINE | re.DOTALL
)


def build_section(code_file: Path) -> str:
    code = code_file.read_text().rstrip("\n")
    return f"{SECTION_HEADING}\n\nThe complete code of the example, `{code_file.name}`:\n\n```python\n{code}\n```\n"


def render(markdown: str, section: str) -> str:
    if SECTION_PATTERN.search(markdown):
        # a following section needs a blank line before its heading
        return SECTION_PATTERN.sub(lambda match: section + ("\n" if match.end() < len(markdown) else ""), markdown)

    return markdown.rstrip("\n") + "\n\n" + section


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report out of date files without changing them")
    args = parser.parse_args()

    out_of_date = []
    for example_dir in sorted(EXAMPLES_DIR.glob("example_*")):
        code_file = example_dir / f"{example_dir.name}.py"
        markdown_file = example_dir / f"{example_dir.name}.md"

        if not code_file.exists() or not markdown_file.exists():
            print(f"skipping {example_dir.relative_to(ROOT)}: missing {code_file.name} or {markdown_file.name}")
            continue

        markdown = markdown_file.read_text()
        updated = render(markdown, build_section(code_file))
        if updated == markdown:
            continue

        out_of_date.append(markdown_file)
        if not args.check:
            markdown_file.write_text(updated)

    for markdown_file in out_of_date:
        action = "out of date" if args.check else "updated"
        print(f"{action}: {markdown_file.relative_to(ROOT)}")

    if args.check and out_of_date:
        print("run `python scripts/update_driver_code.py` to update them")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
