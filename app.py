# app.py

# Define a class for an expense with amount, category, date, description, and tags.
# It should also have an auto-incrementing id.

from datetime import datetime
from typing import List, Optional
import csv
import json

# Optional imports for charting
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("⚠️ Charts unavailable: pandas/matplotlib not installed")

class Expense:
    """Class to represent an expense with auto-incrementing ID."""
    
    _next_id = 1  # Class variable for auto-incrementing ID
    
    def __init__(self, amount: float, category: str, date: datetime, description: str, tags: List[str] = None):
        """
        Initialize an expense with the given details.
        
        Args:
            amount: The expense amount
            category: The expense category (e.g., 'Food', 'Transport', 'Entertainment')
            date: The date of the expense
            description: A description of the expense
            tags: Optional list of tags for the expense
        """
        self.id = Expense._next_id
        Expense._next_id += 1
        
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description
        self.tags = tags or []
    
    def __str__(self):
        """String representation of the expense."""
        return f"Expense(id={self.id}, amount=${self.amount:.2f}, category='{self.category}', date={self.date.strftime('%Y-%m-%d')}, description='{self.description}', tags={self.tags})"
    
    def __repr__(self):
        """Detailed representation of the expense."""
        return self.__str__()
    
    def to_dict(self):
        """Convert expense to dictionary for easy serialization."""
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.isoformat(),
            'description': self.description,
            'tags': self.tags
        }

# Define the data file names
DATA_FILE = "expenses.csv"
BUDGETS_FILE = "budgets.json"

# Global expenses list
expenses = []

def set_expenses(expense_list: List[Expense]):
    """Set the global expenses list."""
    global expenses
    expenses = expense_list

# Budget management functions
def load_budgets() -> dict:
    """Load budgets from JSON file."""
    try:
        with open(BUDGETS_FILE, 'r', encoding='utf-8') as file:
            budgets = json.load(file)
        print(f"✅ Loaded budgets from {BUDGETS_FILE}")
        return budgets
    except FileNotFoundError:
        # Default budgets if file doesn't exist
        default_budgets = {
            "Food": 100.00,
            "Transport": 200.00,
            "Entertainment": 150.00,
            "Utilities": 300.00,
            "Shopping": 200.00,
            "Other": 250.00
        }
        print(f"📁 {BUDGETS_FILE} not found, using default budgets")
        return default_budgets
    except Exception as e:
        print(f"❌ Error loading budgets: {e}")
        return {}

def save_budgets(budgets: dict):
    """Save budgets to JSON file."""
    try:
        with open(BUDGETS_FILE, 'w', encoding='utf-8') as file:
            json.dump(budgets, file, indent=2)
        print(f"✅ Saved budgets to {BUDGETS_FILE}")
    except Exception as e:
        print(f"❌ Error saving budgets: {e}")

# Add functions to save the expenses list to a CSV file and load them on startup.
# The load function must handle recreating Expense objects from the saved dictionary data.
def save_expenses(expense_list: List[Expense]):
    """Save expenses to a CSV file."""
    try:
        # Define the order of the columns
        fieldnames = ['id', 'amount', 'category', 'date', 'description', 'tags']
        
        # Convert Expense objects to dictionaries
        expense_dicts = [expense.to_dict() for expense in expense_list]
        
        # NOTE: CSV doesn't handle Python lists well, so we convert the 'tags' list to a string
        for d in expense_dicts:
            d['tags'] = "|".join(d['tags']) # Join tags with a pipe separator

        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(expense_dicts)
            
        print(f"✅ Saved {len(expense_list)} expenses to {DATA_FILE}")
    except Exception as e:
        print(f"❌ Error saving expenses: {e}")

def load_expenses() -> List[Expense]:
    """Load expenses from CSV file and recreate Expense objects."""
    try:
        with open(DATA_FILE, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            expense_dicts = list(reader)
        
        loaded_expenses = []
        max_id = 0
        
        for expense_dict in expense_dicts:
            # Recreate datetime object and convert amount/id back to numbers
            amount = float(expense_dict['amount'])
            expense_id = int(expense_dict['id'])
            date_obj = datetime.fromisoformat(expense_dict['date'])
            # Convert the pipe-separated string back to a list of tags
            tags_list = expense_dict['tags'].split('|') if expense_dict['tags'] else []

            # Create expense object (using helper to bypass auto-incrementing id)
            temp_expense = Expense(amount, expense_dict['category'], date_obj, expense_dict['description'], tags_list)
            
            # Manually set the ID and update max_id
            temp_expense.id = expense_id
            max_id = max(max_id, expense_id)
            
            loaded_expenses.append(temp_expense)
        
        # Reset the global next ID to continue properly
        if max_id > 0:
            Expense._next_id = max_id + 1
        
        print(f"✅ Loaded {len(loaded_expenses)} expenses from {DATA_FILE}")
        return loaded_expenses
        
    except FileNotFoundError:
        print(f"📁 {DATA_FILE} not found, starting with empty expenses list")
        return []
    except Exception as e:
        print(f"❌ Error loading expenses: {e}")
        return []

# CRUD - Create: Function to add a new expense.
def create_expense(amount: float, category: str, date_str: str, description: str, tags: Optional[List[str]] = None) -> Optional[Expense]:
    """Creates a new Expense object and adds it to the global list."""
    global expenses
    
    # NOTE: date_str needs to be converted to a datetime object
    try:
        date_obj = datetime.fromisoformat(date_str)
    except ValueError:
        print(f"❌ Invalid date format: {date_str}. Use YYYY-MM-DD format.")
        return None
    
    new_expense = Expense(amount, category, date_obj, description, tags)
    expenses.append(new_expense)
    print(f"✅ Created expense with ID {new_expense.id}.")
    return new_expense

# CRUD - Read: Function to find an expense by ID or list all expenses.
def get_expense(expense_id: int) -> Optional[Expense]:
    """Retrieves a single expense by its ID."""
    global expenses
    for expense in expenses:
        if expense.id == expense_id:
            return expense
    return None

# CRUD - Update: Function to modify an existing expense by ID.
def update_expense(expense_id: int, amount: Optional[float] = None, category: Optional[str] = None, 
                   date_str: Optional[str] = None, description: Optional[str] = None, 
                   tags: Optional[List[str]] = None) -> bool:
    """Updates the fields of an existing expense."""
    expense = get_expense(expense_id)
    if expense:
        if amount is not None:
            expense.amount = amount
        if category is not None:
            expense.category = category
        if date_str is not None:
            try:
                expense.date = datetime.fromisoformat(date_str)
            except ValueError:
                print(f"❌ Invalid date format for update: {date_str}.")
                return False
        if description is not None:
            expense.description = description
        if tags is not None:
            expense.tags = tags
        print(f"✅ Updated expense with ID {expense_id}.")
        return True
    print(f"❌ Failed to find expense ID {expense_id} for update.")
    return False

# CRUD - Delete: Function to remove an expense by ID.
def delete_expense(expense_id: int) -> bool:
    """Deletes an expense from the global list by its ID."""
    global expenses
    initial_length = len(expenses)
    
    # Use list comprehension to filter out the expense with the matching ID
    expenses[:] = [e for e in expenses if e.id != expense_id]
    
    # Check if the length changed to confirm deletion
    if len(expenses) < initial_length:
        print(f"✅ Expense ID {expense_id} successfully deleted.")
        return True
    
    print(f"❌ Failed to find or delete expense ID {expense_id}.")
    return False

# CRUD - Filter: Function to filter expenses by category and/or tag.
def filter_expenses(category: Optional[str] = None, tag: Optional[str] = None) -> List[Expense]:
    """Filters expenses based on category and/or tag (case-insensitive)."""
    global expenses
    
    # Start with the full list
    filtered_list = expenses
    
    # Filter by Category
    if category and category.strip():
        # Filter for expenses where the category matches the search term
        filtered_list = [e for e in filtered_list if e.category.lower() == category.strip().lower()]
    
    # Filter by Tag
    if tag and tag.strip():
        # Filter for expenses where the tag is present in the expense's tags list
        search_tag = tag.strip().lower()
        filtered_list = [e for e in filtered_list if search_tag in [t.lower() for t in e.tags]]
        
    return filtered_list

# Charts: Function to display spending charts by category.
def display_charts():
    """Aggregates expenses by category and displays a bar chart."""
    global expenses

    if not CHARTS_AVAILABLE:
        print("❌ Charts not available. Please install: pip install pandas matplotlib")
        return

    if not expenses:
        print("📊 No expenses to chart. Add some data first!")
        return

    # 1. Convert data model to a Pandas DataFrame
    # Uses the Expense.to_dict() method you already created
    df = pd.DataFrame([e.to_dict() for e in expenses])

    # 2. Aggregate the data: Group by 'category' and sum the 'amount'
    category_summary = df.groupby('category')['amount'].sum().sort_values(ascending=False)
    
    # 3. Plot the chart
    plt.figure(figsize=(10, 6))
    category_summary.plot(kind='bar', color='darkblue')
    
    plt.title('Total Spending by Category')
    plt.xlabel('Category')
    plt.ylabel('Total Amount ($)')
    plt.xticks(rotation=45, ha='right') # Rotate labels for readability
    plt.tight_layout()
    plt.show() # This command opens the chart window
    print("✅ Spending chart displayed.")

# Budget: Function to check spending against budgets
def check_budgets() -> dict:
    """Calculates spending vs. fixed budgets for key categories."""
    global expenses

    if not expenses:
        return {"budgets": {}, "over_budget_count": 0, "total_budgets": 0}
    
    # Load budgets from file
    BUDGETS = load_budgets()
    
    if not BUDGETS:
        return {"budgets": {}, "over_budget_count": 0, "total_budgets": 0}
    
    # 1. Manual/Fallback Calculation (when pandas is NOT available)
    if not CHARTS_AVAILABLE:
        print("📊 Charts unavailable: using manual calculation path.")
        
        # Manually calculate spending by category
        spending_summary = {}
        for expense in expenses:
            if expense.category in spending_summary:
                spending_summary[expense.category] += expense.amount
            else:
                spending_summary[expense.category] = expense.amount
                
        results = {}
        over_budget_count = 0
        
        for category, budget in BUDGETS.items():
            spent = spending_summary.get(category, 0.00)
            remaining = budget - spent
            
            results[category] = {
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "status": "Over Budget" if remaining < 0 else "Good"
            }
            if remaining < 0:
                over_budget_count += 1
                
        # EXPLICIT RETURN - stops here when pandas unavailable
        return {
            "budgets": results,
            "over_budget_count": over_budget_count,
            "total_budgets": len(BUDGETS)
        }
        
    # 2. Pandas Calculation (Only runs if CHARTS_AVAILABLE is True)
    else:
        print("📊 Charts available: using Pandas calculation path.")
        df = pd.DataFrame([e.to_dict() for e in expenses])
        
        # Calculate actual spending by category using Pandas
        spending_summary = df.groupby('category')['amount'].sum()
        
        results = {}
        over_budget_count = 0
        
        for category, budget in BUDGETS.items():
            spent = spending_summary.get(category, 0.00)
            remaining = budget - spent
            
            results[category] = {
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "status": "Over Budget" if remaining < 0 else "Good"
            }
            if remaining < 0:
                over_budget_count += 1
                
        # EXPLICIT RETURN for pandas path
        return {
            "budgets": results,
            "over_budget_count": over_budget_count,
            "total_budgets": len(BUDGETS)
        }

# CRUD - Read: Function to list all expenses.
def list_expenses() -> List[Expense]:
    """Returns the list of all expenses."""
    global expenses
    return expenses

# In-memory data storage
expenses: List[Expense] = []

# Sample data for testing
def initialize_sample_data():
    """Initialize some sample expenses for testing."""
    sample_expenses = [
        Expense(12.50, "Food", datetime(2025, 10, 20), "Lunch at cafe", ["lunch", "work"]),
        Expense(45.00, "Transport", datetime(2025, 10, 21), "Gas for car", ["car", "fuel"]),
        Expense(25.99, "Entertainment", datetime(2025, 10, 22), "Movie tickets", ["movies", "weekend"]),
        Expense(8.75, "Food", datetime(2025, 10, 23), "Coffee and pastry", ["coffee", "morning"]),
        Expense(120.00, "Utilities", datetime(2025, 10, 24), "Electric bill", ["bills", "monthly"])
    ]
    
    expenses.extend(sample_expenses)
    print(f"Initialized {len(sample_expenses)} sample expenses")

def run_cli():
    """Main CLI function to run the interactive expense tracker."""
    global expenses
    
    # 1. Load data at startup
    expenses = load_expenses()
    if not expenses:
        print("\nWelcome! No existing data found. Initializing...")
        initialize_sample_data()
    
    print("\n--- Expense Tracker CLI ---")
    
    while True:
        print("\nOptions:")
        print("  1: Add New Expense")
        print("  2: View All Expenses")
        print("  3: Filter Expenses")
        print("  4: View Spending Charts")
        print("  5: Delete Expense by ID")
        print("  6: Save & Exit")
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            # Collect user input for a new expense
            try:
                amount = float(input("Amount: $"))
                category = input("Category: ")
                date_str = input("Date (YYYY-MM-DD): ")
                description = input("Description: ")
                tags_str = input("Tags (comma-separated, e.g., work,travel): ")
                tags = [t.strip() for t in tags_str.split(',') if t.strip()]

                create_expense(amount, category, date_str, description, tags)
                
            except ValueError:
                print("❌ Invalid input. Amount must be a number.")
            
        elif choice == '2':
            # List all expenses
            print("\n--- All Expenses ---")
            if not expenses:
                print("No expenses recorded yet.")
            for e in list_expenses():
                print(e)
                
        elif choice == '3':
            # Filter expenses
            print("\n--- Filter Expenses ---")
            category_filter = input("Filter by category (leave blank to skip): ").strip()
            tag_filter = input("Filter by tag (leave blank to skip): ").strip()
            
            # Apply filters
            if not category_filter and not tag_filter:
                print("❌ No filters provided. Showing all expenses instead.")
                filtered_expenses = list_expenses()
            else:
                filtered_expenses = filter_expenses(
                    category=category_filter if category_filter else None,
                    tag=tag_filter if tag_filter else None
                )
            
            # Display filtered results
            if filtered_expenses:
                print(f"\n--- Found {len(filtered_expenses)} matching expenses ---")
                for e in filtered_expenses:
                    print(e)
            else:
                print("❌ No expenses match your filter criteria.")
                
        elif choice == '4':
            # Display spending charts
            print("\n--- Spending Charts ---")
            display_charts()
                
        elif choice == '5':
            # Delete an expense
            try:
                expense_id = int(input("Enter ID of expense to delete: "))
                delete_expense(expense_id)
            except ValueError:
                print("❌ Invalid input. ID must be a number.")
            
        elif choice == '6':
            # Save data and exit
            save_expenses(expenses)
            print("\n👋 Application closed. Data saved.")
            break
            
        else:
            print("🛑 Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    # Ensure all components are ready (you may need to define initialize_sample_data() here if you removed it)
    run_cli()
