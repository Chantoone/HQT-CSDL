## Create and active the virtual environment
python -m venv .venv
.venv/scripts/activate

## Install dependence
pip install -r requirements.txt

## Run FastAPI
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

## Update database with Alembic
0. Init
alembic init alembic
1. Create new version of db:
alembic revision --autogenerate
2. Upgrade to newest version
alembic upgrade head -m "message"