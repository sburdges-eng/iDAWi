# LARIAT BANQUET SYSTEM - Q&A CUSTOMIZATION GUIDE
**Interactive Questions for System Setup**

---

## 🎯 PURPOSE

This guide contains questions to ask when customizing the Lariat Banquet System for your specific business needs. Work through each section to tailor templates, workflows, and features.

---

## 💰 **SECTION 1: PRICING & FINANCIAL STRUCTURE**

### Question 1: What are your minimum spend requirements by event size?

**Options:**
- A) Standard tiered minimums (e.g., <50 guests = $2,500, 50-100 = $5,000)
- B) Custom minimums based on venue/day
- C) No minimums, charge per head only
- D) Minimums only for certain days (weekends vs weekdays)

**Your Answer:** _________________

**System Impact:**
- Updates cell E32 in Invoice Template
- Creates conditional formatting rules
- Adds validation alerts

---

### Question 2: Do you offer volume discounts?

**Options:**
- A) Yes, percentage off at certain thresholds
- B) Yes, tiered pricing structure
- C) No, pricing is fixed
- D) Case-by-case negotiation

**If A or B, specify:**
- Threshold 1: ____ guests → ____% discount
- Threshold 2: ____ guests → ____% discount
- Threshold 3: ____ guests → ____% discount

**Your Answer:** _________________

**System Impact:**
- Adds discount calculation rows
- Creates lookup table for discount tiers
- Adds conditional formula to invoice

---

### Question 3: What is your sales tax rate?

**Current setting:** 8.15%

**Your tax rate:** _______% (if different)

**System Impact:**
- Updates formula in cell D22: `=D21*0.0815` → `=D21*[YOUR RATE]`

---

### Question 4: What is your service fee/gratuity structure?

**Current setting:** 20% of subtotal

**Options:**
- A) Keep 20%
- B) Different percentage: _____%
- C) Variable by event type (specify below)
- D) Itemized service fees (setup, breakdown, etc.)

**If C, specify:**
- Corporate events: _____%
- Weddings: _____%
- Private parties: _____%

**Your Answer:** _________________

**System Impact:**
- Updates formula in cell D23
- May add dropdown for event type
- May split service fees into line items

---

### Question 5: Do you charge delivery/travel fees?

**Options:**
- A) No delivery fees
- B) Flat fee: $______
- C) Distance-based (specify rates below)
- D) Time-based (hourly rate)

**If C, specify:**
- 0-10 miles: $______
- 10-20 miles: $______
- 20-30 miles: $______
- 30+ miles: $______ per additional mile

**Your Answer:** _________________

**System Impact:**
- Adds delivery fee line item
- May add distance calculator
- May link to Google Maps API

---

### Question 6: What are your deposit and payment terms?

**Current structure:**
- Booking: 25% deposit
- 14 days before: 50% payment
- Day of event: Final 25% + additions

**Your structure:**
- Booking: _____%
- ____ days before: _____%
- Day of event: _____%

**Your Answer:** _________________

**System Impact:**
- Creates payment schedule sheet
- Adds deposit calculator
- May generate payment reminders

---

### Question 7: Do you charge setup/breakdown fees separately?

**Options:**
- A) No, included in service fee
- B) Yes, flat fee: $______
- C) Yes, hourly rate: $______ per hour
- D) Depends on event complexity

**Your Answer:** _________________

**System Impact:**
- Adds setup/breakdown line items
- May add time estimator
- Updates service fee calculations

---

### Question 8: Do you require event insurance or security deposits?

**Options:**
- A) No requirements
- B) Insurance required (minimum coverage: $______)
- C) Security deposit required (amount: $______)
- D) Both insurance and deposit

**Your Answer:** _________________

**System Impact:**
- Adds insurance/deposit tracking
- Creates contract addendum
- Adds to invoice notes

---

## 🍽️ **SECTION 2: MENU & OFFERINGS**

### Question 9: Which menu items are seasonal only?

**List items that are only available certain times of year:**

| Item Name | Available Months |
|-----------|------------------|
| _________ | ________________ |
| _________ | ________________ |
| _________ | ________________ |

**System Impact:**
- Adds seasonal indicator to price lookup table
- Creates availability calendar
- Adds validation to prevent off-season booking

---

### Question 10: Which items require special equipment?

**List items and required equipment:**

| Item Name | Equipment Needed | Available (Y/N)? |
|-----------|------------------|------------------|
| _________ | ________________ | ________________ |
| _________ | ________________ | ________________ |
| _________ | ________________ | ________________ |

**System Impact:**
- Adds equipment column to kitchen sheet
- Creates equipment checklist
- Flags equipment conflicts

---

### Question 11: Do you have minimum order quantities for certain items?

**Options:**
- A) No minimums
- B) Yes, minimums for some items (list below)

**If B, list items and minimums:**

| Item Name | Minimum Quantity | Reason |
|-----------|------------------|--------|
| _________ | ________________ | ______ |
| _________ | ________________ | ______ |

**Your Answer:** _________________

**System Impact:**
- Adds validation to quantity column
- Shows alert if below minimum
- Suggests alternatives

---

### Question 12: Which items can't be made in advance?

**List items that must be prepared day-of:**

| Item Name | Lead Time | Reason |
|-----------|-----------|--------|
| _________ | _________ | ______ |
| _________ | _________ | ______ |

**System Impact:**
- Marks items in kitchen sheet
- Adjusts production schedule
- Flags timing conflicts

---

### Question 13: Do you offer dietary accommodations?

**Check all that apply:**
- [ ] Vegetarian
- [ ] Vegan
- [ ] Gluten-free
- [ ] Dairy-free
- [ ] Nut-free
- [ ] Halal
- [ ] Kosher
- [ ] Other: ______________

**Surcharge for modifications?**
- A) No surcharge
- B) Percentage: _____%
- C) Flat fee: $______

**Your Answer:** _________________

**System Impact:**
- Adds dietary options dropdown
- Creates modification tracking
- Adjusts pricing if applicable

---

### Question 14: Are there items that pair well or poorly together?

**Good pairings (suggest these combinations):**
- _________ + _________ = Great combo!
- _________ + _________ = Popular choice!

**Bad pairings (warn against these):**
- _________ + _________ = Don't recommend (reason: ______)
- _________ + _________ = Avoid (reason: ______)

**System Impact:**
- Adds pairing suggestions to invoice
- Warns of poor combinations
- Creates "frequently bought together" section

---

## 👨‍🍳 **SECTION 3: KITCHEN WORKFLOW**

### Question 15: How many staff typically work your events?

**By event size:**
- Small (20-50 guests): ____ staff
- Medium (50-100 guests): ____ staff
- Large (100-200 guests): ____ staff
- Extra large (200+ guests): ____ staff

**Your Answer:** _________________

**System Impact:**
- Creates staffing calculator
- Estimates labor costs
- Generates staff schedule

---

### Question 16: What is your kitchen capacity for simultaneous prep?

**Options:**
- A) Can prep multiple events same day
- B) One event at a time only
- C) Up to ____ events per day
- D) Depends on event size/complexity

**Specify constraints:**
- Oven capacity: ____ items simultaneously
- Cooktop burners: ____
- Refrigeration: ____ cubic feet
- Freezer: ____ cubic feet

**Your Answer:** _________________

**System Impact:**
- Creates capacity planning tool
- Prevents overbooking
- Optimizes prep schedules

---

### Question 17: Do you prep on-site or off-site?

**Options:**
- A) Always off-site (commercial kitchen)
- B) Always on-site at venue
- C) Depends on event (specify criteria)
- D) Combination of both

**If C, when do you prep on-site vs off-site?**
_________________________________

**System Impact:**
- Adjusts equipment requirements
- Updates logistics planning
- Modifies kitchen sheet

---

### Question 18: What is your maximum batch size per recipe?

**For key recipes:**
- Braised items: ____ lbs at once
- Sauces: ____ quarts at once
- Baked goods: ____ pans at once
- Fried items: ____ lbs per batch

**Your Answer:** _________________

**System Impact:**
- Adds batch warnings to kitchen sheet
- Calculates number of batches needed
- Adjusts timing estimates

---

### Question 19: Do you have cold storage limitations?

**Specify:**
- Walk-in cooler capacity: ____ cubic feet
- Reach-in fridge capacity: ____ cubic feet
- Freezer capacity: ____ cubic feet
- Maximum storage time for preps: ____ days

**Your Answer:** _________________

**System Impact:**
- Creates storage capacity calculator
- Warns of space conflicts
- Optimizes prep timing to avoid storage issues

---

## 🛒 **SECTION 4: VENDOR & ORDERING**

### Question 20: Who are your preferred vendors by category?

**Fill in your primary vendors:**

| Category | Vendor Name | Account # | Contact | Order Method |
|----------|-------------|-----------|---------|--------------|
| Proteins | ___________ | _________ | _______ | ____________ |
| Produce | ___________ | _________ | _______ | ____________ |
| Dairy | ___________ | _________ | _______ | ____________ |
| Dry Goods | ___________ | _________ | _______ | ____________ |
| Beverages | ___________ | _________ | _______ | ____________ |
| Specialty | ___________ | _________ | _______ | ____________ |

**System Impact:**
- Updates order guide
- Creates vendor contact sheet
- Generates automated orders

---

### Question 21: Do you have negotiated pricing agreements?

**List contracts:**

| Vendor | Contract Type | Discount/Terms | Expiration |
|--------|---------------|----------------|------------|
| ______ | _____________ | ______________ | __________ |
| ______ | _____________ | ______________ | __________ |

**System Impact:**
- Tracks contract pricing
- Alerts before expiration
- Calculates cost savings

---

### Question 22: What are vendor minimum order amounts?

**List minimums:**

| Vendor | Minimum Order | Delivery Fee if Under |
|--------|---------------|----------------------|
| ______ | $__________ | $___________________ |
| ______ | $__________ | $___________________ |

**System Impact:**
- Warns if order below minimum
- Suggests combining orders
- Calculates delivery fees

---

### Question 23: What are typical delivery windows?

**For each vendor:**

| Vendor | Order By | Delivery Day/Time | Lead Time |
|--------|----------|-------------------|-----------|
| ______ | ________ | _________________ | _________ |
| ______ | ________ | _________________ | _________ |

**System Impact:**
- Creates order deadline tracker
- Sends ordering reminders
- Flags late orders

---

### Question 24: Who are your backup vendors?

**For each category, list backup:**

| Category | Primary Vendor | Backup Vendor | When to Use Backup |
|----------|----------------|---------------|-------------------|
| ________ | ______________ | _____________ | _________________ |
| ________ | ______________ | _____________ | _________________ |

**System Impact:**
- Creates vendor failover plan
- Tracks primary availability
- Speeds up backup ordering

---

## 🎉 **SECTION 5: EVENT EXECUTION**

### Question 25: Do you offer staffing services?

**Check all that apply:**
- [ ] Servers (rate: $____/hour, minimum: ____ hours)
- [ ] Bartenders (rate: $____/hour, minimum: ____ hours)
- [ ] Chef on-site (rate: $____/hour, minimum: ____ hours)
- [ ] Event coordinator (rate: $____/hour, minimum: ____ hours)
- [ ] Setup crew (rate: $____/hour, minimum: ____ hours)
- [ ] Breakdown crew (rate: $____/hour, minimum: ____ hours)

**Your Answer:** _________________

**System Impact:**
- Adds staffing options to invoice
- Creates staff scheduling tool
- Calculates labor costs

---

### Question 26: Do you provide rentals?

**Check all that apply:**
- [ ] Tables ($ per table: _____)
- [ ] Chairs ($ per chair: _____)
- [ ] Linens ($ per piece: _____)
- [ ] Dishes/Flatware ($ per setting: _____)
- [ ] Glassware ($ per piece: _____)
- [ ] Serving equipment ($ per piece: _____)
- [ ] Other: ____________ ($ per: _____)

**Your Answer:** _________________

**System Impact:**
- Adds rental section to invoice
- Creates rental inventory tracker
- Calculates rental fees

---

### Question 27: What is your service area?

**Delivery/service radius:**
- Primary service area: ____ miles from kitchen
- Extended service area: ____ miles (may include travel fee)
- Will not travel beyond: ____ miles

**Exceptions?**
- [ ] Will travel farther for large events (> ____ guests)
- [ ] Will travel farther for minimum spend (> $______)

**Your Answer:** _________________

**System Impact:**
- Adds address validation
- Calculates travel distance
- Applies travel fees if needed

---

### Question 28: Do you offer setup/breakdown services?

**What's included in standard service:**
- [ ] Table setup
- [ ] Food station setup
- [ ] Buffet arrangement
- [ ] Bar setup
- [ ] Breakdown and cleanup
- [ ] Leftover packaging
- [ ] Other: ______________

**Additional services available (separate charge):**
- [ ] Decorations (specify: _______)
- [ ] Centerpieces (specify: _______)
- [ ] Signage (specify: _______)
- [ ] Other: ______________

**Your Answer:** _________________

**System Impact:**
- Defines service inclusions
- Creates setup checklist
- Itemizes additional services

---

### Question 29: Do you handle decorations/ambiance?

**Options:**
- A) No, client handles all decor
- B) Yes, we offer decor services (pricing below)
- C) We partner with decorator (contact: _______)
- D) We provide basic decor (included/additional charge)

**If B, specify services:**
- Centerpieces: $______ each
- Table runners/linens: $______ per table
- Lighting: $______ (describe: _______)
- Other: ______________

**Your Answer:** _________________

**System Impact:**
- Adds decor options to invoice
- Creates partnership referrals
- Includes decor in execution plan

---

### Question 30: What are your cancellation and refund policies?

**Specify policies:**
- More than ____ days before: ____% refund
- ____ to ____ days before: ____% refund
- Less than ____ days before: ____% refund
- Day of event: No refund

**Rescheduling policy:**
- Fee to reschedule: $______ (or ____ %)
- Must reschedule by: ____ days before

**Weather/emergency cancellations:**
- Force majeure policy: _________________

**Your Answer:** _________________

**System Impact:**
- Adds policies to contract
- Creates cancellation calculator
- Tracks rescheduled events

---

## 🔧 **SECTION 6: SYSTEM PREFERENCES**

### Question 31: Do you want automated email reminders?

**Options:**
- A) Yes, send reminders at key milestones
- B) No, I'll track manually
- C) Only for specific events (criteria: ______)

**If A, when should reminders go out?**
- [ ] ____ days before: "Finalize headcount"
- [ ] ____ days before: "Menu confirmation needed"
- [ ] ____ days before: "Payment due"
- [ ] ____ day before: "Event tomorrow - final details"

**Your Answer:** _________________

**System Impact:**
- Sets up automated reminders
- Creates email templates
- Tracks sent reminders

---

### Question 32: How do you want to handle client changes after booking?

**Policy:**
- Headcount changes allowed until: ____ days before
- Menu changes allowed until: ____ days before
- Change fee: $______ (or ____ % of change amount)
- Major changes (> ____ % of original) require: ___________

**Your Answer:** _________________

**System Impact:**
- Adds change policy to contract
- Creates change order tracking
- Calculates change fees

---

### Question 33: Do you want to track food costs per event?

**Options:**
- A) Yes, track actual ingredient costs
- B) Yes, track estimated costs only
- C) No, just focus on revenue

**If A or B:**
- Update costs: After every event / Monthly / Quarterly
- Compare to: Budget / Historical average / Industry standard

**Your Answer:** _________________

**System Impact:**
- Creates cost tracking sheet
- Calculates profit margins
- Generates cost reports

---

### Question 34: Do you want to track client feedback?

**Options:**
- A) Yes, send survey after every event
- B) Yes, track informal feedback only
- C) No formal tracking

**If A:**
- Survey platform: ______________
- Questions to include: ______________
- How to use feedback: ______________

**Your Answer:** _________________

**System Impact:**
- Creates survey templates
- Tracks satisfaction scores
- Generates feedback reports

---

### Question 35: What reports do you want the system to generate?

**Check all that apply:**
- [ ] Weekly event summary
- [ ] Monthly revenue report
- [ ] Food cost analysis
- [ ] Labor efficiency report
- [ ] Customer satisfaction trends
- [ ] Most/least popular menu items
- [ ] Vendor spending analysis
- [ ] Profitability by event type
- [ ] Other: ______________

**Your Answer:** _________________

**System Impact:**
- Creates custom reports
- Schedules automatic generation
- Sets up dashboards

---

## ✅ **NEXT STEPS**

After completing this questionnaire:

1. **Review your answers** - Ensure all information is accurate
2. **Prioritize customizations** - Which features are most important?
3. **Schedule implementation** - What's the timeline?
4. **Test the system** - Run through a sample event
5. **Train your team** - Everyone understands new features
6. **Go live!** - Start using for real events

---

## 📝 **CUSTOMIZATION WORKSHEET**

Use this space to note specific customizations needed:

**High Priority (Must Have):**
1. _________________________________
2. _________________________________
3. _________________________________

**Medium Priority (Nice to Have):**
1. _________________________________
2. _________________________________
3. _________________________________

**Low Priority (Future Enhancement):**
1. _________________________________
2. _________________________________
3. _________________________________

**Questions/Concerns:**
_________________________________
_________________________________
_________________________________

---

**Document Version:** 1.0  
**Last Updated:** November 19, 2025  
**Your Business:** ________________  
**Completed By:** ________________  
**Date Completed:** ________________  

---

## 🎯 **REMEMBER:**

This is YOUR system. Customize it to fit YOUR workflow, not the other way around!

Every business is unique - don't be afraid to make it your own.

**Questions? Need help implementing?** Reference the PROJECT_RULES.md file or contact your system administrator.
