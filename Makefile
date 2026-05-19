PY := backend/venv/Scripts/python.exe

.PHONY: backend frontend dev kill install clean help

help:
	@echo "make backend  - run FastAPI dev server (Swagger at http://localhost:8000/docs)"
	@echo "make frontend - run Nuxt dev server (http://localhost:3000)"
	@echo "make dev      - run backend and frontend together"
	@echo "make kill     - kill processes listening on ports 8000 and 3000"
	@echo "make install  - install backend dependencies"
	@echo "make clean    - wipe local Chroma vector store"

backend:
	cd backend && venv\Scripts\python.exe -m uvicorn main:app --reload

frontend:
	cd frontend && npm run dev

dev:
	$(MAKE) -j2 backend frontend

kill:
	-powershell -NoProfile -Command 'Get-NetTCPConnection -LocalPort 8000,3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $$_ -Force -ErrorAction SilentlyContinue }'

install:
	$(PY) -m pip install -r backend/requirements.txt

clean:
	rm -rf backend/chroma_db
