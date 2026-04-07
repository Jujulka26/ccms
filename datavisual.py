import pandas as pd
import matplotlib.pyplot as plt
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "figure.figsize": (10, 6),
    "axes.titlesize": 14,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
})


def show_bar_chart(series, title, xlabel, ylabel="Count", rotate=45):
    fig, ax = plt.subplots(figsize=(10, 5))
    series.plot(kind="bar", ax=ax, color="#4C72B0", edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=rotate)
    fig.tight_layout()
    plt.show()


def show_histogram(series, title, xlabel):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(series.dropna(), bins=20, color="#55A868", edgecolor="white", alpha=0.9)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    plt.show()

# =========================================================
# 1. LOAD DATA
# =========================================================
df = pd.read_csv("client_counselor_dataset.csv")

print("===== BASIC INFO =====")
print(df.info())

print("\n===== HEAD =====")
print(df.head())

print("\n===== DESCRIBE =====")
print(df.describe())

# =========================================================
# 2. TARGET DISTRIBUTION
# =========================================================
print("\n===== TARGET DISTRIBUTION =====")
print(df["match_success"].value_counts(normalize=True))

show_bar_chart(
    df["match_success"].value_counts().sort_index(),
    "Match Success Distribution",
    "Match (0 = No, 1 = Yes)",
)

# =========================================================
# 3. NUMERICAL DISTRIBUTIONS
# =========================================================
num_cols = ["client_age", "counselor_age", "experience_years"]

for col in num_cols:
    show_histogram(df[col], f"Distribution of {col}", col)

# =========================================================
# 4. CATEGORICAL DISTRIBUTION
# =========================================================
cat_cols = [
    "client_issue",
    "preferred_language",
    "preferred_modality",
    "counselor_language",
    "specialization"
]

for col in cat_cols:
    show_bar_chart(df[col].value_counts(), f"Distribution of {col}", col)

# =========================================================
# 5. CORRELATION WITH TARGET
# =========================================================
numeric_df = df.select_dtypes(include=["int64", "float64"])
target_corr = (
    numeric_df.corr(numeric_only=True)["match_success"]
    .drop("match_success")
    .sort_values(ascending=False)
    .to_frame(name="correlation_with_target")
)

print("\n===== CORRELATION WITH TARGET =====")
print(target_corr.round(2).to_string())

print("\nEDA Completed ✅")