import json
import os
import re
import uuid
from contextlib import contextmanager
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

app = FastAPI(title="Therapy Project", version="0.2.0")
WEB = Path.cwd() / "web"
INDEX = WEB / "index.html"
ASSETS = WEB / "assets"
DATABASE_URL = os.getenv("DATABASE_URL", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
THERAPIST_MODEL = os.getenv("OPENAI_THERAPIST_MODEL", "gpt-5.6-sol")
MEMORY_MODEL = os.getenv("OPENAI_MEMORY_MODEL", "gpt-5.6-luna")
SUPERVISOR_MODEL = os.getenv("OPENAI_SUPERVISOR_MODEL", "gpt-5.6-terra")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(id uuid PRIMARY KEY, created_at timestamptz DEFAULT now());
CREATE TABLE IF NOT EXISTS sessions(id uuid PRIMARY KEY, user_id uuid REFERENCES users(id), created_at timestamptz DEFAULT now());
CREATE TABLE IF NOT EXISTS messages(id bigserial PRIMARY KEY, session_id uuid REFERENCES sessions(id), role text NOT NULL, content text NOT NULL, created_at timestamptz DEFAULT now());
CREATE TABLE IF NOT EXISTS memories(id bigserial PRIMARY KEY, user_id uuid REFERENCES users(id), kind text NOT NULL, content text NOT NULL, confidence real DEFAULT .6, source_message_id bigint, active boolean DEFAULT true, created_at timestamptz DEFAULT now());
CREATE TABLE IF NOT EXISTS treatment_state(user_id uuid PRIMARY KEY REFERENCES users(id), target text DEFAULT 'در حال شناخت مسئله', stage text DEFAULT 'assessment_formulation', formulation text DEFAULT '', homework text DEFAULT '', progress real DEFAULT 0, confidence real DEFAULT .2, updated_at timestamptz DEFAULT now());
"""

@contextmanager
def db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing")
    with psycopg.connect(DATABASE_URL) as conn:
        yield conn

@app.on_event("startup")
def startup():
    with db() as conn:
        conn.execute(SCHEMA)
        conn.commit()

class SessionCreate(BaseModel):
    user_id: str | None = None

class ChatIn(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=12000)


def recent_messages(conn, session_id, limit=18):
    rows = conn.execute("SELECT role,content FROM messages WHERE session_id=%s ORDER BY id DESC LIMIT %s", (session_id, limit)).fetchall()
    return list(reversed(rows))


def get_context(conn, user_id):
    state = conn.execute("SELECT target,stage,formulation,homework,progress,confidence FROM treatment_state WHERE user_id=%s", (user_id,)).fetchone()
    memories = conn.execute("SELECT kind,content,confidence FROM memories WHERE user_id=%s AND active=true ORDER BY confidence DESC, id DESC LIMIT 14", (user_id,)).fetchall()
    return state, memories


def safety_signal(text: str) -> bool:
    t = text.lower()
    patterns = ["خودکشی", "خودمو بکشم", "خودم را بکشم", "نمیخوام زنده", "نمی‌خوام زنده", "به خودم آسیب", "suicide", "kill myself", "self harm"]
    return any(p in t for p in patterns)


def therapist_prompt(state, memories):
    target, stage, formulation, homework, progress, confidence = state
    memory_text = "\n".join(f"- [{k}|{c:.2f}] {v}" for k, v, c in memories) or "- هنوز حافظه تثبیت‌شده‌ای نداریم."
    return f"""تو درمانگر مکالمه‌ای اصلی یک سیستم treatment-first فارسی‌زبان هستی. هدف تو فقط جواب دادن نیست؛ باید هم‌زمان به حال فعلی فرد کمک کنی و مسیر بلندمدت درمان را گم نکنی.

قواعد غیرقابل مذاکره:
- گرم، دقیق، انسانی و غیرکلیشه‌ای باش؛ از تعریف و تایید بی‌دلیل خودداری کن.
- تشخیص قطعی، علت‌تراشی قطعی درباره کودکی، یا وعده درمان نده. فرضیه را فرضیه بنام.
- از اطلاعات حافظه فقط وقتی مرتبط است استفاده کن و طوری اشاره کن که کاربر حس شناخت پیوسته داشته باشد، نه جاسوسی.
- اگر کاربر فقط نیاز به تخلیه هیجانی دارد، اول regulate/understand کن؛ ولی Treatment State را در ذهن نگه دار.
- در پایان هر پاسخ فقط وقتی طبیعی است یک سؤال یا next step مشخص بده. جواب‌ها را بی‌جهت طولانی نکن.
- اگر تکلیف فعال مرتبط است، آن را فراموش نکن.
- اگر نشانه خطر فوری خودآسیبی/خودکشی وجود دارد، به جای درمان عادی روی ایمنی فوری، تماس با فرد قابل اعتماد و خدمات اورژانسی محلی تمرکز کن.

Treatment State:
Target: {target}
Stage: {stage}
Formulation: {formulation or 'هنوز در حال شکل‌گیری'}
Active homework: {homework or 'فعلاً ندارد'}
Progress estimate: {progress:.0f}% (confidence {confidence:.2f}; این درصد درمان‌شدن نیست)

Relevant longitudinal memory:
{memory_text}
"""


def run_memory_agent(user_id, source_id, user_text, assistant_text):
    if not client:
        return
    instruction = """از این تعامل فقط اطلاعاتی را استخراج کن که برای شناخت بلندمدت فرد یا درمان آینده واقعاً مهم است. خروجی فقط JSON array باشد. هر آیتم: {\"kind\":\"fact|pattern|preference|event|goal|clinical_hypothesis|achievement\",\"content\":\"...\",\"confidence\":0.0}. فرضیه را fact نکن. حداکثر 4 آیتم. اگر چیزی ارزش نگهداری ندارد [] بده."""
    try:
        r = client.responses.create(model=MEMORY_MODEL, input=[{"role":"system","content":instruction},{"role":"user","content":f"USER: {user_text}\nASSISTANT: {assistant_text}"}])
        raw = r.output_text.strip()
        raw = re.sub(r"^```json\s*|\s*```$", "", raw)
        items = json.loads(raw)
        with db() as conn:
            for x in items[:4]:
                if x.get("content"):
                    conn.execute("INSERT INTO memories(user_id,kind,content,confidence,source_message_id) VALUES(%s,%s,%s,%s,%s)", (user_id, x.get("kind","fact"), x["content"][:1200], max(0,min(1,float(x.get("confidence",.6)))), source_id))
            conn.commit()
    except Exception:
        pass


def run_supervisor(user_id, session_id):
    if not client:
        return
    with db() as conn:
        count = conn.execute("SELECT count(*) FROM messages WHERE session_id=%s AND role='user'", (session_id,)).fetchone()[0]
        if count < 4 or count % 4:
            return
        state, memories = get_context(conn, user_id)
        history = recent_messages(conn, session_id, 20)
    prompt = """تو Clinical Supervisor هستی. مکالمه را مرور کن و مسیر درمان را از چت آزاد جدا نگه دار. خروجی فقط JSON object با کلیدهای target, stage, formulation, homework, progress, confidence باشد. progress بین 0 و100 و فقط تخمین پیشرفت نسبت به target است، نه درصد درمان. بدون شواهد مرحله را جلو نبر و تشخیص قطعی نساز."""
    payload = {"state":state,"memories":memories,"history":history}
    try:
        r = client.responses.create(model=SUPERVISOR_MODEL, input=[{"role":"system","content":prompt},{"role":"user","content":json.dumps(payload, ensure_ascii=False)}])
        raw = re.sub(r"^```json\s*|\s*```$", "", r.output_text.strip())
        x = json.loads(raw)
        with db() as conn:
            conn.execute("UPDATE treatment_state SET target=%s,stage=%s,formulation=%s,homework=%s,progress=%s,confidence=%s,updated_at=now() WHERE user_id=%s", (str(x.get("target",state[0]))[:500],str(x.get("stage",state[1]))[:100],str(x.get("formulation",state[2]))[:3000],str(x.get("homework",state[3]))[:1200],max(0,min(100,float(x.get("progress",state[4])))),max(0,min(1,float(x.get("confidence",state[5])))),user_id))
            conn.commit()
    except Exception:
        pass

@app.get("/api/health")
def health():
    return {"status":"ok","service":"therapy-project","web_ready":INDEX.is_file(),"ai_connected":bool(client)}

@app.get("/api/bootstrap")
def bootstrap():
    return {"phase":"alpha-runtime","ai_connected":bool(client),"therapist_model":THERAPIST_MODEL,"clinical_team":["therapist","formulation","supervisor","memory","outcome_progress","safety"],"principle":"present-state first; treatment-state always preserved"}

@app.post("/api/sessions")
def create_session(body: SessionCreate):
    try:
        uid = uuid.UUID(body.user_id) if body.user_id else uuid.uuid4()
    except ValueError:
        raise HTTPException(400,"invalid user_id")
    sid = uuid.uuid4()
    with db() as conn:
        conn.execute("INSERT INTO users(id) VALUES(%s) ON CONFLICT DO NOTHING", (uid,))
        conn.execute("INSERT INTO treatment_state(user_id) VALUES(%s) ON CONFLICT DO NOTHING", (uid,))
        conn.execute("INSERT INTO sessions(id,user_id) VALUES(%s,%s)", (sid,uid))
        conn.commit()
    return {"user_id":str(uid),"session_id":str(sid)}

@app.get("/api/sessions/{session_id}/messages")
def list_messages(session_id: str):
    with db() as conn:
        rows = conn.execute("SELECT role,content,created_at FROM messages WHERE session_id=%s ORDER BY id", (session_id,)).fetchall()
    return [{"role":r,"content":c,"created_at":t.isoformat()} for r,c,t in rows]

@app.get("/api/users/{user_id}/state")
def user_state(user_id: str):
    with db() as conn:
        state, memories = get_context(conn,user_id)
    return {"target":state[0],"stage":state[1],"formulation":state[2],"homework":state[3],"progress":state[4],"confidence":state[5],"memories":[{"kind":k,"content":v,"confidence":c} for k,v,c in memories]}

@app.post("/api/chat")
def chat(body: ChatIn):
    if not client:
        raise HTTPException(503,"OPENAI_API_KEY هنوز روی سرور تنظیم نشده است")
    try:
        sid = uuid.UUID(body.session_id)
    except ValueError:
        raise HTTPException(400,"invalid session_id")
    with db() as conn:
        row = conn.execute("SELECT user_id FROM sessions WHERE id=%s",(sid,)).fetchone()
        if not row:
            raise HTTPException(404,"session not found")
        uid = row[0]
        cur = conn.execute("INSERT INTO messages(session_id,role,content) VALUES(%s,'user',%s) RETURNING id",(sid,body.message))
        user_msg_id = cur.fetchone()[0]
        state, memories = get_context(conn,uid)
        history = recent_messages(conn,sid,16)
        conn.commit()
    system = therapist_prompt(state,memories)
    if safety_signal(body.message):
        system += "\nSafety signal detected: پاسخ را روی ایمنی فوری و ارزیابی مستقیم خطر متمرکز کن و درمان عادی را موقتاً متوقف کن."
    inputs = [{"role":"system","content":system}] + [{"role":r,"content":c} for r,c in history]
    try:
        response = client.responses.create(model=THERAPIST_MODEL,input=inputs)
        answer = response.output_text.strip()
    except Exception as exc:
        raise HTTPException(502,f"AI provider error: {type(exc).__name__}")
    with db() as conn:
        conn.execute("INSERT INTO messages(session_id,role,content) VALUES(%s,'assistant',%s)",(sid,answer))
        conn.commit()
    run_memory_agent(uid,user_msg_id,body.message,answer)
    run_supervisor(uid,sid)
    return {"answer":answer,"user_id":str(uid),"safety_mode":safety_signal(body.message)}

if ASSETS.is_dir():
    app.mount("/assets",StaticFiles(directory=ASSETS),name="assets")

@app.get("/{path:path}")
def spa(path:str):
    if not INDEX.is_file():
        return {"status":"error","detail":"Web bundle missing","expected_path":str(INDEX)}
    return FileResponse(INDEX)
