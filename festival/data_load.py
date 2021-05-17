from sqlalchemy import create_engine
import pandas as pd
import sqlite3


db_URI='sqlite:///C:\\Users\\jccla\Desktop\\Projects\\Portfolio\\music_app\\festival\\site.db'

fest = pd.read_csv("festival.csv")
new_columns = [column.replace(' ','_').lower() for column in fest]
fest.columns=new_columns

engine = create_engine(db_URI, echo=True)
conn = engine.connect()
print(conn)
table='performers'


fest.to_sql(name=table, con=conn, if_exists='replace', index=False)