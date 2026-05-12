import random
import pandas as pd
import numpy as np

# ======================================================
# 1. GLOBAL SETTINGS
# ======================================================
NUM_CLIENTS = 1200
NUM_COUNSELORS = 200
COUNSELORS_PER_CLIENT = 60

random.seed(42)
np.random.seed(42)

# ======================================================
# 2. VALUE POOLS
# ======================================================
GENDERS = ["Male", "Female"]
ETHNICITIES = ["Malay", "Chinese", "Indian", "Other"]
LANGUAGES = ["English", "Malay", "Mandarin", "Tamil"]
ISSUES = ["Anxiety", "Depression", "Stress", "Trauma"]
MODALITIES = ["CBT", "Humanistic", "Mindfulness", "REBT"]

# ======================================================
# 3. HELPER FUNCTIONS
# ======================================================
def generate_experience_years(age):
    max_exp = max(1, age - 23)

    if max_exp < 8:
        return random.randint(1, max_exp)

    if random.random() < 0.7:
        return random.randint(1, 7)
    else:
        return random.randint(8, min(20, max_exp))

# ======================================================
# 4. ISSUE SIMILARITY
# ======================================================
ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety":1.0,"Stress":0.7,"Trauma":0.6,"Depression":0.6},
    "Stress":     {"Stress":1.0,"Anxiety":0.7,"Trauma":0.6,"Depression":0.5},
    "Trauma":     {"Trauma":1.0,"Stress":0.6,"Anxiety":0.6,"Depression":0.6},
    "Depression": {"Depression":1.0,"Anxiety":0.6,"Stress":0.5,"Trauma":0.6}
}

# Clinical evidence: how well each modality treats each issue
MODALITY_ISSUE_FIT = {
    "Anxiety":    {"CBT": 1.0, "Mindfulness": 0.8, "REBT": 0.7, "Humanistic": 0.5},
    "Depression": {"CBT": 1.0, "Mindfulness": 0.8, "Humanistic": 0.6, "REBT": 0.6},
    "Stress":     {"Mindfulness": 1.0, "CBT": 0.7, "Humanistic": 0.7, "REBT": 0.5},
    "Trauma":     {"CBT": 1.0, "Humanistic": 0.6, "Mindfulness": 0.5, "REBT": 0.3},
}

# ======================================================
# 5. GENERATE CLIENTS
# ======================================================
clients = []

for i in range(NUM_CLIENTS):
    clients.append({
        "client_id": i,
        "client_age": random.randint(18, 65),

        "client_gender": random.choices(GENDERS, weights=[0.48, 0.52])[0],

        "client_ethnicity": random.choices(
            ETHNICITIES, weights=[0.6, 0.25, 0.1, 0.05]
        )[0],

        "client_issue": random.choices(
            ISSUES, weights=[0.35, 0.3, 0.25, 0.1]
        )[0],

        "previous_counseling_experience": np.random.choice([0, 1], p=[0.6, 0.4]),

        "preferred_language": random.choices(
            LANGUAGES, weights=[0.5, 0.3, 0.15, 0.05]
        )[0],

        "preferred_modality": random.choices(
            MODALITIES, weights=[0.4, 0.25, 0.2, 0.15]
        )[0],

        "preferred_counselor_gender": random.choice(["No preference", "Male", "Female"]),
    })

# ======================================================
# 6. GENERATE COUNSELORS (FIXED)
# ======================================================
counselors = []

for i in range(NUM_COUNSELORS):
    age = random.randint(25, 65)

    exp = generate_experience_years(age)
    exp = min(exp, age - 23)
    exp = max(1, exp)

    counselors.append({
        "counselor_id": i,
        "counselor_age": age,

        "counselor_gender": random.choices(GENDERS, weights=[0.48, 0.52])[0],

        "counselor_ethnicity": random.choices(
            ETHNICITIES, weights=[0.6, 0.25, 0.1, 0.05]
        )[0],

        # ✅ MULTI-LANGUAGE (MAX 2)
        "counselor_language": ", ".join(
            random.sample(LANGUAGES, k=random.choice([1, 2]))
        ),

        "specialization": random.choices(
            ISSUES, weights=[0.35, 0.3, 0.25, 0.1]
        )[0],

        "counselor_modality": random.choices(
            MODALITIES, weights=[0.4, 0.25, 0.2, 0.15]
        )[0],

        "experience_years": exp
    })

# ======================================================
# 7. GENERATE PAIRS & LABEL (FIXED)
# ======================================================
rows = []
MAX_SCORE = 75  # 26 + 6 + 6 + 8 + 6 + 9 (trauma exp) + 14 (modality fit)

for client in clients:
    for counselor in random.sample(counselors, COUNSELORS_PER_CLIENT):

        # ✅ FIXED LANGUAGE FILTER
        counselor_langs = counselor["counselor_language"].split(", ")

        if client["preferred_language"] not in counselor_langs:
            continue  # REMOVE invalid pairs

        S = 0

        # Issue similarity
        sim = ISSUE_SIMILARITY[client["client_issue"]][counselor["specialization"]]
        S += 26 * sim

        # Modality preference match
        if client["preferred_modality"] == counselor["counselor_modality"]:
            S += 5 + sim
        else:
            S += 1 + sim

        # Previous experience
        S += 6 if client["previous_counseling_experience"] == 1 else 3

        # Gender
        preferred = client["preferred_counselor_gender"]
        c_gender = counselor["counselor_gender"]
        if preferred == "No preference":
            S += 5
        elif preferred == c_gender:
            S += 8
        else:
            S += 2

        # Ethnicity
        if client["client_ethnicity"] == counselor["counselor_ethnicity"]:
            S += 6
        else:
            S += 2

        # Experience bonus - weighted by clinical complexity of the issue
        if client["client_issue"] == "Trauma":
            S += min(counselor["experience_years"], 15) * 0.6  # up to 9 pts
        elif client["client_issue"] == "Depression":
            S += min(counselor["experience_years"], 12) * 0.5  # up to 6 pts
        else:
            S += min(counselor["experience_years"], 10) * 0.3  # up to 3 pts

        # Clinical modality-issue fit (evidence-based)
        fit = MODALITY_ISSUE_FIT[client["client_issue"]][counselor["counselor_modality"]]
        S += 14 * fit  # up to 14 pts

        # ======================================================
        # FINAL LABEL
        # ======================================================
        base_prob = S / MAX_SCORE
        base_prob += random.uniform(-0.05, 0.05)
        final_prob = max(0.05, min(0.95, base_prob))

        if final_prob > 0.65:
            match_success = 1
        elif final_prob < 0.55:
            match_success = 0
        else:
            match_success = np.random.binomial(1, final_prob)

        rows.append({
            **client,
            **counselor,
            "match_success": match_success
        })

# ======================================================
# 8. SAVE DATASET
# ======================================================
df = pd.DataFrame(rows)
df.to_csv("client_counselor_dataset.csv", index=False)

print("Dataset generated successfully!")
print("Total rows:", len(df))
print("Match distribution:")
print(df["match_success"].value_counts(normalize=True))