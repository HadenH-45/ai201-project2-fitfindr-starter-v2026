# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
The initial search step relies on keyword matching across user inputs and listing metadata, so there will be natural language variation in search queries that can occasionally fail to match listings. 4 out of 5 allows for this margin while still enforcing high overall reliability.
---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. Something about state

Given a successful search that populates the session state, the session["selected_item"]'s id strictly matches the item object passed into suggest_outfit().


**Why this target:**

A target of 5 of 5 is essential because the state propogation is a determistic not probabilistic model output. The tool calls will recieve corrupted or mismatched data if the state payload mutates, drops fields, or selects different item mid-pipeline.

---

## 4. Something about the fit card

Given a valid item and outfit recommendation from suggest_outfit(), create_fit_card() must generate a caption that references at least one specific attribute of the selected item like brand, color, or style term, and stays within 280 characters through 4 out of 5 tries.

**Why this target:**

Since create_fit_card() calls an LLM, temperature and prompt sampling introduce variability in wording. Target setting at 4 of 5 allows for minor non-deterministic output variances while enforcing strict, verifiable constraints on length and core contextual grounding.

---

## 5. Your choice

Given a non-empty user wardrobe, the recommendations returned by suggest_outfit() must incorporate or complement at least one specific item from the user's wardrobe and match by color, aesthetic, or item type in at least 4 out of 5 tries.

**Why this target:**

The agent should not default to generic styling advice when wardrobe context is present. A target of 4 of 5 ensures the model effectively conditions its styling output on existing session state without failing when wardrobe descriptions are minimal or edge-case items are used.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
