# ------------------------
# Filename: sephora_viz.py
# Author: Anu R
# Created: Sept 2020
# Python version: 3.7
# ------------------------

from sephora_data import *

# Read in csv
sample = pd.read_csv('sephora_website_dataset.csv')
df = pd.DataFrame(sample)

# Recode products into broader categories and filter for clean products
df_products_filtered = product_filter(df)
df_clean_beauty_only = ingredient_filter(df_products_filtered)

# Select relevant columns to create charts with
df_clean_beauty_cols = df_clean_beauty_only[['online_only', 'brand', 'category', 'love', 'number_of_reviews', 'price']]

# For each brand, get medians of numeric columns
df_clean_beauty_medians = df_clean_beauty_cols.groupby(['brand']).median().reset_index()

# Number of products by category per brand
df_clean_beauty_counts = df_clean_beauty_cols.groupby(['brand', 'category']).size().reset_index(name='number_of_products').sort_values(by=['number_of_products'], ascending=False)

# Consolidate category counts with median metrics for each brand
df_clean_beauty = pd.merge(df_clean_beauty_medians, df_clean_beauty_counts)

# Get top 10 brands by median number of reviews
ranked_by_reviews = df_clean_beauty.sort_values(by='number_of_reviews', ascending=False)
top_reviewed_brands = ranked_by_reviews.groupby(['brand']).median().reset_index().sort_values(by='number_of_reviews', ascending=False)
top_reviewed_brands_10 = top_reviewed_brands[:10]
top_reviewed_brands_10_names = top_reviewed_brands_10['brand'].tolist()
df_clean_beauty_top_reviewed = df_clean_beauty[df_clean_beauty['brand'].isin(top_reviewed_brands_10_names)]
df_clean_beauty_top_reviewed_brands_and_cats = df_clean_beauty_top_reviewed.groupby(['brand', 'category']).median().reset_index().sort_values(by='number_of_reviews', ascending=False)

# Get top 10 brands by total number of clean products
ranked_by_product_count = df_clean_beauty.groupby(['brand']).sum().reset_index().sort_values(by='number_of_products', ascending=False)
top_product_counts_10 = ranked_by_product_count[:10]
top_product_counts_10_names = top_product_counts_10['brand'].tolist()
df_clean_beauty_top_product_counts = df_clean_beauty[df_clean_beauty['brand'].isin(top_product_counts_10_names)]
df_clean_beauty_top_product_counts_grouped = df_clean_beauty_top_product_counts.groupby(['brand']).sum().reset_index()

# Get median reviews by product category for top 10 reviewed brands
reviews_by_cat = df_clean_beauty.groupby(['brand', 'category']).median().reset_index()
reviews_by_cat = reviews_by_cat[reviews_by_cat['brand'].isin(top_reviewed_brands_10_names)]

# Produce the charts from here
product_chart = stacked_bar_chart(sample=df_clean_beauty_top_reviewed_brands_and_cats,
                                  grouper_col='brand',
                                  x='number_of_products',
                                  y='brand',
                                  color_col='category',
                                  x_title='',
                                  y_title='Brand',
                                  main_title='Top 10 brands by clean beauty product count',
                                  orientation='h',
                                  file='product_chart'
                                  )

product_by_cat_chart = stacked_bar_chart(sample=reviews_by_cat,
                                         grouper_col='brand',
                                         x='number_of_reviews',
                                         y='brand',
                                         color_col='category',
                                         x_title='',
                                         y_title='Brand',
                                         main_title='Median number of reviews by product category for top 10 most reviewed brands',
                                         orientation='h',
                                         file='product_by_cat_chart'
                                         )

reviews_chart = dual_axis_bar(sample=df_clean_beauty_top_product_counts_grouped,
                              x='brand',
                              y1='number_of_reviews',
                              y2='number_of_products',
                              legend_y1='Reviews',
                              legend_y2='Products',
                              y1_title='Median number of reviews',
                              y2_title='Total number of clean products',
                              main_title='Top 10 brands by number of reviews',
                              file='reviews_chart'
                              )

price_chart = box_plot(sample=df_clean_beauty,
                       x='category',
                       y='price',
                       x_title='',
                       y_title='Median price (USD)',
                       main_title='Distribution of median price by product category',
                       file='price_chart'
                       )
