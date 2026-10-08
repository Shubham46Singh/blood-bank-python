# Blood Bank Donor Matching

**Language:** Python &nbsp;|&nbsp; **Needs:** Postgres + Redis

This is a **starter**. The application already works. Your job is everything
that gets it building, tested and running in CI.

---

## You do not need Python installed

You will build this into a container, and the container brings its own
Python 3.12. If you have never written a line of Python, you can still finish
this assignment — you are not being asked to extend the app, you are being
asked to ship it.

Read the two sections below in order. The first tells you what the app needs;
the second is how you turn that into a Dockerfile.

---

## 1. What this app actually needs

This is the whole contract. Everything in your Dockerfile and compose file
comes from this table.

| | |
|---|---|
| **Runtime** | Python 3.12 |
| **Install dependencies** | `pip install -r requirements.txt` |
| **Start the app** | `uvicorn app.main:app --host 0.0.0.0 --port 8080` |
| **Listens on** | port 8080, bound to `0.0.0.0` |
| **Environment variables** | `DATABASE_URL`, `REDIS_URL` |
| **Needs running first** | Postgres, Redis, and the migrations applied |

### Endpoints

```
GET  /health                    is it alive, and are Postgres and Redis reachable
GET  /compatibility/{group}     who this group can give to and receive from
GET  /donors                    every donor
POST /donors                    add one
GET  /match/{group}             compatible, eligible donors, nearest first
GET  /donors/{id}/eligible      can this person donate today, and if not why
```

`/health` reports Postgres and Redis **separately**. Use it constantly:
if it says `postgres: false`, the app started fine and your compose wiring
is wrong — do not go looking in the application code.

### Migrations

`migrations/` holds `.sql` files that must be applied **in filename order**,
before the app starts. They create the tables and insert sample data, so the
app is worth looking at the first time you run it.

You do not need an ORM or a migration tool. A container running `psql` over
the files in order is enough, and works whatever language the app is in.

---

## 2. What you must write

| File | What it has to do |
|---|---|
| `Dockerfile` | Build this app into an image. Install dependencies **before** copying the source, pin the base image version, and do not run as root. |
| `docker-compose.yml` | Start the app, Postgres, Redis and a migration step with one `docker compose up`. |
| `.circleci/config.yml` | lint → unit tests → integration tests → secret scan → image build |
| Unit tests | For `app/matching.py`. No database, no network. |
| Integration tests | Against a real Postgres and Redis as CircleCI service containers. |

Then push your image to **your own Docker Hub account**, tagged with a real
version number — `:1.0`, not only `:latest`.

### When it works

```bash
docker compose up --build
curl localhost:8080/health
```

```json
{"status":"ok","postgres":true,"redis":true}
```

Both true, or you are not finished.

---

## 3. If you want to run it without Docker first

Optional, and only useful if you already have Python 3.12. Most people should
skip straight to the Dockerfile — the whole point is that the container
removes this step.

```bash
pip install -r requirements.txt
export DATABASE_URL=...
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

---

## Where the marks are

`app/matching.py` is **pure logic** — plain functions over plain data, no database and
no HTTP. That is deliberate, so a 70% coverage target is achievable rather
than busywork. Start your tests there.

Use pytest. `pytest --cov=app --cov-report=term-missing`.

## The hard part

Compatibility is **not symmetric**. O- can donate to A+, but A+ cannot donate to O-. Students invert this constantly — test both directions of every pair. There are 8 groups, so 8 x 8 = 64 cases. Exactly 27 are compatible; if your tests say otherwise, something is wrong.

Write your answer to this in your README. It is worth more marks than the
feature itself.

---

## Getting unstuck

| Symptom | Almost always |
|---|---|
| `/health` says `postgres: false` | Wrong hostname. Inside compose the host is the **service name**, not `localhost`. |
| Page will not load, logs look fine | No `ports:` mapping, or the app is bound to `127.0.0.1` instead of `0.0.0.0`. |
| `relation "..." does not exist` | Migrations did not run, or the app started before they finished. |
| Build takes minutes every time | `COPY . .` is above your dependency install. |
| CI cannot reach the database | In CircleCI service containers the host **is** `localhost` — the opposite of compose. |
