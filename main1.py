from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import URL
from schemas import URLCreate, URLResponse
from utils import generate_short_code
import fakeredis
import json

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener")

BASE_URL = "http://localhost:8000"

# Redis cache — using fakeredis (no Redis server needed)
cache = fakeredis.FakeRedis()
CACHE_EXPIRY = 3600  # 1 hour

@app.get("/")
def health():
    return {"status": "URL Shortener is running"}

@app.post("/shorten", response_model=URLResponse)
def shorten_url(payload: URLCreate, db: Session = Depends(get_db)):
    for _ in range(5):
        code = generate_short_code()
        if not db.query(URL).filter(URL.short_code == code).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique code")

    url = URL(short_code=code, long_url=payload.long_url)
    db.add(url)
    db.commit()
    db.refresh(url)

    # Save to cache
    cache.setex(code, CACHE_EXPIRY, url.long_url)

    return {**url.__dict__, "short_url": f"{BASE_URL}/{code}"}

@app.get("/analytics/{short_code}", response_model=URLResponse)
def get_analytics(short_code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="Not found")
    return {**url.__dict__, "short_url": f"{BASE_URL}/{short_code}"}

@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    # Step 1 — check cache first
    cached = cache.get(short_code)
    if cached:
        print(f"CACHE HIT for {short_code}")
        return RedirectResponse(url=cached.decode(), status_code=302)

    # Step 2 — cache miss, check database
    print(f"CACHE MISS for {short_code}")
    url = db.query(URL).filter(URL.short_code == short_code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Step 3 — save to cache for next time
    cache.setex(short_code, CACHE_EXPIRY, url.long_url)

    url.hit_count += 1
    db.commit()
    return RedirectResponse(url=url.long_url, status_code=302)