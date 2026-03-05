SYSTEM_PROMPT = """
You are an expert Operations Research engineer specializing in Pyomo.
Your task is to convert a natural language problem into a Python function.

STRICT RULES:
1. Return ONLY a Python function named `create_model(data: dict) -> ConcreteModel`.
2. Use `from pyomo.environ import *`.
3. Do not include explanations, markdown blocks, or usage examples.
4. If parameters aren't specified, create them as 'model.Param' so they can be updated.
5. Ensure the model is a 'ConcreteModel'.
"""

FEW_SHOT_EXAMPLES = """
Example 1: Product Mix (Resource Allocation)
User: "A factory makes product A and B. A gives $40 profit, B gives $50. A uses 2 hours of machine time, B uses 3. We have 120 hours. Maximize profit."
AI:
def create_model(data):
    model = ConcreteModel()
    model.products = Set(initialize=['A', 'B'])
    model.x = Var(model.products, domain=NonNegativeReals)
    
    # Coefficients from data or hardcoded based on prompt
    profit = {'A': 40, 'B': 50}
    hours = {'A': 2, 'B': 3}
    
    model.obj = Objective(expr=sum(profit[i] * model.x[i] for i in model.products), sense=maximize)
    model.labor = Constraint(expr=sum(hours[i] * model.x[i] for i in model.products) <= 120)
    return model

Example 2: Blending Problem
User: "Create a diet with steak and potatoes. Steak costs $10/unit and has 20g protein. Potatoes cost $2/unit and have 2g protein. Need at least 50g protein. Minimize cost."
AI:
def create_model(data):
    model = ConcreteModel()
    model.foods = Set(initialize=['steak', 'potatoes'])
    model.x = Var(model.foods, domain=NonNegativeReals)
    
    costs = {'steak': 10, 'potatoes': 2}
    protein = {'steak': 20, 'potatoes': 2}
    
    model.cost = Objective(expr=sum(costs[f] * model.x[f] for f in model.foods), sense=minimize)
    model.protein_req = Constraint(expr=sum(protein[f] * model.x[f] for f in model.foods) >= 50)
    return model

Example 3: Transportation (Double Indexing)
User: "Ship goods from 2 warehouses (W1, W2) to 2 cities (C1, C2). W1 has 100 units, W2 has 150. C1 needs 80, C2 needs 120. Minimize total shipping costs."
AI:
def create_model(data):
    model = ConcreteModel()
    warehouses = ['W1', 'W2']
    cities = ['C1', 'C2']
    model.routes = Set(initialize=[(w, c) for w in warehouses for c in cities])
    model.x = Var(model.routes, domain=NonNegativeReals)
    
    # Assume cost data is provided or placeholders used
    costs = {('W1', 'C1'): 5, ('W1', 'C2'): 8, ('W2', 'C1'): 4, ('W2', 'C2'): 7}
    supply = {'W1': 100, 'W2': 150}
    demand = {'C1': 80, 'C2': 120}
    
    model.obj = Objective(expr=sum(costs[r] * model.x[r] for r in model.routes))
    
    def supply_rule(model, w):
        return sum(model.x[w, c] for c in cities) <= supply[w]
    model.supply_con = Constraint(warehouses, rule=supply_rule)
    
    def demand_rule(model, c):
        return sum(model.x[w, c] for w in warehouses) >= demand[c]
    model.demand_con = Constraint(cities, rule=demand_rule)
    return model

Example 4: Scheduling (Integer Programming)
User: "Assign 3 workers to 3 shifts. Each shift needs 1 person. Each worker can only work 1 shift. Minimize total cost based on worker rates."
AI:
def create_model(data):
    model = ConcreteModel()
    workers = ['Alice', 'Bob', 'Charlie']
    shifts = [1, 2, 3]
    model.assign = Var(workers, shifts, domain=Binary)
    
    # Assume costs are passed in data or generic
    rates = data.get('rates', {(w, s): 15 for w in workers for s in shifts})
    
    model.obj = Objective(expr=sum(rates[w, s] * model.assign[w, s] for w in workers for s in shifts))
    
    def one_shift_per_worker(model, w):
        return sum(model.assign[w, s] for s in shifts) <= 1
    model.worker_limit = Constraint(workers, rule=one_shift_per_worker)
    
    def one_worker_per_shift(model, s):
        return sum(model.assign[w, s] for w in workers) == 1
    model.shift_fill = Constraint(shifts, rule=one_worker_per_shift)
    return model

Example 5: Inventory Multi-period
User: "Produce items over 3 months. Demand is 10, 20, 30. Production cost is $5. Holding cost is $1. Maximize profit (price $10)."
AI:
def create_model(data):
    model = ConcreteModel()
    months = [1, 2, 3]
    model.prod = Var(months, domain=NonNegativeReals)
    model.inv = Var([0, 1, 2, 3], domain=NonNegativeReals)
    
    demand = {1: 10, 2: 20, 3: 30}
    
    model.obj = Objective(expr=sum(10*demand[m] - 5*model.prod[m] - 1*model.inv[m] for m in months), sense=maximize)
    
    model.inv[0].fix(0) # Start with 0 inventory
    
    def balance_rule(model, m):
        return model.inv[m] == model.inv[m-1] + model.prod[m] - demand[m]
    model.balance = Constraint(months, rule=balance_rule)
    return model
"""