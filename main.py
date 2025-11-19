import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import db
from schemas import Settings, QuizQuestion
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLECTION = "settings"

# Helpers

def get_settings_doc():
    doc = db[COLLECTION].find_one({"key": "singleton"})
    if not doc:
        default = Settings().model_dump()
        default["created_at"] = datetime.utcnow()
        default["updated_at"] = datetime.utcnow()
        db[COLLECTION].insert_one(default)
        doc = db[COLLECTION].find_one({"key": "singleton"})
    return doc

@app.get("/api/settings")
async def get_settings():
    doc = get_settings_doc()
    doc["_id"] = str(doc["_id"])  # stringify for JSON
    return doc

class SettingsUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    primaryColor: Optional[str] = None
    accentColor: Optional[str] = None
    heroLogoUrl: Optional[str] = None
    wheelBgUrl: Optional[str] = None
    quizQuestions: Optional[list[QuizQuestion]] = None

@app.post("/api/settings")
async def update_settings(payload: SettingsUpdate):
    updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not updates:
        return JSONResponse({"updated": False, "message": "No changes"})
    updates["updated_at"] = datetime.utcnow()
    db[COLLECTION].update_one({"key": "singleton"}, {"$set": updates}, upsert=True)
    return {"updated": True}

# Simple in-DB file store using GridFS-like bucket is not available here; we'll store as base64 strings.
# For simplicity and speed in this environment, store uploaded file bytes into a dedicated collection and return an id URL.
from bson import ObjectId

MEDIA_COLLECTION = "media"

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    content = await file.read()
    doc = {
        "filename": file.filename,
        "content_type": file.content_type,
        "data": content,
        "created_at": datetime.utcnow(),
    }
    res = db[MEDIA_COLLECTION].insert_one(doc)
    return {"url": f"/api/media/{str(res.inserted_id)}"}

from fastapi import HTTPException
from fastapi.responses import Response

@app.get("/api/media/{media_id}")
async def get_media(media_id: str):
    try:
        oid = ObjectId(media_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid media id")
    doc = db[MEDIA_COLLECTION].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(content=doc["data"], media_type=doc.get("content_type") or "application/octet-stream")

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
