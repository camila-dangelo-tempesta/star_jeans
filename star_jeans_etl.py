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

# Data Colletion
## Job 01: Extraction

### 0.1. Loading data
def get_showroom_data(url, headers):
    page = requests.get( url, headers=headers )
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # 1.0. Scrape data - Showroom products
    products = soup.find('ul', class_ = 'products-listing small')
    product_list = products.find_all('article', class_= 'hm-product-item')
    
    # product id
    product_id = [p.get('data-articlecode') for p in product_list]
    
    # product type
    product_type = [p.get('data-category') for p in product_list]
    
    # product name
    product_list = products.find_all('a', class_='link')
    product_name = [p.get_text() for p in product_list]
    
    # product price
    product_list = products.find_all('span', class_='price regular')
    product_price = [p.get_text() for p in product_list]
    
    # dataFrame creation
    data = pd.DataFrame([product_id,
                         product_name,
                         product_type,
                         product_price,]).T
    
    # Rename colomns DataFrame
    data.columns = ['product_id',
                    'product_type',
                    'product_name',
                    'product_price']
    
    # scrapy datetime
    data['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return data

# Data Collection by Product
## Job 02: Transformation

def get_product_details( data ):
    # 2.0. Scrape data - Products Details
    
    df_details = pd.DataFrame()
    
    # unique columns for all products
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
        url = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id'] +'.html'
        print('Product: {}'.format(url))
        logger.debug('Product: %s',url)
        
        
        # Request
        page = requests.get( url, headers=headers )
        
        # Instantiating Beautiful Soup object
        soup = BeautifulSoup(page.text, 'html.parser')
    
        #============================ color_name =============================
        product_atributes_list = soup.find_all('a', {'class':['filter-option miniature', 'filter-option miniature active']})
        color_name = [p.get('data-color') for p in product_atributes_list]
    
        # product id
        product_id_c = [p.get('data-articlecode') for p in product_atributes_list]
    
        # DataFrame creation
        df_color = pd.DataFrame([product_id_c, color_name]).T
        
        # Rename colomns DataFrame
        df_color.columns = ['product_id', 'color_name']
        
        # ==================== Iterate over colors =================================
    
        for j in range( len( df_color ) ):
            url = 'https://www2.hm.com/en_us/productpage.' + df_color.loc[j,'product_id'] + '.html'
            print( 'Color: {}'.format( url ) )
            logger.debug('Color: %s',url)
        
            page = requests.get( url, headers=headers )
        
            # Beautiful Soup object
            soup = BeautifulSoup( page.text, 'html.parser' )
    
        # Generate Style id + Color id
        df_color['style_id'] = df_color['product_id'].apply(lambda x: x[:-3])
        df_color['color_id'] = df_color['product_id'].apply(lambda x: x[-3:])
    
    #============================ Composition =============================
    product_composition_list = soup.find_all('div', class_='details-attributes-list-item')
    product_composition = [list(filter(None, p.get_text().split('\n'))) for p in product_composition_list]
    
    # rename DataFrame
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
        
    # Joining the DataFrames: data + details
    data['style_id'] = data['product_id'].apply(lambda x: x[:-3])
    data['color_id'] = data['product_id'].apply(lambda x: x[-3:])

    data = pd.merge(data, df_details[['style_id','color_name','Fit','Composition', 'Description','messages.waistRise']], how='left', on='style_id')
        
    return data

# Data Cleaning
## Job 03: Transformation

def data_cleaning( data ):
    # product id      
    data = data.dropna(subset=['product_id'])
    data['product_id'] = data['product_id'].astype( int )
    
    # product name
    data['product_name'] = data['product_name'].apply( lambda x: x.replace(' ', '_').lower())

    # product price
    data['product_price'] = data['product_price'].apply(lambda x: x.replace('$', '') )
    data['product_price'] = data['product_price'].apply(lambda x: x.replace('$', '') ).astype(float)
    
    # scrapy datetime
    data['scrapy_datetime'] = pd.to_datetime(data['scrapy_datetime'], format= '%Y-%m-%d %H:%M:%S')
    
    # color name
    data['color_name'] = data['color_name'].apply( lambda x: x.replace(' ', '_').replace('/', '_').lower() if pd.notnull(x) else x)

    # fit
    data['Fit'] = data['Fit'].apply( lambda x: x.replace(' ', '_').lower() if pd.notnull(x) else x)

    # composition
    data = data[~data['Composition'].str.contains( 'Pocket lining:', na=False )]
    #data = data[~data['Composition'].str.contains( 'Shell:', na=False )]
    
    # drop duplicates
    data = data.drop_duplicates( subset=['product_id', 'product_type','product_name', 'product_price','scrapy_datetime', 'color_id','color_name', 'Fit'], keep='last' )
    
    # reset index
    data = data.reset_index( drop=True )
    
    # break composition by comma
    df1 = data['Composition'].str.split( ',', expand=True )

    # ------ shell_cotton -------

    data['shell_cotton'] = ''
    data['shell_cotton'] = df1[0]
    data['shell_cotton'] = data['shell_cotton'].apply( lambda x: int(re.search ('\d+', x).group(0)) / 100 if pd.notnull(x) else x)


    # ------ shell_spandex -------

    data['shell_spandex'] = ''
    data['shell_spandex'] = df1[1]
    data['shell_spandex'] = data['shell_spandex'].apply( lambda x: int(re.search ('\d+', x).group(0)) / 100 if pd.notnull(x) else x)


    # Drop columns
    data = data.drop(columns=['Composition', 'Description'], axis=1)

    # Drop duplicates
    data = data.drop_duplicates()
    
    return data


if __name__ == "__main__":
    # logging
    path = 'C:/Users/Utilizador/repos/Python_ds_ao_dev/Projeto_Star_Jeans'
    
    if not os.path.exists (path + 'Logs'):
        os.makedirs(path + 'Logs')
    
    logging.basicConfig(
    filename= path + 'Logs/database_hm.txt',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger('database_hm')
    
    
    # parameters
    url = 'https://www2.hm.com/en_us/men/products/jeans.html'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    
    # Extraction
    data = get_showroom_data( url, headers )
    logger.info('get_showroom_data DONE')
    
    # Transformation
    data = get_product_details( data )
    logger.info('get_product_details DONE')
    
    # Carga
    data = data_cleaning( data )
    logger.info('data_cleaning DONE')


# In[2]:


data.to_csv('data_hm.csv')


# In[3]:


## Database SQLite


# In[4]:


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

# Creat query
query_showroom_schema_2 = """
    CREATE TABLE hm_vitrine (
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

try:
    # Connect to dataset
    conn = sqlite3.connect('database_hm.sqlite')
    cursor = conn.cursor()
    print("Database created and Successfully Connected to SQLite")
    
    
    query_showroom_schema_2 = "select sqlite_version();"
    
    # Run
    cursor.execute(query_showroom_schema_2)
    conn.commit()
    
    record = cursor.fetchall()
    print("SQLite Database Version is: ", record)
    
except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
finally:
    if conn:
        conn.close()
        print("The SQLite connection is closed")
        
# Creat database connection
conn = create_engine('sqlite:///hm_db.sqlite',echo=False, pool_pre_ping=True)

# data insert
data_insert.to_sql( 'hm_vitrine', con=conn, if_exists='append', index=False )

query = """
    SELECT * FROM hm_vitrine
"""

df = pd.read_sql_query( query, conn )

