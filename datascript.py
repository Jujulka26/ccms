import random
import pandas as pd
import numpy as np

# ======================================================
# 1. GLOBAL SETTINGS
# ======================================================
NUM_CLIENTS = 700
NUM_COUNSELORS = 120
COUNSELORS_PER_CLIENT = 40

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
    "Anxiety": {"Anxiety":1.0,"Stress":0.7,"Trauma":0.5,"Depression":0.6},
    "Stress": {"Stress":1.0,"Anxiety":0.7,"Trauma":0.6,"Depression":0.5},
    "Trauma": {"Trauma":1.0,"Stress":0.6,"Anxiety":0.5,"Depression":0.4},
    "Depression": {"Depression":1.0,"Anxiety":0.6,"Stress":0.5,"Trauma":0.4}
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
MAX_SCORE = 74

for client in clients:
    for counselor in random.sample(counselors, COUNSELORS_PER_CLIENT):

        # ✅ FIXED LANGUAGE FILTER
        counselor_langs = counselor["counselor_language"].split(", ")

        if client["preferred_language"] not in counselor_langs:
            continue  # REMOVE invalid pairs

        S = 0

        # Issue similarity
        sim = ISSUE_SIMILARITY[client["client_issue"]][counselor["specialization"]]
        S += 30 * sim

        # Modality
        if client["preferred_modality"] == counselor["counselor_modality"]:
            S += 15 + (5 * sim)
        else:
            S += 3 + (2 * sim)

        # Previous experience
        S += 6 if client["previous_counseling_experience"] == 1 else 3

        # Gender
        preferred = client["preferred_counselor_gender"]
        c_gender = counselor["counselor_gender"]
        if preferred == "No preference":
            S += 6
        elif preferred == c_gender:
            S += 10
        else:
            S += 2

        # Ethnicity
        if client["client_ethnicity"] == counselor["counselor_ethnicity"]:
            S += 5
        else:
            S += 3

        # Experience bonus
        S += min(counselor["experience_years"], 10) * 0.3

        # ======================================================
        # FINAL LABEL
        # ======================================================
        base_prob = S / MAX_SCORE
        base_prob += random.uniform(-0.05, 0.05)
        final_prob = max(0.05, min(0.95, base_prob))

        if final_prob > 0.70:
            match_success = 1
        elif final_prob < 0.50:
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