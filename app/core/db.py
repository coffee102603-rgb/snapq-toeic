import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    return None

def init_db():
    conn = get_conn()
    if not conn: return
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_storage (
                player_id TEXT PRIMARY KEY,
                saved_questions JSONB DEFAULT '[]',
                saved_expressions JSONB DEFAULT '[]',
                updated_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS survey_log (
                id SERIAL PRIMARY KEY,
                player_id TEXT,
                device TEXT,
                phone_model TEXT,
                posture TEXT,
                eye_distance TEXT,
                screen_width INT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY,
                player_id TEXT,
                event TEXT,
                data JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS diagnosis_log (
                id SERIAL PRIMARY KEY,
                player_id TEXT,
                day_num INT,
                score INT,
                total INT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        conn.commit()
    conn.close()

def load_storage_db(player_id):
    conn = get_conn()
    if not conn:
        return {"saved_questions": [], "saved_expressions": []}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM user_storage WHERE player_id=%s", (player_id,))
        row = cur.fetchone()
    conn.close()
    if row:
        return {
            "saved_questions": row["saved_questions"] or [],
            "saved_expressions": row["saved_expressions"] or []
        }
    return {"saved_questions": [], "saved_expressions": []}

def save_storage_db(player_id, data):
    conn = get_conn()
    if not conn: return
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO user_storage (player_id, saved_questions, saved_expressions, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (player_id) DO UPDATE
            SET saved_questions=EXCLUDED.saved_questions,
                saved_expressions=EXCLUDED.saved_expressions,
                updated_at=NOW()
        """, (player_id, json.dumps(data.get("saved_questions",[])), json.dumps(data.get("saved_expressions",[]))))
        conn.commit()
    conn.close()

def save_survey_db(player_id, answers, screen_width, user_agent):
    conn = get_conn()
    if not conn: return
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO survey_log (player_id, device, phone_model, posture, eye_distance, screen_width, user_agent)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (player_id, answers.get("q1",""), answers.get("q2",""), answers.get("q3",""), answers.get("q4",""), screen_width, user_agent))
        conn.commit()
    conn.close()

def save_activity_db(player_id, event, data={}):
    conn = get_conn()
    if not conn: return
    with conn.cursor() as cur:
        cur.execute("INSERT INTO activity_log (player_id, event, data) VALUES (%s,%s,%s)",
                    (player_id, event, json.dumps(data)))
        conn.commit()
    conn.close()

def save_diagnosis_db(player_id, day_num, score, total):
    conn = get_conn()
    if not conn: return
    with conn.cursor() as cur:
        cur.execute("INSERT INTO diagnosis_log (player_id, day_num, score, total) VALUES (%s,%s,%s,%s)",
                    (player_id, day_num, score, total))
        conn.commit()
    conn.close()

def is_db_available():
    return DATABASE_URL is not None
