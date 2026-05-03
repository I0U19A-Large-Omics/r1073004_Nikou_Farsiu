import vcfpy
import pandas as pd
import sqlite3
import sys
import os

# get input and output from command line arguments
vcf_file = sys.argv[1]
db_file = sys.argv[2]

# lists to collect rows for each table
snp_rows = []
effect_rows = []
call_rows = []

# unique id for each snp
snp_id = 0

print("reading vcf file...")

reader = vcfpy.Reader.from_path(vcf_file)

for record in reader:
    snp_id += 1

    # --- SNP table ---
    # basic info about the variant
    chrom = record.CHROM
    pos = record.POS
    ref = record.REF
    alt = str(record.ALT[0].value)
    qual = record.QUAL

    snp_rows.append({
        "snp_id": snp_id,
        "chrom": chrom,
        "pos": pos,
        "ref": ref,
        "alt": alt,
        "qual": qual
    })

    # --- Effect table ---
    # parse the ANN field from snpEff
    # ANN contains multiple effects separated by comma
    # each effect has 16 subfields separated by |
    ann_field = record.INFO.get("ANN", [])
    for ann in ann_field:
        parts = ann.split("|")
        if len(parts) >= 4:
            effect_rows.append({
                "snp_id": snp_id,
                "effect_type": parts[1],
                "impact": parts[2],
                "gene": parts[3]
            })

    # --- Call table ---
    # one row per sample per SNP
    for call in record.calls:
        genotype = call.data.get("GT", "./.")
        call_rows.append({
            "snp_id": snp_id,
            "sample": call.sample.replace("020.aligned/", "").replace(".bam", ""),
            "genotype": genotype
        })

reader.close()

print(f"found {len(snp_rows)} snps")
print(f"found {len(effect_rows)} effects")
print(f"found {len(call_rows)} calls")

# build dataframes
snp_df = pd.DataFrame(snp_rows)
effect_df = pd.DataFrame(effect_rows)
call_df = pd.DataFrame(call_rows)

# write to sqlite database
os.makedirs(os.path.dirname(db_file), exist_ok=True)

conn = sqlite3.connect(db_file)

snp_df.to_sql("SNP", conn, if_exists="replace", index=False)
effect_df.to_sql("Effect", conn, if_exists="replace", index=False)
call_df.to_sql("Call", conn, if_exists="replace", index=False)

conn.close()

print("database created successfully at", db_file)
