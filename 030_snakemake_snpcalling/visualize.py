import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

db_file = sys.argv[1]
output_dir = sys.argv[2]

os.makedirs(output_dir, exist_ok=True)

conn = sqlite3.connect(db_file)

# ── Figure 1 — SNP impact severity per sample ──────────────────────────────
# grouped bar chart showing number of SNPs per impact category per sample
# using a join of SNP, Effect, and Call tables

query1 = """
SELECT c.sample, e.impact, COUNT(DISTINCT s.snp_id) as count
FROM SNP s
JOIN Effect e ON s.snp_id = e.snp_id
JOIN Call c ON s.snp_id = c.snp_id
WHERE c.genotype NOT IN ('./.', '0/0')
GROUP BY c.sample, e.impact
"""

df1 = pd.read_sql_query(query1, conn)

# order impact categories as required
impact_order = ["HIGH", "MODERATE", "LOW", "MODIFIER"]
df1["impact"] = pd.Categorical(df1["impact"], categories=impact_order, ordered=True)
df1 = df1.sort_values("impact")

# colorblind safe palette - blue and orange
palette = {"TLE66_N": "#0072B2", "TLE66_T": "#E69F00"}

fig1, ax1 = plt.subplots(figsize=(8, 5))
sns.barplot(
    data=df1,
    x="impact",
    y="count",
    hue="sample",
    palette=palette,
    ax=ax1
)

ax1.set_xlabel("Impact Category", fontsize=13)
ax1.set_ylabel("Number of SNPs", fontsize=13)
ax1.set_title("SNP Impact Severity per Sample", fontsize=15)
ax1.set_ylim(0, None)
ax1.legend(title="Sample", fontsize=11)
plt.tight_layout()
fig1.savefig(f"{output_dir}/fig1_impact_severity.svg")
fig1.savefig(f"{output_dir}/fig1_impact_severity.png")
print("saved fig1")

# ── Figure 2 — Shared vs unique SNPs between samples ──────────────────────
# a stacked bar chart is clearest here because it shows both total counts
# and the proportion shared/unique in one glance - more informative than a venn diagram
# for two samples with very different counts

query2 = """
SELECT snp_id,
    SUM(CASE WHEN sample = 'TLE66_N' AND genotype NOT IN ('./.', '0/0') THEN 1 ELSE 0 END) as in_normal,
    SUM(CASE WHEN sample = 'TLE66_T' AND genotype NOT IN ('./.', '0/0') THEN 1 ELSE 0 END) as in_tumor
FROM Call
GROUP BY snp_id
"""

df2 = pd.read_sql_query(query2, conn)

only_normal = ((df2["in_normal"] > 0) & (df2["in_tumor"] == 0)).sum()
only_tumor = ((df2["in_normal"] == 0) & (df2["in_tumor"] > 0)).sum()
shared = ((df2["in_normal"] > 0) & (df2["in_tumor"] > 0)).sum()

categories = ["Normal only", "Shared", "Tumor only"]
counts = [only_normal, shared, only_tumor]
colors = ["#0072B2", "#999999", "#E69F00"]

fig2, ax2 = plt.subplots(figsize=(6, 5))
bars = ax2.bar(categories, counts, color=colors)
ax2.set_ylabel("Number of SNPs", fontsize=13)
ax2.set_xlabel("SNP Category", fontsize=13)
ax2.set_title("Shared vs Unique SNPs between Samples", fontsize=15)
ax2.set_ylim(0, None)

for bar, count in zip(bars, counts):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
             str(count), ha="center", fontsize=11)

plt.tight_layout()
fig2.savefig(f"{output_dir}/fig2_shared_vs_unique.svg")
fig2.savefig(f"{output_dir}/fig2_shared_vs_unique.png")
print("saved fig2")

conn.close()
print("done!")
