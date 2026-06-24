import polars as pl
import mysql.connector

df = pl.read_csv("tension.csv")

print(df.head())
df = df.rename({
    "Systolic BP": "systolic_bp",
    "Diastolic BP": "diastolic_bp",
    "Smoking Status": "smoking_status",
})

df = df.with_columns([
    pl.col("age").cast(pl.Int32, strict=False),
    pl.col("bmi").cast(pl.Float64, strict=False),
    pl.col("cholesterol").cast(pl.Int32, strict=False),
    pl.col("systolic_bp").cast(pl.Int32, strict=False),
    pl.col("diastolic_bp").cast(pl.Int32, strict=False),
    pl.col("heart_rate").cast(pl.Int32, strict=False),
    pl.col("glucose").cast(pl.Int32, strict=False),
    pl.col("ldl").cast(pl.Int32, strict=False),
    pl.col("hdl").cast(pl.Int32, strict=False),
    pl.col("triglycerides").cast(pl.Int32, strict=False),
])

df = df.drop_nulls()

conn = mysql.connector.connect(
    host="localhost",
    user="hell",
    password="*******",
    database="tension"
)

cursor = conn.cursor()

columns = df.columns

sql = f"""
INSERT INTO tension ({", ".join(columns)})
VALUES ({", ".join(["%s"] * len(columns))})
"""

data = df.to_numpy().tolist()
cursor.executemany(sql, data)
conn.commit()
cursor.close()
conn.close()
