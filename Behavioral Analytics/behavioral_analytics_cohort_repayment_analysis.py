# -*- coding: utf-8 -*-
"""Behavioral Analytics : Cohort Repayment Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dhg9FVy8lwEbXOKEp42OU7SV9vh4rPs2

## Customer Behavioral Analytics : A Statistical Analysis of User Repayment over time

Customer cohort analysis is the act of segmenting customers into groups based on their shared characteristics, and then analyzing those groups to gather targeted insights on their behaviors and actions.
"""

#load libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors

# import data 
accounts_df = pd.read_csv("/content/drive/MyDrive/Data/Account.csv")
customers_df= pd.read_csv("/content/drive/MyDrive/Data/Customer.csv")
payment_df = pd.read_csv("/content/drive/MyDrive/Data/Payment.csv")
payment_plan_df = pd.read_csv("/content/drive/MyDrive/Data/PaymentPlan.csv")

"""Due the requirements, I prefer to **merge the other relevant data to the payment table.** 
The idea is to have **every payment associated with a region & product.** 
This will ensure that the credit team would be able to filter how the repayment curves differ.
"""

# columns available in each table
print("Account:", accounts_df.columns,"\n")
print("Customer:", customers_df.columns,"\n")
print("Payment:", payment_df.columns,"\n")
print("Payment Plan", payment_plan_df.columns,"\n")

"""Columns needed are: 

Payment Table: **`PaymentId`   `Amount` `ReceivedWhen` `AccountId`**

Payment Plan Table: **`Total Value` `Product`** 

Customer: **`Region`** 

Account Table: **`RegistrationDate`**


"""

#merge account_customer_plan
cus_account = accounts_df.merge(customers_df, on= "CustomerId").merge(payment_plan_df,on="PaymentPlanId")
cus_account

#merge table to the payment data
master_payment_df = payment_df[['PaymentId','Amount','ReceivedWhen','AccountId']].merge(cus_account[['TotalValue','Product','Region','RegistrationDate','AccountId']], on="AccountId")
master_payment_df

#Add the cohort to the data by converting registration date to month & year format

master_payment_df['RegistrationDate']=pd.to_datetime(master_payment_df['RegistrationDate'])
master_payment_df['Cohort']=master_payment_df['RegistrationDate'].dt.to_period('M')
master_payment_df

# Add the Months After Column
master_payment_df['Months After']=(pd.to_datetime(master_payment_df['ReceivedWhen']).dt.to_period("M").view(int)-pd.to_datetime(master_payment_df['RegistrationDate']).dt.to_period("M").view(int))
master_payment_df

"""We have the data all the data and we have also created the various Cohorts for futher analysis. 

Now we have to group data by **Cohort, Months After, AccountId, Region & Product**

We are interested in the Total **Amount** received  over the **Total Value**. 

"""

payment_grouped_df= master_payment_df[['Cohort','Months After', 'Amount', 'TotalValue','AccountId','Region','Product']].groupby(['Cohort', 'Months After','AccountId','Region', 'Product']).agg({'Amount':sum, 'TotalValue':max}).reset_index()
payment_grouped_df

"""We are only taking **the first unique value of the Total Value per each AccountId** since we linked it to every payment and replacing the subsequent ones to **Zero**.

There are only 2000 unique accounts, and each account is linked with a total value for the product purchase. However our current table has 18364 rows. Therefore, summing the Total Value will lead to inaccurate results. *italicized text*
"""

payment_grouped_df['TotalValue']=np.where(payment_grouped_df.duplicated(subset='AccountId'),0,payment_grouped_df['TotalValue'])
payment_grouped_df

"""`At this point,The data can be exported to Excel or any Data Viz tool like Power BI to create interactive visuals. However, I will proceed to create a pivot table & Viz with Python (The limitation is that Python isn't interactive with end user so they cannot filter with a button like in Power BI)`

"""

#downloading csv for further analysis (commented out)
#payment_grouped_df.to_csv('/content/drive/MyDrive/Data/new.csv')

"""The data is now grouped by `Cohort` & `Month After`and summed by **Amount** & **TotalValue**

The dataset has now been reduced to 156 rows.
"""

cohort_df=payment_grouped_df[['Cohort','Months After', 'Amount', 'TotalValue']].groupby(['Cohort', 'Months After']).sum(['Amount','TotalValue']).reset_index()
cohort_df

"""To accurately calculate the Percentage Paid we will need a **Running Total of the Amount paid by the entire cohort** & **the entire Total Value for the Cohort**."""

cohort_df["cum_amount"]= cohort_df.groupby(['Cohort'])['Amount'].cumsum(axis=0)
cohort_df['cum_total']=cohort_df.groupby(['Cohort'])['TotalValue'].cumsum(axis=0)
cohort_df['percentage_paid']=cohort_df['cum_amount']/cohort_df['cum_total']
cohort_df

"""We can now create a Pivot Chart with the data.
We can also export this and use to create a visualization.
However, this will not include any information on product type & region. 
"""

cohort_pivot=cohort_df.pivot_table(index = 'Cohort',

                        columns = 'Months After',

                        values = 'percentage_paid')
cohort_pivot

"""We can now plot a Cohort Analysis Chart to give us information of how much our credit have recovered from our clients."""

cohort_size = cohort_pivot.iloc[:,0]
retention_matrix = cohort_pivot.divide(cohort_size, axis = 0)

with sns.axes_style("white"):
    fig, ax = plt.subplots(1,figsize=(12, 8))
    
    # retention matrix
    sns.heatmap(cohort_pivot, 
                mask=retention_matrix.isnull(), 
                annot=True, 
                fmt='.0%',
                cmap='RdYlGn',
                ax=ax)
    ax.set_title('Cohort Repayment Chart', fontsize=16)
    ax.set(xlabel='# of Months',
              ylabel='Cohort')


    fig.tight_layout()

"""**Discussions**

*   The visual above shows an improvement in the percentage paid metric over down the row( old cohorts to new cohorts)


*   Generally, it takes less months for the newer cohorts to repay 80% of their credit around 8 months.


*   The highest change in payment percentage in the registration month happened between May 2020 & June 2020







"""