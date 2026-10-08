from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import cache, db
from .matching import (
    GROUPS,
    UnknownGroup,
    compatible_donors,
    compatible_recipients,
    is_eligible,
    rank_donors,
)

app = FastAPI(title="blood-bank")


class Donor(BaseModel):
    name: str
    group: str
    distance_km: float = 0
    age: int | None = None
    last_donation: date | None = None


@app.get("/health")
def health():
    out = {"status": "ok", "postgres": False, "redis": False}
    try:
        db.query("SELECT 1")
        out["postgres"] = True
    except Exception as exc:
        out["pg_error"] = str(exc)
    try:
        cache.client().ping()
        out["redis"] = True
    except Exception as exc:
        out["redis_error"] = str(exc)
    if not (out["postgres"] and out["redis"]):
        raise HTTPException(status_code=503, detail=out)
    return out


@app.get("/")
def root():
    return {
        "service": "blood-bank",
        "groups": GROUPS,
        "endpoints": ["GET /health", "GET /compatibility/{group}",
                      "GET /donors", "POST /donors", "GET /match/{group}"],
    }


@app.get("/compatibility/{group}")
def compatibility(group: str):
    """Who this group can give to, and receive from. Cached - it never changes."""
    key = f"compat:{group.upper()}"
    hit = cache.get(key)
    if hit:
        return {**hit, "cached": True}
    try:
        out = {
            "group": group.upper(),
            "can_donate_to": compatible_recipients(group),
            "can_receive_from": compatible_donors(group),
        }
    except UnknownGroup as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    cache.set(key, out, ttl=86400)
    return {**out, "cached": False}


@app.get("/donors")
def list_donors():
    return {"donors": db.query(
        "SELECT id, name, blood_group AS group, distance_km, age, last_donation"
        " FROM donors ORDER BY id")}


@app.post("/donors", status_code=201)
def add_donor(d: Donor):
    try:
        compatible_recipients(d.group)
    except UnknownGroup as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    rows = db.query(
        "INSERT INTO donors (name, blood_group, distance_km, age, last_donation)"
        " VALUES (%s,%s,%s,%s,%s) RETURNING id",
        (d.name, d.group.upper(), d.distance_km, d.age, d.last_donation))
    cache.drop("match:")
    return {"id": rows[0]["id"], **d.model_dump()}


@app.get("/match/{group}")
def match(group: str):
    """Compatible, eligible donors for a recipient, nearest first."""
    key = f"match:{group.upper()}"
    hit = cache.get(key)
    if hit:
        return {**hit, "cached": True}
    try:
        compatible_donors(group)
    except UnknownGroup as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    rows = db.query(
        "SELECT id, name, blood_group AS group, distance_km, age, last_donation FROM donors")
    ranked = rank_donors([dict(r) for r in rows], group.upper())
    out = {"recipient": group.upper(), "matches": ranked, "count": len(ranked)}
    cache.set(key, out, ttl=60)
    return {**out, "cached": False}


@app.get("/donors/{donor_id}/eligible")
def eligible(donor_id: int):
    rows = db.query("SELECT last_donation, age FROM donors WHERE id = %s", (donor_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="no such donor")
    ok, reason = is_eligible(rows[0]["last_donation"], age=rows[0]["age"])
    return {"donor_id": donor_id, "eligible": ok, "reason": reason}
