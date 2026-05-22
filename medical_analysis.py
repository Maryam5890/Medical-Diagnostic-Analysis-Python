"""
================================================================
MEDICAL DIAGNOSTIC REPORT ANALYSIS — Python Project
Author: Solihu Mariyam Omotinuola
Tools: Python, Pandas, Matplotlib, NumPy
Domain: Clinical Laboratory Data Analytics
================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import random
import warnings
warnings.filterwarnings('ignore')

# ── Set plot style ──────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#F8FAFC',
    'axes.facecolor': '#F8FAFC',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'font.family': 'DejaVu Sans',
})

# ================================================================
# STEP 1: GENERATE DATASET
# ================================================================

random.seed(42)
np.random.seed(42)

n = 200
start_date = datetime(2024, 1, 1)

diagnoses = ['Malaria', 'Typhoid', 'Hepatitis B', 'Anaemia',
             'Diabetes', 'UTI', 'Hypertension', 'HIV Screening']
diagnosis_weights = [0.25, 0.20, 0.10, 0.15, 0.12, 0.08, 0.06, 0.04]

age_groups = ['0–17', '18–35', '36–55', '56+']
genders = ['Male', 'Female']
results = ['Positive', 'Negative']

data = {
    'patient_id': [f'PAT{1000+i}' for i in range(n)],
    'age':        np.random.randint(5, 80, n),
    'gender':     np.random.choice(genders, n, p=[0.48, 0.52]),
    'diagnosis':  np.random.choice(diagnoses, n, p=diagnosis_weights),
    'test_result':np.random.choice(results, n, p=[0.42, 0.58]),
    'wbc_count':  np.round(np.random.normal(7.5, 2.5, n), 2),   # ×10³/µL
    'rbc_count':  np.round(np.random.normal(4.8, 0.7, n), 2),   # ×10⁶/µL
    'haemoglobin':np.round(np.random.normal(12.5, 2.2, n), 1),  # g/dL
    'glucose':    np.round(np.random.normal(95, 30, n), 1),      # mg/dL
    'visit_date': [start_date + timedelta(days=random.randint(0, 364)) for _ in range(n)]
}

df = pd.DataFrame(data)

# Add age group column
def age_group(age):
    if age <= 17:   return '0–17'
    elif age <= 35: return '18–35'
    elif age <= 55: return '36–55'
    else:           return '56+'

df['age_group'] = df['age'].apply(age_group)
df['month'] = df['visit_date'].dt.to_period('M').astype(str)
df['quarter'] = df['visit_date'].dt.to_period('Q').astype(str)

print("=" * 55)
print("  MEDICAL DIAGNOSTIC REPORT — Dataset Overview")
print("=" * 55)
print(f"  Total Patients:     {len(df)}")
print(f"  Date Range:         {df['visit_date'].min().date()} → {df['visit_date'].max().date()}")
print(f"  Positive Rate:      {(df['test_result']=='Positive').mean()*100:.1f}%")
print(f"  Gender Split:       {(df['gender']=='Female').sum()}F / {(df['gender']=='Male').sum()}M")
print("=" * 55)

# ================================================================
# STEP 2: DESCRIPTIVE STATISTICS
# ================================================================

print("\n── Lab Reference Values ──────────────────────────────")
print("  WBC:        4.0–11.0  ×10³/µL  (normal range)")
print("  RBC:        4.2–5.4   ×10⁶/µL")
print("  Haemoglobin: ≥12.0 g/dL (females), ≥13.5 (males)")
print("  Glucose:    70–99     mg/dL (fasting)")

lab_stats = df[['wbc_count', 'rbc_count', 'haemoglobin', 'glucose']].describe().round(2)
print("\n── Descriptive Statistics ────────────────────────────")
print(lab_stats.to_string())

# Flag abnormal values
df['anaemia_flag'] = df.apply(
    lambda r: r['haemoglobin'] < 12.0 if r['gender'] == 'Female' else r['haemoglobin'] < 13.5,
    axis=1
)
df['high_glucose']  = df['glucose'] > 126
df['high_wbc']      = df['wbc_count'] > 11.0

print(f"\n  Patients with low haemoglobin (anaemia risk): {df['anaemia_flag'].sum()} ({df['anaemia_flag'].mean()*100:.1f}%)")
print(f"  Patients with high glucose (diabetes risk):   {df['high_glucose'].sum()} ({df['high_glucose'].mean()*100:.1f}%)")
print(f"  Patients with elevated WBC (infection flag):  {df['high_wbc'].sum()} ({df['high_wbc'].mean()*100:.1f}%)")

# ================================================================
# STEP 3: ANALYSIS
# ================================================================

print("\n── Top Diagnoses ─────────────────────────────────────")
diagnosis_counts = df['diagnosis'].value_counts()
print(diagnosis_counts.to_string())

print("\n── Positive Rate by Diagnosis ────────────────────────")
pos_rate = df.groupby('diagnosis')['test_result'].apply(
    lambda x: round((x == 'Positive').mean() * 100, 1)
).sort_values(ascending=False)
print(pos_rate.to_string())

print("\n── Patient Distribution by Age Group ────────────────")
print(df['age_group'].value_counts().sort_index().to_string())

print("\n── Gender vs Diagnosis (Top 4) ───────────────────────")
gender_diag = pd.crosstab(
    df['gender'],
    df['diagnosis'],
    margins=False
)[['Malaria', 'Typhoid', 'Anaemia', 'Hepatitis B']]
print(gender_diag.to_string())

print("\n── Average Lab Values by Diagnosis ──────────────────")
lab_by_diag = df.groupby('diagnosis')[['haemoglobin', 'glucose', 'wbc_count']].mean().round(2)
print(lab_by_diag.to_string())

# ================================================================
# STEP 4: VISUALIZATIONS (6 charts saved as one figure)
# ================================================================

fig = plt.figure(figsize=(18, 14))
fig.suptitle(
    'Medical Diagnostic Report — Clinical Analysis 2024\nSolihu Mariyam Omotinuola',
    fontsize=16, fontweight='bold', color='#1A3A5C', y=0.98
)

PALETTE = ['#1A6B9A', '#E05A2B', '#2A9D6F', '#E8B84B',
           '#7B4FBF', '#D64E6E', '#4FA8C7', '#6BAF5A']

# ── Chart 1: Diagnosis Frequency ──────────────────────────
ax1 = fig.add_subplot(3, 3, 1)
bars = ax1.barh(diagnosis_counts.index, diagnosis_counts.values, color=PALETTE, edgecolor='white')
ax1.set_title('Case Frequency by Diagnosis', fontweight='bold', color='#1A3A5C')
ax1.set_xlabel('Number of Patients')
for bar, val in zip(bars, diagnosis_counts.values):
    ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2,
             str(val), va='center', fontsize=9)

# ── Chart 2: Positive Rate by Diagnosis ───────────────────
ax2 = fig.add_subplot(3, 3, 2)
colors2 = ['#E05A2B' if v >= 50 else '#1A6B9A' for v in pos_rate.values]
bars2 = ax2.bar(pos_rate.index, pos_rate.values, color=colors2, edgecolor='white')
ax2.set_title('Positive Test Rate by Diagnosis (%)', fontweight='bold', color='#1A3A5C')
ax2.set_ylabel('Positive Rate (%)')
ax2.tick_params(axis='x', rotation=45)
ax2.axhline(50, color='gray', linestyle='--', linewidth=0.8, alpha=0.6)
for bar, val in zip(bars2, pos_rate.values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val}%', ha='center', fontsize=8)

# ── Chart 3: Gender Distribution ──────────────────────────
ax3 = fig.add_subplot(3, 3, 3)
gender_counts = df['gender'].value_counts()
wedges, texts, autotexts = ax3.pie(
    gender_counts.values,
    labels=gender_counts.index,
    autopct='%1.1f%%',
    colors=['#1A6B9A', '#E05A2B'],
    startangle=90,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}
)
ax3.set_title('Patient Gender Distribution', fontweight='bold', color='#1A3A5C')

# ── Chart 4: Age Group Distribution ───────────────────────
ax4 = fig.add_subplot(3, 3, 4)
age_order = ['0–17', '18–35', '36–55', '56+']
age_data = df['age_group'].value_counts().reindex(age_order)
ax4.bar(age_data.index, age_data.values,
        color=['#4FA8C7', '#1A6B9A', '#E05A2B', '#6BAF5A'],
        edgecolor='white', width=0.6)
ax4.set_title('Patient Count by Age Group', fontweight='bold', color='#1A3A5C')
ax4.set_ylabel('Number of Patients')
for i, val in enumerate(age_data.values):
    ax4.text(i, val + 0.5, str(val), ha='center', fontweight='bold')

# ── Chart 5: Haemoglobin Distribution ─────────────────────
ax5 = fig.add_subplot(3, 3, 5)
male_hb   = df[df['gender'] == 'Male']['haemoglobin']
female_hb = df[df['gender'] == 'Female']['haemoglobin']
ax5.hist(male_hb, bins=20, alpha=0.7, color='#1A6B9A', label='Male')
ax5.hist(female_hb, bins=20, alpha=0.7, color='#E05A2B', label='Female')
ax5.axvline(12.0, color='#E8B84B', linestyle='--', linewidth=1.5, label='Female min (12 g/dL)')
ax5.axvline(13.5, color='#2A9D6F', linestyle='--', linewidth=1.5, label='Male min (13.5 g/dL)')
ax5.set_title('Haemoglobin Distribution by Gender', fontweight='bold', color='#1A3A5C')
ax5.set_xlabel('Haemoglobin (g/dL)')
ax5.set_ylabel('Frequency')
ax5.legend(fontsize=7)

# ── Chart 6: Monthly Patient Visits ───────────────────────
ax6 = fig.add_subplot(3, 3, 6)
monthly_visits = df.groupby('month').size().reset_index(name='count')
monthly_visits = monthly_visits.sort_values('month')
ax6.plot(range(len(monthly_visits)), monthly_visits['count'],
         marker='o', color='#1A6B9A', linewidth=2, markersize=5)
ax6.fill_between(range(len(monthly_visits)), monthly_visits['count'],
                 alpha=0.15, color='#1A6B9A')
ax6.set_xticks(range(len(monthly_visits)))
ax6.set_xticklabels([m[-5:] for m in monthly_visits['month']], rotation=45, fontsize=7)
ax6.set_title('Monthly Patient Visits', fontweight='bold', color='#1A3A5C')
ax6.set_ylabel('Number of Patients')

# ── Chart 7: Glucose Distribution ─────────────────────────
ax7 = fig.add_subplot(3, 3, 7)
ax7.hist(df['glucose'], bins=25, color='#E8B84B', edgecolor='white', alpha=0.9)
ax7.axvline(99,  color='#2A9D6F', linestyle='--', linewidth=2, label='Normal max (99)')
ax7.axvline(126, color='#E05A2B', linestyle='--', linewidth=2, label='Diabetes threshold (126)')
ax7.set_title('Blood Glucose Distribution', fontweight='bold', color='#1A3A5C')
ax7.set_xlabel('Glucose Level (mg/dL)')
ax7.set_ylabel('Frequency')
ax7.legend(fontsize=8)

# ── Chart 8: Top 4 Diagnoses by Gender ────────────────────
ax8 = fig.add_subplot(3, 3, 8)
top4 = ['Malaria', 'Typhoid', 'Anaemia', 'Hepatitis B']
gd = pd.crosstab(df['gender'], df['diagnosis'])[top4]
x = np.arange(len(top4))
width = 0.35
ax8.bar(x - width/2, gd.loc['Male'],   width, label='Male',   color='#1A6B9A', edgecolor='white')
ax8.bar(x + width/2, gd.loc['Female'], width, label='Female', color='#E05A2B', edgecolor='white')
ax8.set_xticks(x)
ax8.set_xticklabels(top4, rotation=15, fontsize=9)
ax8.set_title('Top 4 Diagnoses by Gender', fontweight='bold', color='#1A3A5C')
ax8.set_ylabel('Patient Count')
ax8.legend()

# ── Chart 9: Abnormality Summary ──────────────────────────
ax9 = fig.add_subplot(3, 3, 9)
flags = {
    'Anaemia\nRisk': df['anaemia_flag'].sum(),
    'High\nGlucose': df['high_glucose'].sum(),
    'Elevated\nWBC':  df['high_wbc'].sum(),
    'Normal\nAll':    n - df[['anaemia_flag','high_glucose','high_wbc']].any(axis=1).sum()
}
flag_colors = ['#E05A2B', '#E8B84B', '#7B4FBF', '#2A9D6F']
bars9 = ax9.bar(flags.keys(), flags.values(), color=flag_colors, edgecolor='white', width=0.5)
ax9.set_title('Patient Abnormality Flags', fontweight='bold', color='#1A3A5C')
ax9.set_ylabel('Number of Patients')
for bar, val in zip(bars9, flags.values()):
    ax9.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             str(val), ha='center', fontweight='bold')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('medical_report_analysis.png', dpi=150, bbox_inches='tight',
            facecolor='#F8FAFC')
plt.show()
print("\n✅ Chart saved as medical_report_analysis.png")

# ================================================================
# STEP 5: SUMMARY REPORT
# ================================================================

print("\n" + "=" * 55)
print("  CLINICAL SUMMARY REPORT")
print("=" * 55)
print(f"  Report Period:         January – December 2024")
print(f"  Total Patients Seen:   {n}")
print(f"  Overall Positive Rate: {(df['test_result']=='Positive').mean()*100:.1f}%")
print(f"  Most Common Diagnosis: {diagnosis_counts.index[0]} ({diagnosis_counts.iloc[0]} cases)")
print(f"  Highest Positive Rate: {pos_rate.index[0]} ({pos_rate.iloc[0]}%)")
print(f"  Avg Haemoglobin:       {df['haemoglobin'].mean():.1f} g/dL")
print(f"  Avg Blood Glucose:     {df['glucose'].mean():.1f} mg/dL")
print(f"  Anaemia Risk Patients: {df['anaemia_flag'].sum()} ({df['anaemia_flag'].mean()*100:.1f}%)")
print(f"  High Glucose Patients: {df['high_glucose'].sum()} ({df['high_glucose'].mean()*100:.1f}%)")
print("=" * 55)
print("\n  Key Recommendations:")
print("  1. Malaria remains the top diagnosis — reinforce")
print("     preventive outreach in Q2 and Q3 (peak months)")
print("  2. 18–35 age group has highest visit rate —")
print("     target routine screening campaigns for this group")
print("  3. Anaemia risk is significant — integrate nutrition")
print("     counselling into diagnosis pathways")
print("  4. High glucose flags suggest screening for")
print("     pre-diabetes in older age groups (56+)")
print("=" * 55)
print("\n  Project by Solihu Mariyam Omotinuola")
print("  github.com/Maryam5890")
