# ============================================================
# E-Commerce Sales & Customer Retention Analysis
# Step 1: Data Cleaning & EDA
# ============================================================

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 5)

# ---------- 1. LOAD DATA ----------
print("=" * 60)
print("STEP 1: Loading data...")
print("=" * 60)

df = pd.read_csv('../data/raw/superstore.xlsx', encoding='latin-1')
print(f"Loaded shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# ---------- 2. BASIC INFO ----------
print("\n" + "=" * 60)
print("STEP 2: Basic info")
print("=" * 60)
print(df.info())
print("\nNull values:\n", df.isnull().sum())
print("\nDuplicate rows:", df.duplicated().sum())

# ---------- 3. CLEANING ----------
print("\n" + "=" * 60)
print("STEP 3: Cleaning")
print("=" * 60)

df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Ship Date']  = pd.to_datetime(df['Ship Date'], errors='coerce')

before = len(df)
df = df.dropna(subset=['Order Date', 'Sales'])
print(f"Dropped {before - len(df)} rows with null dates/sales")

before = len(df)
df = df.drop_duplicates(subset=['Order ID', 'Product ID'])
print(f"Dropped {before - len(df)} duplicate rows")

df['Year']         = df['Order Date'].dt.year
df['Month']        = df['Order Date'].dt.month
df['YearMonth']    = df['Order Date'].dt.to_period('M').astype(str)
df['ShipDays']     = (df['Ship Date'] - df['Order Date']).dt.days
df['ProfitMargin'] = np.where(df['Sales'] > 0, df['Profit'] / df['Sales'], 0)

print(f"Final cleaned shape: {df.shape}")

# ---------- 4. SAVE CLEANED DATA ----------
os.makedirs('../data/cleaned', exist_ok=True)
df.to_csv('../data/cleaned/superstore_clean.csv', index=False)
print("\n[OK] Saved cleaned data to data/cleaned/superstore_clean.csv")

# ---------- 5. KPIs ----------
print("\n" + "=" * 60)
print("STEP 4: KEY PERFORMANCE INDICATORS")
print("=" * 60)

total_sales      = df['Sales'].sum()
total_profit     = df['Profit'].sum()
total_orders     = df['Order ID'].nunique()
total_customers  = df['Customer ID'].nunique()
avg_order_value  = total_sales / total_orders

print(f"Total Sales:      ${total_sales:,.2f}")
print(f"Total Profit:     ${total_profit:,.2f}")
print(f"Total Orders:     {total_orders:,}")
print(f"Total Customers:  {total_customers:,}")
print(f"Avg Order Value:  ${avg_order_value:,.2f}")

# ---------- 6. CHART: MONTHLY SALES ----------
os.makedirs('../images', exist_ok=True)

monthly = df.groupby('YearMonth')['Sales'].sum().reset_index()
plt.figure(figsize=(14, 5))
plt.plot(monthly['YearMonth'], monthly['Sales'], marker='o', color='#2E86AB', linewidth=2)
plt.xticks(rotation=45, ha='right')
plt.title('Monthly Sales Trend', fontsize=14, fontweight='bold')
plt.ylabel('Sales ($)')
plt.tight_layout()
plt.savefig('../images/monthly_sales.png', dpi=120)
plt.close()
print("[OK] Saved monthly_sales.png")

# ---------- 7. CHART: CATEGORY & REGION ----------
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

df.groupby('Category')['Sales'].sum().sort_values().plot(
    kind='barh', ax=ax[0], color='#E63946')
ax[0].set_title('Sales by Category', fontweight='bold')

df.groupby('Region')['Sales'].sum().sort_values().plot(
    kind='barh', ax=ax[1], color='#457B9D')
ax[1].set_title('Sales by Region', fontweight='bold')

plt.tight_layout()
plt.savefig('../images/category_region.png', dpi=120)
plt.close()
print("[OK] Saved category_region.png")

# ---------- 8. RFM ANALYSIS ----------
print("\n" + "=" * 60)
print("STEP 5: RFM ANALYSIS")
print("=" * 60)

snapshot_date = df['Order Date'].max() + pd.Timedelta(days=1)

rfm = df.groupby('Customer ID').agg({
    'Order Date': lambda x: (snapshot_date - x.max()).days,
    'Order ID':   'nunique',
    'Sales':      'sum'
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

rfm['R'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1]).astype(int)
rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4]).astype(int)
rfm['M'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4]).astype(int)

rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

def segment(row):
    if row['R'] >= 3 and row['F'] >= 3 and row['M'] >= 3:
        return 'Champions'
    if row['R'] >= 3 and row['F'] >= 2:
        return 'Loyal'
    if row['R'] <= 2 and row['F'] >= 3:
        return 'At Risk'
    if row['R'] <= 2 and row['F'] <= 2:
        return 'Lost'
    return 'Potential'

rfm['Segment'] = rfm.apply(segment, axis=1)
print(rfm['Segment'].value_counts())

rfm.to_csv('../data/cleaned/rfm_segments.csv', index=False)
print("[OK] Saved rfm_segments.csv")

# ---------- 9. CHART: RFM SEGMENTS ----------
seg_counts = rfm['Segment'].value_counts()
plt.figure(figsize=(10, 5))
sns.barplot(x=seg_counts.index, y=seg_counts.values, palette='viridis')
plt.title('Customer Segments (RFM Analysis)', fontsize=14, fontweight='bold')
plt.ylabel('Customer Count')
plt.tight_layout()
plt.savefig('../images/rfm_segments.png', dpi=120)
plt.close()
print("[OK] Saved rfm_segments.png")

# ---------- 10. COHORT RETENTION ----------
print("\n" + "=" * 60)
print("STEP 6: COHORT RETENTION")
print("=" * 60)

df['CohortMonth'] = df.groupby('Customer ID')['Order Date'].transform('min').dt.to_period('M')
df['OrderMonth']  = df['Order Date'].dt.to_period('M')
df['CohortIndex'] = (df['OrderMonth'] - df['CohortMonth']).apply(lambda x: x.n)

cohort = df.groupby(['CohortMonth', 'CohortIndex'])['Customer ID'].nunique().reset_index()
cohort_pivot = cohort.pivot(index='CohortMonth', columns='CohortIndex', values='Customer ID')
cohort_size = cohort_pivot.iloc[:, 0]
retention = cohort_pivot.divide(cohort_size, axis=0).round(3)

plt.figure(figsize=(14, 7))
sns.heatmap(retention, annot=True, fmt='.0%', cmap='Blues', cbar_kws={'label': 'Retention Rate'})
plt.title('Cohort Retention Matrix', fontsize=14, fontweight='bold')
plt.ylabel('Cohort Month')
plt.xlabel('Months Since First Purchase')
plt.tight_layout()
plt.savefig('../images/cohort_retention.png', dpi=120)
plt.close()
print("[OK] Saved cohort_retention.png")

# ---------- 11. EXPORT FOR EXCEL ----------
with pd.ExcelWriter('../excel/rfm_export.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='CleanedData', index=False)
    rfm.to_excel(writer, sheet_name='RFM', index=False)
print("\n[OK] Exported to excel/rfm_export.xlsx")

# ---------- 12. SUMMARY INSIGHTS ----------
print("\n" + "=" * 60)
print("PROJECT COMPLETE - SUMMARY INSIGHTS")
print("=" * 60)
print(f"Total Revenue:        ${total_sales:,.2f}")
print(f"Total Profit:         ${total_profit:,.2f}")
print(f"Total Orders:         {total_orders:,}")
print(f"Total Customers:      {total_customers:,}")
print(f"Avg Order Value:      ${avg_order_value:,.2f}")
print(f"Champions + Loyal:    {rfm['Segment'].isin(['Champions','Loyal']).sum()} customers")
print(f"At Risk:              {(rfm['Segment'] == 'At Risk').sum()} customers")
print("\nCheck your folders:")
print("   - data/cleaned/  -> 2 CSV files")
print("   - images/        -> 4 PNG charts")
print("   - excel/         -> rfm_export.xlsx")
print("\nDONE! Move on to Step 3: SQL Server")