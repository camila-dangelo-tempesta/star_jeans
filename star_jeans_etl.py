#!/usr/bin/env python
# coding: utf-8

# ## Imports

# In[1]:


# Libraries

import re
import requests
import numpy as np
import pandas as pd
import sqlite3
import sqlalchemy

import logging
import os

from datetime import datetime

from bs4 import BeautifulSoup

from sqlalchemy import create_engine


# ## Data Colletion

# ### Job 01: Extraction

# In[2]:


# Browser camouflage for website request (parameters)
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Website URL for all men's jeans
url = 'https://www2.hm.com/en_us/men/products/jeans.html'

# Request to URL
page = requests.get( url, headers=headers )

# Returning the page's HTML
page.text

# Instantiating Beautiful Soup object
soup = BeautifulSoup(page.text, 'html.parser')

#============================================= Product Data =============================================
# HTML structure where the showcase is stored
products = soup.find('ul', class_ = 'products-listing small')

#  HTML Structure (Class) where all data (data-articlecode and data-category) is stored
product_list = products.find_all('article', class_= 'hm-product-item')

# Returning first element of product_list
product_list[1]

# Number of items in the product_list
len(product_list)

#============================================= product_id =============================================

# Returned first item from  data-articlecode (product_id) items from product_list
product_list[0].get('data-articlecode')

# Looping to collect all data-articlecode (product_id) items from product_list
product_id = [p.get('data-articlecode') for p in product_list]

#============================================= product_type =============================================

# Returned first item from  data-category (product_type) items from product_list
product_list[0].get('data-category')

# Looping to collect all data-category (product_type) items from product_list
product_type = [p.get('data-category') for p in product_list]

#============================================= product_name =============================================
#  HTML structure (class) where the data (product_name) is stored
product_list = products.find_all('a', class_='link')

# Returning the first item (product_name) from the product_list list data
product_list[0].get_text()

# Looping to collect all data (product_name) items from product_list
product_name = [p.get_text() for p in product_list]

#============================================= product_price =============================================
#  HTML structure (class) where the data (product_price) is stored
product_list = products.find_all('span', class_='price regular')

# Returning the first item (product_price) from the product_list list data
product_list[0].get_text()

# Looping to collect all data (product_price) items from product_list
product_price = [p.get_text() for p in product_list]

#============================================= Data Frame =============================================
# DataFrame creation
data = pd.DataFrame([product_id,
                     product_name,
                     product_type,
                     product_price,]).T

# Rename colomns DataFrame
data.columns = ['product_id',
                'product_type',
                'product_name',
                'product_price']

# Irregular date and time setting
data['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

data.head()


# ## Data Collection by Product

# ### Job 02: Transformation

# In[3]:


# Browser camouflage for website request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Empty DataFrame
df_details = pd.DataFrame()

# Unique columns for all products
aux = []

set(aux)

cols = ['Art. No.',
        'Care instructions',
        'Composition',
        'Concept',
        'Description',
        'Fit',
        'Imported',
        'Material',
        'Nice to know',
        'messages.garmentLength',
        'messages.waistRise']

df_pattern = pd.DataFrame(columns = cols)
 
# Looping for all products on the site
for i in range(len(data)):
    #Website url for all products
    url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id'] +'.html'
    print('Product: {}'.format(url))
    
    # Request
    page = requests.get( url, headers=headers )
    
    # Instantiating Beautiful Soup object
    soup = BeautifulSoup(page.text, 'html.parser')
    
    #============================ color_name =============================
    product_atributes_list = soup.find_all('a', {'class':['filter-option miniature', 'filter-option miniature active']})
    color_name = [p.get('data-color') for p in product_atributes_list]
    
    # product id
    # Looping para coleta de todos os itens product_id_c da lista product_atributes_list
    product_id_c = [p.get('data-articlecode') for p in product_atributes_list]
    
    # DataFrame creation
    df_color = pd.DataFrame([product_id_c, color_name]).T
    
    # Rename colomns DataFrame
    df_color.columns = ['product_id', 'color_name']
    
    for j in range( len( df_color ) ):
        # API Requests
        url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j,'product_id'] + '.html'
        print( 'Color: {}'.format( url ) )
        
        page = requests.get( url, headers=headers )
        
        # Beautiful Soup object
        soup = BeautifulSoup( page.text, 'html.parser' )
    
    # Generate Style id + Color id
    df_color['style_id'] = df_color['product_id'].apply(lambda x: x[:-3])
    df_color['color_id'] = df_color['product_id'].apply(lambda x: x[-3:])
    
    #============================ Composition =============================
    product_composition_list = soup.find_all('div', class_='details-attributes-list-item')
    product_composition = [list(filter(None, p.get_text().split('\n'))) for p in product_composition_list]
    
    # Rename DataFrame
    df_composition = pd.DataFrame(product_composition).T
    df_composition.columns = df_composition.iloc[0]
    
    # Delete First row
    df_composition = df_composition.iloc[1:].fillna(method='ffill')
    
    # garantee the same number of columns
    df_composition = pd.concat([df_pattern, df_composition], axis=0)
    
    # Generate Style id + Color id
    df_composition['style_id'] = df_composition['Art. No.'].apply(lambda x: x[:-3])
    df_composition['color_id'] = df_composition['Art. No.'].apply(lambda x: x[-3:])
    
    aux = aux + df_composition.columns.tolist()
    
    # Merge Data Color + Data Composition
    data_color_composition = pd.merge(df_color, df_composition[['style_id','Fit','Composition', 'Material','Description','messages.waistRise']] , how='left', on='style_id')
    
    # All details products
    df_details = pd.concat([df_details, data_color_composition], axis=0)
    
df_details.head()

# Joining the DataFrames: data + details
data['style_id'] = data['product_id'].apply(lambda x: x[:-3])
data['color_id'] = data['product_id'].apply(lambda x: x[-3:])

data_raw = pd.merge(data, df_details[['style_id','color_name','Fit','Composition', 'Description','messages.waistRise']], how='left', on='style_id')
data_raw.head()

data_raw.to_csv('data_row.csv')


# ## Data Cleaning

# ### Job 03: Transformation

# In[4]:


path = 'C:/Users/Utilizador/repos/Python_ds_ao_dev/Projeto_Star_Jeans/data_row.csv'
data = pd.read_csv(path)

data.drop(["Unnamed: 0"], axis=1, inplace=True)

data = data.reset_index(drop=True)

data.head()

data.columns

# Checking NAN of entire dataset
data.isna().sum()

# Checking type of variables
data.dtypes

len(data['product_id'].unique())

#============================================= product_id ===============================================
# Deleting NA from column: product_id      
data = data.dropna(subset=['product_id'])

#============================================= product_name =============================================
# Replacing empty spaces with _ and making everything lowercase
data['product_name'] = data['product_name'].apply( lambda x: x.replace(' ', '_').lower())

#============================================= product_price =============================================
# Withdrawing the $
data['product_price'] = data['product_price'].apply(lambda x: x.replace('$', '') )

# Changing variable type from objtct to float
data['product_price'] = data['product_price'].apply(lambda x: x.replace('$', '') ).astype(float)

# Outras formas de se fazer
# Formula para quando existir NA: data['product_price'] = data['product_price'].apply(lambda x: x.replace('$', '') if pd.notnull (x) else x)
# Formula para mudar tipo: data['product_price'] = data['product_price'].astype(float)

#============================================= scrapy_datetime =============================================
# Changing the variable type to datetime
data['scrapy_datetime'] = pd.to_datetime(data['scrapy_datetime'], format= '%Y-%m-%d %H:%M:%S')

#============================================= color_name ==================================================
# Know the values of color_name: checking for NA or strange characters
data['color_name'].unique()

# Replacing empty spaces with _, as / with _ and putting everything in lowercase and NA conference
data['color_name'] = data['color_name'].apply( lambda x: x.replace(' ', '_').replace('/', '_').lower() if pd.notnull(x) else x)

#============================================= fit =========================================================
# Knowing the Fit values: checking for NA or strange characters
data['Fit'].unique()

# Replacing empty spaces with _, lowering everything and NA conference
data['Fit'] = data['Fit'].apply( lambda x: x.replace(' ', '_').lower() if pd.notnull(x) else x)

#============================================= composition =================================================
# Knowing Composition values: checking for NA or strange characters
data['Composition'].unique()

# Checking the distribution on dataFrame columns
data[['product_id', 'Composition']].sample(10)

len(data['product_id'].unique())

# composition
data = data[~data['Composition'].str.contains( 'Pocket lining:', na=False )]
data = data[~data['Composition'].str.contains( 'Shell:', na=False )]

# drop duplicates
data = data.drop_duplicates( subset=['product_id', 'product_type','product_name', 'product_price','scrapy_datetime', 'color_id','color_name', 'Fit'], keep='last' )

# reset index
data = data.reset_index( drop=True )

# break composition by comma
df1 = data['Composition'].str.split( ',', expand=True )

# ------ shell_cotton -------
# Creat new column
data['shell_cotton'] = ''

# Assigning values
data['shell_cotton'] = df1[0]

# Format Composition Data
data['shell_cotton'] = data['shell_cotton'].apply( lambda x: int(re.search ('\d+', x).group(0)) / 100 if pd.notnull(x) else x)


# ------ shell_spandex -------
# Creat new column
data['shell_spandex'] = ''

# Assigning values
data['shell_spandex'] = df1[1]

# Format Composition Data
data['shell_spandex'] = data['shell_spandex'].apply( lambda x: int(re.search ('\d+', x).group(0)) / 100 if pd.notnull(x) else x)

#============================================= Data ======================================================
# Drop columns
data = data.drop(columns=['Composition', 'Description'], axis=1)

# Drop duplicates
data = data.drop_duplicates()

data.head()
data.shape

data.to_csv('data_product_hm_cleaned.csv')


# ## Data Insert

# ### Job 04: Charge

# In[5]:


path = 'C:/Users/Utilizador/repos/Python_ds_ao_dev/Projeto_Star_Jeans/data_product_hm_cleaned.csv'
data = pd.read_csv(path)

data.drop(["Unnamed: 0"], axis=1, inplace=True)
data = data.reset_index(drop=True)

data.dtypes

data.head()


# In[6]:


data_insert = data[[
    'product_id',
    'style_id',
    'color_id',
    'product_name',
    'color_name',
    'product_type',
    'Fit',
    'product_price',
    'messages.waistRise',
    'shell_cotton',
    'shell_spandex',
    'scrapy_datetime'   
]]

data_insert.head()


# In[7]:


# Creat query
query_showroom_schema_1 = """
    CREATE TABLE vitrines (
        product_id             INTEGER,
        style_id               INTEGER
        color_id               INTEGER
        product_name           TEXT,
        color_name             TEXT,
        product_type           TEXT,
        Fit                    TEXT,
        product_price          REAL,
        messages.waistRise     TEXT,
        shell_cotton           REAL,
        shell_spandex          REAL,
        scrapy_datetime        TEXT
        )
"""


# In[8]:


# Create table
try:
    # Connect to dataset
    conn = sqlite3.connect('database_hm.sqlite')
    cursor = conn.cursor()
    print("Database created and Successfully Connected to SQLite")
    
    
    query_showroom_schema_1 = "select sqlite_version();"
    
    # Run
    cursor.execute(query_showroom_schema_1)
    conn.commit()
    
    record = cursor.fetchall()
    print("SQLite Database Version is: ", record)
    
except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
finally:
    if conn:
        conn.close()
        print("The SQLite connection is closed")


# In[9]:


# Creat database connection
conn = create_engine('sqlite:///hm_db.sqlite',echo=False, pool_pre_ping=True)

# data insert
data_insert.to_sql( 'vitrines', con=conn, if_exists='append', index=False )


# In[10]:


query = """
    SELECT * FROM vitrines
"""

df = pd.read_sql_query( query, conn )
df.head()

