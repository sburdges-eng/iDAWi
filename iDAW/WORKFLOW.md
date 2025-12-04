# LARIAT BANQUET SYSTEM - WORKFLOW DOCUMENTATION
**Complete Step-by-Step Process Guide**

---

## 🎯 **OVERVIEW**

This document outlines the complete workflow for managing banquet events from initial booking through final execution. Each step is designed to build upon the previous one, ensuring no detail is missed and all systems stay synchronized.

**Total Timeline:** Typically 7-14 days from booking to event  
**Key Personnel:** Event Coordinator, Kitchen Manager, Prep Staff, Service Staff  
**Critical Documents:** Invoice, Kitchen Sheet, Production Schedule, Execution Plan

---

## 📊 **WORKFLOW DIAGRAM**

```
┌─────────────────────────────────────────────────────────────────┐
│                        LARIAT BANQUET WORKFLOW                   │
└─────────────────────────────────────────────────────────────────┘

STEP 1: EVENT BOOKING
   ↓ (Client consultation)
STEP 2: CREATE INVOICE
   ↓ (Using template)
STEP 3: CLIENT APPROVAL
   ↓ (Contract signed, deposit received)
STEP 4: GENERATE KITCHEN SHEET
   ↓ (Auto-populated from invoice)
STEP 5: CALCULATE INGREDIENTS
   ↓ (Recipe scaling)
STEP 6: CREATE PRODUCTION SCHEDULE
   ↓ (Timeline planning)
STEP 7: ORDER INGREDIENTS
   ↓ (Vendor placement)
STEP 8: RECEIVE & INVENTORY
   ↓ (Check-in & storage)
STEP 9: PREP & PRODUCTION
   ↓ (Following schedule)
STEP 10: EVENT EXECUTION
   ↓ (Service & delivery)
COMPLETED ✅
```

---

## 📝 **DETAILED WORKFLOW STEPS**

---

### **STEP 1: EVENT BOOKING** 📅

**Objective:** Gather all essential event information from the client

**Duration:** 30-60 minutes (initial consultation)

**Responsible:** Event Coordinator / Sales

**Tasks:**
1. **Initial Client Contact**
   - Receive inquiry (phone, email, website form)
   - Schedule consultation call/meeting
   - Send company information packet

2. **Client Consultation**
   - Discuss event details:
     * Date and time
     * Location (venue address, kitchen access)
     * Guest count (estimated and final deadline)
     * Event type (wedding, corporate, private party)
     * Budget range
     * Dietary restrictions/preferences
     * Service style (buffet, plated, passed apps, etc.)
   
3. **Menu Discussion**
   - Review available menu options
   - Discuss seasonal availability
   - Explain pricing structure
   - Suggest pairings and popular combinations
   - Note any special requests

4. **Quote Preparation**
   - Calculate preliminary pricing
   - Check date availability
   - Review minimum spend requirements
   - Discuss deposit and payment terms

**Outputs:**
- [ ] Client information collected
- [ ] Event details documented
- [ ] Preliminary menu selected
- [ ] Date reserved (pending deposit)
- [ ] Follow-up scheduled

**Handoff to Step 2:** Client details and menu selections documented

---

### **STEP 2: CREATE INVOICE** 📄

**Objective:** Generate formal invoice with accurate pricing and calculations

**Duration:** 15-30 minutes

**Responsible:** Event Coordinator / Office Manager

**Tasks:**
1. **Open Invoice Template**
   - File → Copy `Invoice_Template.xlsx`
   - Rename: `Invoice_[ClientName]_[EventDate]_v1.xlsx`
   - Save in `ACTIVE_EVENTS/[ClientName]/` folder

2. **Enter Client Information**
   - Client name (Header)
   - Event date and time (Header)
   - Guest count (Header)
   - Event type (Header)
   - Contact information (Header)
   - Special notes/requests (Header)

3. **Enter Menu Items**
   - List each item in Column A
   - Verify VLOOKUP populates correct prices in Column B
   - Enter quantities in Column C
   - Check totals calculate in Column D
   - Add notes in Column E (dietary, timing, etc.)

4. **Verify Calculations**
   - Check Subtotal (D21)
   - Verify Tax (D22) = 8.15%
   - Verify Service Fee (D23) = 20%
   - Check Total (D24)
   - Enter Minimum Spend (E32)
   - Check Over/Under (E33)

5. **Add Additional Items** (if applicable)
   - Bar spend
   - Booking fee
   - Delivery fee
   - Rental fees
   - Setup/breakdown charges
   - Special equipment fees

6. **Quality Check**
   - No #N/A errors (item names match price list exactly)
   - All formulas calculating correctly
   - All client information complete
   - Notes captured accurately
   - File saved with proper naming

**Outputs:**
- [ ] Complete invoice generated
- [ ] All calculations verified
- [ ] File properly named and saved
- [ ] Ready to send to client

**Handoff to Step 3:** Invoice file ready for client review

---

### **STEP 3: CLIENT APPROVAL** ✅

**Objective:** Obtain client approval, signed contract, and deposit

**Duration:** 1-3 days (client review time)

**Responsible:** Event Coordinator

**Tasks:**
1. **Send Invoice to Client**
   - Export invoice as PDF
   - Email to client with:
     * Invoice attached
     * Payment instructions
     * Deposit amount and deadline
     * Contract terms
     * Cancellation policy
     * Contact information
   - Set follow-up reminder (24-48 hours)

2. **Answer Client Questions**
   - Clarify menu items
   - Explain pricing breakdown
   - Discuss substitutions
   - Address concerns
   - Modify invoice if needed (save as v2, v3, etc.)

3. **Finalize Agreement**
   - Receive signed contract
   - Process deposit payment
   - Confirm final guest count (or set deadline)
   - Verify event date/time
   - Confirm venue details
   - Get final dietary restrictions

4. **Update Calendar**
   - Block event date
   - Add to production calendar
   - Schedule staff (if needed)
   - Reserve equipment

**Outputs:**
- [ ] Signed contract received
- [ ] Deposit processed
- [ ] Event confirmed on calendar
- [ ] Final invoice approved (or changes documented)
- [ ] Client communication preferences noted

**Handoff to Step 4:** Approved invoice with finalized menu

---

### **STEP 4: GENERATE KITCHEN SHEET** 🍳

**Objective:** Translate invoice into actionable kitchen prep tasks

**Duration:** 30-45 minutes

**Responsible:** Kitchen Manager / Head Chef

**Tasks:**
1. **Open Kitchen Sheet** (Sheet 2 of Invoice file)
   - Item names and quantities auto-populate from Invoice Sheet
   - Verify all items copied correctly
   - Check for any special instructions from invoice notes

2. **Assign Prep Days** (Column C)
   - Review each item
   - Determine prep timeline based on:
     * Item type (braise vs fresh assembly)
     * Holding capacity
     * Kitchen capacity
     * Event date
   - Assign to:
     * Thursday: Long-braise items, stocks, bases, sauces
     * Friday: Final prep, assembly, fresh items
     * Saturday (day-of): Service prep, plating

3. **Detail Pre-Prep Tasks** (Column D)
   - Reference Recipe Book for each item
   - List specific prep requirements:
     * "Braise pork shoulder - 4 hours"
     * "Slice avocados, prepare batter"
     * "Cook noodles, make cheese sauce"
     * "Roast peppers, make salsa"
   - Note equipment needed
   - Flag any dependencies

4. **Add Plating Instructions** (Column E)
   - Describe final assembly
   - Note presentation requirements
   - List garnishes needed
   - Specify serving vessels
   - Reference photos if available

5. **Set Service Times** (Column F)
   - Calculate when each item must be ready
   - Work backwards from service time
   - Account for:
     * Travel time (if off-site)
     * Final plating time
     * Holding time
     * Buffer for delays
   - Use time format (HH:MM)

6. **Add Critical Notes** (Column G)
   - Flag special orders: "Order extra avocados"
   - Equipment needs: "Need slider buns"
   - Vendor specifics: "Order from Sysco"
   - Timing concerns: "Must be served hot"
   - Quality checks: "Taste for seasoning"

7. **Review for Conflicts**
   - Check for oven/stove conflicts
   - Verify cold storage capacity
   - Confirm equipment availability
   - Check staff capacity
   - Adjust timing if needed

**Outputs:**
- [ ] Complete kitchen sheet with all items
- [ ] Prep days assigned
- [ ] Pre-prep tasks detailed
- [ ] Plating instructions clear
- [ ] Service times calculated
- [ ] Special notes captured
- [ ] Conflicts resolved

**Handoff to Step 5:** Kitchen sheet ready for ingredient calculation

---

### **STEP 5: CALCULATE INGREDIENTS** 📊

**Objective:** Determine exact quantities of all ingredients needed

**Duration:** 1-2 hours

**Responsible:** Kitchen Manager / Sous Chef

**Tasks:**
1. **List All Menu Items**
   - Extract from Kitchen Sheet Column A
   - Group similar items together
   - Note quantities from Column B

2. **Find Recipes**
   - Open Lariat_Recipe_Book.docx
   - Locate recipe for each menu item
   - Note original yield of recipe

3. **Scale Recipes**
   - For each recipe:
     * Original yield: _____ servings
     * Needed quantity: _____ servings
     * Scale factor = Needed ÷ Original
   
   **Example:**
   ```
   Buttermilk Brine Recipe
   Original: Makes 12 qt (yields 12 qt of brined chicken)
   Event needs: 80 pieces of chicken
   
   Scale: 80 ÷ 12 = 6.67x
   
   Scaled ingredients:
   - Buttermilk: 0.5 gal × 6.67 = 3.34 gal → Round to 4 gallons
   - Hot Sauce: 500g × 6.67 = 3,335g → Round to 3.5 kg
   - Garlic Powder: 1/4 cup × 6.67 = 1.67 cups
   ```

4. **Create Ingredient Master List**
   - Compile all ingredients across all recipes
   - Combine quantities for same ingredients
   - Example format:
   
   | Ingredient | Total Needed | Unit | Notes |
   |------------|--------------|------|-------|
   | Buttermilk | 4 gal | gallon | For brine |
   | Hot Sauce | 3.5 kg | kg | Frank's brand |
   | Onions (yellow) | 15 | each | Large |
   | Garlic (minced) | 2 cups | cup | Fresh |

5. **Add Buffer**
   - Add 10% to raw ingredients (accounts for waste, trim, mistakes)
   - Example: Need 10 onions → Order 11 onions
   - Don't add buffer to:
     * Expensive proteins (order exact amount)
     * Pre-portioned items
     * Shelf-stable goods with long shelf life

6. **Check Inventory**
   - Cross-reference with current stock
   - Subtract on-hand quantities
   - Mark items that need to be ordered

7. **Organize by Vendor**
   - Sort ingredients by vendor/supplier
   - Reference LARIAT_ORDER_GUIDE_OFFICIAL.xlsx
   - Create separate lists for:
     * Shamrock (primary distributor)
     * Sysco (specialty items)
     * US Foods (backup)
     * Local stores (last-minute/specialty)

**Outputs:**
- [ ] Master ingredient list created
- [ ] All recipes scaled correctly
- [ ] Quantities calculated with buffer
- [ ] Inventory checked and subtracted
- [ ] Ingredients organized by vendor
- [ ] Order lists prepared

**Handoff to Step 6:** Ingredient lists ready for production schedule creation

---

### **STEP 6: CREATE PRODUCTION SCHEDULE** ⏰

**Objective:** Build detailed timeline for all prep and production tasks

**Duration:** 30-60 minutes

**Responsible:** Kitchen Manager

**Tasks:**
1. **Determine Event Timeline**
   - Event date and start time
   - Setup time (if applicable)
   - Service start time
   - Expected end time
   - Breakdown time

2. **Work Backwards from Service Time**
   - When must food be ready?
   - Subtract travel time (if off-site)
   - Subtract final plating time
   - This = "Kitchen Complete" time

3. **Map All Prep Tasks**
   - From Kitchen Sheet, list all pre-prep tasks
   - Assign to specific days (Thursday, Friday, Saturday)
   - Estimate time for each task

4. **Create Day-by-Day Schedule**

   **Thursday (T-3 Days)**
   | Time | Task | Staff | Notes |
   |------|------|-------|-------|
   | 8:00 AM | Receive ingredient delivery | 1 | Check against order |
   | 8:30 AM | Start pork shoulder braise | 2 | 4-hour cook time |
   | 9:00 AM | Prep green chile | 2 | Can hold 5 days |
   | 12:00 PM | Make sauces (aioli, salsa) | 1 | Refrigerate |
   | 2:00 PM | Check braises, adjust seasoning | 1 | - |
   | 4:00 PM | Cool and store all items | 1 | Label with date |
   
   **Friday (T-2 Days)**
   | Time | Task | Staff | Notes |
   |------|------|-------|-------|
   | 8:00 AM | Receive fresh produce | 1 | Check quality |
   | 8:30 AM | Prep vegetables (slice, dice) | 2 | Keep refrigerated |
   | 10:00 AM | Make cold items (coleslaw, salads) | 2 | - |
   | 11:00 AM | Portion proteins | 1 | Wrap individually |
   | 12:00 PM | Bake cornbread | 1 | Cool and wrap |
   | 2:00 PM | Prep batter/breading stations | 1 | Cover and refrigerate |
   | 3:00 PM | Final inventory check | 1 | Note any missing items |
   
   **Saturday (Event Day)**
   | Time | Task | Staff | Notes |
   |------|------|-------|-------|
   | 6:00 AM | Arrive, equipment check | 2 | Heat ovens |
   | 6:30 AM | Reheat braised items | 1 | Low and slow |
   | 7:00 AM | Prep fresh items (avo, lettuce) | 2 | Last-minute only |
   | 8:00 AM | Begin frying/final cooking | 2 | Maintain temp |
   | 9:00 AM | Plate/pack buffet items | 3 | Hot boxes ready |
   | 10:00 AM | Load vehicles | 2 | Check list |
   | 10:30 AM | Depart for venue | - | Travel time |
   | 11:00 AM | Arrive, setup | All | Buffet arrangement |
   | 12:00 PM | Service begins | - | - |

5. **Add Checkpoints**
   - Key milestones where manager reviews progress
   - Quality checks for taste, temperature, appearance
   - Go/no-go decisions

6. **Assign Staff**
   - Match tasks to staff skill levels
   - Balance workload
   - Account for breaks
   - Add backup staff if needed

7. **Build in Buffers**
   - Add 15-20% time buffer for each major task
   - Allow for equipment delays
   - Plan for traffic/travel delays
   - Have backup plans for common issues

**Outputs:**
- [ ] Complete production schedule created
- [ ] All tasks assigned to specific days/times
- [ ] Staff assignments made
- [ ] Equipment needs identified
- [ ] Checkpoints established
- [ ] Buffers built in
- [ ] Schedule printed and posted

**Handoff to Step 7:** Production schedule finalized, ready to order ingredients

---

### **STEP 7: ORDER INGREDIENTS** 🛒

**Objective:** Place orders with all vendors to ensure timely delivery

**Duration:** 1-2 hours (spread across multiple days)

**Responsible:** Kitchen Manager / Purchasing

**Tasks:**
1. **Review Final Ingredient Lists**
   - Confirm quantities from Step 5
   - Check production schedule for timing
   - Verify nothing missing

2. **Check Vendor Availability**
   - Call/email primary vendors
   - Confirm items in stock
   - Check delivery windows
   - Verify pricing (if changed since last order)

3. **Place Orders** (In Priority Order)

   **Thursday Delivery (T-3 Days):**
   - **Shamrock Order** (Primary distributor)
     * Proteins (pork shoulder, beef, chicken)
     * Some produce (onions, peppers - long shelf life)
     * Dry goods
     * Call by: Tuesday 2PM
     * Confirm: Tuesday 4PM
   
   - **Sysco Order** (Specialty items)
     * Specialty proteins
     * Unique ingredients
     * Frozen items
     * Call by: Tuesday 3PM
     * Confirm: Tuesday 5PM

   **Friday Delivery (T-2 Days):**
   - **Shamrock Order** (Fresh produce)
     * Lettuce, herbs, fresh vegetables
     * Dairy (milk, cream, butter)
     * Call by: Thursday 12PM
     * Confirm: Thursday 3PM
   
   **Saturday Morning (If needed):**
   - **Local Stores** (King Soopers, Costco)
     * Last-minute items only
     * Emergency replacements
     * Send runner: 7AM

4. **Confirm Each Order**
   - Receive order confirmation number
   - Verify delivery date/time
   - Note delivery address
   - Check for minimum order amounts
   - Calculate delivery fees
   - Record in order tracking spreadsheet

5. **Set Reminders**
   - Day before delivery: Call to reconfirm
   - Morning of delivery: Check estimated arrival
   - Alert receiving staff of timing

6. **Document Everything**
   - Save order confirmations
   - Print receiving sheets
   - Note any substitutions approved
   - Track order numbers

**Outputs:**
- [ ] All orders placed with vendors
- [ ] Order confirmation numbers received
- [ ] Delivery schedules confirmed
- [ ] Receiving sheets printed
- [ ] Staff alerted to delivery times
- [ ] Order tracking updated

**Handoff to Step 8:** Orders placed, ready for receiving

---

### **STEP 8: RECEIVE & INVENTORY** 📦

**Objective:** Receive deliveries, verify accuracy, and store properly

**Duration:** 1-2 hours per delivery

**Responsible:** Receiving Staff / Kitchen Manager

**Tasks:**
1. **Prepare for Delivery**
   - Print receiving sheet (lists all ordered items)
   - Clear receiving area
   - Prepare storage areas
   - Have scale, thermometer, and checklist ready

2. **Receive Delivery** (For Each Vendor)
   
   **Initial Check:**
   - Count boxes/cases
   - Check for damage
   - Verify truck temperature (if refrigerated)
   - Note delivery time

   **Detailed Inspection:**
   For each item:
   - [ ] Verify quantity matches order
   - [ ] Check quality (no damage, discoloration)
   - [ ] Check temperature (proteins <40°F, frozen <0°F)
   - [ ] Verify expiration dates (must be after event date)
   - [ ] Check for substitutions (accept or reject)
   - [ ] Weigh items if sold by weight
   - [ ] Note any discrepancies

3. **Handle Discrepancies**
   - **Missing items:**
     * Note on receiving sheet
     * Contact vendor immediately
     * Request credit or replacement
     * Source from backup vendor if critical
   
   - **Wrong items:**
     * Accept if suitable substitute
     * Reject if not usable
     * Request credit
   
   - **Quality issues:**
     * Reject damaged/spoiled items
     * Take photos for documentation
     * Request replacement or credit
     * Don't accept if compromises food safety

4. **Sign Delivery Receipt**
   - Note any issues on driver's receipt
   - Keep copy for records
   - Get driver's name and contact

5. **Store Immediately**
   
   **Storage Guidelines:**
   - **Refrigerated (34-40°F):**
     * Proteins (bottom shelf, in containers)
     * Dairy
     * Fresh produce
     * Prepared items
   
   - **Frozen (0°F or below):**
     * Frozen proteins
     * Frozen vegetables
     * Ice cream/frozen desserts
   
   - **Dry Storage (50-70°F, low humidity):**
     * Dry goods (flour, sugar, rice)
     * Canned goods
     * Oils and vinegars
     * Spices
   
   - **Room Temperature (if specified):**
     * Tomatoes (for ripening)
     * Onions
     * Potatoes
     * Bread

6. **Label Everything**
   - Item name
   - Delivery date
   - Use-by date
   - Event name (if dedicated)
   - Storage location

7. **Update Inventory**
   - Record received quantities
   - Note any issues
   - Update cost tracking (if applicable)
   - Mark items received in order tracking

8. **Final Verification**
   - Cross-check against ingredient list
   - Flag any critical missing items
   - Calculate if you have enough of everything
   - Determine if additional shopping needed

**Outputs:**
- [ ] All deliveries received and inspected
- [ ] Items stored properly
- [ ] Inventory updated
- [ ] Discrepancies documented
- [ ] Vendor credits requested
- [ ] Missing items sourced from backups
- [ ] Ready for production

**Handoff to Step 9:** All ingredients received, verified, and stored properly

---

### **STEP 9: PREP & PRODUCTION** 👨‍🍳

**Objective:** Execute all prep and cooking following production schedule

**Duration:** 3 days (Thursday through Saturday)

**Responsible:** Kitchen Team (Chef, Sous Chef, Prep Cooks)

**Tasks:**

**GENERAL PROTOCOL FOR ALL DAYS:**
1. **Start of Shift**
   - Review production schedule
   - Check task assignments
   - Gather equipment needed
   - Review recipe cards
   - Set up mise en place stations

2. **Throughout Shift**
   - Follow schedule timing strictly
   - Check tasks off as completed
   - Note any issues immediately
   - Maintain clean work area
   - Label and date all items
   - Monitor temperatures
   - Taste and adjust seasoning

3. **End of Shift**
   - Clean and sanitize stations
   - Store all prepped items properly
   - Update production schedule (mark completed tasks)
   - Brief next shift on progress
   - Note any concerns for manager

---

**THURSDAY (T-3 Days) - LONG PREP & BRAISING**

| Time Block | Tasks | Key Points |
|------------|-------|------------|
| **8:00 AM** | Shift Start | - Review day's tasks<br>- Equipment check<br>- Receive delivery (if today) |
| **8:30 AM** | Start Braised Items | - Pork shoulder for carnitas<br>- Beef cheeks for barbacoa<br>- Season and sear<br>- Into braise liquid<br>- Into oven at 225°F |
| **10:00 AM** | Prep Bases & Sauces | - Green chile (braise pork, make sauce)<br>- Chicken stock<br>- Blackened salsa<br>- Special sauce<br>- Can hold 3-5 days |
| **12:00 PM** | Check Braises | - Stir and check liquid levels<br>- Adjust seasoning<br>- Add more liquid if needed<br>- Rotate pans |
| **2:00 PM** | Make Dry Rubs | - Lariat rub<br>- Nashville hot rub<br>- QB seasoning<br>- Store in airtight containers |
| **3:00 PM** | Prep Aiolis & Dressings | - Chipotle aioli<br>- Aji verde<br>- Alabama white sauce<br>- Santa Fe Caesar<br>- Tartar sauce<br>- Store refrigerated |
| **4:00 PM** | Final Check on Braises | - Should be fork-tender<br>- Pull from oven<br>- Cool properly<br>- Shred if needed<br>- Store in braising liquid |
| **5:00 PM** | Clean & Store | - All items labeled and dated<br>- Refrigerate properly<br>- Clean all equipment<br>- Update production schedule |

**Critical Quality Checks:**
- [ ] Braises are fork-tender
- [ ] All sauces properly emulsified
- [ ] Everything labeled with date
- [ ] Cold storage temperatures correct
- [ ] All items ready for Friday

---

**FRIDAY (T-2 Days) - FINAL PREP & ASSEMBLY**

| Time Block | Tasks | Key Points |
|------------|-------|------------|
| **8:00 AM** | Shift Start | - Receive fresh produce delivery<br>- Quality check all items<br>- Review Friday tasks |
| **8:30 AM** | Vegetable Prep | - Wash all produce<br>- Dice onions, peppers<br>- Slice for garnish<br>- Store properly (wet vs dry) |
| **10:00 AM** | Protein Portioning | - Portion chicken for frying<br>- Make burger patties<br>- Cut fish fillets<br>- Wrap individually<br>- Refrigerate |
| **11:00 AM** | Make Cold Items | - Coleslaw<br>- Pico de gallo<br>- Tomatillo salsa<br>- Caesar salad components<br>- Cobb dressing |
| **12:00 PM** | Bake Cornbread | - Mix batter (see recipe)<br>- Bake at 500°F for 1.5 hours<br>- Cool completely<br>- Wrap for storage |
| **1:30 PM** | Prep Fry Stations | - Set up breading station<br>- Mix beer batter<br>- Corndog batter<br>- Cover and refrigerate |
| **2:30 PM** | Assemble Components | - Mac balls<br>- Deviled eggs<br>- Caprese skewers<br>- Store refrigerated |
| **3:30 PM** | Final Inventory Check | - Verify all items prepped<br>- Check quantities<br>- Note any missing items<br>- Last chance for emergency shopping |
| **4:30 PM** | Set Up Saturday Stations | - Label hot boxes<br>- Prep serving utensils<br>- Check equipment (fryers, ovens, warmers)<br>- Load non-perishables into vehicle |
| **5:30 PM** | Clean & Review | - Deep clean kitchen<br>- Review Saturday schedule with team<br>- Confirm arrival times<br>- Final briefing |

**Critical Quality Checks:**
- [ ] All proteins portioned and weighed correctly
- [ ] Cold items fresh and properly seasoned
- [ ] Cornbread fully cooked (no residue on toothpick)
- [ ] All items labeled with use-by times
- [ ] Equipment ready for Saturday
- [ ] Team knows Saturday plan

---

**SATURDAY (Event Day) - FINAL COOKING & SERVICE**

| Time Block | Tasks | Key Points |
|------------|-------|------------|
| **6:00 AM** | Arrive & Setup | - Full team arrives<br>- Turn on all equipment<br>- Preheat ovens, fryers<br>- Final equipment check |
| **6:30 AM** | Reheat Braised Items | - Carnitas, barbacoa in low oven (300°F)<br>- Green chile on stovetop (low heat)<br>- Monitor constantly<br>- Stir frequently |
| **7:00 AM** | Prep Fresh Items | - Slice avocados (for battered avo tacos)<br>- Chop fresh herbs<br>- Slice lemons/limes<br>- Wash lettuce<br>- Everything "day-of" fresh |
| **7:30 AM** | Begin Frying Program | - Heat fryers to temp (350-375°F)<br>- Start with corn dogs<br>- Then battered items<br>- Nashville hot chicken<br>- Keep in warmers |
| **8:30 AM** | Cook Slider Patties | - On flat-top grill<br>- Season with Lariat rub<br>- Cook to temp (165°F internal)<br>- Hold hot |
| **9:00 AM** | Assemble Buffet Items | - Green chile mac (combine noodles + sauce)<br>- Rope Caesar (toss salad)<br>- Tacos (warm tortillas, prep toppings)<br>- Everything in serving vessels |
| **9:30 AM** | Plate Passed Apps | - Mini rellenos<br>- Pig wings<br>- Mac balls<br>- Arranged on trays<br>- Garnished |
| **10:00 AM** | Final Quality Check | - Taste everything<br>- Check temperatures<br>- Verify garnishes<br>- Visual appearance check<br>- Manager approval |
| **10:15 AM** | Pack for Transport** | - Hot items in hot boxes<br>- Cold items in coolers<br>- Serving utensils<br>- Setup supplies<br>- Execution checklist |
| **10:30 AM** | Load Vehicles | - Double-check all items loaded<br>- Verify nothing left behind<br>- Secure for transport |
| **10:45 AM** | Depart for Venue | - Travel time (adjust based on distance)<br>- Driver has venue address<br>- Phone fully charged |
| **11:15 AM** | Arrive at Venue | - Unload quickly but carefully<br>- Set up buffet stations<br>- Arrange serving area<br>- Final temp checks |
| **11:45 AM** | Final Touches | - Garnishes on all items<br>- Labels/signage<br>- Utensils in place<br>- Visual check |
| **12:00 PM** | **SERVICE BEGINS** | - Team in position<br>- Smile!<br>- Serve with pride |

**During Service:**
- [ ] Monitor food temperatures
- [ ] Replenish items as needed
- [ ] Maintain buffet appearance
- [ ] Clear empty dishes
- [ ] Respond to client requests
- [ ] Take notes for future events

**After Service:**
- [ ] Pack remaining food (label for client)
- [ ] Clean up service area
- [ ] Load all equipment
- [ ] Final walk-through with client
- [ ] Return to kitchen

**Back at Kitchen:**
- [ ] Unload and clean all equipment
- [ ] Store any reusable items
- [ ] Dispose of waste properly
- [ ] Complete end-of-event checklist
- [ ] Team debrief - what went well/what to improve

**Critical Quality Checks:**
- [ ] All hot food at safe temperatures (>140°F)
- [ ] All cold food at safe temperatures (<40°F)
- [ ] Everything tastes properly seasoned
- [ ] Visual presentation is beautiful
- [ ] Nothing missing from client order
- [ ] Team is professional and friendly

**Outputs:**
- [ ] All food prepared according to recipes
- [ ] Quality standards met
- [ ] Production schedule followed
- [ ] Food safety protocols maintained
- [ ] All items ready for service
- [ ] Team briefed on event details

**Handoff to Step 10:** Food prepared, packed, and ready for event execution

---

### **STEP 10: EVENT EXECUTION** 🎉

**Objective:** Deliver, setup, serve, and execute flawless event

**Duration:** 4-8 hours (varies by event)

**Responsible:** Full Service Team (Chef, Servers, Coordinator)

**Tasks:**

**A. PRE-SERVICE (Arrival to Service Start)**

1. **Arrival & Unloading** (15-30 minutes)
   - Park in designated area
   - Unload systematically:
     * Hot boxes first (maintain temp)
     * Cold items to holding area
     * Equipment and supplies
     * Service ware
   - Team carries items to service area
   - No running, stay professional

2. **Setup Service Area** (30-45 minutes)
   - **Layout buffet/stations according to floor plan:**
     * Proteins first
     * Sides next
     * Salads and cold items
     * Bread/extras
     * Desserts separate
   - **Arrange equipment:**
     * Chafing dishes with fuel
     * Cold holding with ice
     * Serving utensils at each station
     * Plates, napkins, flatware accessible
   - **Visual arrangement:**
     * Height variation (use risers)
     * Color contrast
     * Garnishes and décor
     * Labels/signage

3. **Final Quality Control** (10-15 minutes)
   - Check all food temperatures
     * Hot: >140°F (use thermometer)
     * Cold: <40°F
   - Taste test (chef only)
   - Adjust seasoning if needed
   - Visual inspection
   - Verify quantities sufficient

4. **Team Briefing** (5 minutes)
   - Review service style
   - Assign positions
   - Clarify roles
   - Answer questions
   - Motivational moment

---

**B. DURING SERVICE**

**Service Team Responsibilities:**

1. **Greeter/Host**
   - Welcome guests
   - Explain buffet layout
   - Answer menu questions
   - Direct traffic flow

2. **Buffet Attendants** (2-3 people)
   - Replenish items as needed
   - Maintain appearance
   - Clean spills immediately
   - Monitor food levels
   - Check temperatures regularly
   - Engage with guests politely

3. **Runner**
   - Bring replenishments from kitchen/vehicle
   - Fetch additional supplies
   - Handle special requests
   - Communicate with chef

4. **Chef/Kitchen Manager**
   - Final prep/plating as needed
   - Quality control
   - Temperature monitoring
   - Troubleshoot issues
   - Coordinate with event coordinator

5. **Event Coordinator**
   - Client liaison
   - Timing of service
   - Address concerns
   - Oversee operations
   - Handle payments/tips

**Service Protocols:**
- [ ] Smile and be friendly
- [ ] Answer questions about food
- [ ] Maintain professional appearance
- [ ] Keep buffet clean and organized
- [ ] Refill items BEFORE they run out
- [ ] Never let station look depleted
- [ ] Take photos for portfolio (if allowed)

**Common Issues & Solutions:**

| Issue | Solution |
|-------|----------|
| Item running low | Bring backup from vehicle immediately |
| Item too cold | Reheat in chafing dish, add hot water |
| Item too hot | Let cool slightly, don't serve dangerously hot |
| Spill | Clean immediately, have towels ready |
| Guest allergy | Know ingredients, offer alternatives |
| Special request | Consult with chef, accommodate if possible |
| Equipment failure | Have backup plan (sterno, coolers) |

---

**C. POST-SERVICE (After Event)**

1. **Pack Remaining Food** (15-20 minutes)
   - Separate leftovers for client (if contracted)
   - Pack securely in labeled containers
   - Include reheating instructions
   - Store properly (cold items on ice)

2. **Break Down Service Area** (20-30 minutes)
   - Turn off all equipment
   - Pack chafing dishes (wait until cool)
   - Collect all serving utensils
   - Dispose of trash properly
   - Wipe down surfaces
   - Leave area cleaner than you found it

3. **Load Vehicle** (15 minutes)
   - Systematic packing
   - Secure all items
   - Don't leave anything behind
   - Final walk-through of area

4. **Client Final Check-in** (5-10 minutes)
   - Ask how event went
   - Address any concerns
   - Hand over leftovers
   - Collect final payment (if due)
   - Thank client
   - Request feedback/review

5. **Return to Kitchen** (Travel time)

6. **Unload & Clean** (30-45 minutes)
   - Unload all equipment
   - Wash all items immediately
   - Sanitize properly
   - Store equipment
   - Dispose of waste
   - Clean vehicle interior

7. **End-of-Event Wrap-Up** (15 minutes)
   - Team debrief
   - Note what went well
   - Note areas for improvement
   - Update client file
   - Complete paperwork
   - Schedule any follow-ups

8. **Post-Event Documentation** (Next business day)
   - Send thank-you email to client
   - Request online review
   - File all paperwork
   - Update food cost tracking
   - Update inventory
   - Archive event file
   - Note lessons learned

**Outputs:**
- [ ] Event executed successfully
- [ ] Client satisfied
- [ ] All equipment returned and cleaned
- [ ] Final payment received
- [ ] Documentation complete
- [ ] Lessons learned captured
- [ ] Ready for next event

---

## 🔄 **POST-EVENT CONTINUOUS IMPROVEMENT**

After every event, conduct a brief team debrief:

**What Went Well:**
- Celebrate successes
- Note things to repeat
- Recognize team members

**What Needs Improvement:**
- Identify issues (no blame)
- Discuss solutions
- Update procedures if needed

**Action Items:**
- Recipe adjustments?
- Equipment needs?
- Timing changes?
- Training needed?
- Update templates?

**Update Project Rules:**
- Incorporate learnings
- Refine estimates
- Adjust templates
- Share with team

---

## ✅ **WORKFLOW COMPLETION CHECKLIST**

Use this to verify all steps completed properly:

**Step 1: Event Booking**
- [ ] Client information collected
- [ ] Menu preferences noted
- [ ] Date reserved

**Step 2: Create Invoice**
- [ ] Invoice generated
- [ ] Formulas working
- [ ] File properly named

**Step 3: Client Approval**
- [ ] Contract signed
- [ ] Deposit received
- [ ] Final menu approved

**Step 4: Generate Kitchen Sheet**
- [ ] Items auto-populated
- [ ] Prep days assigned
- [ ] Tasks detailed

**Step 5: Calculate Ingredients**
- [ ] Recipes scaled
- [ ] Master list created
- [ ] Inventory checked

**Step 6: Create Production Schedule**
- [ ] Timeline built
- [ ] Staff assigned
- [ ] Equipment reserved

**Step 7: Order Ingredients**
- [ ] All orders placed
- [ ] Confirmations received
- [ ] Delivery scheduled

**Step 8: Receive & Inventory**
- [ ] Deliveries inspected
- [ ] Items stored properly
- [ ] Inventory updated

**Step 9: Prep & Production**
- [ ] All prep completed
- [ ] Quality checks passed
- [ ] Ready for event

**Step 10: Event Execution**
- [ ] Event executed perfectly
- [ ] Client happy
- [ ] Team debriefed

---

## 📞 **SUPPORT & ESCALATION**

**For Workflow Questions:**
- Review this WORKFLOW.md document
- Check PROJECT_RULES.md for details
- Consult with Kitchen Manager

**For Recipe/Ingredient Questions:**
- Reference Lariat_Recipe_Book.docx
- Consult with Head Chef
- Check vendor order guide

**For Client/Event Questions:**
- Contact Event Coordinator
- Reference client contract
- Check invoice notes

**For Emergencies:**
- Missing critical ingredient: Source from backup vendor
- Equipment failure: Use backup equipment
- Staff no-show: Call backup staff list
- Client emergency: Contact Event Coordinator immediately

---

**Document Version:** 1.0  
**Last Updated:** November 19, 2025  
**Next Review:** February 19, 2026  
**Maintained By:** Lariat Operations Team

---

## 🎯 **REMEMBER:**

**Communication is key** - Keep everyone informed throughout the workflow

**Document everything** - Details matter when planning events

**Quality over speed** - Better to be slightly late than to serve subpar food

**Team success** - Everyone plays a critical role

**Continuous improvement** - Learn from every event

---

**"Proper planning prevents poor performance!"** 📋✨
