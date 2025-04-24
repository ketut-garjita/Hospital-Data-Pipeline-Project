import pandas as pd

# Contoh hasil query ClickHouse (asumsi hasilnya adalah DataFrame)
df = pd.DataFrame({'epoch_col': [20198, -200]})

# Konversi epoch (hari) ke tanggal
df['date'] = pd.to_datetime(df['epoch_col'], unit='D', origin='unix')  # Konversi ke datetime
df['date_string'] = df['date'].dt.strftime('%Y-%m-%d')  # Konversi ke string

print(df)
