# SalaryPay License Server - Setup Instructions

## Backend Setup (Port: 8661)

### Windows:
```bash
setup-windows.bat
```

Backend server **http://localhost:8661** var run hoil.

API Docs: **http://localhost:8661/docs**

---

## Frontend Setup (Port: 3441)

### Windows:
```bash
run-frontend.bat
```

Frontend UI **http://localhost:3441** var run hoil.

---

## Manual Commands

### Backend:
```bash
# Virtual environment activate
venv\Scripts\activate

# Server run
uvicorn app.main:app --host 0.0.0.0 --port 8661 --reload
```

### Frontend:
```bash
cd frontend

# Dependencies install (first time only)
npm install

# Development server run
npm run dev
```

---

## Ports Configuration

- **Backend API**: 8661
- **Frontend UI**: 3441
- **API Proxy**: Frontend automatically proxies `/api` requests to backend

---

## Troubleshooting

### Backend Issues:
- Python 3.13+ required
- Check `.env` file exists
- Run `venv\Scripts\pip.exe install -r requirements-windows.txt`

### Frontend Issues:
- Node.js required (v18+)
- Delete `node_modules` and run `npm install` again
- Check if port 3441 is already in use

---

## Project Structure

```
license-server/
├── app/                    # Backend FastAPI code
├── frontend/               # React UI
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
├── setup-windows.bat       # Backend setup script
└── run-frontend.bat        # Frontend run script
```
