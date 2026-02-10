
import os
import json
import pandas as pd
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevance,
    context_precision,
    context_recall,
)
from datasets import Dataset
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Import your RAG system
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from RAG.query import QuerySystem
from dotenv import load_dotenv

load_dotenv()

def run_evaluation():
    # 0. Setup Gemini for Ragas
    # Ragas uses LangChain LLMs. We need to configure it to use Gemini.
    if not os.getenv("GEMINI_API_KEY"):
         print("Error: GEMINI_API_KEY not found in environment")
         return

    # Initialize Gemini LLM and Embeddings for Ragas evaluation
    # Note: Ragas metrics often require an LLM to judge.
    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", # Use a standard model for eval
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )
    
    # We also need embeddings for some metrics
    gemini_embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    # 1. Load Test Dataset
    if not os.path.exists("tests/test_dataset.json"):
        print("Creating test dataset first...")
        import create_test_dataset
    
    with open("tests/test_dataset.json", "r") as f:
        test_data = json.load(f)
    
    # 2. Initialize RAG System
    rag_system = QuerySystem()
    
    # 3. Generate Answers
    results = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [] # Ragas expects 'ground_truth' (string) or 'ground_truths' (list of strings). Dataset features might prefer 'ground_truth' col for singular. 
                           # Actually Ragas standard is 'ground_truth' (string) for some versions, but 'ground_truths' (list) for datasets. 
                           # Let's stick to 'ground_truth' column which Ragas `Dataset` expects as `ground_truth` (string) usually? 
                           # Wait, Ragas documentation says `ground_truth` (string) or `ground_truths` (list[str]). 
                           # Let's use `ground_truth` column with string if one, or `ground_truths` with list. 
                           # The test dataset has single ground truth.
    }
    
    print("Running RAG pipeline on test set...")
    for item in test_data:
        q = item["question"]
        print(f"Processing: {q}")
        
        # Get answer from RAG
        response = rag_system.query(text=q)
        
        if response["success"]:
            results["question"].append(q)
            results["answer"].append(response["answer"])
            
            # Use the new source_contexts field
            contexts = response.get("source_contexts", [])
            results["contexts"].append(contexts)
            
            # Ragas/Datasets formatting
            results["ground_truth"].append(item["ground_truth"])
        else:
            print(f"Error processing query: {q}")

    # 4. Evaluate with Ragas
    # Convert to HuggingFace Dataset
    dataset = Dataset.from_dict(results)
    
    print("Calculating evaluation metrics with Ragas (using Gemini)...")
    # We pass the llm and embeddings to the evaluate function or configure metrics
    # New Ragas versions allow passing llm/embeddings in `evaluate` or `run_config`? 
    # Actually we need to set the llm for each metric or globally.
    # Let's try passing `llm` and `embeddings` to `evaluate` if supported (v0.1+)
    
    # Configure metrics with LLM
    # This represents a simplified setup; for robust use, we might need to configure each metric instance.
    # checking documentation pattern:
    
    # For now, let's try the simple `evaluate` call passing llm and embeddings.
    try:
        scores = evaluate(
            dataset=dataset,
            metrics=[
                faithfulness,
                answer_relevance,
                context_precision,
                context_recall,
            ],
            llm=gemini_llm, 
            embeddings=gemini_embeddings
        )
    except TypeError:
        # Fallback for older ragas versions: might need to set `measure.llm = gemini_llm`
        print("Passing llm/embeddings directly to evaluate failed. Trying to configure metrics...")
        for m in [faithfulness, answer_relevance, context_precision, context_recall]:
             # This is hacky and version dependent.
             if hasattr(m, 'llm'): m.llm = gemini_llm
             if hasattr(m, 'embeddings'): m.embeddings = gemini_embeddings
        
        scores = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevance, context_precision, context_recall]
        )

    
    # 5. Save Results
    df = scores.to_pandas()
    df.to_csv("tests/evaluation_report.csv", index=False)
    print("\nEvaluation complete! Results saved to tests/evaluation_report.csv")
    print(df[["question", "faithfulness", "answer_relevance", "context_precision", "context_recall"]])

if __name__ == "__main__":
    run_evaluation()
