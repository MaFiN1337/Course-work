import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("blob_official_results_ubuntu.csv")

print("\nМАТРИЦЯ 2.1 - Відношення часу (FS Time / DB Time)")
print("=" * 80)

df_fs = df[df['storage_type'] == 'File System'][['blob_size_kb', 'total_time_sec']].set_index('blob_size_kb')
df_sql_2mb = df[(df['storage_type'] == 'SQLite') & (df['cache_mb'].astype(float) == 2)]
matrix = pivot_table = df_sql_2mb.pivot(index='blob_size_kb', columns='page_size_bytes', values='total_time_sec')

ratio_matrix = matrix.copy()
for col in ratio_matrix.columns:
    ratio_matrix[col] = df_fs['total_time_sec'] / matrix[col]

ratio_matrix = ratio_matrix.round(3)
ratio_matrix.columns = [f"{c} bytes" for c in ratio_matrix.columns]
print(ratio_matrix)
print("=" * 80)
ratio_matrix.to_csv("blob_ratio_matrix_ubuntu.csv")

# 2. ГРАФІК 1: Порівняння швидкості читання (FS vs SQLite 2MB)
plt.figure(figsize=(10, 6))
sns.set_theme(style="whitegrid")
sns.lineplot(data=df[df['storage_type'] == 'File System'], x='blob_size_kb', y='total_time_sec', 
             label='File System (Ext4/NTFS)', color='red', linewidth=3, marker='s')

colors = sns.color_palette("viridis", len(matrix.columns))
for i, page_size in enumerate(matrix.columns):
    subset = df_sql_2mb[df_sql_2mb['page_size_bytes'] == page_size]
    sns.lineplot(data=subset, x='blob_size_kb', y='total_time_sec', 
                 label=f'SQLite (Page: {page_size})', color=colors[i], linewidth=1.5, marker='o')

plt.title("Час читання 100 МБ даних: File System vs SQLite (2MB Cache)", fontsize=14, fontweight='bold')
plt.xlabel("Розмір об'єкта BLOB (КБ)", fontsize=12)
plt.ylabel("Загальний час читання (секунди) - МЕНШЕ КРАЩЕ", fontsize=12)
plt.xscale('log')
plt.xticks([10, 20, 50, 100, 200, 500, 1000], ['10', '20', '50', '100', '200', '500', '1000'])
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("2_5_blob_fs_vs_sqlite_ubuntu.png", dpi=300)
plt.close()

# 3. ГРАФІК 2: Вплив розміру кешу на читання (Page Size 16384)
df_cache = df[(df['storage_type'] == 'SQLite') & (df['page_size_bytes'].astype(float) == 16384)].copy()

plt.figure(figsize=(10, 6))
sns.lineplot(data=df_cache, x='blob_size_kb', y='total_time_sec', hue='cache_mb', 
             palette="coolwarm", linewidth=2.5, marker='o', markersize=8)

plt.title("Вплив обсягу кешу (PRAGMA cache_size) на швидкість читання\n(SQLite Page Size = 16384 Bytes)", fontsize=14, fontweight='bold')
plt.xlabel("Розмір об'єкта BLOB (КБ)", fontsize=12)
plt.ylabel("Загальний час читання (секунди)", fontsize=12)
plt.xscale('log')
plt.xticks([10, 20, 50, 100, 200, 500, 1000], ['10', '20', '50', '100', '200', '500', '1000'])
plt.legend(title="Розмір кешу (МБ)")
plt.tight_layout()
plt.savefig("2_5_blob_cache_impact_ubuntu.png", dpi=300)
plt.close()