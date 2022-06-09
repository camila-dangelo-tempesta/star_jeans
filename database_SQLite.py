#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

import sqlite3

import sqlalchemy
from sqlalchemy import create_engine


# In[2]:


path = 'C:/Users/Utilizador/repos/Python_ds_ao_dev/Projeto_Star_Jeans/data_product_hm_cleaned.csv'
data = pd.read_csv(path)

data.drop(["Unnamed: 0"], axis=1, inplace=True)
data = data.reset_index(drop=True)

data.head()


# In[3]:


data.dtypes


# In[4]:


# Creat query
query_showroom_schema = """
    CREATE TABLE vitrine (
        product_id             INTEGER,
        product_name           TEXT,
        product_type           TEXT,
        product_price          REAL,
        scrapy_datetime        TEXT,
        style_id               INTEGER
        color_id               INTEGER
        color_name             TEXT,
        Fit                    TEXT,
        messages.waistRise     TEXT,
        shell_cotton           REAL,
        shell_spandex          REAL,
        )
"""


# In[5]:


# Connect to dataset
# Planning the query execution in DB
# Run
# Close conection

try:
    conn = sqlite3.connect('hm_db.sqlite')
    cursor = conn.cursor()
    print("Database created and Successfully Connected to SQLite")

    query_showroom_schema = "select sqlite_version();"
    cursor.execute(query_showroom_schema)
    conn.commit()
    record = cursor.fetchall()
    print("SQLite Database Version is: ", record)
    cursor.close()

except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
finally:
    if conn:
        conn.close()
        print("The SQLite connection is closed")


# In[6]:


conn = create_engine('sqlite:///hm_db.sqlite',echo=False, pool_pre_ping=True)
conn


# In[7]:


# insert data to table
data.to_sql( 'vitrine', con=conn, if_exists='append', index=False )


# In[8]:


query = """
    SELECT * FROM vitrine
"""
df = pd.read_sql_query( query, conn )
df.head()


# In[9]:


#Command - UPDATE
#query = """
#   UPDATE vitrine
#  SET product_type = 'Jeans'
#  WHERE product_id = 1074475001
#"""


## Command - DROP TABLE
#query = """
#   DROP TABLE vitrine
#"""

## Command - ALTER TABLE
#query = """
# ALTER TABLE vitrine
# RENAME TO vitrine_two
#"""

## Command - CREATE INDEX
#query = """
# CREATE INDEX idx_product_id
# ON vitrine_two ( product_id )
#"""

#conn = sqlite3.connect( 'hm_db.sqlite' )
#cursor = conn.execute( query )
#conn.commit()
#conn.close()

