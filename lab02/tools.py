
import ast
import operator
from datetime import date
from pathlib import Path

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def _calc(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_calc(node.left), _calc(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_calc(node.operand))
    raise ValueError("only numbers and + - * / ** % are allowed")


def calculator(expression: str) -> str:
    """Do arithmetic, e.g. '240 * 0.15 + 12'."""
    expression = expression.strip().strip("`\"'").replace(",", "")
    try:
        return str(_calc(ast.parse(expression, mode="eval").body))
    except ZeroDivisionError:
        return "Error: cannot divide by zero"
    except Exception as e:  # noqa: BLE001
        return f"Error: {e}"


FACTS_FILE = Path(__file__).resolve().parent.parent / "lab01" / "facts.md"


def campus_fact(query: str) -> str:
    """Return up to 3 lines of the campus facts file that contain words from the query."""
    if not FACTS_FILE.exists():
        return "Error: facts file not found (lab01/facts.md)"
    words = [w.strip("?.,!").lower() for w in query.split()]
    words = [w for w in words if len(w) > 2]
    lines = [l.strip() for l in FACTS_FILE.read_text(encoding="utf-8").splitlines()]
    scored = []
    for line in lines:
        if not line or line.startswith("#"):
            continue
        score = sum(1 for w in words if w in line.lower())
        if score:
            scored.append((score, line))
    scored.sort(key=lambda x: -x[0])
    return "\n".join(line for _, line in scored[:3]) if scored else "No matching fact."


def today(_: str = "") -> str:
    """Return today's weekday and date, e.g. 'Wednesday 2026-11-25'."""
    d = date.today()
    return f"{d:%A} {d.isoformat()}"



TOOLS = {"calculator": calculator, "campus_fact": campus_fact, "today": today}

TOOL_DESCRIPTIONS = """calculator: does arithmetic. Input: a maths expression such as 240 * 0.15 + 12
campus_fact: looks up campus information (offices, opening hours, services). Input: a few keywords such as library hours
today: gives today's weekday and date. Input: anything (it is ignored)"""


if __name__ == "__main__": 
    print("calculator('240 * 0.15 + 12') ->", calculator("240 * 0.15 + 12"))
    print("calculator('10 / 0')          ->", calculator("10 / 0"))
    print("calculator('__import__(\"os\")') ->", calculator('__import__("os")'))
    print("campus_fact('library hours')  ->", campus_fact("library hours"))
    print("today()                       ->", today())
