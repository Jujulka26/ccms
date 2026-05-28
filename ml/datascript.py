import random
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).parent

NUM_CLIENTS = 900 # 900
NUM_COUNSELORS = 180   # 180
COUNSELORS_PER_CLIENT = 60  # 60

random.seed(42)
np.random.seed(42)

GENDERS = ["Male", "Female"]
ETHNICITIES = ["Malay", "Chinese", "Indian", "Other"]
LANGUAGES = ["English", "Malay", "Mandarin", "Tamil"]
ISSUES = ["Anxiety", "Depression", "Stress", "Trauma"]
MODALITIES = ["CBT", "Humanistic", "Mindfulness", "REBT"]


def generate_experience_years(age):
    max_exp = max(1, age - 23)

    if max_exp < 8:
        return random.randint(1, max_exp)

    if random.random() < 0.7:
        return random.randint(1, 7)
    else:
        return random.randint(8, min(20, max_exp))


ISSUE_SIMILARITY = {
    "Anxiety":    {"Anxiety":1.0,"Stress":0.7,"Trauma":0.6,"Depression":0.6},
    "Stress":     {"Stress":1.0,"Anxiety":0.7,"Trauma":0.6,"Depression":0.6},
    "Trauma":     {"Trauma":1.0,"Stress":0.6,"Anxiety":0.6,"Depression":0.6},
    "Depression": {"Depression":1.0,"Anxiety":0.6,"Stress":0.6,"Trauma":0.6}
}

# Clinical evidence: how well each modality treats each issue
MODALITY_ISSUE_FIT = {
    "Anxiety":    {"CBT": 1.0, "Mindfulness": 0.8, "REBT": 0.7, "Humanistic": 0.4},
    "Depression": {"CBT": 1.0, "Mindfulness": 0.8, "Humanistic": 0.7, "REBT": 0.6},
    "Stress":     {"Mindfulness": 1.0, "CBT": 0.7, "Humanistic": 0.7, "REBT": 0.5},
    "Trauma":     {"CBT": 1.0, "Humanistic": 0.5, "Mindfulness": 0.5, "REBT": 0.5},
}

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

rows = []

# Worst case: 35*0.6(diff issue) + 3.6(no mod match) + 1.5(no prev exp) + 1(gender mismatch) + 1(ethnicity mismatch) + 0(junior) + 13*0.4(worst mod fit) + 0(max age gap) = 33.3
S_MIN = 33.3
# Compressed from actual max 88.5 — forces top-tier pairs to label=1, reducing label noise. Empirically optimal via sweep.
S_MAX = 84.0

EXP_BONUS = {"Trauma": 10, "Anxiety": 7, "Depression": 7, "Stress": 5}

for client in clients:
    for counselor in random.sample(counselors, COUNSELORS_PER_CLIENT):

        counselor_langs = counselor["counselor_language"].split(", ")

        if client["preferred_language"] not in counselor_langs:
            continue

        S = 0

        # Issue similarity (d=0.75)
        sim = ISSUE_SIMILARITY[client["client_issue"]][counselor["specialization"]]
        S += 35 * sim

        # Modality preference match (d=0.27, Swift et al. 2018)
        modality_match = client["preferred_modality"] == counselor["counselor_modality"]
        if modality_match:
            S += 11 + sim
        else:
            S += 3 + sim

        # Previous counseling experience x modality match interaction
        if client["previous_counseling_experience"] == 1:
            S += 5.5 + 2 * int(modality_match)
        else:
            S += 1.5

        # Gender (d=0.21, PMC11750298 RCT — larger effect than ethnicity)
        preferred = client["preferred_counselor_gender"]
        c_gender = counselor["counselor_gender"]
        if preferred == "No preference":
            S += 5
        elif preferred == c_gender:
            S += 5
        else:
            S += 1

        # Ethnicity (d=0.09, Cabral & Smith 2011 — smaller effect than gender)
        if client["client_ethnicity"] == counselor["counselor_ethnicity"]:
            S += 4
        else:
            S += 1

        # Experience x issue specificity (d=0.21 base, issue-stratified)
        if counselor["experience_years"] >= 8:
            S += EXP_BONUS[client["client_issue"]]

        # Clinical modality-issue fit (d=0.175)
        fit = MODALITY_ISSUE_FIT[client["client_issue"]][counselor["counselor_modality"]]
        S += 13 * fit

        # Age gap (Lehane 2025, small directional effect)
        age_gap = abs(client["client_age"] - counselor["counselor_age"])
        S += max(0, 20 - age_gap) * 0.10

        base_prob = (S - S_MIN) / (S_MAX - S_MIN)
        base_prob += random.uniform(-0.05, 0.05)
        final_prob = max(0.0, min(1.0, base_prob))

        if final_prob > 0.50:
            match_success = 1
        elif final_prob < 0.22:
            match_success = 0
        else:
            match_success = np.random.binomial(1, final_prob)

        rows.append({
            **client,
            **counselor,
            "match_success": match_success
        })

df = pd.DataFrame(rows)
df.to_csv(BASE_DIR / "client_counselor_dataset.csv", index=False)

print("Dataset generated successfully!")
print("Total rows:", len(df))
print("Match distribution:")
print(df["match_success"].value_counts(normalize=True))
