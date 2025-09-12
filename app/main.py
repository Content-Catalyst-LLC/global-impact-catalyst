from fastapi import FastAPI

app = FastAPI(title="Global Impact Catalyst")

@app.get("/healthz")
def healthz():
    return {"ok": True}
