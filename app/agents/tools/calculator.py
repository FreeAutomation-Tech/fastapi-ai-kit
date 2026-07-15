import ast
import operator

from app.agents.tools.base import BaseTool

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Evaluate a mathematical expression. Supports +, -, *, /, **, %, //."
    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate (e.g. '2 + 2 * 3')",
            }
        },
        "required": ["expression"],
    }

    async def run(self, expression: str) -> str:
        try:
            tree = ast.parse(expression.strip(), mode="eval")
            result = self._eval(tree.body)
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {e}"

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            return node.n if isinstance(node.n, (int, float)) else 0
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            return _ALLOWED_OPS[op_type](self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in _ALLOWED_OPS:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
            return _ALLOWED_OPS[op_type](self._eval(node.operand))
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")
