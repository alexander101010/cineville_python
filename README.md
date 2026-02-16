# Cineville Technical Challenge - Members and Visits

This repo supports two evaluation paths:
- CLI: run the Python processor directly.
- Web: start a local FastAPI server and view a React + Tailwind UI.

## 1) CLI
Defaults (no args):
```
python3 backend/processor.py
```
#Reads:
- `backend/data/members.csv`
- `backend/data/visits.csv`
  
#Writes:
- `backend/data/output.csv`
- `backend/data/summary.json`

Override paths:
```
python3 backend/processor.py --members backend/data/members.csv --visits backend/data/visits.csv --output backend/data/output.csv
```

## 2) Web
### Backend
From the project root:
```
pip install fastapi uvicorn
uvicorn backend.app:app --reload
```
Open `http://localhost:8000`.

### Frontend
Choose one:

Option A: build the UI so FastAPI can serve it on `http://localhost:8000`:
```
cd frontend
npm install
npm run build
```

Option B: run the dev server (separate port) while FastAPI runs at `http://localhost:8000`:
```
cd frontend
npm install
npm run dev
```

## 3) Testing
```
pytest
```
 Tests use `pytest`. Even in a small project, tests lock in the CSV parsing/validation rules and make it safer to evolve the logic if the data volume or requirements grow. Always good to make sure logic is behaving as you expect it to, with validation working correctly and data being shaped as expected, especially when writing documents.

## Notes
- Core logic lives in `backend/logic.py`. The CLI entrypoint is `backend/processor.py`.
- The FastAPI UI reads `backend/data/summary.json`. It can be generated via the CLI or via a button in the frontend if you spin up the backend and frontend and visit the localhost page before running the actual program.
- The summary includes the bonus outputs (top 5 members and total walk-ins).


## Approach Summary
- Parse `members.csv` into a barcode → member index.
- Parse `visits.csv`, validate barcode presence and existence in members index.
- Group valid visits by member (python dictionary with (barcode, member_id) tuple as key: value is list of valid visits).
- Emit output CSV: `member_id,barcode,visit_id1,visit_id2,...`
    - Extra bonus: build summary.json out of data for FastAPI endpoint to serve to frontend of simple react app.
- Log invalid visits (missing barcode or unknown barcode) to stderr in terminal.
- Bonus: 
    - print top 5 members by visit count (sort grouped data that was used to build CSV to get top 5)
    - total walk-ins (count while validating visits).
        - Also add this info to summary for web page

## AI Usage
- For the actual backend work I asked AI for some guidance geared towards a Typescript developer coding in Python for the first time. Pitfalls, similarities and differences, common file structure and explanations of loops, indentation, common data structures (particularly ones similar to sets in Javascript for quick lookups) and variable assignment in Python. The actual writing of the functions was pretty easy once I understood the syntax, as mostly we are looping through the data to build what we need in memory in absence of any database. I had to look up handling the reading and writing of CSV documents as well, but that was pretty boilerplate once I found an example or two.

- I also used Codex to advise me about Python frameworks for building a simple webpage to display some of the results of the program. I was curious if I could quickly get a simple react page and api endpoint up and running and Codex helped me setup FastAPI and Vite, two things I had not previously used. 

- I also used Codex to help build the tests, one of my favorite uses of AI. As the core functions were already built, Codex made quick work of building the tests, though I did steer it and change them a bit of course.
