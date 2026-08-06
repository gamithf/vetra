# Vetra — 5-Minute Demo Video Script (WINNING CUT)

**Product:** Vetra — the AI-assisted veterinary clinic operating system
**Runtime:** ~5:00 (soft cap)
**Mode:** Full stack — real backend + real Gemini 2.5 Flash agent pipeline (see README to run all three services)
**One-line pitch to keep in mind:** *"A dog walks in, the vet dictates, and one AI pipeline writes the record, updates stock, builds the bill, notifies the owner — and books the follow-up — before the client even reaches the counter."*

---

## THE STORY IN ONE LINE
> A dog with chronic itchy skin checks in. The vet dictates the exam into an AI co-pilot. In seconds a single pipeline writes the medical record, updates inventory, generates the bill, texts the owner, **and auto-schedules a 7-day follow-up**. The owner's secure link shows the whole visit and the booked follow-up — and lets them manage appointments from their phone.

**Characters (from the seeded database):**
- **Ishara Kumari** — front-desk staff (`staff1@vetra.com` / `password123`)
- **Dr. Kasun Perera** — veterinarian (`vet1@vetra.com` / `password123`)
- **Nuwan Fernando** — pet owner (Cooper's dad)
- **Cooper** — Labrador Retriever, male, 28 kg, 10:00 appointment — *"Severe itching — suspected atopic dermatitis"*

**The dictated transcript — read this aloud, it also appears on screen:**
> "Cooper has atopic dermatitis. Prescribe Amoxicillin 250mg. Check if Meloxicam interacts with Cooper's current medications. Dispensed Amoxicillin 250mg. Schedule a follow-up in 7 days."

---

## ⏱ Time Budget (plan your cuts — every section is tighten-able)
| Act | Content | Target |
|---|---|---|
| 1 | Opening + login (Staff) | 0:00 – 0:20 |
| 2 | Check-in + triage | 0:20 – 0:55 |
| 3 | Handoff to Vet, EMR | 0:55 – 1:35 |
| 4 | AI co-pilot + 8-agent pipeline (the showpiece) | 1:35 – 3:40 |
| 5 | Checkout & payment | 3:40 – 4:15 |
| 6 | Owner portal: follow-up + booking (close) | 4:15 – 5:00 |

> If you run long, cut the portal "book a slot" picker (Act 6) to a 10-second glance — the auto-scheduled follow-up is mandatory, the booking interaction is a bonus.

---

## Before You Record (Setup & Prep)

1. **Start all three services** (three terminals):
   ```bash
   # Terminal 1 — backend (port 8000)
   cd backend && uvicorn app.main:app --reload
   # Terminal 2 — agent service (port 8001), requires GEMINI_API_KEY
   cd agent && uvicorn app.main:app --port 8001 --reload
   # Terminal 3 — frontend
   cd frontend && npm run dev
   ```
2. **Re-seed fresh** so pet/appointment IDs and stock are exactly in narrated state:
   ```bash
   cd backend && venv\Scripts\python.exe scripts/seed.py
   ```
3. **Verify both logins once** (then log out): Staff `staff1@vetra.com` / `password123`, Vet `vet1@vetra.com` / `password123`.
4. **Generate a magic-link owner portal token** (needed for Act 6). From the repo root run the helper or use the backend venv:
   ```
   set PYTHONPATH=backend
   backend\venv\Scripts\python.exe C:\path\to\make_token.py
   ```
   Copy the token → your owner link is `http://localhost:5173/p/<token>`. Keep it open on the clipboard; you'll paste/click it in Act 6. (This works whether or not WhatsApp is configured.)
5. **Optional — WhatsApp owner notification** (best demo). Add Meta Cloud API creds to `backend/.env`:
   ```bash
   AK_WHATSAPP__ACCESS_TOKEN=<token>
   AK_WHATSAPP__PHONE_NUMBER_ID=<number id>
   AK_WHATSAPP__API_VERSION=v22.0
   FRONTEND_URL=http://localhost:5173
   AK_WHATSAPP__TEMPLATE_NAME=vetra_visit_summary   # pre-approved template, always delivers
   ```
   The owner (Nuwan, `94707393930`) can then receive the visit summary + the secure link. If it's unconfigured, the pipeline just prints "WhatsApp skipped" — it never fails. Either way, use the pre-generated token for Act 6 so the ending is guaranteed.
6. **Window:** 16:9 (≥1280×720), maximized — sidebar, queue, floating co-pilot all visible. **Turn on the cursor.** Record **screen + mic** (OBS / Loom / Screen Studio), 1080p in, 1080p H.264 MP4 out.
7. **Do one 30-second dry run** of the pipeline (below) so timing feels natural. It calls real Gemini — pipeline ≈ 5–10 s; the transcript is deterministic (no Whisper call).
8. Soft burned-in captions are strongly recommended for judges.
9. Have the narration (this script, minus formatting) on a second monitor — don't read from the screen.

---

## ACT 1 — The Opening (0:00 – 0:20)

**🎙️ "Vetra is an intelligent operating system for the modern veterinary clinic. It connects the front desk, the exam room, and the billing counter into one real-time platform — and it wraps the whole visit with an AI agent that does the paperwork for you."**

**🖱️** Login as **Staff** (`staff1@vetra.com` / `password123`).

**📺** Staff dashboard (Ishara) — stat cards: Today's Appointments, Checked-In, **Low Stock** (amber), Pending Invoices.

---

## ACT 2 — Arrival & Check-In (0:20 – 0:55)

**🎙️ "Nuwan is checking in Cooper for a ten o'clock appointment. Ishara opens today's calendar."**
**🖥️** Open **Calendar** tab → show Cooper's appointment ("Severe itching — suspected atopic dermatitis").

**🎙️ "One click on check-in — no paper, no retyping — and Cooper is live in the system."**
**🖥️** Open **Check-In/Out** tab → find Cooper (Scheduled) → **Check In**.
**📺** Badge flips **Scheduled → Checked In**, toast **"Checked in"**, a **"Send to Vet"** button appears.

**🎙️ "Notice Tucker flagged red — a vomiting emergency surfaced for triage automatically. Vetra keeps the whole clinic in sync in real time."**

---

## ACT 3 — The Handoff to the Vet (0:55 – 1:35)

**🎙️ "Because the handoff is live, Dr. Kasun never has to hunt for the patient."**
**🖥️** Log out → log in as **Vet** (`vet1@vetra.com` / `password123`).
**📺** Vet dashboard — Patient Queue with **Cooper near the top**, urgent Tucker above.

**🎙️ "Cooper is already waiting in the queue. Dr. Kasun opens the record — Vetra has his full history on hand."**
**🖥️** Click **Cooper** in the queue.
**📺** Cooper's EMR: species/breed, 28kg, DOB, microchip + **Medical Timeline** showing past **atopic dermatitis** and his **current Meloxicam**. The **AI Co-Pilot** button turns green with a pulse — auto-locked to Cooper.

**🎙️ "The co-pilot locks to the active patient automatically — no patient IDs typed. And note: Cooper is already on Meloxicam, an NSAID. That becomes important in a moment."**

---

## ACT 4 — The AI Co-Pilot + 8-Agent Pipeline (1:35 – 3:40) ⭐ THE SHOWPIECE

**🎙️ "Dr. Kasun dictates the exam just as he would to a colleague."**
**🖥️** Open the **"AI Co-Pilot"** (note the **LOCKED** chip + Cooper). Click **Record**.

**📺** Listening animation — red dot, pulsing waveform, "Listening...".

**🎙️ Read into the mic, word for word:**
> "Cooper's itchy. Cooper has atopic dermatitis. Prescribe Amoxicillin 250mg. Check if Meloxicam interacts with Cooper's current medications. Dispensed Amoxicillin 250mg. Schedule a follow-up in 7 days."

**🖥️** Click **Stop** → transcript appears. Pass the cursor over it ("fully editable"). Click **Submit**.

**📺 THE BREAKDOWN — the pipeline panel opens and runs 8 agents live (each with an input, streaming steps, and an output in the right pane, and a status icon on the left):**
1. **Patient Context** — loads Cooper + current meds.
2. **Medical Reasoning** — Gemini 2.5 Flash streams clinical analysis word-by-word.
3. **Clinical Safety (RAG)** — semantic vector search over the embedded veterinary drug index; pulls Cooper's **Meloxicam (NSAID)**, looks up prescribed **Amoxicillin**, retrieves references → emerald **"Clinical safety check passed"**. (A high-risk pair would raise a red pop-up.)
4. **Clinical Note** — SOAP note saved.
5. **Medical Record** — diagnosis & treatment written to timeline.
6. **Inventory** — deducts dispensed Amoxicillin 250mg.
7. **Billing** — itemized invoice lines in Sri Lankan Rupees.
8. **Finalize** — marks the visit complete, **notifies the owner via WhatsApp**, and — the new opener — **auto-schedules the 7-day follow-up** → *"Follow-up scheduled for Cooper on 2026-08-13 09:00 UTC."* and *"A follow-up for Cooper was scheduled automatically."*

**🎙️ While it runs: "Watch the Clinical Safety agent — it's doing semantic vector retrieval across the drug manual. It pulls Meloxicam's interaction references and checks them against Amoxicillin. No significant interaction, so the prescription clears. A high-risk pair would trigger an instant red alert instead. And notice the Finalize step: when the visit ended, Vetra didn't stop — it booked Cooper's follow-up for him automatically."**

**🖥️** After the pipeline: click **Medical Reasoning** and **Billing** (left) to reveal each output; click **Finalize**, **highlight the "Follow-up scheduled" line**. Click **Done**.
**📺** Toasts: **"Visit complete — records, inventory & bill updated"** + **"Bill generated ... Rs."**; Cooper shows **Completed**; timeline gains the new record; his new Definite follow-up appears in the calendar/queue.

---

## ACT 5 — The Checkout (3:40 – 4:15)

**🎙️ "By the time Nuwan reaches the desk, the bill is already waiting — built by the agent, line by line."**
**🖥️** Log out → log in as **Staff**. Open **Check-In/Out** → **Pending Checkout** ⇒ Cooper with the green Rs. total.
**🎙️ "Vetra knows which completed visits still owe payment."**
**🖥️** Click **Checkout** → show the modal: invoice lines (Consultation + 10 × Amoxicillin 250mg) and the Total in Rs.
**🎙️ "The bill was produced from the visit itself — no manual entry."** Choose **Credit Card** → **Pay Rs.**
**📺** Success toast **"Payment processed successfully!"**; Cooper leaves the pending list.

---

## ACT 6 — The Owner Side: the Auto-Booked Follow-up (4:15 – 5:00) 🔥 FINALE

**🎙️ "Now the owner's side. Nuwan got a secure link — the same one from the WhatsApp notification. Let's open it."**
**🖥️** Open your pre-generated link: `http://localhost:5173/p/<token>`. (Or, if WhatsApp delivered, show the message on the phone and tap the link.)
**📺** The secure pet portal loads with two tabs: **"Appointments & Booking"** and **"Visit Summary & Bill"**, plus a "Secure pet link" badge.

**🎙️ "This is the owner's secure portal. Look at this — it's showing Cooper's **next appointment**, already there: the **7-day follow-up the vet's co-pilot ordered, scheduled automatically.**"**
**🖥️** Tap the **Visit Summary & Bill** tab — diagnosis "atopic dermatitis", treatment, the bill total → the exact payout of the AI step.
**🖥️** Back to **Appointments & Booking** → click **Reschedule** on the follow-up, or pick a free slot to show the self-service **booking** (past slots greyed out, 30-min clinic hours). Then keep the scheduled follow-up.

**🎙️ Closing line:**
> "That's the full loop, end to end. The vet thought in medicine. Vetra did the paperwork: composed the record, watched for drug interactions, updated the stock, made the bill, texted the owner, and **booked the next visit on its own** — and the owner can manage it from their phone with a secure link. Less clipboard. More medicine. This is Vetra."

**📺** End card / fade to black.

---

## Production Tips
- ~3 lines of narration / 30s; pause after each toast + pipeline step.
- Move the cursor slowly and deliberately; don't rush clicks.
- Good mic, quiet room, steady confident voice, 1080p H.264.
- Soft burned-in captions (recommended).
- End card with a **"call to action":** Vetra logo + tagline.

---

## 30-Second Rehearsal Cheat Sheet
1. Staff login → Calendar → Check-In/Out → **Check In** Cooper.
2. Logout → Vet login → click Cooper → open **Co-Pilot (LOCKED)**.
3. Record → read the exact transcript → Stop → Submit.
4. Watch **8 agents** stream → click Medical Reasoning + Billing + **Finalize (follow-up line)** → Done.
5. Logout → Staff → **Pending Checkout** → Checkout Cooper → Pay.
6. Open **`/p/<token>`** portal → show **follow-up already booked** → tab to Visit Summary & Bill → Reschedule/book → close.

> Verify `GEMINI_API_KEY` is set in `agent/.env`. The pipeline makes real calls. After re-seeding, **regenerate the token** (pets get new UUIDs). Time: pipeline ≈5–10 s. Build natural pauses around it.