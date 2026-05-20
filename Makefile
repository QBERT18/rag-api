ifeq ($(OS),Windows_NT)
	SHELL := cmd.exe
	.SHELLFLAGS := /C
	PY := backend\venv\Scripts\python.exe
	VENV_PY := venv\Scripts\python.exe
	VENV_CHECK := if exist backend\venv\Scripts\python.exe (echo venv exists) else (cd backend && python -m venv venv)
	KILL_PORTS := powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000,3000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $$_.OwningProcess -Force -ErrorAction SilentlyContinue }"
	CLEAN_CHROMA := if exist backend\chroma_db rmdir /S /Q backend\chroma_db
else
	PY := backend/venv/bin/python
	VENV_PY := venv/bin/python
	VENV_CHECK := test -x $(PY) || (cd backend && python -m venv venv)
	KILL_PORTS := lsof -ti:8000,3000 | xargs kill -9 2>/dev/null || true
	CLEAN_CHROMA := rm -rf backend/chroma_db
endif

.PHONY: backend frontend dev kill venv install clean help

help:
	@echo "make venv     - create backend venv using pyenv-pinned Python"
	@echo "make install  - install backend dependencies into venv"
	@echo "make backend  - run FastAPI dev server (Swagger at http://localhost:8000/docs)"
	@echo "make frontend - run Nuxt dev server (http://localhost:3000)"
	@echo "make dev      - run backend and frontend together"
	@echo "make kill     - kill processes listening on ports 8000 and 3000"
	@echo "make clean    - wipe local Chroma vector store"

venv:
	@$(VENV_CHECK)
	$(PY) -m pip install --upgrade pip

install: venv
	$(PY) -m pip install -r backend/requirements.txt

backend:
	cd backend && $(VENV_PY) -m uvicorn main:app --reload

frontend:
	cd frontend && npm run dev

dev:
	$(MAKE) -j2 backend frontend

kill:
	-$(KILL_PORTS)

clean:
	$(CLEAN_CHROMA)
