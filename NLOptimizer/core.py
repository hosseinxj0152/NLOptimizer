from .client import OpenAIClient
from .parser import clean_code, validate_safety, execute_and_get_model
from pyomo.environ import Var, SolverFactory, value

class PyomoGenerator:
    def __init__(self, api_key, solver_name='highs'):
        self.client = OpenAIClient(api_key)
        self.solver_name = solver_name

    def solve_description(self, text, data=None):
        raw_ai_output = self.client.fetch_pyomo_code(text)
        code = clean_code(raw_ai_output)
        validate_safety(code)

        # Pass data through to the parser
        pyomo_model = execute_and_get_model(code, data=data)
        return pyomo_model
    
    def solve_problem(self, description, data=None):
        # 1. Generate the model object using existing logic
        raw_ai_output = self.client.fetch_pyomo_code(description)
        code = clean_code(raw_ai_output)
        validate_safety(code)
        model = execute_and_get_model(code, data=data)

        # 2. Internal Solver Logic
        solver = SolverFactory(self.solver_name)
        
        # Check if solver is available on the machine
        if not solver.available():
            raise RuntimeError(f"Solver '{self.solver_name}' not found. Please install it (e.g., brew install glpk).")

        results = solver.solve(model, tee=False, timelimit=60,) # tee=True shows solver logs
        
        return model, results
    
    def solve(self, description, data=None):
        # 1. Generate and solve (using your existing logic)
        model, results = self.solve_problem(description, data)
        
        # 2. Extract variable values into a simple dictionary
        results_dict = {}
        for v in model.component_objects(Var, active=True):
            for index in v:
                results_dict[f"{v.name}[{index}]"] = v[index].value
        
        # Add the objective value
        # results_dict["objective_value"] = model.objective()
        results_dict = {}
        for v in model.component_objects(Var, active=True):
            for index in v:
                results_dict[f"{v.name}[{index}]"] = v[index].value

        # --- REPLACE THE CRASHING LINE WITH THIS ---
        from pyomo.environ import Objective

        # Find the first active objective and get its value
        try:
            # This looks for any Objective component and gets its current value
            active_obj = next(model.component_data_objects(Objective, active=True))
            results_dict["objective_value"] = value(active_obj)
        except StopIteration:
            results_dict["objective_value"] = "Unknown (No objective found)"

        # 3. Get the AI summary
        human_summary = self.client.summarize_results(description, results_dict)
        
        return {
            "model": model,
            "results": results,
            "summary": human_summary,
            "data": results_dict
        }
    
    