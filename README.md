# **THE STAR JEANS COMPANY**

## E-commerce business model

<div align="center">
<p float="left">
  <img src="/images/rossman_1.jpg" width="1000" height="500"/>
</p>
</div>

***

## 1. BUSINESS PROBLEMS

Eduardo and Marcelo are two Brazilians, friends and business partners. After several successful business, they are planning to enter the US fashion market as a E-commerce business model.

The initial idea is to enter the market with just one product and for a specific audience, in the case the product would be Jenas pants for the male audience. The objective is to keep the cost of operation down and scale as they get customers.

However, even with the entry product and audience defined, the two partners lack experience in this fashion market and therefore don't know how to define basic things like price, the type of pants and the material for the manufacture of each part.


 ### 1.1 **Context:**
 
 * Thus, the two partners hired a Data Science consultancy to answer the following questions:

**Questions:**
- **1. What is the best selling price for the pants?**
- **2. How many types of pants and their colors for the initial product?**
- **3. What raw materials are needed to make the pants?**

# 2. Business Assumptions.

| Mainly competitors | Target Product | Rules                                    | 
|:-------------------|:---------------|:-----------------------------------------|
| H & M              | Men's Jeans    |                                          | 
| Macys              | Men's Jeans    |                                          |


# 3. Solution Strategy
SAPE method

**Step 01. Data Description:** My goal is to use statistics metrics to identify data outside the scope of business.

- Calculate the average price by category.

**Step 02. Feature Engineering:** Derive new attributes based on the original variables to better describe the phenomenon that will be modeled.

**Step 03. Data Filtering:** Filter rows and select columns that do not contain information for modeling or that do not match the scope of the business.

- Webscraping from the H&M website (BeautifulSoup)
- Data cleaning and organization.
- Inserting the data into the database.
- Query data with SQL.

**Step 04. Exploratory Data Analysis:** Explore the data to find insights and better understand the impact of variables on model learning.
