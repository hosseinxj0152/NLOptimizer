# NLOptimizer 🤖
Convert plain English optimization problems into insight within seconds.

## Installation
```bash
pip install .
```

## Usage  

[Sample Google Colab Notebook](https://colab.research.google.com/drive/1tFUHLEB1Njj3e9OY4U9ueCUFoosF1tRf?usp=sharing)  

```python
from NLOptimizer import PyomoGenerator

gen = PyomoGenerator(api_key="your_key")

output = gen.solve("""A bakery makes sourdough bread and croissants. 
Sourdough gives $5 profit per loaf, croissants give $3 each. 
Each sourdough loaf takes 2 hours of oven time and 1kg of flour. 
Each croissant takes 1 hour of oven time and 0.5kg of flour. 
We have 40 hours of oven time and 30kg of flour available. 
Maximize total profit.""")

print(output['summary'])
```