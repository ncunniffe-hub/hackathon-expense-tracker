# api.py - FastAPI REST API for Expense Tracker

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import csv

# Import the Expense class from app.py
import app
from app import (
    Expense, 
    load_expenses, 
    save_expenses,
    set_expenses,
    create_expense, 
    get_expense, 
    update_expense, 
    delete_expense, 
    filter_expenses,
    list_expenses,
    check_budgets,
    load_budgets,
    save_budgets
)

# Initialize FastAPI app
app = FastAPI(
    title="Expense Tracker API",
    description="REST API for managing personal expenses",
    version="1.0.0"
)

# Pydantic models for request/response validation
class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: str  # Format: YYYY-MM-DD
    description: str
    tags: Optional[List[str]] = []

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    date: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    date: str
    description: str
    tags: List[str]

# Global expenses list
expenses = []

# Load expenses on startup
@app.on_event("startup")
async def startup_event():
    """Load expenses from CSV file when API starts."""
    loaded = load_expenses()
    set_expenses(loaded)  # Set the global expenses variable in app.py
    if not loaded:
        print("No existing expenses found. Starting with empty list.")
    else:
        print(f"✅ Loaded {len(loaded)} expenses and set global variable")

# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint."""
    return {
        "message": "Welcome to Expense Tracker API",
        "version": "1.0.0",
        "dashboard": "Visit /dashboard for the web interface",
        "endpoints": {
            "GET /expenses": "List all expenses",
            "GET /expenses/{id}": "Get expense by ID",
            "POST /expenses": "Create new expense",
            "PUT /expenses/{id}": "Update expense",
            "DELETE /expenses/{id}": "Delete expense",
            "GET /expenses/filter/search": "Filter expenses by category or tag",
            "GET /expenses/summary/category": "Get spending summary by category",
            "GET /budgets/status": "Get budget status and over-budget alerts",
            "GET /dashboard/data": "Get comprehensive dashboard data"
        }
    }

# Dashboard HTML page
@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the HTML dashboard."""
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# GET all expenses
@app.get("/expenses", response_model=List[ExpenseResponse])
async def get_all_expenses():
    """Retrieve all expenses."""
    return [
        ExpenseResponse(
            id=e.id,
            amount=e.amount,
            category=e.category,
            date=e.date.strftime('%Y-%m-%d'),
            description=e.description,
            tags=e.tags
        )
        for e in list_expenses()
    ]

# GET expense by ID
@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense_by_id(expense_id: int):
    """Retrieve a specific expense by ID."""
    expense = get_expense(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail=f"Expense with ID {expense_id} not found")
    
    return ExpenseResponse(
        id=expense.id,
        amount=expense.amount,
        category=expense.category,
        date=expense.date.strftime('%Y-%m-%d'),
        description=expense.description,
        tags=expense.tags
    )

# POST create new expense
@app.post("/expenses", response_model=ExpenseResponse, status_code=201)
async def create_new_expense(expense_data: ExpenseCreate):
    """Create a new expense."""
    new_expense = create_expense(
        amount=expense_data.amount,
        category=expense_data.category,
        date_str=expense_data.date,
        description=expense_data.description,
        tags=expense_data.tags
    )
    
    if not new_expense:
        raise HTTPException(status_code=400, detail="Failed to create expense. Check date format (YYYY-MM-DD).")
    
    # Auto-save after creating
    save_expenses(list_expenses())
    
    return ExpenseResponse(
        id=new_expense.id,
        amount=new_expense.amount,
        category=new_expense.category,
        date=new_expense.date.strftime('%Y-%m-%d'),
        description=new_expense.description,
        tags=new_expense.tags
    )

# PUT update expense
@app.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_existing_expense(expense_id: int, expense_data: ExpenseUpdate):
    """Update an existing expense."""
    success = update_expense(
        expense_id=expense_id,
        amount=expense_data.amount,
        category=expense_data.category,
        date_str=expense_data.date,
        description=expense_data.description,
        tags=expense_data.tags
    )
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Expense with ID {expense_id} not found or update failed")
    
    # Auto-save after updating
    save_expenses(list_expenses())
    
    # Return updated expense
    updated_expense = get_expense(expense_id)
    return ExpenseResponse(
        id=updated_expense.id,
        amount=updated_expense.amount,
        category=updated_expense.category,
        date=updated_expense.date.strftime('%Y-%m-%d'),
        description=updated_expense.description,
        tags=updated_expense.tags
    )

# DELETE expense
@app.delete("/expenses/{expense_id}")
async def delete_existing_expense(expense_id: int):
    """Delete an expense by ID."""
    success = delete_expense(expense_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Expense with ID {expense_id} not found")
    
    # Auto-save after deleting
    save_expenses(list_expenses())
    
    return {"message": f"Expense {expense_id} deleted successfully"}

# GET filtered expenses
@app.get("/expenses/filter/search", response_model=List[ExpenseResponse])
async def filter_expenses_endpoint(category: Optional[str] = None, tag: Optional[str] = None):
    """Filter expenses by category and/or tag."""
    filtered = filter_expenses(category=category, tag=tag)
    
    return [
        ExpenseResponse(
            id=e.id,
            amount=e.amount,
            category=e.category,
            date=e.date.strftime('%Y-%m-%d'),
            description=e.description,
            tags=e.tags
        )
        for e in filtered
    ]

# GET spending summary
@app.get("/expenses/summary/category")
async def get_spending_summary():
    """Get total spending by category."""
    import pandas as pd
    
    if not expenses:
        return {"summary": {}, "total": 0.0}
    
    df = pd.DataFrame([e.to_dict() for e in expenses])
    category_summary = df.groupby('category')['amount'].sum().to_dict()
    total = df['amount'].sum()
    
    return {
        "summary": category_summary,
        "total": float(total),
        "expense_count": len(expenses)
    }

# GET budget status
@app.get("/budgets/status")
async def get_budget_status():
    """Get budget status showing spending vs budgets for key categories."""
    budget_data = check_budgets()
    return budget_data

# GET all budgets
@app.get("/budgets")
async def get_budgets():
    """Get all budget categories and amounts."""
    budgets = load_budgets()
    return {"budgets": budgets}

# POST/PUT to set budgets
@app.post("/budgets/set")
@app.put("/budgets/set")
async def set_budgets(budgets: dict):
    """Set budget amounts for categories. Example: {"Food": 150.00, "Transport": 300.00}"""
    save_budgets(budgets)
    return {"message": "Budgets updated successfully", "budgets": budgets}

# GET dashboard data (combined summary)
@app.get("/dashboard/data")
async def get_dashboard_data():
    """Get comprehensive dashboard data including spending summary and budget status."""
    # Get spending summary
    summary_data = {}
    total_spent = 0.0
    
    expenses = list_expenses()  # Get expenses from app.py
    
    if expenses:
        try:
            import pandas as pd
            df = pd.DataFrame([e.to_dict() for e in expenses])
            category_summary = df.groupby('category')['amount'].sum().to_dict()
            total_spent = df['amount'].sum()
            summary_data = category_summary
        except ImportError:
            # Manual calculation if pandas not available
            for e in expenses:
                if e.category in summary_data:
                    summary_data[e.category] += e.amount
                else:
                    summary_data[e.category] = e.amount
            total_spent = sum(e.amount for e in expenses)
    
    # Get budget status
    budget_data = check_budgets()
    
    return {
        "total_spent": float(total_spent),
        "expense_count": len(expenses),
        "spending_by_category": summary_data,
        "budget_status": budget_data
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
