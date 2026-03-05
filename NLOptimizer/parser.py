import re
import io
from contextlib import redirect_stdout

def clean_code(raw_response: str) -> str:
    """Extracts only the python code from the AI's markdown response."""
    # Use Regex to find content between ```python and ```
    match = re.search(r"```python\n(.*?)\n```", raw_response, re.DOTALL)
    if match:
        return match.group(1)
    return raw_response.strip()

def validate_safety(code: str):
    """Basic security check to prevent malicious code execution."""
    forbidden = ["import os", "import sys", "subprocess", "rmdir", "eval("]
    for word in forbidden:
        if word in code:
            raise PermissionError(f"Security Alert: Generated code contains forbidden keyword: {word}")

from pyomo.environ import *

def execute_and_get_model(code: str, data: dict = None):
    # 1. Prepare the global environment for the AI code
    # We include everything from pyomo.environ here
    exec_globals = {
        "ConcreteModel": ConcreteModel,
        "Var": Var,
        "Objective": Objective,
        "Constraint": Constraint,
        "NonNegativeReals": NonNegativeReals,
        "NonNegativeIntegers": NonNegativeIntegers,
        "maximize": maximize,
        "minimize": minimize,
        "Param": Param,
        "SolverFactory": SolverFactory
    }
    
    local_env = {}
    if data is None:
        data = {}

    try:
        # 2. Execute with the injected globals
        exec(code, exec_globals, local_env)
        
        if 'create_model' in local_env:
            return local_env['create_model'](data)
        else:
            raise ValueError("AI failed to provide a 'create_model' function.")
    except Exception as e:
        raise RuntimeError(f"Generated Pyomo code is invalid: {e}")