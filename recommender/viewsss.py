from django.shortcuts import render
from sklearn.cluster import KMeans
import pandas as pd
import joblib

# Load the preprocessed data and model

# Filter by city and restaurant
def filter_by_city_and_restaurant(data, city=None, restaurant=None):
    if city:
        data = data[data['City'] == city]
    if restaurant:
        data = data[data['Restaurant Name'] == restaurant]
    return data

def top_restaurants_view(request):
    city = request.GET.get('city', 'Gurgaon')  # Default to Gurgaon if city is not specified
    restaurant = request.GET.get('restaurant', None)
    Featured_data_cleaned = joblib.load(r'C:\Users\praneet_bawa\Desktop\food_recommend\zomato_recommendation\recommender\cleaned_zomato_data.pkl')
    kmeans = joblib.load(r'C:\Users\praneet_bawa\Desktop\food_recommend\zomato_recommendation\recommender\kmeans_model.pkl')
    data = Featured_data_cleaned

# Calculate popularity score and assign clusters
    data['Popularity_Score'] = data['Aggregate rating'] * data['Votes']
    kmeans = KMeans(n_clusters=3, random_state=42)
    data['Cluster'] = kmeans.fit_predict(data[['Aggregate rating', 'Votes']])

    # Identify the cluster with the highest popularity score
    cluster_means = data.groupby('Cluster')['Popularity_Score'].mean()
    highest_cluster = cluster_means.idxmax()
    highest_cluster_data = data[data['Cluster'] == highest_cluster]


    # Apply filter and sort by Popularity_Score
    filtered_data = filter_by_city_and_restaurant(highest_cluster_data, city=city, restaurant=restaurant)
    filtered_data_sorted = filtered_data.sort_values(by='Popularity_Score', ascending=False).head(10)
    print(filtered_data_sorted.head())  # Print the top rows of the DataFrame
    filtered_data_sorted.rename(columns={
    'Restaurant Name': 'Restaurant_Name',
    'City': 'City',
    'Aggregate rating': 'Aggregate_rating',
    'Votes': 'Votes',
    'Popularity_Score': 'Popularity_Score'
    }, inplace=True)

    # Pass data to the template
    context = {
        'restaurants': filtered_data_sorted.to_dict(orient='records')  # Convert DataFrame to dictionary
    }
    #print(filtered_data_sorted)
    return render(request, 'home.html', context)
