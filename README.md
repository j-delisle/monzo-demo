# Monzo Demo MVP

A full-stack banking demo application inspired by Monzo's features, showcasing microservice architecture with automatic transaction categorization and TopUp functionality.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │ Go Categorizer  │
│   (TypeScript)   │◄───┤    (Python)     │◄───┤  Microservice   │
│                 │    │                  │    │                 │
│ • Accounts      │    │ • User Accounts  │    │ • ML-style      │
│ • Transactions  │    │ • Transactions   │    │   categorization│
│ • TopUp Rules   │    │ • Auto TopUp     │    │ • HTTP API      │
│ • Dashboard     │    │ • API Gateway    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Features

### ✅ Implemented
- **Account Management**: View multiple accounts with live balances
- **Transaction Processing**: Create transactions with automatic categorization
- **Auto TopUp Logic**: Set rules to automatically top up accounts when balance falls below threshold
- **Transaction Categorization**: AI-style categorization using Go microservice
- **Real-time Dashboard**: React dashboard with live updates
- **Microservice Architecture**: Demonstrates service separation and communication

### 📊 Transaction Categories
- Transport (Uber, TfL, Taxi)
- Food & Drink (Starbucks, Restaurants)
- Shopping (Amazon, Retail)
- Groceries (Tesco, Sainsbury's)
- Entertainment (Netflix, Cinema)
- Bills & Utilities (Gas, Electric, Internet)
- ATM/Cash Withdrawals
- Income & Housing

## 🛠️ Tech Stack

- **Frontend**: React 18, TypeScript, Vite, TailwindCSS, shadcn/ui
- **Backend**: FastAPI (Python), Pydantic, HTTP Client
- **Microservice**: Go, Gin Framework, REST API
- **Infrastructure**: Docker, Docker Compose
- **Development**: Hot reload, TypeScript, ESLint

## 📦 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local development)
- Go 1.21+ (for local development)
- Python 3.11+ (for local development)

### 🐳 Docker Setup (Recommended)

1. **Clone and Start**
```bash
git clone <your-repo>
cd monzo-demo
docker-compose up --build
```

2. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Go Categorizer: http://localhost:9000
- API Docs: http://localhost:8000/docs

### 💻 Local Development

#### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Categorizer (Go)
```bash
cd categorizer
go mod download
go run main.go
```

#### Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Demo Usage

### 1. **View Accounts**
- Two pre-loaded demo accounts (Current & Savings)
- Real-time balance display
- Click to select an account

### 2. **Create Transactions**
- Choose account, merchant, amount
- Automatic categorization via Go service
- Watch balance update in real-time

### 3. **Set TopUp Rules**
- Define threshold (e.g., £50)
- Set TopUp amount (e.g., £100)
- Automatic triggering when balance drops

### 4. **Test Auto TopUp**
1. Create a large debit transaction
2. Watch balance drop below threshold
3. See automatic TopUp trigger
4. View TopUp history

## 🔧 API Endpoints

### Accounts
- `GET /accounts` - List all accounts
- `GET /accounts/{id}` - Get specific account

### Transactions
- `GET /transactions` - List transactions (optionally filtered by account)
- `POST /transactions` - Create new transaction

### TopUp Management
- `GET /topup-rules` - List TopUp rules
- `POST /topup-rules` - Create TopUp rule
- `GET /topup-events` - View TopUp history
- `POST /trigger-topup` - Manually trigger TopUp

### Categorization Service (Go)
- `POST /categorize` - Categorize transaction
- `GET /health` - Health check

## 🧪 Testing Scenarios

### Scenario 1: Shopping Transaction
```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "acc_1",
    "amount": 25.50,
    "merchant": "Amazon",
    "description": "Books and electronics",
    "transaction_type": "debit"
  }'
```
Expected: Categorized as "Shopping"

### Scenario 2: Transport
```bash
curl -X POST http://localhost:8000/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "acc_1", 
    "amount": 12.40,
    "merchant": "Uber",
    "description": "Ride to airport",
    "transaction_type": "debit"
  }'
```
Expected: Categorized as "Transport"

### Scenario 3: Auto TopUp
1. Create TopUp rule with £100 threshold, £200 topup
2. Create £60 transaction (balance goes to £90.50)
3. Watch automatic TopUp trigger
4. Balance becomes £290.50

## 🏃‍♂️ Development Commands

```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f backend
docker-compose logs -f categorizer
docker-compose logs -f frontend

# Restart specific service  
docker-compose restart backend

# Clean rebuild
docker-compose down
docker-compose up --build
```

## 📁 Project Structure

```
monzo-demo/
├── backend/              # FastAPI Python service
│   ├── main.py          # API routes and logic
│   ├── models.py        # Pydantic data models
│   ├── database.py      # In-memory database
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Backend container
├── categorizer/         # Go microservice
│   ├── main.go         # Categorization logic
│   ├── go.mod          # Go dependencies
│   └── Dockerfile      # Go container
├── frontend/           # React TypeScript app
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── services/   # API clients
│   │   └── types/      # TypeScript types
│   ├── package.json   # Node dependencies
│   └── Dockerfile     # Frontend container
├── docker-compose.yml # Service orchestration
└── README.md         # This file
```

## 🎨 UI Features

- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live balance and transaction updates
- **Modern UI**: Built with shadcn/ui and TailwindCSS
- **Interactive Dashboard**: Click accounts, create transactions, manage rules
- **Visual Categorization**: Color-coded transaction categories
- **TopUp History**: Track all automatic topups

## 🚀 Deployment

The application is containerized and ready for deployment to:
- **Local**: Docker Compose
- **Cloud**: Any container platform (AWS ECS, Google Cloud Run, etc.)
- **Kubernetes**: Can be adapted for k8s deployment

## 🤝 Contributing

This is a demo project for Monzo job application. Features to potentially add:

1. **Authentication**: User login/signup
2. **Real Database**: PostgreSQL integration  
3. **Advanced ML**: Improve categorization accuracy
4. **Spending Analytics**: Charts and insights
5. **Mobile App**: React Native version
6. **Real-time Notifications**: WebSocket updates

## 📄 License

This project is for demonstration purposes only.

---

Built with ❤️ for Monzo • Demonstrates microservice architecture, real-time updates, and modern full-stack development