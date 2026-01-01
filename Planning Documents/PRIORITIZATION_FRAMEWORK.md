# Prioritization Framework

> **How to structure priorities for what to work on next**

## 🎯 Priority Framework: MoSCoW + Impact/Effort Matrix

Use this framework to evaluate every task and decide what to work on next.

### Priority Levels (MoSCoW)

1. **MUST HAVE** (Critical Path)
   - Blocks other work
   - Required for MVP
   - Breaks functionality if missing
   - Example: Database schema, API endpoints

2. **SHOULD HAVE** (High Value)
   - Important for user experience
   - Expected by users
   - Adds significant value
   - Example: Mobile optimization, authentication

3. **COULD HAVE** (Nice to Have)
   - Improves experience but not essential
   - Can be deferred
   - Example: Advanced analytics, animations

4. **WON'T HAVE** (Future)
   - Out of scope for current phase
   - Can be added later
   - Example: Multi-language, social features

### Impact/Effort Matrix

Evaluate each task on two dimensions:

**Impact:**
- **High:** Significantly improves UX, unblocks major features, fixes critical bugs
- **Medium:** Moderate improvement, nice enhancement
- **Low:** Minor improvement, polish

**Effort:**
- **Low:** < 2 hours, straightforward
- **Medium:** 2-8 hours, moderate complexity
- **High:** > 8 hours, complex or risky

**Priority Order:**
1. **Quick Wins** (High Impact, Low Effort) - Do first!
2. **Major Projects** (High Impact, High Effort) - Plan carefully
3. **Fill-ins** (Low Impact, Low Effort) - Do when time allows
4. **Time Sinks** (Low Impact, High Effort) - Avoid or defer

---

## 📊 Current State Assessment

### ✅ Completed
- Phase 0: UX + API Planning
- Basic frontend structure (Next.js)
- Leaderboard table component
- Basic styling and glassmorphism design
- Database schema (Phase 1 foundation)

### 🚧 In Progress / Issues
- **Mobile optimization** - Not responsive (HIGH PRIORITY)
- **Cloud header visibility** - Not showing (MEDIUM PRIORITY)
- **Absolute positioning bugs** - Breaking layout (MEDIUM PRIORITY)

### 📋 Next Phase (Per BUILD_PHASES.md)
- **Phase 1:** Core Data Foundation
  - Database setup complete
  - Need: 10 boxes registered
  - Need: Manual metrics entry system
  - Need: Sample data entry

---

## 🎯 Recommended Priority Structure

### **TIER 1: Critical Path (Do First)**

These block progress or break functionality:

1. **Fix Critical Bugs** ⚠️
   - [ ] Cloud header visibility (blocks visual polish)
   - [ ] Absolute positioning issues (breaks mobile layout)
   - [ ] Percentage column alignment (user-facing bug)

2. **Complete Phase 1 Foundation** 🏗️
   - [ ] Register 10 One Piece boxes in database
   - [ ] Manual metrics entry endpoint working
   - [ ] Enter 7-14 days of sample data
   - **Why:** Enables all future phases, unblocks frontend development

### **TIER 2: High Value (Do Soon)**

These significantly improve user experience:

3. **Mobile Optimization** 📱
   - [ ] Responsive navigation (hamburger menu)
   - [ ] Responsive leaderboard table (horizontal scroll)
   - [ ] Responsive text sizes
   - [ ] Touch-friendly controls
   - **Why:** Your README says "Mobile-first application" - this is core to your strategy

4. **Polish & UX Improvements** ✨
   - [ ] Fix "New Releases" absolute positioning
   - [ ] Improve glassmorphism effects
   - [ ] Ensure all columns align properly
   - **Why:** Professional appearance builds trust

### **TIER 3: Phase 2+ (Plan Next)**

These follow the build phases:

5. **Phase 2: Manual Metrics Entry** 📊
   - Admin panel for data entry
   - Metrics calculation from manual data
   - **Why:** Enables full app functionality with manual data

6. **Phase 3: Unified Metrics Calculation** 🔢
   - EMA calculations
   - Liquidity scores
   - Derived metrics
   - **Why:** Core business logic, needed for rankings

7. **Phase 6: Rankings & Caching** 🏆
   - Ranking calculation
   - Redis caching
   - Performance optimization
   - **Why:** Required before API layer

8. **Phase 7: API Layer** 🔌
   - REST endpoints
   - Response models
   - OpenAPI docs
   - **Why:** Frontend needs this to consume data

### **TIER 4: Future Enhancements (Defer)**

9. **Phase 8: Monetization** 💰
   - Authentication
   - Stripe integration
   - Paywall
   - **Why:** Can launch without this initially

10. **Phase 2B/4: API Integration** 🔄
    - TCGplayer API
    - eBay API
    - **Why:** Manual-first approach means this comes later

---

## 📅 Weekly Priority Planning Template

Use this template each week to plan priorities:

### Week of [DATE]

**This Week's Focus:**
- [ ] Tier 1: [Specific task]
- [ ] Tier 1: [Specific task]
- [ ] Tier 2: [Specific task]

**Time Allocation:**
- 60% - Tier 1 (Critical Path)
- 30% - Tier 2 (High Value)
- 10% - Tier 3 (Planning/Research)

**Blockers:**
- [ ] [What's blocking progress?]

**Decisions Needed:**
- [ ] [What decision is needed to proceed?]

---

## 🎯 Decision Framework

When choosing between tasks, ask:

1. **Does it unblock other work?**
   - Yes → Higher priority
   - No → Can wait

2. **Is it user-facing?**
   - Yes → Higher priority (if visible)
   - No → Can be internal

3. **Is it in the critical path?**
   - Yes → Must do
   - No → Can defer

4. **What's the impact/effort ratio?**
   - High impact, low effort → Do now
   - Low impact, high effort → Defer

5. **Does it align with MVP goals?**
   - Yes → Prioritize
   - No → Future phase

---

## 🚦 Recommended Next Steps (This Week)

Based on current state, work on in this order:

### Day 1-2: Fix Critical Issues
1. ✅ Fix cloud header visibility
2. ✅ Fix absolute positioning bugs
3. ✅ Fix percentage column alignment

### Day 3-4: Mobile Optimization
4. ✅ Add responsive navigation
5. ✅ Make leaderboard table mobile-friendly
6. ✅ Add responsive text sizes

### Day 5-7: Phase 1 Completion
7. ✅ Register 10 boxes in database
8. ✅ Build manual metrics entry endpoint
9. ✅ Enter sample data (7-14 days)

---

## 📊 Tracking Progress

### Use GitHub Issues or Project Board

Create labels:
- `priority:critical` - Tier 1
- `priority:high` - Tier 2
- `priority:medium` - Tier 3
- `priority:low` - Tier 4

### Weekly Review

Every Monday:
1. Review completed tasks
2. Update priorities based on new information
3. Identify blockers
4. Plan week's focus

---

## 🎯 Key Principles

1. **Follow the Build Phases** - They're designed to build on each other
2. **Fix Bugs Before Features** - Technical debt compounds
3. **Mobile-First** - Your strategy says mobile-first, prioritize accordingly
4. **Manual-First Approach** - Don't wait for API access, build with manual data
5. **User-Facing First** - Visible improvements > internal improvements

---

## 🔄 When Priorities Change

Re-evaluate priorities when:
- New requirements emerge
- Blockers are discovered
- User feedback indicates different needs
- Technical constraints change
- Business goals shift

**Always refer back to:**
- BUILD_PHASES.md for phase dependencies
- This framework for prioritization logic
- MVP definition for scope control

---

**Last Updated:** 2025-01-01
**Next Review:** Weekly

