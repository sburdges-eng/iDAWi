# LARIAT BANQUET SYSTEM - PROJECT RULES & GUIDELINES
**Version 1.0** | Created: November 2025

---

## 🎯 **SYSTEM PURPOSE**
This system manages the complete lifecycle of Lariat banquet events from booking through execution, ensuring:
- Accurate pricing and invoicing
- Efficient kitchen prep and production
- Proper ingredient ordering and inventory
- Seamless day-of execution

---

## 📋 **PROJECT STRUCTURE**

```
LARIAT_BANQUET_SYSTEM/
├── 📁 DOCUMENTATION/
│   ├── PROJECT_RULES.md (this file)
│   ├── WORKFLOW.md
│   ├── SYSTEM_OVERVIEW.md
│   └── QA_CUSTOMIZATION_GUIDE.md
│
├── 📁 TEMPLATES/
│   ├── Invoice_Template.xlsx
│   ├── Kitchen_Prep_Sheet_Template.xlsx
│   ├── Production_Schedule_Template.xlsx
│   └── Event_Execution_Plan_Template.xlsx
│
├── 📁 DATABASES/ (Read-Only Reference)
│   ├── LARIAT_ORDER_GUIDE_OFFICIAL.xlsx
│   ├── LARIAT_INGREDIENTS_MASTER.xlsx
│   └── Lariat_Recipe_Book.docx
│
├── 📁 ANALYSIS/
│   ├── SYSTEM_ANALYSIS.xlsx
│   └── VENDOR_COMPARISON.xlsx
│
└── 📁 ACTIVE_EVENTS/
    └── [Individual event folders]
```

---

## 🔄 **CORE WORKFLOW** (10 Steps)

```
1. EVENT BOOKING
   ↓
2. CREATE INVOICE (from template)
   ↓
3. CLIENT APPROVAL
   ↓
4. GENERATE KITCHEN SHEET (auto-populated from invoice)
   ↓
5. CALCULATE INGREDIENTS (recipe scaling)
   ↓
6. CREATE PRODUCTION SCHEDULE (prep timeline)
   ↓
7. ORDER INGREDIENTS (vendor selection)
   ↓
8. RECEIVE & INVENTORY
   ↓
9. PREP & PRODUCTION (follow schedule)
   ↓
10. EVENT EXECUTION (day-of operations)
```

---

## 🎯 **CORE PRINCIPLES**

### 1. **SINGLE SOURCE OF TRUTH**
- **Recipe Book** = Master for all recipes and procedures
- **Order Guide** = Master for products, vendors, and pricing
- **Invoice Template** = Master for menu pricing
- **Kitchen Sheet** = Master for prep workflow and timing

### 2. **DATA FLOW DIRECTION**
```
Event Booking → Invoice → Kitchen Sheet → Production Schedule → Execution
     ↓            ↓             ↓                ↓                  ↓
[Client Info] [Menu Items] [Ingredients]    [Timeline]        [Day-of Ops]
```

### 3. **NO DUPLICATE DATA ENTRY**
- Use VLOOKUP/XLOOKUP for pricing (references master price list)
- Use formulas for all calculations (subtotal, tax, service fee)
- Copy data forward between documents - NEVER retype

### 4. **FORWARD COMPATIBILITY**
- Templates work for events of any size (20-500 guests)
- Easy to add new menu items
- Scalable recipes (batch calculations built-in)
- Flexible prep schedules

---

## 💰 **INVOICE TEMPLATE SPECIFICATIONS**

### **Structure:**
```
SHEET 1: CLIENT INVOICE
├── Header Section (A1:E1)
│   ├── Client Name
│   ├── Event Date
│   ├── Guest Count
│   ├── Event Type
│   └── Notes
│
├── Order Section (A3:E25)
│   ├── Column A: Item Name (manual entry)
│   ├── Column B: Unit Cost (VLOOKUP from F:G)
│   ├── Column C: Quantity
│   ├── Column D: Total (=B*C)
│   └── Column E: Notes
│
├── Totals Section (A27:D31)
│   ├── Row 27: Subtotal = SUM(D3:D25)
│   ├── Row 28: Tax (8.15%) = Subtotal * 0.0815
│   ├── Row 29: Service Fee (20%) = Subtotal * 0.20
│   └── Row 31: TOTAL = SUM(Subtotal + Tax + Service Fee)
│
├── Minimum Spend Check (D33:E34)
│   ├── D33: "Minimum Spend" label
│   ├── E33: Minimum amount (manual entry)
│   ├── D34: "Over/Under" label
│   └── E34: =E33-D27 (shows difference)
│
└── Price Lookup Table (F2:G100)
    ├── Column F: Item Name
    └── Column G: Unit Price

SHEET 2: KITCHEN PREP SHEET
├── Column A: Item Name (from Sheet1)
├── Column B: Quantity (from Sheet1)
├── Column C: Prep Day
├── Column D: Pre-Prep Tasks
├── Column E: Plating Instructions
├── Column F: Time to Serve
└── Column G: Notes
```

### **Critical Formulas:**

**VLOOKUP for Pricing (Column B):**
```excel
=IFNA(VLOOKUP(A3,F$2:G$100,2,FALSE),"")
```
*Looks up item name in price table, returns price, shows blank if not found*

**Line Total (Column D):**
```excel
=B3*C3
```
*Multiplies unit cost by quantity*

**Subtotal (D27):**
```excel
=SUM(D3:D25)
```
*Sums all line item totals*

**Tax (D28):**
```excel
=D27*0.0815
```
*8.15% sales tax*

**Service Fee (D29):**
```excel
=D27*0.20
```
*20% service charge*

**Total (D31):**
```excel
=D27+D28+D29
```
*Or: =SUM(D27:D29)*

**Minimum Spend Check (E34):**
```excel
=E33-D27
```
*Positive = over minimum, Negative = under minimum*

### **Key Features:**
✅ Auto-pricing via VLOOKUP  
✅ Error handling (IFNA prevents #N/A errors)  
✅ Automatic tax calculation  
✅ Automatic service fee calculation  
✅ Minimum spend validator  
✅ Kitchen sheet auto-populates from invoice

---

## 🍳 **KITCHEN PREP SHEET SPECIFICATIONS**

### **Purpose:**
Translates invoice line items into actionable prep tasks with timing

### **Data Sources:**
- Item names: FROM Invoice Sheet1, Column A
- Quantities: FROM Invoice Sheet1, Column C
- Prep instructions: FROM Recipe Book
- Timing: Based on recipe requirements

### **Critical Elements:**

**Prep Day Assignment:**
```
Thursday → Long-braise items, stocks, bases
Friday → Final prep, assembly items
Saturday (Day-of) → Service prep, plating
```

**Timing Standards:**
- Buffet items: Ready 45 minutes before service
- Passed apps: Ready 15 minutes before service
- Desserts: Completed during main service

**Notes Column:**
- Ingredient concerns ("order extra avocados")
- Equipment needs ("slider buns required")
- Special instructions ("order from Sysco")

---

## 📊 **RECIPE SCALING RULES**

### **Standard Formula:**
```
New Quantity = (Current Quantity ÷ Original Yield) × Desired Yield
```

### **Example:**
```
Recipe: Buttermilk Brine (from Recipe Book)
Original Yield: 12 qt (48 servings @ 1 cup each)
Event Needs: 80 servings

Calculation:
Scale Factor = 80 ÷ 48 = 1.667
Buttermilk: 0.5 gallon × 1.667 = 0.833 gallons (round to 1 gallon)
Hot Sauce: 500g × 1.667 = 833g
```

### **Batch Cooking Guidelines:**
- Maximum batch size: Follow recipe "Max Batch" note
- If exceeding max: Split into multiple batches
- Timing between batches: 15-30 minutes
- Label each batch with time/date

---

## 🛒 **ORDERING & INVENTORY RULES**

### **Vendor Priority:**
```
1st Choice: SHAMROCK (Broadline distributor)
2nd Choice: SYSCO (Specialty items)
3rd Choice: US FOODS (Backup)
Local: King Soopers, Costco (Emergency/specialty)
```

### **Order Timing:**
- **Thursday Delivery:** Long-lead proteins (pork butt, beef cheeks)
- **Friday Delivery:** Fresh produce, dairy
- **Saturday Morning:** Last-minute items only

### **Inventory Checks:**
- Before ordering: Check existing stock
- After ordering: Update inventory spreadsheet
- After event: Record waste/leftovers

### **PAR Levels** (Maintain minimum stock):
```
Dry goods: 2-week supply
Frozen proteins: 1-week supply
Fresh produce: 3-day supply
Dairy: 5-day supply
```

---

## 💵 **PRICING & FINANCIAL RULES**

### **Standard Pricing Structure:**
```
Food Cost Target: 28-32% of menu price
Labor Cost Target: 25-30% of menu price
Total COGS Target: <60% of menu price
```

### **Minimum Spend Requirements:**
```
<50 guests: $2,500 minimum
50-100 guests: $5,000 minimum
100-200 guests: $10,000 minimum
200+ guests: $15,000 minimum
```

### **Deposit & Payment Terms:**
```
Booking: 25% deposit
14 days before: 50% payment
Day of event: Final 25% + any additions
```

### **Pricing Updates:**
```
Review quarterly: March, June, September, December
Update based on: Vendor cost changes, labor costs, market conditions
Version control: Save old price list before updating
```

---

## 📅 **PRODUCTION SCHEDULE TEMPLATE**

### **Timeline Structure:**

**T-7 Days (One Week Before):**
- Finalize headcount with client
- Confirm menu items
- Order long-lead ingredients
- Schedule staff

**T-3 Days (Thursday):**
- Receive ingredient deliveries
- Start long-braise items (carnitas, barbacoa, green chile)
- Prep stocks and bases
- Make sauces (can hold 3-5 days)

**T-2 Days (Friday):**
- Receive fresh produce delivery
- Complete remaining prep
- Portion proteins
- Prep vegetables
- Bake cornbread
- Make cold items (salads, salsas)

**T-1 Day (Saturday Morning):**
- Final inventory check
- Last-minute fresh items
- Setup mise en place
- Equipment check

**Event Day:**
- Reheat items (per schedule)
- Final plating
- Service
- Breakdown
- Inventory remaining

---

## ✅ **QUALITY CONTROL CHECKLIST**

### **Before Sending Invoice:**
- [ ] All VLOOKUP formulas working (no #N/A errors)
- [ ] Quantities accurate
- [ ] Subtotal calculates correctly
- [ ] Tax calculates correctly (8.15%)
- [ ] Service fee calculates correctly (20%)
- [ ] Total is accurate
- [ ] Minimum spend checked
- [ ] Client information complete
- [ ] Event date/time confirmed
- [ ] Special requests noted

### **Before Ordering Ingredients:**
- [ ] Kitchen sheet complete
- [ ] Recipe scaling calculated
- [ ] Ingredient quantities finalized
- [ ] Existing inventory checked
- [ ] Vendor availability confirmed
- [ ] Delivery dates scheduled
- [ ] Storage space available
- [ ] Budget approved

### **Before Event:**
- [ ] All ingredients received
- [ ] All prep tasks completed
- [ ] Staff assignments made
- [ ] Equipment ready and tested
- [ ] Execution plan printed
- [ ] Backup plans in place
- [ ] Emergency contacts available

---

## 🔧 **CUSTOMIZATION Q&A GUIDE**

*These questions should be asked when building/customizing the system:*

### **Invoice Customization:**
1. What is your typical minimum spend by event size?
2. Do you offer discounts for large orders? (Threshold? Percentage?)
3. Are there seasonal pricing adjustments?
4. Do you charge delivery fees? (Flat rate? Distance-based?)
5. Do you offer payment plans? (Deposit structure?)
6. Do you itemize bar spend separately?
7. Do you charge setup/breakdown fees?
8. Do you require event insurance?

### **Menu Customization:**
9. Which menu items are seasonal only?
10. Which items require special equipment?
11. Which items have minimum order quantities?
12. Which items can't be made in advance?
13. Are there items that pair well/poorly together?
14. Do you offer substitutions? (Dietary restrictions?)

### **Kitchen Workflow:**
15. How many staff typically work events?
16. What is your kitchen capacity for simultaneous prep?
17. Do you prep on-site or off-site?
18. What equipment do you have available?
19. What is your maximum batch size per recipe?
20. Do you have cold storage limitations?

### **Vendor Preferences:**
21. Who are your preferred vendors by category?
22. Do you have negotiated pricing agreements?
23. What are vendor minimum order amounts?
24. What are typical delivery windows?
25. Who are backup vendors if primary unavailable?

### **Event Execution:**
26. Do you offer staffing? (Servers, bartenders?)
27. Do you provide rentals? (Tables, linens, etc?)
28. What is your service area? (Delivery radius?)
29. Do you offer setup/breakdown services?
30. Do you handle decorations/ambiance?

---

## 🔐 **VERSION CONTROL**

### **File Naming Convention:**
```
[Template Type]_[Client Name]_[Event Date]_v[#].xlsx

Examples:
Invoice_KaitlynTori_2025-10-17_v1.xlsx
KitchenSheet_Logan_2025-09-18_v2.xlsx
```

### **Version Increment Triggers:**
- Client requests menu changes
- Headcount changes
- Pricing updates
- Scope changes (added/removed services)

### **Archive System:**
```
ACTIVE_EVENTS/
└── ClientName_EventDate/
    ├── Invoice_v1.xlsx
    ├── Invoice_v2.xlsx (current)
    ├── KitchenSheet_v1.xlsx
    └── NOTES.txt (change log)
```

---

## 📈 **METRICS & KPIs**

### **Track Per Event:**
- **Food Cost %** = (Ingredient Cost ÷ Menu Price) × 100
- **Labor Hours** = Total staff hours for event
- **Waste %** = (Leftover Food ÷ Total Food Prepared) × 100
- **Client Satisfaction** = Post-event survey score
- **Profit Margin** = (Revenue - COGS - Labor) ÷ Revenue

### **Review Quarterly:**
- Average food cost % across all events
- Most/least profitable menu items
- Vendor pricing trends
- Labor efficiency trends
- Client satisfaction trends

### **Continuous Improvement:**
```
Event Complete → Team Debrief → Document Issues →
Update Procedures → Test Next Event → Measure Results
```

---

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Issue: #N/A Error in Invoice**
**Cause:** Item name doesn't match price lookup table exactly  
**Solution:** Check spelling, spacing, capitalization - must match exactly

### **Issue: Kitchen Sheet Not Auto-Populating**
**Cause:** Cell references broken  
**Solution:** Verify formulas reference correct sheet/cells

### **Issue: Recipe Scaling Produces Odd Numbers**
**Cause:** Rounding needed for practical measurements  
**Solution:** Round to nearest practical increment (1/4 cup, 25g, etc.)

### **Issue: Ingredient Order Too Large**
**Cause:** Recipe scaled incorrectly or no waste factor  
**Solution:** Add 10% buffer to raw ingredients, recheck scaling math

### **Issue: Minimum Spend Not Met**
**Cause:** Client order below threshold  
**Solution:** Suggest add-ons, increase portions, or apply minimum fee

---

## 🎓 **TRAINING REQUIREMENTS**

### **New Staff Must Learn:**
1. How to use Invoice Template
2. How to read Kitchen Prep Sheet
3. Recipe scaling calculations
4. Vendor ordering process
5. Quality control standards
6. Food safety protocols
7. Event execution roles

### **Managers Must Learn:**
- All of the above, PLUS:
- How to customize templates
- How to update pricing
- How to analyze event metrics
- How to train new staff
- How to handle client changes

---

## 📝 **MAINTENANCE SCHEDULE**

### **Weekly:**
- [ ] Review active events
- [ ] Check ingredient inventory
- [ ] Confirm upcoming deliveries

### **Monthly:**
- [ ] Update price list if vendor costs changed
- [ ] Review previous month's events
- [ ] Archive completed event files
- [ ] Update staff training materials

### **Quarterly:**
- [ ] Full system review
- [ ] Vendor performance analysis
- [ ] Menu pricing updates
- [ ] Recipe refinements
- [ ] Template improvements

### **Annually:**
- [ ] Complete system audit
- [ ] Update all documentation
- [ ] Vendor contract renewals
- [ ] Staff performance reviews
- [ ] Strategic planning

---

## 🔒 **DATA SECURITY**

### **Backup Protocol:**
- Daily: Auto-backup to cloud (Google Drive)
- Weekly: Manual backup to external drive
- Monthly: Archive backup off-site

### **Access Control:**
- Managers: Full edit access
- Staff: View-only access to templates
- Clients: Invoice access only
- Vendors: Order sheets only

### **Confidentiality:**
- Client information: Private
- Pricing: Internal only
- Recipes: Proprietary - protect carefully
- Vendor contracts: Confidential

---

## ⚡ **QUICK REFERENCE**

### **Most Common Tasks:**

**Create New Event Invoice:**
1. Copy Invoice Template
2. Rename: `Invoice_[Client]_[Date]_v1.xlsx`
3. Fill client info header
4. Enter menu items in Column A
5. Enter quantities in Column C
6. Verify VLOOKUP prices populate
7. Check totals calculate
8. Enter minimum spend
9. Save and send to client

**Generate Kitchen Sheet:**
1. Copy item names from Invoice Sheet1-A to Sheet2-A
2. Copy quantities from Invoice Sheet1-C to Sheet2-B
3. Fill prep day based on item type
4. Add prep tasks from Recipe Book
5. Set service times
6. Add special notes
7. Print for kitchen

**Calculate Ingredient Order:**
1. List all menu items from Kitchen Sheet
2. Find recipes in Recipe Book
3. Scale recipes to quantities needed
4. Sum all ingredients across recipes
5. Add 10% buffer for waste
6. Check inventory - subtract on-hand
7. Create vendor order list

---

## 📞 **SUPPORT & RESOURCES**

### **System Questions:**
- Review this PROJECT_RULES.md file first
- Check WORKFLOW.md for process questions
- See QA_CUSTOMIZATION_GUIDE.md for features

### **Recipe Questions:**
- Refer to Lariat_Recipe_Book.docx
- Contact head chef for clarifications

### **Vendor Questions:**
- Check LARIAT_ORDER_GUIDE_OFFICIAL.xlsx
- Contact vendor rep directly

### **Technical Issues:**
- Check formulas in template
- Verify cell references
- Contact system administrator

---

**Document Version:** 1.0  
**Last Updated:** November 19, 2025  
**Next Review:** February 19, 2026  
**Maintained By:** Lariat Banquet Team  
**Questions/Suggestions:** [contact info]

---

## 🎯 **REMEMBER:**

✅ **Templates are your friends** - use them, don't reinvent  
✅ **Double-check formulas** - one error cascades everywhere  
✅ **Scale recipes carefully** - math errors = food disasters  
✅ **Communicate clearly** - client, kitchen, vendors all need info  
✅ **Document everything** - today's notes save tomorrow's headaches  

**"Mise en place" applies to paperwork too!** 🍳

