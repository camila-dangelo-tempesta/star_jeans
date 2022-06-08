#!/usr/bin/env python
# coding: utf-8

# HTML Data Extraction
# 
# source: H&M <https://www2.hm.com/en_us/men/products/jeans.html>

# Data to be collected for table creation:
# 
# - product_id
# - product_name
# - product_type
# - product_color
# - composition
# - price

# In[1]:


# Libraries

import requests

import pandas as pd

import numpy as np

import math

from datetime import datetime

from bs4 import BeautifulSoup


# Browser camouflage for website request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Website URL for all men's jeans
url1 = 'https://www2.hm.com/en_us/men/products/jeans.html'

# Request
page = requests.get( url1, headers=headers )
page

# Returning the page's HTML
page.text

# Instantiating Beautiful Soup object
soup = BeautifulSoup(page.text, 'html.parser')
soup

# Pagination: Returning all site pages
soup.find_all('h2', class_='load-more-heading')

# Returning all products from all pages on the site
total_item = soup.find_all('h2', class_='load-more-heading')[0].get('data-total')
total_item

# Transforming into integer to know how many pages I need
# Ex: 36 products fit per page, so I need 2.41 pages
int(total_item)/36

# Rounding the values to know how many pages I need
page_number = math.ceil(int(total_item)/36)
page_number

# Rounding off values (another way to do it)
#page_number = np.round(int(total_item)/36)
#page_number

# Secondary url with all products from all site pages
url02 = url1 + '?pagesize=' + str(int(page_number*36))
url02

# HTML structure where the showcase is stored
products = soup.find('ul', class_ = 'products-listing small')
products


# In[2]:


#  HTML Structure (Class) where all data (data-articlecode and data-category) is stored
product_list = products.find_all('article', class_= 'hm-product-item')
product_list

# Returning first element of product_list
product_list[1]

# Number of items in the product_list
len(product_list)

#============================================= product_id =============================================

# Returned first item from  data-articlecode (product_id) items from product_list
product_list[0].get('data-articlecode')

# Looping to collect all data-articlecode (product_id) items from product_list
product_id = [p.get('data-articlecode') for p in product_list]
product_id

#============================================= product_type =============================================

# Returned first item from  data-category (product_type) items from product_list
product_list[0].get('data-category')

# Looping to collect all data-category (product_type) items from product_list
product_type = [p.get('data-category') for p in product_list]
product_type


# In[3]:


#  HTML structure (class) where the data (product_name) is stored
product_list = products.find_all('a', class_='link')
product_list

#============================================= product_name =============================================

# Returning the first item (product_name) from the product_list list data
product_list[0].get_text()

# Looping to collect all data (product_name) items from product_list
product_name = [p.get_text() for p in product_list]
product_name


# In[4]:


#  HTML structure (class) where the data (product_price) is stored
product_list = products.find_all('span', class_='price regular')
product_list

#============================================= product_price =============================================

# Returning the first item (product_price) from the product_list list data
product_list[0].get_text()

# Looping to collect all data (product_price) items from product_list
product_price = [p.get_text() for p in product_list]
product_price


# In[5]:


# DataFrame creation
data = pd.DataFrame([product_id,
              product_name,
              product_type,
              product_price,]).T

# Rename colomns DataFrame
data.columns = ['product_id',
                'product_name',
                'product_type',
                'product_price']

# Irregular date and time setting
data['scrapy_datetime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

data.head()


# # One product

# In[6]:


# Browser camouflage for website request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# Website url for just one product
url = 'https://www2.hm.com/en_us/productpage.1024256001.html'
#print(url)

# Request
page = requests.get( url, headers=headers )

# Returning the page's HTML
page.text

# Instantiating Beautiful Soup object
soup = BeautifulSoup(page.text, 'html.parser')
soup
type(soup)

# HTML Structure (Class) where all data is stored
soup.find_all('li', class_='list-item')

# Returning the first elements of the list item
soup.find_all('li', class_='list-item')[0]

#============================================= Color Name =============================================

# HTML structure (Class) where color data is stored
soup.find_all('a', class_='filter-option miniature active')[0]
soup.find_all('a', class_='filter-option miniature active')[0].get('data-color')


product_atributes_list = soup.find_all('a', {'class':['filter-option miniature', 'filter-option miniature active']})
color_name = [p.get('data-color') for p in product_atributes_list]
color_name

# Looping para coleta de todos os itens product_id_c da lista product_atributes_list
product_id_c = [p.get('data-articlecode') for p in product_atributes_list]
product_id_c

# DataFrame creation
df_color = pd.DataFrame([product_id_c, color_name]).T
df_color

# Rename colomns DataFrame
df_color.columns = ['product_id', 'color_name']

df_color.head()

# Generate Style id + Color id
df_color['style_id'] = df_color['product_id'].apply(lambda x: x[:-3])
df_color['color_id'] = df_color['product_id'].apply(lambda x: x[-3:])
df_color

#============================================= Composition =============================================

# HTML structure where the all data is stored:
soup.find_all('div', class_='details-attributes-list-item')

# Returning the first elements of the list item
soup.find_all('div', class_='details-attributes-list-item')[0]
soup.find_all('div', class_='details-attributes-list-item')[0].get_text()

# HTML structure (Class) where composition data is stored
product_composition_list = soup.find_all('div', class_='details-attributes-list-item')

# Looping to collect all product_composition items from the product_attributes_list list
product_composition = [list(filter(None, p.get_text().split('\n'))) for p in product_composition_list]
product_composition

# DataFrame creation
df_composition = pd.DataFrame(product_composition).T
df_composition

# Rename colomns DataFrame
df_composition.columns = df_composition.iloc[0]
df_composition

# Delete First row
df_composition = df_composition.iloc[1:].fillna(method='ffill')
df_composition

# Generate Style id + Color id
df_composition['style_id'] = df_composition['Art. No.'].apply(lambda x: x[:-3])
df_composition['color_id'] = df_composition['Art. No.'].apply(lambda x: x[-3:])

# Merge Data Color + Data Composition
data_color_composition = pd.merge(df_color, df_composition[['style_id','Fit','Composition']] , how='left', on='style_id')
data_color_composition


# In[7]:


data.head()
len(data)


# # Multiple Products

# In[8]:


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
    url_all = 'https://www2.hm.com/en_us/productpage.' + data.loc[i, 'product_id'] +'.html'
    #print(url_all)
    
    # Request
    page = requests.get( url, headers=headers )
    
    # Instantiating Beautiful Soup object
    soup = BeautifulSoup(page.text, 'html.parser')
    
    #============================ Color Name =============================
    product_atributes_list = soup.find_all('a', {'class':['filter-option miniature', 'filter-option miniature active']})
    color_name = [p.get('data-color') for p in product_atributes_list]
    
    # product id
    # Looping para coleta de todos os itens product_id_c da lista product_atributes_list
    product_id_c = [p.get('data-articlecode') for p in product_atributes_list]
    
    # DataFrame creation
    df_color = pd.DataFrame([product_id_c, color_name]).T
    
    # Rename colomns DataFrame
    df_color.columns = ['product_id', 'color_name']
    
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


# In[9]:


data_raw


# In[10]:


data_raw.to_csv('data_row.csv')

