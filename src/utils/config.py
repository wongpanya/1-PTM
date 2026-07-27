from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(relative_path: str) -> dict:
    path = PROJECT_ROOT / relative_path
    with path.open("r", encoding="utf-8") as f:
        text = f.read()
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ModuleNotFoundError:
        return _parse_simple_yaml(text)


def _parse_simple_yaml(text: str) -> dict:
    """Small YAML subset parser for this prototype's config files.

    It supports nested mappings, lists, inline scalar lists, strings, integers,
    floats, booleans, and nulls. If PyYAML is installed, `load_yaml` uses it.
    """
    lines = [_strip_comment(line.rstrip()) for line in text.splitlines()]
    lines = [line for line in lines if line.strip()]
    root: dict = {}
    stack: list[tuple[int, dict | list]] = [(-1, root)]

    for index, line in enumerate(lines):
        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if content.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"Invalid YAML list item at line {index + 1}: {line}")
            item_text = content[2:].strip()
            if ": " in item_text or item_text.endswith(":"):
                key, value = _split_key_value(item_text)
                item: dict = {}
                parent.append(item)
                if value == "":
                    child = _new_child_container(lines, index, indent)
                    item[key] = child
                    stack.append((indent + 2, item))
                    stack.append((indent + 4, child))
                else:
                    item[key] = _parse_scalar(value)
                    stack.append((indent, item))
            else:
                parent.append(_parse_scalar(item_text))
            continue

        key, value = _split_key_value(content)
        if not isinstance(parent, dict):
            raise ValueError(f"Invalid YAML mapping at line {index + 1}: {line}")
        if value == "":
            child = _new_child_container(lines, index, indent)
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(value)
    return root


def _strip_comment(line: str) -> str:
    in_quote = False
    quote_char = ""
    for i, char in enumerate(line):
        if char in {"'", '"'}:
            if not in_quote:
                in_quote = True
                quote_char = char
            elif quote_char == char:
                in_quote = False
        if char == "#" and not in_quote:
            return line[:i].rstrip()
    return line


def _split_key_value(text: str) -> tuple[str, str]:
    if ":" not in text:
        raise ValueError(f"Expected key/value pair: {text}")
    key, value = text.split(":", 1)
    return key.strip(), value.strip()


def _new_child_container(lines: list[str], current_index: int, current_indent: int) -> dict | list:
    for next_line in lines[current_index + 1 :]:
        next_indent = len(next_line) - len(next_line.lstrip(" "))
        if next_indent <= current_indent:
            continue
        return [] if next_line.strip().startswith("- ") else {}
    return {}


def _parse_scalar(value: str):
    value = value.strip()
    if value == "":
        return ""
    if value in {"null", "None", "~"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value
