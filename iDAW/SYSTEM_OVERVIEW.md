# LARIAT BANQUET SYSTEM - SYSTEM OVERVIEW
**Your Complete Event Management Solution**

---

## 🎯 **EXECUTIVE SUMMARY**

The Lariat Banquet System is an integrated workflow management solution designed to streamline every aspect of banquet event planning, from initial client booking through final execution. This system ensures accuracy, efficiency, and consistency across all events while maintaining the high quality standards Lariat is known for.

**Key Benefits:**
- ✅ **Automated Pricing** - VLOOKUP formulas eliminate manual price lookups
- ✅ **Error Prevention** - Built-in checks prevent calculation mistakes
- ✅ **Time Savings** - Reduces admin time by 60-70%
- ✅ **Consistency** - Every event follows the same proven workflow
- ✅ **Scalability** - Works for events of any size (20-500+ guests)
- ✅ **Professional** - Generates polished, client-ready documents

---

## 📊 **SYSTEM ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────────┐
│                    LARIAT BANQUET SYSTEM                         │
│                         (Complete View)                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌─────────────────┐     ┌───────────────┐
│   CLIENT     │────▶│  EVENT BOOKING  │────▶│    INVOICE    │
│   INQUIRY    │     │  (Step 1)       │     │  TEMPLATE     │
└──────────────┘     └─────────────────┘     │  (Step 2)     │
                                              └───────┬───────┘
                                                      │
                                                      ▼
┌──────────────┐     ┌─────────────────┐     ┌───────────────┐
│   CLIENT     │◀────│    CONTRACT     │◀────│    CLIENT     │
│  APPROVAL    │     │   & DEPOSIT     │     │   APPROVAL    │
│  (Step 3)    │     └─────────────────┘     │   (Step 3)    │
└──────┬───────┘                              └───────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│              KITCHEN PREP SHEET (Auto-Generated)                 │
│  Items & Quantities ← Linked from Invoice                       │
│  (Step 4)                                                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│           INGREDIENT CALCULATION (Recipe Scaling)                │
│  From Recipe Book → Scale to Event Size → Master List           │
│  (Step 5)                                                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│          PRODUCTION SCHEDULE (Timeline Planning)                 │
│  Thursday Prep → Friday Prep → Saturday Service                 │
│  (Step 6)                                                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│             VENDOR ORDERING (Ingredient Procurement)             │
│  Shamrock → Sysco → US Foods → Local                           │
│  (Step 7)                                                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│          RECEIVING & INVENTORY (Quality Check)                   │
│  Inspect → Verify → Store → Update Inventory                    │
│  (Step 8)                                                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│          PREP & PRODUCTION (Kitchen Execution)                   │
│  Thursday: Braises → Friday: Final Prep → Saturday: Service     │
│  (Step 9)                                                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│            EVENT EXECUTION (Service & Delivery)                  │
│  Transport → Setup → Serve → Breakdown → Debrief                │
│  (Step 10)                                                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      EVENT COMPLETE ✅                            │
│  Client Satisfied • Team Debriefed • Lessons Learned             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 **FILE STRUCTURE**

### **Core Templates** (Use for every event)
```
📄 Invoice_Template.xlsx
   ├── Sheet 1: Client Invoice
   │   ├── Header (client info, event details)
   │   ├── Order Section (items, prices, quantities)
   │   ├── Calculations (subtotal, tax, service fee, total)
   │   ├── Minimum Spend Check
   │   └── Price Lookup Table (F:G columns)
   │
   └── Sheet 2: Kitchen Prep Sheet
       ├── Items (linked from Sheet 1)
       ├── Quantities (linked from Sheet 1)
       ├── Prep Day Assignment
       ├── Pre-Prep Tasks
       ├── Plating Instructions
       ├── Service Times
       └── Critical Notes
```

### **Reference Documents** (Read-only)
```
📘 Lariat_Recipe_Book.docx
   ├── Appetizers (Mini Rellenos, Corn Dogs, etc.)
   ├── Sauces (Aioli, Salsa, Queso, etc.)
   ├── Mains (Tacos, Sliders, Braised Meats)
   ├── Sides (Mac, Salads, Vegetables)
   ├── Brines & Marinades
   ├── Rubs & Seasonings
   └── Desserts

📊 LARIAT_ORDER_GUIDE_OFFICIAL.xlsx
   ├── Product List (all items)
   ├── Vendor Information
   ├── Pricing
   ├── Order Codes
   └── Minimum Orders
```

### **Documentation** (System guides)
```
📚 PROJECT_RULES.md
   ├── System specifications
   ├── Formulas and calculations
   ├── Workflow guidelines
   ├── Quality standards
   └── Best practices

📚 WORKFLOW.md
   ├── 10-step process detailed
   ├── Timing for each step
   ├── Checklists
   └── Troubleshooting

📚 QA_CUSTOMIZATION_GUIDE.md
   ├── 35 customization questions
   ├── Business-specific options
   └── Implementation guidance

📚 SYSTEM_OVERVIEW.md (this document)
   ├── High-level summary
   ├── Quick reference
   └── Getting started
```

---

## 🔑 **KEY FEATURES**

### **1. Automated Pricing System**
- **VLOOKUP Formula**: Automatically pulls prices from master list
- **Error Handling**: IFNA prevents #N/A errors when items not found
- **Easy Updates**: Update one price, affects all future invoices
- **No Manual Lookups**: Eliminates human error in pricing

**Formula Used:**
```excel
=IFNA(VLOOKUP(A3,F$2:G$97,2,FALSE),"")
```

---

### **2. Automatic Calculations**
- **Subtotal**: Sums all line items
- **Tax**: 8.15% applied automatically
- **Service Fee**: 20% applied automatically
- **Total**: Sum of subtotal + tax + service fee
- **Minimum Spend Check**: Shows if order meets minimum requirement

**Never manually calculate again!**

---

### **3. Kitchen Sheet Auto-Population**
- **Linked Data**: Items and quantities automatically populate from invoice
- **Real-Time Updates**: Change invoice → kitchen sheet updates automatically
- **Prep Workflow**: Organized by day (Thursday, Friday, Saturday)
- **Task Details**: Pre-prep, plating, timing, notes all in one place

---

### **4. Recipe Scaling System**
- **Standard Formula**: Scale any recipe to any quantity
- **Batch Calculations**: Automatically determine number of batches needed
- **Ingredient Aggregation**: Combine quantities across multiple recipes
- **Buffer Inclusion**: Adds 10% waste factor automatically

---

### **5. Quality Control Checkpoints**
Built-in checkpoints at every stage:
- ✓ Invoice formulas working
- ✓ Kitchen sheet complete
- ✓ Ingredients received and inspected
- ✓ Production schedule followed
- ✓ Food temperatures monitored
- ✓ Event executed successfully

---

## 🎨 **WHO USES WHAT**

### **Event Coordinator / Sales**
**Uses:**
- Invoice Template (Sheet 1)
- Q&A Customization Guide
- Client communication

**Responsibilities:**
- Create invoices
- Manage client relationships
- Process payments
- Handle contracts

---

### **Kitchen Manager / Head Chef**
**Uses:**
- Kitchen Prep Sheet (Sheet 2)
- Recipe Book
- Production Schedule
- Order Guide

**Responsibilities:**
- Generate kitchen sheets
- Scale recipes
- Create production schedules
- Order ingredients
- Oversee prep

---

### **Prep Cooks / Line Cooks**
**Uses:**
- Kitchen Prep Sheet
- Recipe cards
- Production schedule

**Responsibilities:**
- Execute prep tasks
- Follow recipes
- Meet timing deadlines
- Quality control

---

### **Service Staff / Servers**
**Uses:**
- Event Execution Plan
- Setup checklists

**Responsibilities:**
- Setup service area
- Serve guests
- Maintain buffet
- Professional service

---

### **Business Owner / Manager**
**Uses:**
- All documents
- Financial reports
- System analytics

**Responsibilities:**
- System oversight
- Staff training
- Pricing updates
- Continuous improvement

---

## ⏱️ **TYPICAL TIMELINE**

### **Event Booked 14 Days Out:**

| Days Before Event | Tasks | Time Required |
|-------------------|-------|---------------|
| **14 days** | Event booking, invoice creation | 1-2 hours |
| **13-11 days** | Client review and approval | (client time) |
| **10 days** | Generate kitchen sheet, calculate ingredients | 2-3 hours |
| **9 days** | Create production schedule | 1 hour |
| **8 days** | Place orders with vendors | 1-2 hours |
| **7 days** | Final headcount confirmation | 30 min |
| **3 days (Thurs)** | Receive ingredients, start long prep | 8 hours |
| **2 days (Fri)** | Final prep, assembly items | 8 hours |
| **1 day before** | Final inventory check, setup prep | 2 hours |
| **Event Day (Sat)** | Final cooking, transport, service | 8-12 hours |
| **Day after** | Follow-up, documentation | 1 hour |

**Total Staff Time:** ~40-50 hours (varies by event size)

---

## 💰 **COST BREAKDOWN**

**Typical Event (100 guests, $8,000 budget):**

| Category | Typical % | Amount |
|----------|-----------|--------|
| **Food Costs** | 28-32% | $2,240 - $2,560 |
| **Labor** | 25-30% | $2,000 - $2,400 |
| **Overhead** | 8-12% | $640 - $960 |
| **Profit** | 30-35% | $2,400 - $2,800 |

**Target Metrics:**
- Food Cost: <32% of menu price
- Labor: <30% of menu price
- Total COGS: <60% of menu price
- Profit Margin: >30%

---

## 📈 **SCALABILITY**

**This system works for:**

### **Small Events (20-50 guests)**
- Minimum: $2,500
- Staff: 2-3 people
- Prep Time: 2 days
- Example: Private dinner party

### **Medium Events (50-100 guests)**
- Minimum: $5,000
- Staff: 3-5 people
- Prep Time: 3 days
- Example: Corporate lunch, small wedding

### **Large Events (100-200 guests)**
- Minimum: $10,000
- Staff: 5-8 people
- Prep Time: 3-4 days
- Example: Wedding reception, gala

### **Extra Large Events (200+ guests)**
- Minimum: $15,000+
- Staff: 8-15 people
- Prep Time: 4-5 days
- Example: Festival, corporate conference

**Recipe scaling ensures accurate quantities for any size!**

---

## 🎓 **GETTING STARTED**

### **For New Users:**

**Step 1: Read Documentation** (1-2 hours)
1. Read this SYSTEM_OVERVIEW.md first
2. Review PROJECT_RULES.md for details
3. Skim WORKFLOW.md to understand process
4. Browse Q&A_CUSTOMIZATION_GUIDE.md

**Step 2: Familiarize with Templates** (30 minutes)
1. Open Invoice_Template.xlsx
2. Explore both sheets
3. See where formulas are
4. Don't change anything yet!

**Step 3: Review Reference Documents** (1 hour)
1. Browse Lariat_Recipe_Book.docx
2. Look at LARIAT_ORDER_GUIDE_OFFICIAL.xlsx
3. Understand what info is where

**Step 4: Practice Run** (2-3 hours)
1. Create a sample event invoice
2. Generate kitchen sheet
3. Calculate ingredients
4. Walk through entire workflow
5. Get comfortable with process

**Step 5: Go Live!**
1. Use system for real event
2. Follow workflow step-by-step
3. Take notes on improvements needed
4. Debrief with team after

---

### **For Experienced Users:**

**Quick Reference:**

1. **New Event?**
   → Copy `Invoice_Template.xlsx`
   → Fill in client info & menu
   → Send to client

2. **Event Approved?**
   → Generate kitchen sheet (auto-populates)
   → Calculate ingredients
   → Create production schedule
   → Order ingredients

3. **Week of Event?**
   → Follow production schedule
   → Execute prep
   → Deliver and serve

4. **After Event?**
   → Client follow-up
   → Team debrief
   → Update system as needed

---

## 🔧 **CUSTOMIZATION OPTIONS**

The system is designed to be flexible. See **QA_CUSTOMIZATION_GUIDE.md** for 35+ questions covering:

- **Financial:** Minimum spends, discounts, fees
- **Menu:** Seasonal items, dietary options, pairings
- **Kitchen:** Capacity, equipment, workflow
- **Vendors:** Preferences, contracts, backups
- **Service:** Staffing, rentals, setup options
- **System:** Automation, reporting, tracking

**Make it your own!**

---

## 📊 **REPORTING & ANALYTICS**

**Available Reports:**

1. **Event Summary**
   - Client info
   - Menu items
   - Revenue
   - Date

2. **Food Cost Analysis**
   - Ingredient costs
   - Food cost %
   - Comparison to target

3. **Labor Tracking**
   - Staff hours
   - Labor cost
   - Efficiency metrics

4. **Client Satisfaction**
   - Feedback scores
   - Repeat clients
   - Referrals

5. **Menu Popularity**
   - Most ordered items
   - Seasonal trends
   - Profitability by item

6. **Vendor Analysis**
   - Spending by vendor
   - Pricing trends
   - Quality issues

**Use data to continuously improve!**

---

## 🚨 **COMMON QUESTIONS**

### **Q: What if an item isn't in the price lookup table?**
**A:** Add it! Go to columns F:G in the Invoice sheet, scroll to the next empty row, and add the item name and price. Future invoices will find it automatically.

### **Q: Can I change the tax rate or service fee percentage?**
**A:** Yes! In PROJECT_RULES.md, find the formula specifications and update accordingly. Change the formulas in the template, then save as your new master template.

### **Q: What if I need to modify an approved invoice?**
**A:** Save a new version (increment version number: v1 → v2). Document changes in the NOTES.txt file in the event folder. Communicate changes to kitchen team.

### **Q: How do I add a new menu item?**
**A:** 
1. Add recipe to Recipe Book
2. Add item to price lookup table (F:G)
3. Test by creating sample invoice
4. Train team on new item

### **Q: Can I use this for non-banquet catering?**
**A:** Absolutely! The system works for any food service event: corporate lunches, meal prep, weekly deliveries, etc. Adjust as needed.

### **Q: What if my kitchen capacity is smaller/larger?**
**A:** Use the Q&A Customization Guide to adjust:
- Batch sizes in recipes
- Production schedule timing
- Staff requirements
- Equipment limitations

### **Q: Do I need to follow the workflow exactly?**
**A:** The 10 steps represent best practices, but you can adapt. However, skipping steps (especially Steps 4-7) increases risk of errors and missed details.

### **Q: How often should I update pricing?**
**A:** Review quarterly (March, June, September, December). Update when:
- Vendor costs change significantly (>10%)
- Labor costs increase
- Competitors adjust pricing
- Market conditions shift

### **Q: Can multiple people work on the system simultaneously?**
**A:** For different events, yes. For same event, use version control carefully. Consider cloud storage (Google Drive, Dropbox) for real-time collaboration if needed.

---

## 🎯 **SUCCESS METRICS**

**You'll know the system is working when:**

- ✅ **Invoices take <30 minutes** to create (down from 1-2 hours)
- ✅ **Zero pricing errors** (formulas eliminate manual mistakes)
- ✅ **Kitchen sheets auto-populate** (no duplicate data entry)
- ✅ **Ingredient orders are accurate** (proper scaling)
- ✅ **Events run smoothly** (proper planning and timeline)
- ✅ **Food cost % stays in target range** (28-32%)
- ✅ **Clients are happy** (professional, consistent service)
- ✅ **Team is efficient** (clear processes, less confusion)
- ✅ **Business is profitable** (>30% profit margin)

---

## 📞 **SUPPORT & RESOURCES**

### **Documentation:**
- **PROJECT_RULES.md** - Detailed specifications
- **WORKFLOW.md** - Step-by-step process
- **QA_CUSTOMIZATION_GUIDE.md** - Customization questions
- **SYSTEM_OVERVIEW.md** (this document) - High-level summary

### **Reference Materials:**
- **Lariat_Recipe_Book.docx** - All recipes
- **LARIAT_ORDER_GUIDE_OFFICIAL.xlsx** - Product/vendor info

### **For Help:**
1. Check documentation first
2. Consult with kitchen manager
3. Review past events for examples
4. Contact system administrator

---

## 🔐 **DATA SECURITY**

**Backup Protocol:**
- **Daily**: Auto-backup to cloud (Google Drive/Dropbox)
- **Weekly**: Manual backup to external drive
- **Monthly**: Archive backup off-site

**Access Control:**
- **Managers**: Full edit access
- **Staff**: View-only access to templates
- **Clients**: Invoice access only
- **Vendors**: Order sheets only

**Confidentiality:**
- Client information: Private and secure
- Pricing: Internal only
- Recipes: Proprietary - protect carefully
- Vendor contracts: Confidential

---

## 🌟 **CONTINUOUS IMPROVEMENT**

**The system evolves with your business!**

### **Quarterly Reviews:**
- Update pricing
- Refine recipes
- Adjust workflows
- Review vendor relationships
- Analyze event metrics

### **Annual Audits:**
- Complete system review
- Staff training updates
- Technology upgrades
- Strategic planning

### **Feedback Loop:**
```
Event Complete → Team Debrief → Document Lessons →
Update Procedures → Apply to Next Event → Measure Results
```

**Every event makes the system better!**

---

## 🏆 **BEST PRACTICES**

### **DO:**
- ✅ Use templates for every event
- ✅ Follow the 10-step workflow
- ✅ Double-check formulas before sending invoices
- ✅ Scale recipes carefully
- ✅ Communicate clearly with team
- ✅ Document lessons learned
- ✅ Back up files regularly
- ✅ Train new staff thoroughly
- ✅ Quality check at every step
- ✅ Celebrate successes!

### **DON'T:**
- ❌ Skip steps in the workflow
- ❌ Ignore formula errors
- ❌ Guess at recipe scaling
- ❌ Forget to update inventory
- ❌ Rush through quality checks
- ❌ Forget client communication
- ❌ Neglect team debriefs
- ❌ Resist improvements
- ❌ Overlook small details
- ❌ Take shortcuts on food safety

---

## 🎉 **YOU'RE READY!**

**You now have:**
- ✅ Complete system overview
- ✅ Templates ready to use
- ✅ Detailed workflow documentation
- ✅ Recipe scaling formulas
- ✅ Quality control checklists
- ✅ Customization options

**Next Steps:**
1. Review all documentation
2. Practice with sample event
3. Customize as needed
4. Train your team
5. **Go live and crush it!** 🚀

---

**"Excellence is not an act, but a habit."** - Aristotle

**With the Lariat Banquet System, excellence becomes your daily routine!**

---

**Document Version:** 1.0  
**Last Updated:** November 19, 2025  
**Next Review:** February 19, 2026  
**Maintained By:** Lariat Operations Team

---

## 🎓 **REMEMBER:**

**This system is a tool, not a rule.**

Use it to support your creativity and expertise, not replace it.

**Your culinary skills + This systematic approach = Unstoppable success!**

🍽️ **Happy Catering!** 🎉
