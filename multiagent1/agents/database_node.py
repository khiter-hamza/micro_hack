import psycopg
from state import GraphState

# REPLACE 'your_password' with the password you set in the terminal
DB_URI = "postgresql://postgres:password123@127.0.0.1:5432/micro_hack_db"

def init_db():
    """Initializes the table with the Corrected Text field included."""
    query = """
    CREATE TABLE IF NOT EXISTS signals_analysis (
        signal_id TEXT PRIMARY KEY,
        corrected_text TEXT,
        domain TEXT,
        impact FLOAT,
        urgency FLOAT,
        tri FLOAT,
        technologies TEXT[], 
        companies TEXT[],
        location TEXT,
        retry_count INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with psycopg.connect(DB_URI, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
        print("✅ Database Table signals_analysis is ready.")
    except Exception as e:
        print(f"❌ Initialization Error: {e}")

def save_to_db_node(state: GraphState) -> GraphState:
    """The Final Node: Persists state including corrected_text."""
    query = """
    INSERT INTO signals_analysis (
        signal_id, 
        corrected_text, 
        domain, 
        impact, 
        urgency, 
        tri, 
        technologies, 
        companies, 
        location, 
        retry_count
    ) VALUES (
        %(signal_id)s, 
        %(corrected_text)s, 
        %(domain)s, 
        %(impact)s, 
        %(urgency)s, 
        %(tri)s, 
        %(technologies)s, 
        %(companies)s, 
        %(location)s, 
        %(retry_count)s
    )
    ON CONFLICT (signal_id) DO UPDATE SET 
        corrected_text = EXCLUDED.corrected_text,
        domain = EXCLUDED.domain,
        impact = EXCLUDED.impact,
        urgency = EXCLUDED.urgency,
        tri = EXCLUDED.tri,
        retry_count = EXCLUDED.retry_count;
    """
    try:
        with psycopg.connect(DB_URI, autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(query, state)
                print(f"💾 Database updated for signal: {state['signal_id']}")
    except Exception as e:
        print(f"❌ DB Node Save Error: {e}")
    return state

def redis_push_node(state: GraphState) -> GraphState:
    """Pushes the signal to Redis for Tier-2 processing."""
    try:
        import redis
        import json
        
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        
        # Prepare payload
        payload = {
            "signal_id": state['signal_id'],
            "corrected_text": state['corrected_text']
        }
        
        # Push to the queue
        r.lpush("signal_queue", json.dumps(payload))
        print(f"🚀 Pushed to Redis Queue: {state['signal_id']}")
        
    except Exception as e:
        print(f"⚠️ Redis Push Error: {e}")
        
    return state