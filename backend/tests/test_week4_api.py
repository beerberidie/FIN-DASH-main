"""Test script for Week 4 API endpoints (Budgets & Goals)."""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8777/api"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")

def test_budgets():
    """Test budget endpoints."""
    print("\n" + "="*60)
    print("TESTING BUDGET ENDPOINTS")
    print("="*60)
    
    # Test 1: Get current month's budget
    print("\n1. GET /api/budgets/current")
    response = requests.get(f"{BASE_URL}/budgets/current")
    print_response("Current Month Budget", response)
    
    # Test 2: List all budgets
    print("\n2. GET /api/budgets")
    response = requests.get(f"{BASE_URL}/budgets")
    print_response("All Budgets", response)
    
    # Test 3: Get specific budget
    if response.status_code == 200 and response.json():
        budget_id = response.json()[0]['id']
        print(f"\n3. GET /api/budgets/{budget_id}")
        response = requests.get(f"{BASE_URL}/budgets/{budget_id}")
        print_response(f"Budget {budget_id}", response)
        
        # Test 4: Get budget breakdown
        print(f"\n4. GET /api/budgets/{budget_id}/breakdown")
        response = requests.get(f"{BASE_URL}/budgets/{budget_id}/breakdown")
        print_response(f"Budget {budget_id} Breakdown", response)
    
    # Test 5: Create new budget (for next month)
    next_month = datetime.now() + timedelta(days=32)
    new_budget = {
        "year": next_month.year,
        "month": next_month.month,
        "needs_planned": 10000.00,
        "wants_planned": 6000.00,
        "savings_planned": 4000.00,
        "notes": "Test budget for next month"
    }
    print(f"\n5. POST /api/budgets")
    print(f"Payload: {json.dumps(new_budget, indent=2)}")
    response = requests.post(f"{BASE_URL}/budgets", json=new_budget)
    print_response("Create Budget", response)
    
    created_budget_id = None
    if response.status_code == 200:
        created_budget_id = response.json()['id']
        
        # Test 6: Update budget
        update_data = {
            "needs_planned": 11000.00,
            "notes": "Updated test budget"
        }
        print(f"\n6. PUT /api/budgets/{created_budget_id}")
        print(f"Payload: {json.dumps(update_data, indent=2)}")
        response = requests.put(f"{BASE_URL}/budgets/{created_budget_id}", json=update_data)
        print_response("Update Budget", response)
        
        # Test 7: Delete budget
        print(f"\n7. DELETE /api/budgets/{created_budget_id}")
        response = requests.delete(f"{BASE_URL}/budgets/{created_budget_id}")
        print_response("Delete Budget", response)

def test_goals():
    """Test goal endpoints."""
    print("\n" + "="*60)
    print("TESTING GOAL ENDPOINTS")
    print("="*60)
    
    # Test 1: List all goals
    print("\n1. GET /api/goals")
    response = requests.get(f"{BASE_URL}/goals")
    print_response("All Goals", response)
    
    # Test 2: List active goals only
    print("\n2. GET /api/goals?active_only=true")
    response = requests.get(f"{BASE_URL}/goals?active_only=true")
    print_response("Active Goals", response)
    
    # Test 3: Create new goal
    target_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    new_goal = {
        "name": "Test Vacation Fund",
        "target_amount": 15000.00,
        "current_amount": 0.00,
        "target_date": target_date,
        "icon": "Plane",
        "color": "blue"
    }
    print(f"\n3. POST /api/goals")
    print(f"Payload: {json.dumps(new_goal, indent=2)}")
    response = requests.post(f"{BASE_URL}/goals", json=new_goal)
    print_response("Create Goal", response)
    
    created_goal_id = None
    if response.status_code == 200:
        created_goal_id = response.json()['id']
        
        # Test 4: Get specific goal
        print(f"\n4. GET /api/goals/{created_goal_id}")
        response = requests.get(f"{BASE_URL}/goals/{created_goal_id}")
        print_response(f"Goal {created_goal_id}", response)
        
        # Test 5: Contribute to goal
        contribution = {
            "amount": 500.00
        }
        print(f"\n5. POST /api/goals/{created_goal_id}/contribute")
        print(f"Payload: {json.dumps(contribution, indent=2)}")
        response = requests.post(f"{BASE_URL}/goals/{created_goal_id}/contribute", json=contribution)
        print_response("Contribute to Goal", response)
        
        # Test 6: Contribute again
        contribution = {
            "amount": 1000.00
        }
        print(f"\n6. POST /api/goals/{created_goal_id}/contribute (again)")
        print(f"Payload: {json.dumps(contribution, indent=2)}")
        response = requests.post(f"{BASE_URL}/goals/{created_goal_id}/contribute", json=contribution)
        print_response("Contribute to Goal Again", response)
        
        # Test 7: Update goal
        update_data = {
            "name": "Updated Test Vacation Fund",
            "target_amount": 20000.00
        }
        print(f"\n7. PUT /api/goals/{created_goal_id}")
        print(f"Payload: {json.dumps(update_data, indent=2)}")
        response = requests.put(f"{BASE_URL}/goals/{created_goal_id}", json=update_data)
        print_response("Update Goal", response)
        
        # Test 8: Delete goal
        print(f"\n8. DELETE /api/goals/{created_goal_id}")
        response = requests.delete(f"{BASE_URL}/goals/{created_goal_id}")
        print_response("Delete Goal", response)

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("FIN-DASH WEEK 4 API TESTS")
    print("Testing Budget & Goal Management Endpoints")
    print("="*60)
    
    try:
        # Test budgets
        test_budgets()
        
        # Test goals
        test_goals()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
        print("\nCheck the output above for any errors.")
        print("All endpoints should return status 200.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend API")
        print("Make sure the backend is running on http://localhost:8777")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()

