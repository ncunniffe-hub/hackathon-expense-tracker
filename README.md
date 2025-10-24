# 💰 Expense Tracker

A full-featured expense tracking application built for a hackathon challenge, featuring CRUD operations, budget tracking, and a beautiful dark-mode dashboard.

## 🌐 Live Demo

**Public Live Demo:** https://kwgpxm88-8000.uks1.devtunnels.ms/dashboard

**GitHub Repository:** https://github.com/ncunniffe-hub/hackathon-expense-tracker

## ✨ Features

- ✅ **Full CRUD Operations** - Create, Read, Update, and Delete expenses
- 📊 **Budget Tracking** - Set budgets per category and monitor spending
- 💷 **GBP Currency Support** - Track expenses in British Pounds
- 🎨 **Dark Mode Dashboard** - Beautiful, modern UI with dark theme
- 📈 **Spending Analytics** - View spending by category with visual progress bars
- 🔄 **Real-time Updates** - Auto-refresh dashboard every 30 seconds
- 💾 **CSV Persistence** - All data stored in simple CSV format
- 🏷️ **Tags & Categories** - Organize expenses with custom tags and categories
- 📅 **Date Tracking** - Record when expenses occurred

## 🚀 Tech Stack

- **Backend:** Python 3.12, FastAPI 0.120.0
- **Server:** Uvicorn 0.38.0 (ASGI)
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Data Storage:** CSV files (expenses.csv, budgets.json)
- **API:** RESTful API with 10+ endpoints

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/ncunniffe-hub/hackathon-expense-tracker.git
cd hackathon-expense-tracker
```

2. Install dependencies:
```bash
pip install fastapi "uvicorn[standard]"
```

3. Run the server:
```bash
python -m uvicorn api:app --reload
```

4. Open your browser:
```
http://localhost:8000
```

## 🎯 API Endpoints

- `GET /` - Dashboard homepage
- `GET /expenses` - List all expenses
- `POST /expenses` - Create new expense
- `GET /expenses/{id}` - Get expense by ID
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense
- `GET /expenses/filter` - Filter expenses by category/tags
- `GET /budgets` - Get all budgets
- `POST /budgets/set` - Set category budgets
- `GET /budgets/status` - Get budget status
- `GET /dashboard/data` - Get dashboard analytics data

## 💡 Usage Examples

### Add an Expense via Dashboard
1. Navigate to http://localhost:8000
2. Fill in the "Add New Expense" form
3. Click "Log Expense"

### Set Budgets via API
```bash
curl -X POST "http://localhost:8000/budgets/set" \
  -H "Content-Type: application/json" \
  -d '{
    "Food": 500,
    "Transport": 100,
    "Entertainment": 100,
    "Utilities": 1000
  }'
```

### View All Expenses
```bash
curl http://localhost:8000/expenses
```

## 📊 Budget Categories

Default budget categories configured:
- **Food:** £500/month
- **Transport:** £100/month
- **Entertainment:** £100/month
- **Utilities:** £1000/month

## 🎨 Dashboard Features

- **Total Spent:** Real-time calculation of all expenses
- **Expense Count:** Number of logged expenses
- **Over Budget:** Count of categories exceeding budget
- **Budget Status:** Visual progress bars for each category
- **Spending by Category:** Breakdown of expenses by category

## 📁 Project Structure

```
expense-tracker/
├── app.py              # Core business logic & data models
├── api.py              # FastAPI REST API endpoints
├── expenses.csv        # Expense data storage
├── budgets.json        # Budget configuration
├── templates/
│   └── dashboard.html  # Dark mode dashboard UI
└── README.md           # This file
```

## 🏗️ Architecture

The application uses a simple but effective architecture:

1. **Data Layer:** CSV files for expense storage, JSON for budget configuration
2. **Business Logic:** Python classes and functions in `app.py`
3. **API Layer:** FastAPI endpoints in `api.py`
4. **Presentation:** Responsive HTML dashboard with vanilla JavaScript

## 🔧 Configuration

Budgets are stored in `budgets.json` and can be modified directly or via the `/budgets/set` API endpoint.

## 📝 Data Model

### Expense
```python
{
    "id": 1,
    "amount": 46.25,
    "category": "Food",
    "date": "2024-01-15",
    "description": "Weekly groceries",
    "tags": ["groceries", "weekly"]
}
```

## 🎯 Hackathon Challenge Requirements

✅ **CRUD Operations** - Full create, read, update, delete functionality
✅ **Charts/Analytics** - Dashboard with spending visualizations
✅ **Budget Tracking** - Monitor spending against set budgets
✅ **REST API** - Complete API for programmatic access
✅ **Modern UI** - Dark mode dashboard with responsive design

## 🚀 Future Enhancements

- [ ] Add pandas/matplotlib for advanced charts
- [ ] Implement MCP server for AI agent integration
- [ ] Add user authentication
- [ ] Multi-currency support
- [ ] Export to PDF reports
- [ ] Mobile app version

## 👨‍💻 Author

Built during a hackathon challenge by Niall Cunniffe

## 📄 License

MIT License - feel free to use this project for your own expense tracking!

## 🙏 Acknowledgments

Built with FastAPI, inspired by modern expense tracking needs and the requirement for a simple, effective solution.

---

⭐ **Star this repo if you find it useful!**
