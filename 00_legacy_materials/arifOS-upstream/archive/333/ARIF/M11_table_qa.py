import pandas as pd
from smolagents import tool
from model_factory import get_arif_model


@tool
def table_qa_tool(query: str, table_path: str) -> str:
    """
    Analyzes a tabular dataset (CSV, Excel) and answers natural language questions about it.
    This is the A-RIF M11 Sensory Layer component.

    Args:
        query: The natural language question about the table.
        table_path: The absolute path to the CSV or Excel file (e.g., 'C:/ariffazil/arifOS/logs/cooling_ledger.csv').
    """
    try:
        # Load the table
        if table_path.endswith(".csv"):
            df = pd.read_csv(table_path)
        elif table_path.endswith((".xls", ".xlsx")):
            df = pd.read_excel(table_path)
        else:
            return f"Error: Unsupported table format for {table_path}"

        # Get head and description to provide context to the Mind
        context = f"Table Summary:\n{df.describe()}\n\nSample Data (First 5 rows):\n{df.head().to_string()}"

        # Use the Mind to answer the question based on context
        model = get_arif_model()
        prompt = f"Based on the following table data context, answer the user query: '{query}'\n\n{context}"

        # We wrap it in a simple chat message format
        messages = [{"role": "user", "content": prompt}]
        response = model(messages)

        return response.content if hasattr(response, "content") else str(response)

    except Exception as e:
        return f"Error analyzing table: {str(e)}"


class M11TableQA:
    """A-RIF M11: TABULAR SENSORY LAYER"""

    def __init__(self):
        pass

    def analyze(self, query: str, table_path: str):
        return table_qa_tool(query, table_path)
