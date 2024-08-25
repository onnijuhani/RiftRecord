import os

import psycopg2
import pandas as pd
import re


# Tämä skripti päivittää tietokannan


# Funktiot, jotka tarkistaa onko rivi pelaaja- vai joukkuetietoa
def is_player_row(row):
    return pd.notna(row['playername'])

def is_team_row(row):
    return pd.isna(row['playername'])

# Funktio tarkistaa, onko peli jo tietokannassa
def is_game_exists(game_id):
    cursor.execute("SELECT COUNT(*) FROM TeamGameStats WHERE game_id = %s", (game_id,))
    return cursor.fetchone()[0] > 0

# Haetaan data
df = pd.read_csv(os.path.join('data', 'data.csv'))

# Poistetaan välilyönnit ja muut ongelmat sarakenimistä
df.columns = [re.sub(r'\W+', '_', col) for col in df.columns]

# Yhdistä tietokantaan
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cursor = conn.cursor()

# Jaetaan data kahteen osaan: Joukkuedata ja Pelaajadata
joukkue_df = df[df['position'] == 'team']
pelaaja_df = df[df['position'] != 'team']

# Määritellään funktio datan lisäämiseksi ja rivien laskemiseksi
def insert_data(cursor, table_name, df):
    rows_inserted = 0
    for i, row in df.iterrows():
        columns = ', '.join(row.index)
        values = ', '.join(['%s'] * len(row))
        insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING"
        cursor.execute(insert_stmt, tuple(row))
        rows_inserted += cursor.rowcount
    return rows_inserted

# Lisätään data tauluihin ja lasketaan lisättyjen rivien määrä
joukkue_rows_inserted = insert_data(cursor, 'joukkuedata', joukkue_df)
pelaaja_rows_inserted = insert_data(cursor, 'pelaajadata', pelaaja_df)

# Commit muutokset ja suljetaan yhteys
conn.commit()
cursor.close()
conn.close()

# Tulostetaan lisättyjen rivien määrä
print(f"Rivejä lisättiin joukkuedata-tauluun: {joukkue_rows_inserted}")
print(f"Rivejä lisättiin pelaajadata-tauluun: {pelaaja_rows_inserted}")


