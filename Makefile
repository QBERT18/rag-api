PY := backend/venv/bin/python

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
	cd backend && python -m venv venv
	$(PY) -m pip install --upgrade pip

install: venv
	$(PY) -m pip install -r backend/requirements.txt

backend:
	cd backend && venv/bin/python -m uvicorn main:app --reload

frontend:
	cd frontend && npm run dev

dev:
	$(MAKE) -j2 backend frontend

kill:
	-lsof -ti:8000,3000 | xargs kill -9 2>/dev/null || true

clean:
	rm -rf backend/chroma_db
