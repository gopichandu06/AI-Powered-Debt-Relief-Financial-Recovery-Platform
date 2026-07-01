# FinRelief AI 💰
### AI-Powered Debt Relief & Financial Recovery Platform

> A production-ready, enterprise-grade fintech SaaS application that helps borrowers analyze debt, receive AI-powered settlement recommendations, generate professional lender negotiation letters, and track their financial recovery journey.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Auth** | JWT authentication with bcrypt password hashing |
| 📊 **Financial Analysis** | Debt-to-income ratio, health score, stress levels |
| 🏦 **Loan Management** | Full CRUD — add, edit, delete, track multiple loans |
| 🤖 **AI Settlement Engine** | Google Gemini-powered settlement recommendations |
| 📝 **Letter Generator** | Professional AI-crafted lender negotiation letters |
| 📈 **Analytics Dashboard** | Interactive charts powered by Recharts |
| 🛡️ **Borrower Rights** | Educational content about your legal rights |
| 📋 **History Tracking** | Complete audit trail of recommendations and letters |
| ⚡ **Fallback Engine** | Rule-based AI fallback — never crashes without API key |

---

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI 0.111 (Python 3.11)
- **ORM**: SQLAlchemy 2.0
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT + bcrypt (python-jose + passlib)
- **AI**: Google Gemini 2.0 Flash

### Frontend
- **Framework**: React 18 + Vite 5
- **Routing**: React Router v6
- **HTTP**: Axios with interceptors
- **Forms**: React Hook Form
- **Charts**: Recharts
- **Icons**: Lucide React
- **Notifications**: React Hot Toast

### Deployment
- **Containerization**: Docker + Docker Compose
- **Server**: Uvicorn (backend) + Nginx (frontend)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- (Optional) Docker + Docker Compose

### Option A — Local Development

**1. Clone & setup backend**
```bash
cd finrelief-ai/backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (optional)
```

**2. Start backend**
```bash
uvicorn app.main:app --reload --port 8000
```
Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

**3. Setup frontend**
```bash
cd finrelief-ai/frontend
npm install
cp .env.example .env
```

**4. Start frontend**
```bash
npm run dev
```
Frontend runs at: http://localhost:5173

---

### Option B — Docker Compose (Recommended)

```bash
cd finrelief-ai
cp .env.example .env
# Edit .env with your SECRET_KEY and GEMINI_API_KEY

docker-compose up --build
```

- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ | — | JWT signing key (min 32 chars) |
| `ALGORITHM` | ❌ | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `60` | Token lifetime |
| `DATABASE_URL` | ❌ | `sqlite:///./finrelief.db` | Database connection |
| `GEMINI_API_KEY` | ❌ | `""` | Google Gemini API key |
| `DEBUG` | ❌ | `false` | Debug mode |
| `CORS_ORIGINS` | ❌ | See example | Allowed CORS origins |

> **Getting a Gemini API Key**: Visit [aistudio.google.com](https://aistudio.google.com), click "Get API Key" → "Create API key". Free tier: 1,500 requests/day. If omitted, the fallback rule-based engine activates automatically.

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | ❌ | `http://localhost:8000` | Backend API URL |

---

## 📁 Project Structure

```
finrelief-ai/
├── backend/
│   ├── app/
│   │   ├── api/              # Route handlers (auth, loans, analysis, etc.)
│   │   ├── core/             # Config, security, dependencies
│   │   ├── db/               # Database setup
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic layer
│   │   │   ├── financial_engine.py    # DTI, health score, metrics
│   │   │   ├── settlement_engine.py   # Settlement calculation
│   │   │   ├── gemini_service.py      # Gemini AI integration
│   │   │   ├── fallback_service.py    # Rule-based fallback
│   │   │   └── letter_service.py      # Letter generation
│   │   └── main.py           # FastAPI app entry point
│   ├── tests/                # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── api/              # Axios API client
│   │   ├── components/
│   │   │   ├── layout/       # Sidebar, Navbar, AppLayout
│   │   │   └── ui/           # Reusable UI components
│   │   ├── context/          # Auth context
│   │   ├── pages/            # All pages (Dashboard, Loans, etc.)
│   │   └── styles/           # CSS variables + global styles
│   ├── index.html
│   ├── vite.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🧮 Financial Engine Logic

### Health Score (0–100)
```
Start: 100 points
- DTI > 50%:           -25 pts
- DTI > 40%:           -15 pts
- DTI > 30%:           -10 pts
- Credit < 500:        -25 pts
- Credit < 600:        -15 pts
- Credit < 700:         -5 pts
- Each overdue loan:   -10 pts
- Each defaulted loan: -20 pts
- Negative surplus:    -15 pts
- Unemployed:          -10 pts
```

### Settlement Percentage (25%–85%)
```
Base: 40%
+ overdue_months × 2% (max +20%)
+ loan type bonus (credit_card: +15%, personal: +10%)
+ 15% if defaulted, +8% if overdue
+ 10% if credit < 600, +5% if < 700
- 5% if credit > 750
- 5% if salaried employment
```

---

## 🔌 API Reference

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login, returns JWT |
| `GET` | `/api/auth/me` | Get current user |

### Loans
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/loans` | List all loans |
| `POST` | `/api/loans` | Add new loan |
| `GET` | `/api/loans/{id}` | Get loan details |
| `PUT` | `/api/loans/{id}` | Update loan |
| `DELETE` | `/api/loans/{id}` | Delete loan |

### Analysis & Settlement
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analysis/financial-health` | Full financial metrics |
| `GET` | `/api/analysis/debt-summary` | Debt breakdown |
| `POST` | `/api/settlement/calculate` | Run settlement engine |
| `POST` | `/api/settlement/ai-advice` | Get Gemini AI advice |

### Letters
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/letters/generate` | Generate negotiation letter |
| `GET` | `/api/letters` | List past letters |

Full interactive docs: http://localhost:8000/docs (Swagger UI)

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## 🔒 Security

- Passwords hashed with **bcrypt** (12 rounds)
- JWT tokens signed with **HS256** algorithm
- All endpoints require authentication except `/auth/register` and `/auth/login`
- SQLAlchemy ORM prevents SQL injection
- Input validated by **Pydantic** schemas
- Environment variables for all secrets
- CORS restricted to configured origins

---

## 🚢 Production Deployment

1. Set `SECRET_KEY` to a cryptographically random 32+ char string
2. Set `GEMINI_API_KEY` to your real key
3. Switch `DATABASE_URL` to PostgreSQL for production
4. Set `DEBUG=false`
5. Use a reverse proxy (Nginx/Traefik) in front of both services
6. Enable HTTPS via Let's Encrypt

---

## 📜 License

MIT License — Free for personal and commercial use.

---

*Built with ❤️ as an enterprise-grade fintech SaaS portfolio project.*
