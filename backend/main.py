import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Response
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pypinyin import Style, lazy_pinyin
from snownlp import SnowNLP

from storage import get_history, init_db, save_record

load_dotenv(Path(__file__).with_name(".env"))
ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if not ALLOWED_ORIGINS:
    raise RuntimeError("请在 backend/.env 中配置 ALLOWED_ORIGINS，参考 backend/.env.example")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_credentials=True,
)

init_db()


profile = {
    "heroTitle": "关于我（来自后端）",  # → 临时加的标记，验证完删掉
    "heroSubtitle": "项目，创意，灵感，心得，我的作品",
    "featuredWork": {
        "kicker": "作品",
        "title": "文字实验室",
        "copy": "拼音和情绪，挖掘中文里的细节",
        "linkLabel": "打开作品",
    },
    "identity": {
        "motto": "已识乾坤大，尤怜草木青",
        "learning": "零到全栈",
    },
}


class AnalyzeRequest(BaseModel):
    text: str


def get_session_id(request: Request, response: Response) -> str:
    sid = request.cookies.get("session_id")
    if not sid:
        sid = uuid.uuid4().hex
        response.set_cookie(
            "session_id",
            sid,
            httponly=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30,
        )
    return sid


@app.get("/api/profile")
def get_profile():
    return profile


def score_label(score: float) -> str:
    if score >= 0.6:
        return "偏积极"
    elif score <= 0.4:
        return "偏消极"
    else:
        return "中性"


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest, request: Request, response: Response):
    text = req.text
    if not text.strip():
        raise HTTPException(status_code=422, detail="请输入要分析的文字")
    sid = get_session_id(request, response)
    score = round(SnowNLP(text).sentiments, 2)
    result = {
        "text": text,
        "score": score,
        "label": score_label(score),
        "pinyin": " ".join(lazy_pinyin(text, style=Style.TONE)),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    save_record(sid, result)
    return result


@app.get("/api/history")
def history(request: Request, response: Response, limit: int = Query(default=10, ge=1, le=100)):
    sid = get_session_id(request, response)
    return get_history(sid, limit)
