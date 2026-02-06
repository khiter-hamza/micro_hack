import os
import csv
import json
from workflow import app

def run_pipeline(signals):
    print("🚀 Starting ReAct Multi-Agent Processing...")
    results = []
    
    for i, signal in enumerate(signals, 1):
        sig_id = f"SIG-{i}"
        print(f"\nProcessing {sig_id}...")
        
        # Initializing the state
        initial_state = {
            "signal_id": sig_id,
            "signal_text": signal,
            "corrected_text": "", # Placeholder to be filled by Agent 1
            "retry_count": 0,
            "processing_errors": [],
            "agent_thoughts": []
        }
        
        # Unique thread for LangGraph checkpointer
        config = {"configurable": {"thread_id": f"thread_{sig_id}"}}
        
        try:
            # Running the compiled graph
            final_state = app.invoke(initial_state, config=config)
            results.append(final_state)
            print(f"✅ Success: Tri-Score {final_state.get('tri')}")
        except Exception as e:
            print(f"❌ Error processing {sig_id}: {e}")

    return results

def save_results(results):
    os.makedirs("./data", exist_ok=True)
    
    # 1. Save JSON (Full State Dump)
    with open("./data/processed_signals.json", "w") as f:
        json.dump(results, f, indent=4)
    
    # 2. Save CSV (Clean Spreadsheet View)
    # Added 'corrected_text' to the headers
    keys = [
        "signal_id", 
        "corrected_text", 
        "domain", 
        "impact", 
        "urgency", 
        "tri", 
        "technologies", 
        "companies", 
        "location", 
        "retry_count"
    ]
    
    try:
        with open("./data/processed_signals.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        print("📂 Local CSV/JSON files updated in ./data/")
    except Exception as e:
        print(f"❌ File Save Error: {e}")

if __name__ == "__main__":
    # Add your real hackathon signals here
    test_signals = [
        "IBM announces a new 1000-qubit quantum processor called Condor.",
        "A new IoT sensor system for smart grids in Singapore.",
        "A cybersecurity breach at a major financial institution.",
    ]
    
    processed_data = run_pipeline(test_signals)
    save_results(processed_data)