import json
import os
import subprocess
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
FRONTEND_DIST = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "dist"))
SUMMARY_PATH = os.path.join(BASE_DIR, "data", "summary.json")
PROCESSOR_PATH = os.path.join(BASE_DIR, "processor.py")


@app.get("/api/result")
def get_result():
    if not os.path.exists(SUMMARY_PATH):
        raise HTTPException(status_code=404, detail="summary.json not found. Run the processor first.")
    with open(SUMMARY_PATH, encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/run")
def run_processor():
  result = subprocess.run(
    [sys.executable, PROCESSOR_PATH],
    cwd=PROJECT_ROOT,
    capture_output=True,
    text=True,
  )
  if result.returncode != 0:
    detail = result.stderr.strip() or "Processor failed. Check server logs for details."
    raise HTTPException(status_code=500, detail=detail)
  return {"ok": True}


if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
else:

    @app.get("/")
    def root():
        return HTMLResponse(
            """
            <html>
              <head><title>CSV Results</title></head>
              <body style='font-family: sans-serif; padding: 24px;'>
                <h1>Frontend not built</h1>
                <p>Run the processor and build the React frontend.</p>
                <ul>
                  <li>python backend/processor.py backend/data/input1.csv backend/data/input2.csv backend/data/output.csv</li>
                  <li>cd frontend && npm install</li>
                  <li>npm run build</li>
                </ul>
              </body>
            </html>
            """
        )
