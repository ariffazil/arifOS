from smolagents import tool
from model_factory import get_arif_model

@tool
def doc_qa_tool(query: str, doc_path: str) -> str:
    """
    Analyzes a document (Markdown, Text, PDF) and answers natural language questions about it.
    This is the A-RIF M12 Sensory Layer component.
    
    Args:
        query: The natural language question about the document content.
        doc_path: The absolute path to the document (e.g., 'C:/ariffazil/arifOS/docs/POLICIES.md').
    """
    try:
        # Load the document content (basic text for now)
        if doc_path.endswith('.md') or doc_path.endswith('.txt'):
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
        # Handle large documents by chunking if needed (Simple head/tail for context for now)
        if len(content) > 10000:
            content = content[:5000] + "\n... (omitted) ...\n" + content[-5000:]
            
        context = f"Document content (fragmented if excessively long):\n{content}"
        
        # Use the Mind to answer the question based on context
        model = get_arif_model()
        prompt = f"Based on the following document context, answer the user query: '{query}'\n\n{context}"
        
        messages = [{"role": "user", "content": prompt}]
        response = model(messages)
        
        return response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        return f"Error analyzing document: {str(e)}"

class M12DocQA:
    """A-RIF M12: DOCUMENT SENSORY LAYER"""
    def __init__(self):
        pass
        
    def analyze(self, query: str, doc_path: str):
        return doc_qa_tool(query, doc_path)
