# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1J3jIgvW5_UED5PnQiW1uHnz0ZKdAAWeY

# Import necessary libraries and load the datasets#
Data Preprocessing and Merging the Datasets,
merging the transaction data with customer data
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import davies_bouldin_score, silhouette_score
import matplotlib.pyplot as plt
import seaborn as sns

customers_df = pd.read_csv('Customers.csv')
transactions_df = pd.read_csv('Transactions.csv')

merged_df = transactions_df.merge(customers_df, on='CustomerID', how='left')

"""# Feature Engineering for Customer Profile and Transaction History#
Aggregating purchase information per customer
"""

c_purchase_history = merged_df.groupby('CustomerID').agg(
    total_spent=pd.NamedAgg(column='TotalValue', aggfunc='sum'),
    total_transactions=pd.NamedAgg(column='TransactionID', aggfunc='nunique'),
    avg_transaction_value=pd.NamedAgg(column='TotalValue', aggfunc='mean')
).reset_index()

# Adding customer profile data (e.g., region)
cprofile = pd.merge(c_purchase_history, customers_df[['CustomerID', 'Region']], on='CustomerID')

"""# 3. Normalizing Features and preprocessing"""

#Onehotencoding Region column in region_encoded_df
from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(drop='first', sparse_output=False)
region_encoded = encoder.fit_transform(cprofile[['Region']])
region_encoded_df = pd.DataFrame(region_encoded, columns=encoder.get_feature_names_out(['Region']))

# Removing Region column and concatinating the customer_profile and region_encoded
customers_profile = cprofile.drop('Region',axis=1)
customers_profile = pd.concat([customers_profile, region_encoded_df], axis=1)

#Applying Standardization
sc = StandardScaler()
sc_features = sc.fit_transform(customers_profile.drop('CustomerID', axis=1))

"""# 4. Clustering with KMeans #
Finding the optimal number of clusters using Elbow Method
"""

inertia = []
silhouette_scores = []
db_indexes = []

for k in range(2, 40):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(sc_features)

    inertia.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(sc_features, kmeans.labels_))
    db_indexes.append(davies_bouldin_score(sc_features, kmeans.labels_))

""" 1. Plotting Elbow Method for Inertia"""

plt.figure(figsize=(8, 6))
plt.plot(range(2, 40), inertia, marker='o')
plt.title('Elbow Method: Inertia vs. Number of Clusters')
plt.xlabel('Number of Clusters')
plt.ylabel('Inertia')
plt.show()

"""2. Plotting Silhouette Scores"""

plt.figure(figsize=(8, 6))
plt.plot(range(2, 40), silhouette_scores, marker='o')
plt.title('Silhouette Scores vs. Number of Clusters')
plt.xlabel('Number of Clusters')
plt.ylabel('Silhouette Score')
plt.show()

"""3. Plotting DB Index"""

plt.figure(figsize=(8, 6))
plt.plot(range(2, 40), db_indexes, marker='o')
plt.title('DB Index vs. Number of Clusters')
plt.xlabel('Number of Clusters')
plt.ylabel('DB Index')
plt.show()

"""# Choose optimal number of clusters #
4. Perform KMeans clustering with the optimal number of clusters
"""

optimal_n = 25

kmeans = KMeans(n_clusters=optimal_n, random_state=42)
cprofile['Cluster'] = kmeans.fit_predict(sc_features)

"""5. Evaluating Clustering Performance"""

print(f'Optimal Number of Clusters: {optimal_n}')
print(f'Davies-Bouldin Index: {davies_bouldin_score(sc_features, cprofile["Cluster"])}')
print(f'Silhouette Score: {silhouette_score(sc_features, cprofile["Cluster"])}')

# 6. Visualizing the Clusters using PCA
pca = PCA(n_components=2)
pca_result = pca.fit_transform(sc_features)

# Create a DataFrame for PCA results
pca_df = pd.DataFrame(pca_result, columns=['PCA1', 'PCA2'])
pca_df['Cluster'] = cprofile['Cluster']

plt.figure(figsize=(10, 8))
sns.scatterplot(data=pca_df, x='PCA1', y='PCA2', hue='Cluster', palette='Set1', s=50, alpha=0.7)
plt.title('Customer Segmentation with PCA')
plt.show()

"""7. Reporting the Results: Number of Clusters, DB Index, and other metrics"""

print(f"\nClustering Report:")
print(f"Number of clusters: {optimal_n}")
print(f"Davies-Bouldin Index: {davies_bouldin_score(sc_features, cprofile['Cluster'])}")
print(f"Silhouette Score: {silhouette_score(sc_features, cprofile['Cluster'])}")

"""8. Saving the Final Clusters to a CSV File"""

cprofile.to_csv('Customer_Segmentation.csv', index=False)
print("\nCustomer Segmentation results saved to 'Customer_Segmentation.csv'.")

df = pd.read_csv('Customer_Segmentation.csv')
print(df)