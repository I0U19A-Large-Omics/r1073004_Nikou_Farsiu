import sqlite3
import sys

db_file = sys.argv[1]

conn = sqlite3.connect(db_file)

snp_count = conn.execute("SELECT COUNT(*) FROM SNP").fetchone()[0]
effect_count = conn.execute("SELECT COUNT(*) FROM Effect WHERE gene != ''").fetchone()[0]
call_count = conn.execute("SELECT COUNT(*) FROM Call WHERE genotype != './.';").fetchone()[0]

print("SNP count:", snp_count)
print("Effect count:", effect_count)
print("Call count:", call_count)

assert snp_count > 0, "ERROR: SNP table is empty!"
assert effect_count > 0, "ERROR: Effect table has no gene names!"
assert call_count > 0, "ERROR: Call table has no valid genotypes!"

print("all checks passed!")
conn.close()
