import time
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
from workflow import app  # Imports the compiled LangGraph
from database_tier2 import fetch_pending_signal, update_tier2_results
load_dotenv()

def run_automation_loop():
    print("🤖 Tier-2 Automation Watcher is ONLINE.")
    print("👀 Watching 'signals_analysis' table for new rows...")

    while True:
        try:
            # 1. Check for a pending row
            row = fetch_pending_signal()

            if row:
                sig_id = row['signal_id']
                text = row['corrected_text']
                
                print(f"\n🚀 [EVENT] New signal detected: {sig_id}")
                print(f"📝 Input: {text[:100]}...")

                # 2. Prepare the initial state for Tier-2
                # We initialize dictionaries for confidences and retries
                initial_state = {
                    "signal_id": sig_id,
                    "corrected_text": text,
                    "confidences": {},
                    "retry_counts": {},
                    "agent_thoughts": [f"Starting Tier-2 deep dive for {sig_id}"]
                }

                # 3. Invoke the Multi-Agent Graph
                # thread_id allows us to track this specific execution in the checkpoints
                config = {"configurable": {"thread_id": f"tier2_{sig_id}"}}
                
                print(f"🧠 Agents are thinking...")
                final_state = app.invoke(initial_state, config=config)

                # 4. Save the results back to PostgreSQL
                update_tier2_results(final_state)
                print(f"✅ Deep Dive Complete for {sig_id}. Database updated.")
            
            else:
                # No new data? Wait and try again
                time.sleep(10)

        except KeyboardInterrupt:
            print("\n🛑 Watcher stopped by user.")
            break
        except Exception as e:
            print(f"❌ Error in Watcher Loop: {e}")
            time.sleep(20) # Wait longer if there's a crash (e.g., DB connection lost)

if __name__ == "__main__":
    run_automation_loop()