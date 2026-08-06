# Vetra — 5-Minute Demo Video Script

**Product:** Vetra — the AI-assisted veterinary clinic operating system
**Runtime:** ~5 minutes
**Mode:** Full stack, real backend + real Gemini 2.5 Flash agent pipeline (see README to set up all three services)

---

## Before You Record (Setup & Prep)

1. Start all three services:
   ```bash
   # Terminal 1 — backend (port 8000)
   cd backend && uvicorn app.main:app --reload

   # Terminal 2 — agent service (port 8001), requires GEMINI_API_KEY
   cd agent && uvicorn app.main:app --port 8001 --reload

   # Terminal 3 — frontend
   cd frontend && npm run dev
   ```
2. **Re-seed the database fresh** so the demo starts in the exact narrated state (use the backend venv — the seed needs `bcrypt`):
   ```bash
   cd backend && venv\Scripts\python.exe scripts/seed.py
   ```
3. Open `http://localhost:5173` in a clean browser window. Log in as **Staff** (`staff1@vetra.com` / `password123`) and as **Vet** (`vet1@vetra.com` / `password123`) once to confirm both work, then log out.
4. **Optional — WhatsApp owner notifications.** Add your Meta Cloud API credentials to `backend/.env` so the pipeline can text the owner after a visit (Cooper's owner phone is `94707393930`):
   ```bash
   AK_WHATSAPP__ACCESS_TOKEN=<your token>
   AK_WHATSAPP__PHONE_NUMBER_ID=<your number id>
   AK_WHATSAPP__API_VERSION=v22.0
   FRONTEND_URL=http://localhost:5173
   ```
   Delivery notes:
   - **Free-form text only delivers inside a 24h session** (the owner must message the business first). To make the live demo deliver, send any message to the Vetra business number from the owner's phone within 24h of the demo, or:
   - **Best: an approved template.** Create a `vetra_visit_summary` template in WhatsApp Manager (body with `{{1}}`…`{{8}}`: owner name, pet name, visit id, reason, diagnosis, treatment, total, link) and set `AK_WHATSAPP__TEMPLATE_NAME=vetra_visit_summary`. The pipeline then always delivers (no session needed) and the result line shows "Owner notified via template".
   - If these are missing/unconfigured the pipeline simply reports "WhatsApp skipped" — it never fails.
4. Window size: use **a 16:10 or 16:9 browser window**, ~1280×720 or larger. Keep the window maximized so the sidebar, queue, and floating co-pilot are all visible.
5. Turn **on the cursor / mouse pointer** (macOS: System Settings → Accessibility → Pointer → show pointer; OBS can also highlight the cursor).
6. Pick a recording tool (OBS, Loom, Screen Studio). Record **screen + mic**.
7. **Do a 30-second dry run first** (see "Rehearsal" at the bottom) so timing and the pipeline feel natural.
8. Speak slowly, leave a 1–2 second pause after each major animation (toasts, pipeline).

> Tip: Have the narration lines on a second monitor or printed. Do NOT read from a script on screen.

> ⚠️ The transcript is **deterministic**: when you press Stop, the exact sentence below appears automatically (no real Whisper call). Read it aloud during the recording so the narration and the on-screen text match perfectly.

---

## THE STORY IN ONE LINE
> "A dog with a chronic skin condition walks in. The front desk checks him in, the vet dictates the exam into an AI co-pilot, and by the time the client is at the counter, the medical record, the inventory, and the Rs. bill are already done — while the AI also catches a medication interaction."

**Characters (from the seed database):**
- **Ishara Kumari** — front-desk staff (`staff1@vetra.com` / `password123`)
- **Dr. Kasun Perera** — veterinarian (`vet1@vetra.com` / `password123`)
- **Nuwan Fernando** — pet owner
- **Cooper** — Labrador Retriever, male, 28 kg, 10:00 appointment — "Severe itching — suspected atopic dermatitis"

**The dictated transcript (read this aloud, it appears on screen):**
> "Cooper has atopic dermatitis. Prescribe Amoxicillin 250mg. Check if Meloxicam interacts with Cooper's current medications. Dispensed Amoxicillin 250mg. Schedule follow-up in 7 days."

---

## ACT 1 — The Opening (0:00 – 0:30)

**🎙️ Narrate:**
> "This is Vetra — an intelligent operating system for modern veterinary clinics. It connects the front desk, the exam room, and the billing counter into one real-time platform. Today, a client is walking in with his Labrador, Cooper, who's been scratching non-stop."

**🖱️ Do:**
- On the login page, sign in as **Staff** (`staff1@vetra.com` / `password123`).

**📺 Expect on screen:**
- Staff Dashboard (Ishara Kumari) — Overview with stat cards: Today's Appts, Checked In, **Low Stock** (amber), Pending Invoices.

---

## ACT 2 — The Arrival & Check-In (0:30 – 1:15)

**🎙️ Narrate:**
> "Nuwan arrives with Cooper for a 10 o'clock appointment. Ishara pulls up today's calendar to see the schedule."

**🖱️ Do:**
- Click the **"Calendar"** tab.

**📺 Expect:**
- A date-sorted calendar. Today shows Cooper — "Severe itching — suspected atopic dermatitis" — alongside the rest of the queue.

**🎙️ Narrate:**
> "One click on 'Check In' brings Cooper into the system — no paper, no retyping."

**🖱️ Do:**
- Click the **"Check-In / Out"** tab. Find **Cooper** (scheduled). Click **"Check In"**.

**📺 Expect:**
- Cooper's badge flips **Scheduled → Checked In** with a toast **"Checked in"**, and a new **"Send to Vet"** button appears.

**🎙️ Narrate:**
> "Notice Tucker, flagged red — a vomiting emergency that's automatically surfaced for triage. Vetra keeps the whole clinic in sync."

---

## ACT 3 — The Handoff to the Vet (1:15 – 1:55)

**🎙️ Narrate:**
> "Now let's switch to the veterinarian's view. Because the handoff happens in real time, the doctor doesn't need to hunt for the patient."

**🖱️ Do:**
- Click **log out** (top-right avatar → Logout).
- Sign in as **Vet** (`vet1@vetra.com` / `password123`).

**📺 Expect:**
- Vet Dashboard (Dr. Kasun Perera) — Patient Queue with **Cooper near the top** (pet name + short patient ID), urgent Tucker sorted above.

**🎙️ Narrate:**
> "Cooper is already waiting in the vet's queue. Sarah opens his record — Vetra has his full history right there."

**🖱️ Do:**
- Click **Cooper** in the queue.

**📺 Expect:**
- Cooper's EMR: species, weight (28 kg), DOB, microchip, and the **Medical Timeline** — including a past **atopic dermatitis** record and his **current Meloxicam** medication. The **AI Co-Pilot** floating button turns green with a pulse — automatically locked to Cooper.

**🎙️ Narrate:**
> "The co-pilot locks onto the active patient automatically — the doctor never types a patient ID. And note the timeline: Cooper already has a history of atopic dermatitis, and he's currently on Meloxicam. That matters in a moment."

---

## ACT 4 — The Consultation + AI Co-Pilot (1:55 – 3:45)

**🎙️ Narrate:**
> "Dr. Chen starts the exam, then turns to the AI co-pilot and dictates her findings just as she would to a colleague."

**🖱️ Do:**
- Click the **"AI Co-Pilot"** floating button to expand it (note the **LOCKED** chip and Cooper's name).
- Click **"Record"** (the mic).

**📺 Expect:**
- A **listening animation** — red dot + pulsing waveform bars, label "Listening...".

**🎙️ Narrate (read the transcript aloud into the mic):**
> "Cooper has atopic dermatitis. Prescribe Amoxicillin 250mg. Check if Meloxicam interacts with Cooper's current medications. Dispensed Amoxicillin 250mg. Schedule follow-up in 7 days."

**🖱️ Do:**
- Click **"Stop"**. The transcript appears in the textarea after a moment. Move the cursor over the text so the viewer sees it's editable.

**🎙️ Narrate:**
> "The transcript lands in seconds, fully editable. The doctor can fix anything before submitting."

**🖱️ Do:**
- Click **"Submit"**.

**📺 Expect — the showpiece:**
- The **"Vetra Agent Pipeline"** popup opens (fixed-size panel) and opens a WebSocket to the agent service. Eight steps run in sequence — live streaming reasoning, each with a status icon in the left sidebar:
  1. **Patient Context** — loads Cooper, and his **current medications**, from the backend.
  2. **Medical Reasoning** — Gemini 2.5 Flash streams its clinical analysis word by word.
  3. **Clinical Safety (RAG)** — the **Clinical Safety agent** runs a **semantic vector search over the embedded veterinary-drug index**. It pulls Cooper's current medication (**Meloxicam — NSAID**), looks up the newly-prescribed **Amoxicillin (penicillin)** by name, retrieves the relevant drug-interaction references from the index, and checks the pair. Result: an emerald **"Clinical safety check passed"** banner — "Retrieved N reference(s) — no significant interactions". (A high-risk pairing would instead trigger a red **pop-up**.)
  4. **Clinical Note** — raw transcript + structured SOAP note saved.
  5. **Medical Record** — diagnosis & treatment written to Cooper's timeline.
  6. **Inventory** — deducts the dispensed **Amoxicillin 250mg**.
  7. **Billing** — itemized invoice lines in Sri Lankan Rupees.
  8. **Finalize** — appointment marked completed **and the owner is notified via WhatsApp** (visit ID, reason, diagnosis, bill total, and a secure link to a public pet profile page).
- While an agent is working, a **LIVE** pulse badge shows next to its name and the right pane auto-scrolls with its streaming reasoning.

**🎙️ Narrate (while agents run):**
> "Watch the **Clinical Safety agent**. It runs a semantic retrieval — a vector search against Vetra's indexed veterinary-drug manual — pulling up the Meloxicam interaction references, then checking them against Amoxicillin. No significant interaction: the prescription clears. Had these been a high-risk combination, the system would raise an instant UI alert."

**📺 Expect (after the pipeline — done view):**
- **Diagnosis** and **Treatment** summary, a **Bill** chip with the Rs. total, and **inventory log** chips (e.g. "Amoxicillin 250mg −10").
- The hint: **"Click any agent on the left to review exactly what it did."**
- The **"Done"** button.

**🖱️ Do:**
- Click **"Medical Reasoning"** and **"Billing"** in the left sidebar to show each step's per-agent result (the Rs. line items). Then click **"Finalize"** to show the WhatsApp owner-notification outcome ("Owner notified via template/text" or "WhatsApp skipped — …").
- If WhatsApp is configured, glance at the owner's phone to show the delivered message.
- Click **"Done"**.

**📺 Expect:**
- Toast **"Visit complete — records, inventory & bill updated"** plus a **"Bill generated"** toast with the Rs. total.
- Back in the vet view, Cooper's appointment shows **Completed**; his timeline gains the new record.

---

## ACT 5 — The Checkout (3:45 – 4:30)

**🎙️ Narrate:**
> "The visit is done. By the time Nuwan reaches the front desk, the bill is already waiting — the agent created it automatically."

**🖱️ Do:**
- **Log out**, log back in as **Staff** (Jessica).
- Go to **"Check-In / Out"** tab.

**📺 Expect:**
- A **"Pending Checkout"** section listing **Cooper** with a green **Rs. invoice total** chip (the exact total from the pipeline).

**🎙️ Narrate:**
> "Vetra knows which completed visits still need payment — Cooper is right here, with his bill already calculated."

**🖱️ Do:**
- Click **"Checkout"** on Cooper.

**📺 Expect:**
- Checkout modal showing **Cooper** with his short patient ID and the invoice line items generated by the agents — **Consultation Fee** plus **10 × Amoxicillin 250mg (Rs.25 each)** — and a **Total** in rupees.

**🎙️ Narrate:**
> "The bill was built from the visit itself — consultation plus the ten Amoxicillin tablets the agents dispensed. No manual entry. Jessica takes the payment."

**🖱️ Do:**
- Select a payment method (e.g. **Credit Card**), click **"Pay Rs.…"**.

**📺 Expect:**
- Success toast **"Payment processed successfully!"** — the invoice is now paid and Cooper drops off the pending list.

---

## ACT 6 — The Closing (4:30 – 5:00)

**🎙️ Narrate:**
> "And the payoff: everything stays in sync. Let's check the inventory."

**🖱️ Do:**
- Click the **"Inventory"** tab.

**📺 Expect:**
- **Amoxicillin 250mg** now shows **90 tablets** (was 100 — the 10 dispensed were deducted, with the Rs.25/tablet price shown), and **Meloxicam 1.5mg** is flagged **Low / red** — below its reorder point.

**🎙️ Narrate (closing):**
> "The stock was updated the moment the vet dictated — and Meloxicam is now flagged for reorder before it even becomes a problem. Vetra replaces the clipboard and the calculator with one real-time platform — so the team can focus on medicine, not paperwork. This is Vetra: the modern veterinary clinic."

**📺 Expect:**
- End card / fade to black.

---

## Production Tips

- **Pace:** Aim for ~3 lines of narration per 30 seconds. Pause after each toast and pipeline step.
- **Pointer:** Keep the mouse cursor moving slowly and purposefully to each click — don't rush.
- **Audio:** Use a decent mic, reduce background noise, moderate volume. Narrate confidently.
- **Resolution:** Record at 1080p. Export 1080p MP4 (H.264).
- **Captions:** Adding soft burned-in captions greatly helps competition judges; optional but recommended.
- **Logo/end card:** Add a clean end card with the Vetra logo and tagline.

---

## Rehearsal Cheat Sheet (30-sec dry run)

1. Login as Staff → **Calendar** tab → **Check-In/Out** tab → Check In Cooper.
2. Logout → Login as Vet → click Cooper → expand Co-Pilot (LOCKED to Cooper).
3. Record → read the exact transcript aloud → Stop → transcript appears → Submit.
4. Watch the 7-agent pipeline stream → click Medical Reasoning + Billing → Done → toasts.
5. Logout → Staff → Check-In/Out → Pending Checkout → Checkout Cooper → Pay → success.
6. Inventory tab → Amoxicillin 90 tablets, Meloxicam low-stock alert.

> Verify `GEMINI_API_KEY` is set in `agent/.env` before recording — the pipeline makes real calls to Gemini 2.5 Flash. Time the pipeline: ~5–10 seconds depending on model latency. The transcript is deterministic (no Whisper call) so timing is reliable. Build natural pauses around the pipeline run.
