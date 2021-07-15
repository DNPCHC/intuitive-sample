import psycopg2
import urllib.request
import json
import pandas as pd

# Goes to the indicated url, parses through the json and stores into a dictionary and additionally a data frame
with urllib.request.urlopen("http://api.worldbank.org/v2/countries/CHN/indicators/NY.GDP.MKTP.CD?per_page=5000&format=json") as url:
    data = json.loads(url.read().decode())
    print(json.dumps(data, indent=2, sort_keys=True))
    # Excludes the title of the json when copying the dictionary into the dataframe
    df = pd.DataFrame.from_dict(data[1])

# Reverses the indexes of the dataframe
df = df.iloc[::-1]

#Establishes connection to the database
con = psycopg2.connect(
    host="ec2-52-6-77-239.compute-1.amazonaws.com",
    database="d2bo0a226irnot",
    user="lghdwoxqblmbcc",
    password="2e79c2ca9ef38dd79d8569c53112ecb42e1bdc35bd44a74723915bc0eed755b5",
    port="5432"
)

#cursor
cur = con.cursor()

# For loop iterates through gdp values and inserts them into table
for row in df.itertuples():
    cur.execute("insert into china_gdp (country, date, value) values(%s, %s, %s)", (row.countryiso3code,row.date,row.value))

con.commit()

#execute query
cur.execute("select country, date, value from china_gdp")

# Fetches all of the gdp china values and prints them
rows = cur.fetchall()
for r in rows:
    print(f"country {r[0]} date {r[1]} value {r[2]}")

#close the connection and cursor
cur.close()
con.close()
