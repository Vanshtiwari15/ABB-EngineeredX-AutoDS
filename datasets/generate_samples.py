"""
Script to generate sample datasets for AutoDS-LLM testing
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)

# Create datasets directory if it doesn't exist
datasets_dir = Path(__file__).parent
datasets_dir.mkdir(exist_ok=True)


def create_classification_dataset():
    """Create sample binary classification dataset (Iris-like)"""
    n_samples = 500
    
    data = {
        'sepal_length': np.random.normal(5.8, 0.8, n_samples),
        'sepal_width': np.random.normal(3.0, 0.4, n_samples),
        'petal_length': np.random.normal(3.7, 1.7, n_samples),
        'petal_width': np.random.normal(1.2, 0.8, n_samples),
        'species': np.random.choice(['setosa', 'versicolor', 'virginica'], n_samples)
    }
    
    df = pd.DataFrame(data)
    df.to_csv(datasets_dir / 'classification_iris.csv', index=False)
    print(f"✓ Created classification_iris.csv ({len(df)} samples)")


def create_regression_dataset():
    """Create sample regression dataset (Housing prices)"""
    n_samples = 500
    
    np.random.seed(42)
    square_feet = np.random.uniform(1000, 5000, n_samples)
    bedrooms = np.random.choice([1, 2, 3, 4, 5], n_samples)
    bathrooms = bedrooms * np.random.uniform(0.5, 1.5, n_samples)
    age_years = np.random.uniform(0, 50, n_samples)
    
    # Price is roughly: base + price per sqft + bedroom cost + age factor
    price = 100000 + (square_feet * 150) + (bedrooms * 50000) - (age_years * 500) + np.random.normal(0, 50000, n_samples)
    
    data = {
        'square_feet': square_feet,
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'age_years': age_years,
        'price': np.maximum(price, 50000)  # Ensure no negative prices
    }
    
    df = pd.DataFrame(data)
    df.to_csv(datasets_dir / 'regression_housing.csv', index=False)
    print(f"✓ Created regression_housing.csv ({len(df)} samples)")


def create_clustering_dataset():
    """Create sample clustering dataset"""
    n_samples = 500
    
    # Create 3 clusters
    cluster1 = np.random.normal([2, 2], 0.5, (n_samples//3, 2))
    cluster2 = np.random.normal([8, 8], 0.5, (n_samples//3, 2))
    cluster3 = np.random.normal([5, 2], 0.5, (n_samples - 2*n_samples//3, 2))
    
    X = np.vstack([cluster1, cluster2, cluster3])
    
    data = {
        'feature_1': X[:, 0].tolist(),
        'feature_2': X[:, 1].tolist(),
        'customer_id': list(range(len(X))),
    }
    
    df = pd.DataFrame(data)
    df.to_csv(datasets_dir / 'clustering_customers.csv', index=False)
    print(f"✓ Created clustering_customers.csv ({len(df)} samples)")


def create_nlp_dataset():
    """Create sample NLP sentiment dataset"""
    positive_reviews = [
        'Excellent product, highly recommended!',
        'Great quality and fast shipping',
        'Best purchase ever, very satisfied',
        'Outstanding service, will buy again',
        'Love this product, perfect!',
    ]
    
    negative_reviews = [
        'Terrible quality, complete waste of money',
        'Very disappointed with this purchase',
        'Awful customer service and poor quality',
        'Worst product ever, do not buy',
        'Broken on arrival, very upset',
    ]
    
    neutral_reviews = [
        'Average product, nothing special',
        'It does what it says it does',
        'Decent product for the price',
        'Neither good nor bad',
        'Satisfactory purchase',
    ]
    
    # Create dataset by repeating and adding variations
    reviews = []
    sentiments = []
    
    for _ in range(100):
        reviews.extend(positive_reviews)
        sentiments.extend(['positive'] * len(positive_reviews))
        reviews.extend(negative_reviews)
        sentiments.extend(['negative'] * len(negative_reviews))
        reviews.extend(neutral_reviews)
        sentiments.extend(['neutral'] * len(neutral_reviews))
    
    data = {
        'review': reviews[:500],
        'sentiment': sentiments[:500],
    }
    
    df = pd.DataFrame(data)
    df.to_csv(datasets_dir / 'nlp_sentiment.csv', index=False)
    print(f"✓ Created nlp_sentiment.csv ({len(df)} samples)")


def create_timeseries_dataset():
    """Create sample time series dataset"""
    n_samples = 500
    
    # Create synthetic time series data
    dates = pd.date_range(start='2023-01-01', periods=n_samples, freq='D')
    
    # Base trend
    trend = np.linspace(100, 150, n_samples)
    
    # Seasonal component
    seasonal = 20 * np.sin(2 * np.pi * np.arange(n_samples) / 365)
    
    # Random noise
    noise = np.random.normal(0, 5, n_samples)
    
    # Combine all components
    price = trend + seasonal + noise
    
    data = {
        'date': dates,
        'price': price,
        'volume': np.random.uniform(1000000, 5000000, n_samples),
    }
    
    df = pd.DataFrame(data)
    df.to_csv(datasets_dir / 'timeseries_stock.csv', index=False)
    print(f"✓ Created timeseries_stock.csv ({len(df)} samples)")


def create_mixed_dataset():
    """Create a mixed dataset with multiple features"""
    n_samples = 1000
    
    data = {
        'customer_id': range(1, n_samples + 1),
        'age': np.random.randint(18, 80, n_samples),
        'purchase_amount': np.random.exponential(100, n_samples),
        'loyalty_months': np.random.randint(0, 120, n_samples),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Home', 'Sports'], n_samples),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_samples),
        'purchase_frequency': np.random.randint(1, 50, n_samples),
        'avg_rating_given': np.random.uniform(1, 5, n_samples),
        'will_churn': np.random.choice(['Yes', 'No'], n_samples, p=[0.3, 0.7]),
    }
    
    df = pd.DataFrame(data)
    df.to_csv(datasets_dir / 'mixed_customers.csv', index=False)
    print(f"✓ Created mixed_customers.csv ({len(df)} samples)")


if __name__ == "__main__":
    print("Generating sample datasets...\n")
    create_classification_dataset()
    create_regression_dataset()
    create_clustering_dataset()
    create_nlp_dataset()
    create_timeseries_dataset()
    create_mixed_dataset()
    print("\n✓ All sample datasets generated successfully!")
