# ============================================================
# Step 2: Load cleaned CSV data into SQL Server
# ============================================================

import pandas as pd
import urllib
from sqlalchemy import create_engine

print("Loading cleaned CSV...")
df = pd.read_csv('../data/Cleaned/superstore_clean.csv', encoding='latin-1')
print(f"Loaded {len(df)} rows")

# Rename columns: remove spaces and hyphens
rename_map = {
    'Row ID':       'RowID',
    'Order ID':     'OrderID',
    'Order Date':   'OrderDate',
    'Ship Date':    'ShipDate',
    'Ship Mode':    'ShipMode',
    'Customer ID':  'CustomerID',
    'Customer Name':'CustomerName',
    'Segment':      'Segment',
    'Country':      'Country',
    'City':         'City',
    'State':        'State',
    'Postal Code':  'PostalCode',
    'Region':       'Region',
    'Product ID':   'ProductID',
    'Category':     'Category',
    'Sub-Category': 'SubCategory',
    'Product Name': 'ProductName',
    'Sales':        'Sales',
    'Quantity':     'Quantity',
    'Discount':     'Discount',
    'Profit':       'Profit',
    'Year':         'Year',
    'Month':        'Month',
    'YearMonth':    'YearMonth',
    'ShipDays':     'ShipDays',
    'ProfitMargin': 'ProfitMargin',
}
df = df.rename(columns=rename_map)

# Keep only the 21 columns that match SQL table
sql_cols = ['RowID','OrderID','OrderDate','ShipDate','ShipMode','CustomerID',
            'CustomerName','Segment','Country','City','State','PostalCode',
            'Region','ProductID','Category','SubCategory','ProductName',
            'Sales','Quantity','Discount','Profit']
df = df[sql_cols]

# ---------- CONNECT & UPLOAD ----------
# CHANGE the server name below if your SQL Server uses different name
server   = 'DESKTOP-F9U6CP9\\SQLADMIN'      # try 'localhost\\SQLEXPRESS' if this fails
database = 'EcommerceDB'

params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};DATABASE={database};Trusted_Connection=yes;"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

print("Uploading to SQL Server...")
df.to_sql('Superstore', engine, if_exists='append', index=False, chunksize=500)
print(f"✅ Uploaded {len(df)} rows to SQL Server!")