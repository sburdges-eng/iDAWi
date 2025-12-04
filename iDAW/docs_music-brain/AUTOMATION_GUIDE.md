# Lariat Invoice Automation System
## Complete Guide to Automated Invoice Processing & Reporting

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Features](#features)
4. [How to Use](#how-to-use)
5. [File Structure](#file-structure)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## Overview

The **Lariat Invoice Automation System** automatically:
- ✅ Scans for new invoice files
- ✅ Extracts client and event data
- ✅ Updates the analysis database
- ✅ Generates monthly reports
- ✅ Tracks pricing trends

**No more manual data entry!** Just save your invoice files and run the automation.

---

## Quick Start

### Method 1: Double-Click Launcher (Easiest)

1. **Double-click** `lariat_automation.command`
2. Choose from menu:
   - **Option 1**: Import new invoices
   - **Option 2**: Generate monthly report
   - **Option 3**: Scan for new invoices

### Method 2: Command Line

```bash
# Navigate to BANQUET BEO folder
cd "/Users/seanburdges/Desktop/BANQUET BEO"

# Import new invoices
python3 lariat_invoice_automation.py import

# Generate monthly report
python3 lariat_invoice_automation.py report 2024 9

# Scan for new invoices
python3 lariat_invoice_automation.py scan
```

---

## Features

### 1. Automatic Invoice Detection

The system automatically detects new invoice files in:
```
/Users/seanburdges/Desktop/BANQUET BEO/INVOICE SPREADSHEETS/
```

**Supported formats:**
- `Lariat Invoice [ClientName] [M_D].xlsx`
- `Invoice [ClientName] [M_D].xlsx`

**Skipped files:**
- Kitchen prep sheets
- Files containing "Kitchen" or "Prep"
- Previously processed invoices

### 2. Data Extraction

Automatically extracts from each invoice:
- Client name
- Event date
- Menu items ordered
- Quantities and pricing
- Subtotal, tax (8.15%), service fee (20%)
- Total revenue
- Guest count (if available)

### 3. Database Updates

Updates **7 sheets** in `Lariat_BEO_Database_Analysis.xlsx`:
1. **Event Summary** - All events with financial totals
2. **All Line Items** - Every item from every event
3. **Menu Item Popularity** - Most frequently ordered items
4. **Top Revenue Items** - Highest-earning menu items
5. **Monthly Summary** - Revenue by month
6. **Pricing History** - Price tracking and variance
7. **Executive Summary** - Business insights and recommendations

### 4. Monthly Reports

Generates detailed text reports including:
- Total revenue for the month
- Number of events
- Average event size
- Top 5 items ordered
- Event-by-event breakdown
- Category analysis (bar, tacos, desserts, etc.)

Reports saved to:
```
/Users/seanburdges/Desktop/BANQUET BEO/reports/
```

---

## How to Use

### Importing New Invoices

**When to use:** After saving a new invoice to the INVOICE SPREADSHEETS folder

**Steps:**
1. Save your new invoice file to:
   ```
   /BANQUET BEO/INVOICE SPREADSHEETS/
   ```

2. Double-click `lariat_automation.command`

3. Choose **Option 1: Import New Invoices**

4. The system will:
   - Scan for new files
   - Extract data from each invoice
   - Update the database
   - Mark invoices as processed

**Output:**
```
📥 Found 1 new invoice(s) to process

   Processing: Lariat Invoice Jane Smith 11_20.xlsx
   ✅ Extracted: Jane Smith 11_20 (2024-11-20)
      Items: 12, Total: $14,250.00

📊 Updating database with 1 new event(s)...
   ✅ Database updated: Lariat_BEO_Database_Analysis.xlsx
   📝 Added 1 events
   📝 Added 12 line items
```

### Generating Monthly Reports

**When to use:** End of month, or when you need stats for a specific month

**Steps:**
1. Double-click `lariat_automation.command`

2. Choose **Option 2: Generate Monthly Report**

3. Enter year and month (or press Enter for current month)

4. Report is saved to `/reports/` folder

**Example Report:**
```
📅 Generating report for 2024-09...
✅ Report saved: reports/Lariat_Monthly_Report_2024_09.txt
📊 3 events, $38,976.50 revenue
```

**Report Contents:**
- Summary statistics
- Top 5 items for the month
- All events with totals
- Category breakdown (bar, tacos, etc.)

### Scanning for New Invoices

**When to use:** To check what's new without importing

**Steps:**
1. Double-click `lariat_automation.command`

2. Choose **Option 3: Scan for New Invoices**

3. See list of unprocessed invoices

---

## File Structure

```
BANQUET BEO/
│
├── lariat_invoice_automation.py      # Main automation script
├── lariat_automation.command          # Double-click launcher
├── AUTOMATION_GUIDE.md                # This file
│
├── Lariat_BEO_Database_Analysis.xlsx  # Main database (auto-updated)
├── .processed_invoices.json           # Tracking file (auto-created)
│
├── INVOICE SPREADSHEETS/              # Put new invoices here
│   ├── Lariat Invoice McMahon 7_18.xlsx
│   ├── Lariat Invoice Bob Clauss 8_2.xlsx
│   └── [New invoices go here]
│
├── reports/                           # Monthly reports (auto-created)
│   ├── Lariat_Monthly_Report_2024_07.txt
│   ├── Lariat_Monthly_Report_2024_08.txt
│   └── Lariat_Monthly_Report_2024_09.txt
│
└── [Template files...]
```

---

## Troubleshooting

### "No new invoices found"

**Cause:** All invoices in the folder have been processed already

**Solution:**
- Make sure new invoice files are in `/INVOICE SPREADSHEETS/`
- Check that filename follows the pattern: `Lariat Invoice [Name] [M_D].xlsx`
- If you want to re-process, delete `.processed_invoices.json`

### "Error processing [filename]"

**Possible causes:**
1. File is corrupted or password-protected
2. File structure doesn't match expected format
3. Missing required columns (Item, Cost, Amount, Total)

**Solution:**
- Verify the invoice file opens in Excel
- Check that it has columns A-D with: Item, Cost, Amount, Total
- Make sure subtotal, tax, service fee, and total rows are present

### "No events found for [month]"

**Cause:** No events in the database for that month

**Solution:**
- Verify events exist in the database
- Check date format in Event Summary sheet (should be YYYY-MM-DD)
- Make sure invoices were imported correctly

### Permission denied

**Cause:** Automation script doesn't have permission to run

**Solution:**
```bash
chmod +x lariat_automation.command
chmod +x lariat_invoice_automation.py
```

---

## Advanced Usage

### Command Line Options

```bash
# Import new invoices
python3 lariat_invoice_automation.py import

# Generate report for specific month
python3 lariat_invoice_automation.py report 2024 9

# Scan for new invoices (no import)
python3 lariat_invoice_automation.py scan

# Interactive mode (menu)
python3 lariat_invoice_automation.py
```

### Reprocessing All Invoices

If you need to rebuild the database from scratch:

1. **Backup your current database:**
   ```bash
   cp Lariat_BEO_Database_Analysis.xlsx Lariat_BEO_Database_BACKUP.xlsx
   ```

2. **Delete the processed list:**
   ```bash
   rm .processed_invoices.json
   ```

3. **Clear the database sheets:**
   - Open `Lariat_BEO_Database_Analysis.xlsx`
   - Delete all data rows (keep headers)
   - Save

4. **Run import:**
   ```bash
   python3 lariat_invoice_automation.py import
   ```

### Customizing the System

**Change invoice folder location:**

Edit `lariat_invoice_automation.py`, line ~350:
```python
INVOICE_DIR = "/your/custom/path/INVOICE SPREADSHEETS/"
```

**Change database location:**

Edit `lariat_invoice_automation.py`, line ~351:
```python
DATABASE_PATH = "/your/custom/path/Lariat_BEO_Database_Analysis.xlsx"
```

**Add custom date parsing:**

Edit the `extract_invoice_data()` method to handle different date formats.

---

## Best Practices

### 1. Regular Imports

**Recommended:** Import new invoices weekly or after each event

**Why:** Keeps your database current and reports accurate

### 2. Monthly Reports

**Recommended:** Generate monthly reports at month-end

**Why:** Track trends, identify popular items, monitor revenue

### 3. Backup Database

**Recommended:** Backup `Lariat_BEO_Database_Analysis.xlsx` monthly

**Why:** Protects your historical data

### 4. Consistent File Naming

**Required:** Follow the naming pattern:
```
Lariat Invoice [ClientName] [Month_Day].xlsx
```

**Examples:**
- ✅ `Lariat Invoice Jane Smith 11_20.xlsx`
- ✅ `Invoice Bob Johnson 12_5.xlsx`
- ❌ `Jane Smith Invoice.xlsx` (missing date)
- ❌ `invoice_11_20.xlsx` (missing client name)

### 5. Year Handling

**For 2025+ events:** Include year in filename:
```
Lariat Invoice Sarah Lee 10_17_25.xlsx  # October 17, 2025
```

**Default:** Without year, assumes current year (2024)

---

## Understanding the Data

### Processed Invoices Tracking

The system maintains a hidden file: `.processed_invoices.json`

**Format:**
```json
[
  "Lariat Invoice McMahon 7_18.xlsx",
  "Lariat Invoice Bob Clauss 8_2.xlsx"
]
```

**Purpose:** Prevents duplicate imports

**When to delete:** If you want to reprocess all invoices

### Database Structure

**Event Summary Sheet:**
- One row per event
- Totals row at bottom (auto-updated)
- Sorted by date

**All Line Items Sheet:**
- One row per menu item per event
- Multiple rows for the same client (different events)

**Pricing History Sheet:**
- Shows price variance for each menu item
- Highlights items with price changes

---

## FAQ

**Q: Can I edit the database manually?**

A: Yes, but be careful:
- ✅ You can add notes, adjust categories
- ⚠️ Don't delete the totals row in Event Summary
- ⚠️ Don't change date formats (keep YYYY-MM-DD)
- ⚠️ Don't modify formulas in calculated cells

**Q: What if I have an invoice with a different structure?**

A: The automation expects this structure:
- Column A: Item name
- Column B: Unit cost
- Column C: Quantity
- Column D: Line total
- Rows with "Sub total", "Tax", "Service Fee", "Total"

If your invoice is different, either:
1. Adjust the invoice to match this format, OR
2. Modify the `extract_invoice_data()` function in the script

**Q: Can I generate reports for multiple months at once?**

A: Not currently, but you can run the command multiple times:
```bash
python3 lariat_invoice_automation.py report 2024 7
python3 lariat_invoice_automation.py report 2024 8
python3 lariat_invoice_automation.py report 2024 9
```

**Q: Will this work on Windows?**

A: The Python script will work, but you'll need to:
1. Install Python 3 for Windows
2. Use Command Prompt instead of Terminal
3. Adjust file paths (use `C:\Users\...` instead of `/Users/...`)

---

## Support

If you encounter issues:

1. **Check this guide** - Most common issues are covered
2. **Verify file formats** - Make sure invoices follow the expected structure
3. **Check the console output** - Error messages usually indicate the problem
4. **Backup first** - Before making major changes, backup your database

---

## Version History

**v1.0** (2024-11-19)
- Initial release
- Automatic invoice import
- Database auto-update
- Monthly report generation
- Command-line and interactive modes

---

## Credits

Created for **The Lariat Restaurant** banquet operations
Built with Python 3 and openpyxl

---

**Happy Automating! 🚀**
