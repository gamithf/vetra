"""Veterinary drug-safety knowledge base.

A small, curated subset of open-source veterinary medication references (drug
classes, aliases, interaction rules, monographs). It plays the role of the
"indexed database" the Clinical Safety agent runs a semantic vector search over.
"""

from __future__ import annotations

# Drug name → therapeutic class. Used to resolve trade names, strengths and
# typos to a canonical class so interaction rules stay deterministic.
DRUG_CLASSES: dict[str, str] = {
    # NSAIDs
    "meloxicam": "NSAID",
    "carprofen": "NSAID",
    "aspirin": "NSAID",
    "ketoprofen": "NSAID",
    "ibuprofen": "NSAID",
    "piroxicam": "NSAID",
    "deracoxib": "NSAID",
    "firocoxib": "NSAID",
    "diclofenac": "NSAID",
    "tolfenamic acid": "NSAID",
    "flunixin": "NSAID",
    "nimesulide": "NSAID",
    # Corticosteroids
    "prednisolone": "CORTICOSTEROID",
    "prednisone": "CORTICOSTEROID",
    "dexamethasone": "CORTICOSTEROID",
    "triamcinolone": "CORTICOSTEROID",
    "methylprednisolone": "CORTICOSTEROID",
    "budesonide": "CORTICOSTEROID",
    # Penicillins
    "amoxicillin": "PENICILLIN",
    "ampicillin": "PENICILLIN",
    "amoxicillin clavulanate": "PENICILLIN",
    "penicillin g": "PENICILLIN",
    "clavulanate": "PENICILLIN",
    # Cephalosporins
    "cephalexin": "CEPHALOSPORIN",
    "cefazolin": "CEPHALOSPORIN",
    "cefovecin": "CEPHALOSPORIN",
    "cefpodoxime": "CEPHALOSPORIN",
    # Fluoroquinolones
    "enrofloxacin": "FLUOROQUINOLONE",
    "marbofloxacin": "FLUOROQUINOLONE",
    "ciprofloxacin": "FLUOROQUINOLONE",
    "orbifloxacin": "FLUOROQUINOLONE",
    # Macrolides
    "erythromycin": "MACROLIDE",
    "azithromycin": "MACROLIDE",
    "clarithromycin": "MACROLIDE",
    "tylosin": "MACROLIDE",
    # Aminoglycosides
    "gentamicin": "AMINOGLYCOSIDE",
    "amikacin": "AMINOGLYCOSIDE",
    "neomycin": "AMINOGLYCOSIDE",
    "tobramycin": "AMINOGLYCOSIDE",
    # Other classes
    "metronidazole": "METRONIDAZOLE",
    "doxycycline": "TETRACYCLINE",
    "tetracycline": "TETRACYCLINE",
    "furosemide": "LOOP_DIURETIC",
    "enalapril": "ACE_INHIBITOR",
    "benazepril": "ACE_INHIBITOR",
    "tramadol": "OPIOID",
    "buprenorphine": "OPIOID",
    "phenobarbital": "BARBITURATE",
    "theophylline": "THEOPHYLLINE",
    "maropitant": "ANTIEMETIC",
}

# Human-readable class labels for reports.
CLASS_LABELS: dict[str, str] = {
    "NSAID": "NSAID",
    "CORTICOSTEROID": "corticosteroid",
    "PENICILLIN": "penicillin antibiotic",
    "CEPHALOSPORIN": "cephalosporin antibiotic",
    "FLUOROQUINOLONE": "fluoroquinolone antibiotic",
    "MACROLIDE": "macrolide antibiotic",
    "AMINOGLYCOSIDE": "aminoglycoside antibiotic",
    "METRONIDAZOLE": "nitroimidazole (metronidazole)",
    "TETRACYCLINE": "tetracycline antibiotic",
    "LOOP_DIURETIC": "loop diuretic",
    "ACE_INHIBITOR": "ACE inhibitor",
    "OPIOID": "opioid",
    "BARBITURATE": "barbiturate",
    "THEOPHYLLINE": "theophylline",
    "ANTIEMETIC": "antiemetic",
}

# class-pair interaction rules. `a`/`b` are symmetric.
INTERACTIONS: list[dict] = [
    {
        "a": "NSAID", "b": "NSAID", "severity": "high",
        "summary": "Concurrent NSAID therapy (e.g. Meloxicam with Carprofen) markedly increases the risk of gastrointestinal ulceration, perforation and renal injury.",
        "guidance": "Discontinue one NSAID; allow a washout period before switching agents. Add a gastroprotectant if continued.",
    },
    {
        "a": "NSAID", "b": "CORTICOSTEROID", "severity": "high",
        "summary": "NSAIDs combined with corticosteroids significantly raise the risk of GI ulceration and bleeding.",
        "guidance": "Avoid co-administration. If unavoidable, use a gastroprotectant (e.g. omeprazole) and monitor for melena/anemia.",
    },
    {
        "a": "NSAID", "b": "AMINOGLYCOSIDE", "severity": "high",
        "summary": "NSAIDs with aminoglycoside antibiotics increase the risk of nephrotoxicity.",
        "guidance": "Monitor renal values and hydration; adjust aminoglycoside dosing intervals.",
    },
    {
        "a": "NSAID", "b": "FLUOROQUINOLONE", "severity": "medium",
        "summary": "High-dose NSAIDs with fluoroquinolones may lower the seizure threshold and cause CNS stimulation.",
        "guidance": "Use with caution, especially in seizure-prone patients; monitor for tremors or agitation.",
    },
    {
        "a": "NSAID", "b": "LOOP_DIURETIC", "severity": "medium",
        "summary": "NSAIDs can blunt diuretic effect and increase dehydration and renal risk.",
        "guidance": "Monitor hydration and renal function; ensure adequate water intake.",
    },
    {
        "a": "NSAID", "b": "ACE_INHIBITOR", "severity": "medium",
        "summary": "NSAID with ACE-inhibitor combinations increase the risk of renal impairment.",
        "guidance": "Monitor renal values; avoid in dehydrated or hypotensive patients.",
    },
    {
        "a": "FLUOROQUINOLONE", "b": "THEOPHYLLINE", "severity": "high",
        "summary": "Fluoroquinolones raise theophylline levels, risking toxicity (tachycardia, vomiting, seizures).",
        "guidance": "Reduce theophylline dose or monitor serum levels; watch for toxicity signs.",
    },
    {
        "a": "MACROLIDE", "b": "THEOPHYLLINE", "severity": "high",
        "summary": "Macrolides (e.g. erythromycin) increase theophylline concentrations and toxicity risk.",
        "guidance": "Monitor for theophylline toxicity; reduce dose or avoid combination.",
    },
    {
        "a": "AMINOGLYCOSIDE", "b": "LOOP_DIURETIC", "severity": "high",
        "summary": "Aminoglycosides with loop diuretics increase ototoxicity and nephrotoxicity.",
        "guidance": "Avoid combination; if required, monitor renal function and hearing.",
    },
    {
        "a": "CORTICOSTEROID", "b": "LOOP_DIURETIC", "severity": "medium",
        "summary": "Corticosteroids with loop diuretics can cause potassium depletion.",
        "guidance": "Monitor electrolytes during combined therapy.",
    },
    {
        "a": "BARBITURATE", "b": "CORTICOSTEROID", "severity": "medium",
        "summary": "Phenobarbital induces corticosteroid metabolism, reducing therapeutic effect.",
        "guidance": "Consider dose adjustments; monitor clinical response.",
    },
    {
        "a": "PENICILLIN", "b": "NSAID", "severity": "low",
        "summary": "Penicillins (e.g. amoxicillin) and NSAIDs do not have a clinically significant interaction.",
        "guidance": "None — safe to co-administer.",
    },
    {
        "a": "PENICILLIN", "b": "CORTICOSTEROID", "severity": "low",
        "summary": "Penicillins and corticosteroids are generally safe in combination.",
        "guidance": "None.",
    },
    {
        "a": "METRONIDAZOLE", "b": "OPIOID", "severity": "low",
        "summary": "Metronidazole with opioids has no clinically significant interaction in dogs.",
        "guidance": "None.",
    },
    {
        "a": "FLUOROQUINOLONE", "b": "ANTIEMETIC", "severity": "low",
        "summary": "Fluoroquinolones and maropitant are generally safe together.",
        "guidance": "None.",
    },
]

# Retrieval documents (the "indexed manual"). `text` is what gets embedded and
# semantically searched; used to show which references the RAG agent pulled up.
MONOGRAPHS: list[dict] = [
    {
        "id": "mono-meloxicam",
        "text": "Meloxicam (Metacam). Drug class: NSAID — non-steroidal anti-inflammatory drug. Indications: analgesia, inflammation, osteoarthritis, musculoskeletal pain. Veterinary safety notes: NSAIDs combined with other NSAIDs, corticosteroids, aminoglycosides, ACE inhibitors or loop diuretics increase the risk of gastrointestinal ulceration, bleeding and renal injury. Contraindicated in dehydrated, hypotensive or renally impaired patients. Long-term use requires periodic renal and liver monitoring.",
    },
    {
        "id": "mono-carprofen",
        "text": "Carprofen (Rimadyl). Drug class: NSAID. Indications: postoperative and chronic pain, inflammation. Safety notes: do not combine with other NSAIDs or corticosteroids due to GI ulceration risk. Use with caution with loop diuretics and ACE inhibitors.",
    },
    {
        "id": "mono-amoxicillin",
        "text": "Amoxicillin. Drug class: penicillin (beta-lactam) antibiotic. Indications: bacterial skin, respiratory and urinary tract infections. Safety notes: broad-spectrum, well tolerated; no clinically significant interaction with NSAIDs or corticosteroids. Hypersensitivity reactions possible.",
    },
    {
        "id": "mono-enrofloxacin",
        "text": "Enrofloxacin (Baytril). Drug class: fluoroquinolone antibiotic. Indications: Gram-negative and some Gram-positive infections. Safety notes: with NSAIDs may lower the seizure threshold; with theophylline raises theophylline levels (toxicity risk); avoid in growing large-breed puppies.",
    },
    {
        "id": "mono-prednisolone",
        "text": "Prednisolone. Drug class: corticosteroid. Indications: inflammatory and allergic conditions including atopic dermatitis. Safety notes: combining with NSAIDs significantly increases GI ulceration and bleeding risk; phenobarbital reduces its efficacy; may deplete potassium with loop diuretics.",
    },
    {
        "id": "mono-gentamicin",
        "text": "Gentamicin. Drug class: aminoglycoside antibiotic. Indications: serious Gram-negative infections. Safety notes: nephrotoxicity increased by NSAIDs; ototoxicity and nephrotoxicity increased by loop diuretics such as furosemide. Monitor renal values.",
    },
    {
        "id": "mono-theophylline",
        "text": "Theophylline. Drug class: bronchodilator (methylxanthine). Indications: airway disease. Safety notes: fluoroquinolones and macrolides raise theophylline serum levels, increasing the risk of toxicity manifested as tachycardia, vomiting, tremors and seizures.",
    },
    {
        "id": "mono-erythromycin",
        "text": "Erythromycin. Drug class: macrolide antibiotic. Indications: bacterial infections; also has prokinetic effects. Safety notes: raises theophylline levels (toxicity risk) and may alter GI motility.",
    },
]

# Severity → how the UI should treat it.
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
