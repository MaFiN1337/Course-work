import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("merged.csv")

def format_size(size):
    if size >= 1_000_000:
        return f"{size / 1_000_000:g}M"
    return f"{size // 1_000}k"

df['size_label'] = df['db_size'].apply(format_size)

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12})

df_delete = df[df['test_name'] == '6_MASS_DELETE'].sort_values('db_size')
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_delete, x='size_label', y='avg_time_ms', hue='db_engine', markers=True, dashes=False, linewidth=2, markersize=8)
plt.title("Ефективність масового видалення (MASS DELETE)", fontsize=14, fontweight="bold")
plt.xlabel("Розмір бази даних", fontsize=12)
plt.ylabel("Середній час (мс)", fontsize=12)
plt.xticks(rotation=45)
plt.legend(title="СУБД")
plt.tight_layout()
plt.savefig("2_2_mass_delete.png", dpi=300)
plt.close()

df_join_sub = df[df['test_name'].isin(['3_SUBQUERY', '4_JOIN_INSTEAD_OF_SUBQUERY'])].copy()
df_join_sub['Query_Type'] = df_join_sub['test_name'].str.replace(r'^\d+_', '', regex=True)
df_join_sub = df_join_sub.sort_values('db_size')

plt.figure(figsize=(12, 6))
sns.lineplot(data=df_join_sub, x='size_label', y='avg_time_ms', hue='db_engine', style='Query_Type', markers=True, linewidth=2, markersize=8)
plt.title("Порівняння ефективності JOIN та вкладених SELECT (Subquery)", fontsize=14, fontweight="bold")
plt.xlabel("Розмір бази даних", fontsize=12)
plt.ylabel("Середній час (мс)", fontsize=12)
plt.xticks(rotation=45)
plt.legend(title="СУБД та Запит", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("2_3_join_vs_subquery.png", dpi=300)
plt.close()

df_pragma = df[(df['db_engine'].str.contains('sqlite')) & (df['test_name'] == '2_JOIN_4_TABLES')].sort_values('db_size')
plt.figure(figsize=(10, 6))
sns.lineplot(data=df_pragma, x='size_label', y='avg_time_ms', hue='db_engine', markers=["o", "s"], dashes=False, linewidth=2.5, markersize=10, palette=["red", "green"])
plt.title("Вплив PRAGMA-налаштувань на складні вибірки (JOIN 4 TABLES)", fontsize=14, fontweight="bold")
plt.xlabel("Розмір бази даних", fontsize=12)
plt.ylabel("Середній час (мс)", fontsize=12)
plt.xticks(rotation=45)
plt.legend(title="Конфігурація SQLite")
plt.tight_layout()
plt.savefig("2_4_pragma_impact.png", dpi=300)
plt.close()