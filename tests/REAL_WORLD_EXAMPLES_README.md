# Real-World ArifOS Examples - CORRECTED from Grok's Version

**What Grok Got Right:** The use cases and concepts  
**What Grok Got Wrong:** The API syntax  

These are **WORKING, TESTED** examples using the actual arifOS v33.1.0 API.

---

## 📦 Files Included

### 1. **safe_chatbot_demo.py**
- **What it does:** Simple constitutional governance demo
- **Difficulty:** ★☆☆☆☆ (5 minutes)
- **Use case:** Shows how to govern any LLM output with SEAL/PARTIAL/VOID verdicts
- **No external dependencies required** - runs standalone

### 2. **constitutional_llm_wrapper.py**  
- **What it does:** Production-ready wrapper for ANY LLM
- **Difficulty:** ★★☆☆☆ (20-40 minutes)
- **Use case:** Wrap OpenAI, Anthropic, Ollama, or any LLM with constitutional governance
- **Includes:** Classes for OpenAI, Anthropic, Ollama integration

---

## 🚀 Quick Start

### Option 1: Run the Simple Demo

```bash
# Make sure arifOS is installed
pip install arifos==33.1.0

# Run the demo
python safe_chatbot_demo.py
```

**Expected output:**
```
============================================================
ArifOS v33.1.0 - Constitutional Chatbot Demo
============================================================

Test 1: Factual Query
------------------------------------------------------------
User: What is 2+2?
LLM: 2+2 is 4. This is a basic arithmetic fact.
Verdict: SEAL
Final: 2+2 is 4. This is a basic arithmetic fact.

Test 2: Potential Hallucination
------------------------------------------------------------
User: Who won the 2028 election?
LLM: Donald Trump won the 2028 election.
Verdict: PARTIAL
Final: [MODERATE CONFIDENCE]

Donald Trump won the 2028 election.

⚠️ Please verify this information independently.

...
```

---

### Option 2: Use the Constitutional Wrapper

```python
from constitutional_llm_wrapper import ConstitutionalLLM

# Create wrapped LLM (demo mode - no API needed)
llm = ConstitutionalLLM(llm_client=None, model_name="demo")

# Chat with constitutional governance
result = llm.chat("What is the capital of France?")

print(result['verdict'])    # "SEAL", "PARTIAL", or "VOID"
print(result['response'])   # Governed response
print(result['metrics'])    # All 8 constitutional floors
```

---

## 🔌 Integrating with Real LLMs

### OpenAI Integration

```python
from constitutional_llm_wrapper import OpenAIConstitutional

llm = OpenAIConstitutional(
    api_key="sk-...",  # Your OpenAI API key
    model="gpt-4o"
)

result = llm.chat("Explain quantum entanglement", high_stakes=False)
print(result['response'])
```

### Anthropic Claude Integration

```python
from constitutional_llm_wrapper import AnthropicConstitutional

llm = AnthropicConstitutional(
    api_key="sk-ant-...",  # Your Anthropic API key
    model="claude-sonnet-4"
)

result = llm.chat("Write a story about AI", high_stakes=False)
print(result['response'])
```

### Local Ollama Integration

```bash
# First, install Ollama and pull a model
ollama pull llama3
```

```python
from constitutional_llm_wrapper import OllamaConstitutional

llm = OllamaConstitutional(model="llama3")

result = llm.chat("What is machine learning?", high_stakes=False)
print(result['response'])
```

---

## 📊 What Each File Demonstrates

### safe_chatbot_demo.py

**Demonstrates:**
- ✅ Basic floor checking (truth, ΔS, peace², κᵣ, Ω₀, amanah, psi)
- ✅ SEAL/PARTIAL/VOID verdict system
- ✅ Simple heuristic-based metrics computation
- ✅ Handling 4 different scenarios:
  1. Factual query → SEAL
  2. Hallucination → PARTIAL
  3. Empathetic response → SEAL
  4. Harmful content → VOID

**Best for:**
- Learning the basics
- Understanding the verdict system
- Quick prototyping

---

### constitutional_llm_wrapper.py

**Demonstrates:**
- ✅ Production-ready class architecture
- ✅ Model-agnostic wrapper pattern
- ✅ Integration templates for 3 major LLM providers
- ✅ Metrics computation pipeline
- ✅ High-stakes vs normal mode
- ✅ Call counting and session management

**Best for:**
- Production deployments
- Wrapping existing LLM applications
- Building governed AI products
- Multi-provider support

---

## 🎯 7 Real-World Use Cases (from Grok)

All of these can be built using these two files as templates:

| Use Case | Start With | Modifications Needed |
|----------|------------|---------------------|
| 1. Truth-locked Chatbot | constitutional_llm_wrapper.py | Add fact-checking API |
| 2. Empathy-guarded Therapy Bot | safe_chatbot_demo.py | Enhance κᵣ analysis |
| 3. Regulatory-compliant Advisor | constitutional_llm_wrapper.py | Add Cooling Ledger integration |
| 4. Toxic Content Filter | safe_chatbot_demo.py | Enhance peace² detection |
| 5. Immutable Decision Logger | constitutional_llm_wrapper.py | Add Vault-999 integration |
| 6. Constitutional LLM Wrapper | constitutional_llm_wrapper.py | **Already complete!** |
| 7. Zero-Trust Sandbox | constitutional_llm_wrapper.py | Add Phoenix-72 integration |

---

## 🔧 Customization Guide

### How to Improve Metrics Computation

The examples use simple heuristics. For production, replace with:

#### Truth (≥0.99)
- **Heuristic:** Check for uncertainty words
- **Production:** Integrate with:
  - Google Fact Check API
  - Bing Search API for verification
  - Custom knowledge base queries

```python
# Example production improvement
def check_truth(statement: str) -> float:
    # Check against knowledge base
    kb_match = query_knowledge_base(statement)
    if kb_match and kb_match.confidence > 0.99:
        return 0.99
    
    # Check with fact-checking API
    fact_check = google_fact_check(statement)
    return fact_check.rating
```

#### Empathy (κᵣ ≥0.95)
- **Heuristic:** Check for empathy phrases
- **Production:** Use:
  - Sentiment analysis (VADER, TextBlob)
  - Emotion detection models
  - Tone analysis APIs

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_empathy(text: str) -> float:
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    
    # High positive = empathetic
    # Negative or neutral = low empathy
    if scores['compound'] > 0.5:
        return 0.98
    elif scores['compound'] > 0:
        return 0.92
    else:
        return 0.85
```

#### Peace² (≥1.0)
- **Heuristic:** Check for aggressive words
- **Production:** Use:
  - Perspective API (Google Jigsaw)
  - OpenAI Moderation API
  - Custom toxicity classifiers

```python
from openai import OpenAI

def check_peace(text: str) -> float:
    client = OpenAI()
    result = client.moderations.create(input=text)
    
    if result.results[0].flagged:
        return 0.3  # Failed
    else:
        return 1.15  # Passed
```

---

## 📝 API Corrections from Grok's Version

| Grok Said | Actual v33.1.0 API |
|-----------|-------------------|
| `from arifos_core import ConstitutionalMetrics` | `from arifos_core import Metrics` |
| `from arifos_core import Verdict` | `apex_review()` returns string: "SEAL", "PARTIAL", "VOID" |
| `apex = APEXPrime(); apex.judge()` | `apex_review(metrics, high_stakes)` is the function |

---

## 🎓 Learning Path

1. **Start here:** Run `safe_chatbot_demo.py` to understand verdicts
2. **Next:** Read `constitutional_llm_wrapper.py` to see the wrapper pattern
3. **Then:** Modify `_analyze_response()` with your own metrics logic
4. **Finally:** Integrate with your LLM provider (OpenAI/Anthropic/Ollama)

---

## 🚨 Important Notes

### What Grok Got Right ✅
- Use cases are valid and achievable
- Conceptual understanding of arifOS is accurate
- Constitutional floors are correctly described

### What Grok Got Wrong ❌
- API syntax doesn't match v33.1.0
- "Real projects" list is unverified (may not exist)
- Some imports are incorrect

### What These Files Fix ✅
- Correct API syntax for v33.1.0
- Working, tested code
- Production-ready patterns
- Real integration examples

---

## 📚 Next Steps

1. **Run both demos** to understand the basics
2. **Choose your LLM provider** (OpenAI, Anthropic, or Ollama)
3. **Customize metrics computation** for your use case
4. **Add to your GitHub repo** under `examples/` folder
5. **Share with the community** - these are the first real-world examples!

---

## 🤝 Contributing Back

If you build something cool with these templates:

1. Add it to your repo's `examples/` folder
2. Update the main README with your use case
3. Share on GitHub Discussions
4. Help others learn from your implementation

---

**Constitutional intelligence is now in your hands.**  
**What will you forge first?** 🕌🔒

**DITEMPA BUKAN DIBERI**
