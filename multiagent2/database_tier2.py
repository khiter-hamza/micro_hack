import psycopg
from psycopg.rows import dict_row
import os

# Database Connection URI
DB_URI = "postgresql://postgres:password123@127.0.0.1:5432/micro_hack_db"

def fetch_pending_signal():
    """
    Finds a single row that has been processed by Tier-1 
    but is still 'pending' for Tier-2 analysis.
    """
    try:
        # We use row_factory=dict_row so we can access columns by name (e.g., row['signal_id'])
        with psycopg.connect(DB_URI, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT signal_id, corrected_text 
                    FROM signals_analysis 
                    WHERE tier_2_status = 'pending' 
                    LIMIT 1;
                """)
                return cur.fetchone()
    except Exception as e:
        print(f"❌ Error fetching from database: {e}")
        return None

def update_tier2_results(state: dict):
    """
    Updates the record with the full Tier-2 analysis and marks it as completed.
    """
    query = """
    UPDATE signals_analysis SET 
        tech_assessment = %s,
        tech_stack = %s,
        market_analysis = %s,
        feasibility_score = %s,
        recommendation = %s,
        tier_2_status = 'completed'
    WHERE signal_id = %s;
    """
    
    try:
        with psycopg.connect(DB_URI) as conn:
            with conn.cursor() as cur:
                # We pull data directly from the LangGraph final state
                cur.execute(query, (
                    state.get('technical_assessment'),
                    state.get('tech_stack'),   # psycopg automatically converts Python list to PG Array
                    state.get('market_analysis'),
                    state.get('feasibility_score'),
                    state.get('final_recommendation'),
                    state.get('signal_id')
                ))
            # No need for manual commit if using 'with' block context in psycopg 3
            print(f"💾 Database updated successfully for {state.get('signal_id')}")
            
    except Exception as e:
        print(f"❌ Error updating database: {e}")

def init_tier2_columns():
    """
    Helper function to ensure all required Tier-2 columns exist in the table.
    Run this once if you haven't manually updated your schema.
    """
    commands = [
        "ALTER TABLE signals_analysis ADD COLUMN IF NOT EXISTS tech_assessment TEXT;",
        "ALTER TABLE signals_analysis ADD COLUMN IF NOT EXISTS tech_stack TEXT[];",
        "ALTER TABLE signals_analysis ADD COLUMN IF NOT EXISTS market_analysis TEXT;",
        "ALTER TABLE signals_analysis ADD COLUMN IF NOT EXISTS feasibility_score FLOAT;",
        "ALTER TABLE signals_analysis ADD COLUMN IF NOT EXISTS recommendation TEXT;",
        "ALTER TABLE signals_analysis ADD COLUMN IF NOT EXISTS tier_2_status TEXT DEFAULT 'pending';"
    ]
    
    try:
        with psycopg.connect(DB_URI) as conn:
            with conn.cursor() as cur:
                for cmd in commands:
                    cur.execute(cmd)
        print("✅ Tier-2 Schema check complete.")
    except Exception as e:
        print(f"❌ Schema init failed: {e}")

if __name__ == "__main__":
    # If run directly, prepare the database
    init_tier2_columns()