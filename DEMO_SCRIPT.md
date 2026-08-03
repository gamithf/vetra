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
2. Open `http://localhost:5173` in a clean browser window.
3. Log in as **Staff** (`staff1@vetra.com` / `password123`), verify the seeded data is present, then log out.
4. Window size: use **a 16:10 or 16:9 browser window**, ~1280×720 or larger. Keep the window maximized so the sidebar, queue, and floating co-pilot are all visible.
5. Turn **on the cursor / mouse pointer** (macOS: System Settings → Accessibility → Pointer → show pointer; OBS can also highlight the cursor).
6. Pick a recording tool (OBS, Loom, Screen Studio). Record **screen + mic**.
7. **Do a 30-second dry run first** (see "Rehearsal" at the bottom) so timing and the pipeline feel natural.
8. Speak slowly, leave a 1–2 second pause after each major animation (toasts, pipeline).

> Tip: Have the narration lines on a second monitor or printed. Do NOT read from a script on screen.

---

## THE STORY IN ONE LINE
> "Sarah arrives with her dog Max. The front desk checks him in. The vet sees him instantly, dictates the exam into an AI co-pilot, and by the time the client is at the counter, the record, the inventory, and the bill are already done."

**Characters (from the seed database):**
- **Jessica Rodriguez** — front-desk staff (`staff1@vetra.com`)
- **Dr. Sarah Chen** — veterinarian (`vet1@vetra.com`)
- **Alice Thompson** — pet owner
- **Max** — Golden Retriever, male, 32.5 kg, annual wellness exam

---

## ACT 1 — The Opening (0:00 – 0:30)

**🎙️ Narrate:**
> "This is Vetra — an intelligent operating system for modern veterinary clinics. We connect every part of the patient journey — from the front desk, to the exam room, to the bill — into one real-time platform. Today, a client is walking in with her dog, Max."

**🖱️ Do:**
- On the login page, sign in as **Staff** (`staff1@vetra.com` / `password123`).

**📺 Expect on screen:**
- Staff Dashboard (Jessica Rodriguez) — Overview with stat cards (Appointments, Checked In, Low Stock, Pending Invoices).

---

## ACT 2 — The Arrival & Check-In (0:30 – 1:25)

**🎙️ Narrate:**
> "Alice arrives at the front desk with Max for his annual wellness exam. Jessica pulls up today's calendar to see the schedule at a glance."

**🖱️ Do:**
- Click **"Calendar"** in the left sidebar.

**📺 Expect:**
- A grouped, date-sorted calendar showing today's visits (Max, Cooper, Bella, Buddy, Tucker).

**🎙️ Narrate:**
> "Max is scheduled for 9:00. One click on 'Check In' sends him into the system — no paper, no retyping."

**🖱️ Do:**
- Go to **"Check-In / Out"** tab. Find **Max — Annual wellness exam** (scheduled). Click **"Check In"**.

**📺 Expect:**
- Max's status badge flips **Scheduled → Checked In** with a green toast **"Checked in"**.
- Notice the other patients in the queue — Bella limping, and **Tucker flagged URGENT in red** (vomiting). Vetra surfaces urgency automatically.

**🎙️ Narrate:**
> "Notice the urgent case here — Tucker, vomiting since yesterday — is automatically flagged red so the team can triage. This is a real-time clinic."

---

## ACT 3 — The Handoff to the Vet (1:25 – 2:00)

**🎙️ Narrate:**
> "Now let's switch to the veterinarian's view. Log out, and I'll sign in as Dr. Sarah Chen."

**🖱️ Do:**
- Click **log out** (top-right avatar → Logout).
- On login, sign in as **Vet** (`vet1@vetra.com` / `password123`).

**📺 Expect:**
- Vet Dashboard (Dr. Sarah Chen), Patient Queue.

**🎙️ Narrate:**
> "Because Vetra is real-time, Max is already here in the queue — and urgent cases like Tucker are sorted to the top."

**🖱️ Do:**
- Click **Max** in the queue.

**📺 Expect:**
- Max's full medical record opens: species, weight, microchip, and his **medical timeline** (previous vaccination history).
- The **AI Co-Pilot** floating button turns green with a pulse — it is now **automatically locked to Max**. No manual patient ID entry.

**🎙️ Narrate:**
> "The co-pilot locks onto the active patient automatically — the doctor never has to type a patient ID."

---

## ACT 4 — The Consultation + AI Co-Pilot (2:00 – 3:40)

**🎙️ Narrate:**
> "Dr. Chen starts the exam. She records the appointment, then turns to the AI co-pilot to dictate her findings."

**🖱️ Do:**
- Click **"Start Exam"** (Max's status → **In Progress**).
- Click the **"AI Co-Pilot"** floating button to expand it.
- Click **"Record"** (the mic).

**📺 Expect:**
- A **listening animation** — red dot + pulsing waveform bars, label "Listening...".

**🎙️ Narrate (dictate the exam out loud):**
> "Dr. Chen speaks naturally — temperature, heart rate, exam findings. The co-pilot captures it live."

**🖱️ Do:**
- Click **"Stop"**. Groq Cloud's Whisper Large V3 transcribes the recording and the transcript **appears as editable text**.
- Move the cursor over the text so the viewer sees it's editable.

**🎙️ Narrate:**
> "The doctor can edit anything before submitting. When she's happy, she clicks 'Submit'."

**🖱️ Do:**
- Click **"Submit"**.

**📺 Expect — the showpiece:**
- A full-screen **"Vetra Agent Pipeline"** overlay opens a WebSocket to the agent service. Seven agents run in sequence, each streaming **live reasoning text** as Gemini 2.5 Flash thinks:
  1. **Patient Context** — loads Max from the backend.
  2. **Medical Reasoning** — Gemini streams its clinical analysis, word by word.
  3. **Clinical Note** — raw transcript + structured SOAP note saved.
  4. **Medical Record** — diagnosis & treatment written to the timeline.
  5. **Inventory** — DAPP vaccine (and any supplies) deducted.
  6. **Billing** — itemized invoice lines generated.
  7. **Finalize** — appointment marked completed.
- Each step's checkmark flips as it finishes, and the live "thinking" pane scrolls with the current agent's output.

**🎙️ Narrate (while agents run):**
> "Behind the scenes, Vetra's AI agents work in sequence — powered by Gemini 2.5 Flash. They reason through the findings, draft the diagnosis and treatment plan, then write it straight into the medical record — while other agents update the inventory and pre-calculate the bill. All in a few seconds, while the vet moves on to the next patient."

**📺 Expect (after the pipeline):**
- A success panel: **diagnosis**, **treatment**, the generated **bill total**, and **inventory log** chips.
- Click **"Done"** → toast **"Visit complete — records, inventory & bill updated"**.
- The **medical timeline gains a new record**.
- Max's appointment flips to **Completed**.

---

## ACT 5 — The Checkout (3:40 – 4:30)

**🎙️ Narrate:**
> "The visit is done. By the time Alice brings Max to the front desk, the bill is already waiting."

**🖱️ Do:**
- **Log out**, log back in as **Staff** (Jessica).
- Go to **"Check-In / Out"** tab.

**📺 Expect:**
- A **"Pending Checkout"** section listing Max.

**🎙️ Narrate:**
> "Vetra knows which completed visits still need payment — it shows Max right here. Jessica opens the checkout."

**🖱️ Do:**
- Click **"Checkout"** on Max.

**📺 Expect:**
- Checkout modal with the invoice line items generated by the agent pipeline (consultation fee, vaccine, etc.), plus a **Total**.

**🎙️ Narrate:**
> "The bill was built automatically from the visit — no manual entry. Jessica selects a payment method."

**🖱️ Do:**
- Select **"Credit Card"** (or Cash), click **"Pay"**.

**📺 Expect:**
- Success toast **"Payment processed successfully!"** — invoice now paid.

---

## ACT 6 — The Closing (4:30 – 5:00)

**🎙️ Narrate:**
> "And here's the payoff: everything stays in sync. The dashboard shows the visit recorded, the DAPP vaccine stock updated, and the invoice settled — all from one seamless flow."

**🖱️ Do (optional, if time):**
- Open **"Inventory"** → point to **DAPP Vaccine** showing the decremented count and the **Low Stock** alerts.
- Return to **Overview** so the viewer sees the updated stat cards.

**🎙️ Narrate (closing):**
> "Vetra replaces the clipboard and the calculator with a single, real-time platform — so the team can focus on medicine, not paperwork. This is Vetra: the modern veterinary clinic."

**📺 Expect:**
- End card / fade to black.

---

## Production Tips

- **Pace:** Aim for ~3 lines of narration per 30 seconds. Pause after each toast/pipeline.
- **Pointer:** Keep the mouse cursor moving slowly and purposefully to each click — don't rush.
- **Audio:** Use a decent mic, reduce background noise, moderate volume. Narrate confidently.
- **Resolution:** Record at 1080p. Export 1080p MP4 (H.264).
- **Captions:** Adding soft burned-in captions greatly helps competition judges; optional but recommended.
- **Logo/end card:** Add a clean end card with the Vetra logo and tagline.

---

## Rehearsal Cheat Sheet (30-sec dry run)

1. Login as Staff → Calendar → Check-In/Out → Check In Max.
2. Logout → Login as Vet → click Max → Start Exam.
3. Expand Co-Pilot → Record → Stop → transcript appears → Submit.
4. Watch 7-agent pipeline stream → Done → toasts → timeline updates.
5. Logout → Staff → Check-In/Out → Pending Checkout → Checkout Max → Pay.

> Verify `GEMINI_API_KEY` is set in `agent/.env` before recording — the pipeline makes real calls to Gemini 2.5 Flash. Time the pipeline: ~5–10 seconds depending on model latency. Time the transcription: a few seconds after stopping the recording. Build natural pauses around these.
