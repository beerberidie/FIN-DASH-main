# FIN-DASH Phase 4 User Guide

## Overview

Phase 4 introduces three major enhancements to FIN-DASH:
1. **Card Management** - Track and manage your payment cards
2. **Bank Statement Import** - Import transactions from bank statements
3. **Real Account Data** - Pre-populated with realistic financial data

---

## 1. Card Management

### What is Card Management?

The Card Management feature allows you to track all your payment cards (credit cards, debit cards, prepaid cards, and virtual cards) in one place. Each card is linked to an account and provides detailed insights into spending, balances, and credit utilization.

### How to Access

Navigate to the **Cards** page from the main navigation menu.

### Creating a New Card

1. Click the **"Add Card"** button on the Cards page
2. Fill in the card details:
   - **Card Name** (required) - e.g., "FNB Gold Credit Card"
   - **Card Type** (required) - Credit, Debit, Prepaid, or Virtual
   - **Account** (required) - Select the linked bank account
   - **Card Number** (optional) - Last 4 digits for identification
   - **Credit Limit** (for credit cards) - Maximum credit available
   - **Expiry Date** (optional) - Month and year
   - **Color** (optional) - Visual identifier for the card
   - **Icon** (optional) - Icon to represent the card
   - **Active Status** - Toggle to mark card as active/inactive

3. Click **"Create Card"** to save

### Viewing Card Details

Each card displays:
- **Card name and type** with color-coded badge
- **Available balance** - Current available funds/credit
- **Current balance** - Total balance including pending transactions
- **Credit utilization** (for credit cards) - Percentage of credit limit used
- **Expiry date** - When the card expires
- **Active/Inactive status**

### Card Analytics

Click the **"Analytics"** button on any card to view:
- **Spending by Category** - Pie chart showing where you spend
- **Monthly Spending Trend** - Line chart showing spending over time
- **Top Categories** - List of categories with highest spending
- **Transaction Count** - Total number of transactions

### Editing a Card

1. Click the **"Edit"** button on the card
2. Update any field
3. Click **"Save Changes"**

### Deleting a Card

1. Click the **"Delete"** button on the card
2. Confirm the deletion
3. **Note:** This does not delete associated transactions

### Linking Transactions to Cards

When creating or editing a transaction, you can select a card from the dropdown. This allows you to:
- Track spending per card
- Monitor credit card balances
- Analyze card usage patterns

---

## 2. Bank Statement Import

### What is Bank Statement Import?

The Bank Statement Import feature allows you to automatically import transactions from your bank statements. It supports multiple file formats and intelligently detects duplicates and categorizes transactions.

### Supported File Formats

- **CSV** (.csv) - Comma-separated values
- **Excel** (.xls, .xlsx) - Microsoft Excel spreadsheets
- **PDF** (.pdf) - Bank statement PDFs
- **OFX/QFX** (.ofx, .qfx) - Open Financial Exchange format

### How to Import a Bank Statement

#### Step 1: Upload File

1. Navigate to the **Dashboard** or **Transactions** page
2. Click the **"Import Statement"** button
3. Select the **account** where transactions should be imported
4. **Drag and drop** your bank statement file, or click to browse
5. Toggle **"Auto-categorize transactions"** if you want automatic categorization
6. Click **"Upload & Parse"**

#### Step 2: Preview Transactions

After uploading, you'll see a preview showing:
- **Total Transactions** - Number of transactions found
- **New Transactions** - Transactions that don't exist yet (green badge)
- **Duplicates** - Transactions that already exist (orange badge)

For each transaction, you can see:
- Date
- Description
- Category (auto-assigned if enabled)
- Amount
- Status (New or Duplicate)

#### Step 3: Select Transactions

- By default, all **new transactions** are selected
- **Duplicates are not selected** (if "Skip duplicates" is enabled)
- You can manually select/deselect any transaction
- Use the checkbox at the top to select/deselect all

#### Step 4: Confirm Import

1. Review the selected transactions
2. Toggle **"Skip duplicates"** if you want to exclude duplicates
3. Click **"Import X Transaction(s)"**
4. Wait for the import to complete

#### Step 5: View Results

After import, you'll see:
- **Imported** - Number of transactions successfully imported
- **Skipped** - Number of duplicates skipped
- **Errors** - Number of transactions that failed

### File Format Requirements

#### CSV Files
Your CSV file should have columns for:
- **Date** - Transaction date (various formats supported)
- **Description** - Transaction description
- **Amount** - Transaction amount (positive for income, negative for expenses)
- **Balance** (optional) - Account balance after transaction

Example CSV:
```csv
Date,Description,Amount,Balance
2025-10-01,Salary Deposit,15000.00,25000.00
2025-10-02,Woolworths Grocery,-850.50,24149.50
2025-10-03,Uber Ride,-125.00,24024.50
```

#### Excel Files
Same structure as CSV, but in Excel format (.xls or .xlsx).

#### PDF Files
The parser will attempt to extract transaction data from PDF bank statements. Results may vary depending on the PDF format.

#### OFX/QFX Files
Standard OFX format exported from your bank's online banking system.

### Auto-Categorization

When enabled, the system will:
1. Look for similar transactions in your history
2. Use fuzzy matching to find the best category
3. Assign the category automatically
4. You can still change categories after import

### Duplicate Detection

The system detects duplicates by comparing:
- Transaction date (within 1 day)
- Description (85% similarity threshold)
- Amount (exact match)

Duplicates are flagged with an orange badge and can be skipped during import.

### Tips for Best Results

1. **Use consistent file formats** - Stick to one format for easier processing
2. **Review before importing** - Always check the preview before confirming
3. **Enable auto-categorization** - Saves time on manual categorization
4. **Skip duplicates** - Prevents duplicate transactions in your account
5. **Check import history** - Review past imports to track what was imported

### Troubleshooting

**Problem:** File upload fails
- **Solution:** Check file size (max 10MB) and format

**Problem:** No transactions detected
- **Solution:** Ensure CSV has proper headers or try a different format

**Problem:** Wrong categories assigned
- **Solution:** Disable auto-categorization and assign manually

**Problem:** Duplicates not detected
- **Solution:** Check if transaction dates/amounts match exactly

---

## 3. Real Account Data

### What is Real Account Data?

Phase 4 includes a data seeding feature that populates your FIN-DASH instance with realistic financial data for testing and demonstration purposes.

### Included Data

#### Accounts (5)
1. **FNB Cheque Account** - Primary checking account
2. **FNB Easy Account** - Secondary checking account
3. **FNB Credit Card** - Credit card account
4. **FNB eBucks Savings** - Savings account
5. **FNB Share Investor** - Investment account

#### Cards (1)
- **FNB Gold Credit Card** - Credit card with R30,000 limit

#### Categories (27)
Organized by type:
- **Income:** Salary, Freelance, Investment Income, etc.
- **Expenses:** Groceries, Rent, Utilities, Transport, etc.
- **Savings:** Emergency Fund, Retirement, etc.

#### Budget (October 2025)
Pre-configured budget with realistic allocations for all expense categories.

#### Transactions
Sample transactions for October 2025 demonstrating various spending patterns.

### How to Use Real Data

The data is automatically loaded when you first run FIN-DASH. You can:
- **View accounts** on the Dashboard
- **Explore transactions** on the Transactions page
- **Analyze spending** on the Analytics page
- **Track budgets** on the Budget page
- **Manage cards** on the Cards page

### Resetting Data

To reset to the original seeded data:
1. Stop the backend server
2. Run: `python backend/scripts/seed_real_data.py --verbose`
3. Restart the backend server

**Warning:** This will overwrite existing data!

---

## Getting Started

### Quick Start Guide

1. **Start the application**
   ```bash
   python start.py
   ```

2. **Access the dashboard**
   - Open your browser to `http://localhost:8081`

3. **Explore your accounts**
   - View the 5 pre-configured accounts
   - Check balances and recent transactions

4. **Manage your cards**
   - Navigate to the Cards page
   - View the FNB Gold Credit Card
   - Add more cards if needed

5. **Import bank statements**
   - Click "Import Statement" on the Dashboard
   - Upload a CSV, Excel, PDF, or OFX file
   - Review and confirm the import

6. **Analyze your finances**
   - View spending by category
   - Track budget progress
   - Monitor card usage

---

## Best Practices

### Card Management
- Keep card information up to date
- Mark expired cards as inactive
- Link transactions to the correct card
- Review card analytics monthly

### Bank Statement Import
- Import statements regularly (weekly or monthly)
- Always review the preview before importing
- Enable auto-categorization for faster processing
- Check import history to avoid duplicates

### Data Organization
- Use consistent naming for cards and accounts
- Categorize transactions accurately
- Set realistic budgets
- Review and reconcile monthly

---

## Support

For issues or questions:
1. Check the troubleshooting sections above
2. Review the technical documentation in `docs/PHASE4_TECHNICAL_DOCUMENTATION.md`
3. Check the implementation plan in `docs/PHASE4_IMPLEMENTATION_PLAN.md`

---

**Last Updated:** October 8, 2025  
**Version:** Phase 4.0

