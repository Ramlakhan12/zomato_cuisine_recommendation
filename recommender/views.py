from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from sklearn.cluster import KMeans
import pandas as pd
import joblib
from .models import UserProfile, Order
from .forms import OrderHistoryForm

# ... (other imports and functions remain the same)
def filter_by_city_and_restaurant(data, city=None, restaurant=None):
    if city:
        data = data[data['City'] == city]
    if restaurant:
        data = data[data['Restaurant Name'] == restaurant]
    return data

def top_restaurants_view(request):
    if request.user.is_authenticated:
        user_profile = request.user.userprofile
    else:
        # Handle anonymous users (e.g., default to a generic recommendation)
        user_profile = None

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

    # **User-based recommendation**
    if user_profile:
        user_orders = user_profile.order_history.all()
        user_preferred_restaurants = [order.restaurant for order in user_orders]
        user_recommended_data = highest_cluster_data[highest_cluster_data['Restaurant Name'].isin(user_preferred_restaurants)]
        if not user_recommended_data.empty:
            # User has previous orders, prioritize those recommendations
            recommended_data = user_recommended_data
        else:
            # No previous orders, default to general recommendation
            recommended_data = highest_cluster_data
    else:
        recommended_data = highest_cluster_data

    # Apply filter and sort by Popularity_Score
    filtered_data = filter_by_city_and_restaurant(recommended_data, city=city, restaurant=restaurant)
    filtered_data_sorted = filtered_data.sort_values(by='Popularity_Score', ascending=False).head(10)

    # ... (rest of the view remains the same)
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

@login_required
def add_order_history(request):
    if request.method == 'POST':
        form = OrderHistoryForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            request.user.userprofile.order_history.add(order)
            return redirect('top_restaurants_view')
    else:
        form = OrderHistoryForm()
    return