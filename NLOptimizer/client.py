import openai
from .prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def fetch_pyomo_code(self, user_problem: str) -> str:
        """Sends the problem to the AI with context and returns the code."""
        # Combine instructions and examples into the system context
        full_system_context = f"{SYSTEM_PROMPT}\n\nHERE ARE EXAMPLES OF THE EXPECTED OUTPUT:\n{FEW_SHOT_EXAMPLES}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_system_context},
                    {"role": "user", "content": user_problem}
                ],
                temperature=0.1 
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ConnectionError(f"Failed to reach OpenAI: {e}")
    
    def summarize_results(self, original_problem: str, results_dict: dict) -> str:
        """Translates math results into a human-readable summary."""
        summary_prompt = f"""
        You are a business consultant. 
        Original Problem: {original_problem}
        Numerical Results: {results_dict}
        
        Write a concise 2-3 sentence summary of the optimal solution. 
        Focus on the 'what to do' and the final objective value (profit/cost).
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": summary_prompt}]
        )
        return response.choices[0].message.content