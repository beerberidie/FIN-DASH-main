"""Account API endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException

from models.account import Account, AccountCreate, AccountUpdate, ACCOUNT_FIELDNAMES
from services.csv_manager import csv_manager
from services.calculator import calculator
from utils.ids import generate_account_id
from utils.dates import now_iso

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=List[Account])
def list_accounts():
    """List all accounts."""
    accounts = csv_manager.read_csv("accounts.csv")
    return [Account.from_csv(acc) for acc in accounts]


@router.get("/{account_id}", response_model=Account)
def get_account(account_id: str):
    """Get a single account by ID."""
    accounts = csv_manager.read_csv("accounts.csv")
    
    for acc_data in accounts:
        if acc_data.get('id') == account_id:
            return Account.from_csv(acc_data)
    
    raise HTTPException(status_code=404, detail="Account not found")


@router.get("/{account_id}/balance")
def get_account_balance(account_id: str):
    """Get current balance for an account."""
    accounts = csv_manager.read_csv("accounts.csv")
    transactions = csv_manager.read_csv("transactions.csv")
    
    # Find account
    account = None
    for acc_data in accounts:
        if acc_data.get('id') == account_id:
            account = acc_data
            break
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Calculate balance
    opening_balance = float(account.get('opening_balance', 0))
    current_balance = calculator.calculate_account_balance(
        account_id,
        transactions,
        opening_balance
    )
    
    return {
        "account_id": account_id,
        "account_name": account.get('name'),
        "opening_balance": opening_balance,
        "current_balance": current_balance
    }


@router.post("", response_model=Account, status_code=201)
def create_account(account: AccountCreate):
    """Create a new account."""
    # Generate ID and timestamp
    acc_id = generate_account_id(account.name)
    timestamp = now_iso()
    
    # Check if account already exists
    accounts = csv_manager.read_csv("accounts.csv")
    for acc in accounts:
        if acc.get('id') == acc_id:
            raise HTTPException(status_code=400, detail="Account already exists")
    
    # Create account object
    acc_data = account.model_dump()
    acc_data['id'] = acc_id
    acc_data['created_at'] = timestamp
    
    # Convert to CSV format
    acc_obj = Account(**acc_data)
    
    # Append to CSV
    csv_manager.append_csv("accounts.csv", acc_obj.to_csv(), ACCOUNT_FIELDNAMES)
    
    return acc_obj


@router.put("/{account_id}", response_model=Account)
def update_account(account_id: str, account: AccountUpdate):
    """Update an existing account."""
    accounts = csv_manager.read_csv("accounts.csv")
    
    # Find account
    found = False
    for i, acc_data in enumerate(accounts):
        if acc_data.get('id') == account_id:
            # Update fields
            update_data = account.model_dump(exclude_unset=True)
            acc_data.update(update_data)
            
            accounts[i] = acc_data
            found = True
            break
    
    if not found:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Write back to CSV
    csv_manager.write_csv("accounts.csv", accounts, ACCOUNT_FIELDNAMES)
    
    return Account.from_csv(accounts[i])


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: str):
    """Delete an account."""
    success = csv_manager.delete_csv_row(
        "accounts.csv",
        account_id,
        ACCOUNT_FIELDNAMES
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return None

