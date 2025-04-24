from clickhouse_driver import Client

client = Client(
        host='clickhouse',
        port=9000,
        user='streaming',
        password='password',
        database='hospital'
)

epoch_val = -100  # Nilai epoch dalam hari

# Query ClickHouse dan langsung konversi ke DATE
result = client.execute("SELECT reinterpretAsDate({})".format(epoch_val))[0][0]
# Hasil sudah berupa objek `datetime.date` di Python
print(result)
# Konversi ke string dengan str() atau metode datetime
date_string = str(result)  # Format default: YYYY-MM-DD
# Atau format custom:
date_formatted = result.strftime("%d/%m/%Y")

print(date_string)      # Output: "2025-04-20" (contoh)
print(date_formatted)   # Output: "20/04/2025"
