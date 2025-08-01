import pandas as pd
import joblib
import numpy as np
from core.models import ProductSalesHistory, Product
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime, timedelta

def prepare_training_data():
    """Prepare comprehensive training data with demand features"""
    
    # Get historical sales data
    history_data = ProductSalesHistory.objects.select_related('product').values(
        'product_id', 'weekly_sales', 'selling_price', 'date', 
        'stock_count', 'demand_score',
        'product__base_price', 'product__max_price'
    )
    
    df = pd.DataFrame(history_data)
    
    if df.empty:
        print("No historical data found. Generating sample data...")
        return generate_sample_data()
    
    # Prepare features
    df.rename(columns={
        'product__base_price': 'base_price',
        'product__max_price': 'max_price'
    }, inplace=True)
    
    # Convert categorical product_id to numeric
    df['product_id'] = df['product_id'].astype('category').cat.codes
    
    # Convert date to ordinal
    df['date'] = pd.to_datetime(df['date']).map(pd.Timestamp.toordinal)
    
    # Sort by product and date
    df = df.sort_values(by=['product_id', 'date'])
    
    # Create lag features
    df['prev_week_sales'] = df.groupby('product_id')['weekly_sales'].shift(1).fillna(0)
    df['prev_price'] = df.groupby('product_id')['selling_price'].shift(1)
    df['price_change'] = df['selling_price'] - df['prev_price']
    
    # Create demand trend features
    df['sales_trend'] = df['weekly_sales'] - df['prev_week_sales']
    df['price_position'] = (df['selling_price'] - df['base_price']) / (df['max_price'] - df['base_price'])
    
    # Fill NaN values
    df = df.fillna(0)
    
    return df

def generate_sample_data():
    """Generate sample training data for initial model training"""
    np.random.seed(42)
    
    samples = []
    for product_id in range(1, 11):  # 10 products
        base_price = np.random.uniform(10, 50)
        max_price = base_price * 2
        
        for week in range(52):  # 52 weeks of data
            # Simulate seasonal demand
            seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * week / 52)
            base_sales = np.random.randint(5, 30)
            weekly_sales = int(base_sales * seasonal_factor)
            
            # Price based on demand (simplified logic)
            demand_ratio = weekly_sales / 20  # 20 is average
            price_multiplier = 1 + 0.3 * (demand_ratio - 1)  # Price increases with demand
            selling_price = base_price + (max_price - base_price) * min(price_multiplier, 1)
            
            samples.append({
                'product_id': product_id,
                'weekly_sales': weekly_sales,
                'prev_week_sales': weekly_sales + np.random.randint(-5, 6),
                'stock_count': np.random.randint(0, 100),
                'date': (datetime.now() - timedelta(weeks=52-week)).toordinal(),
                'current_price': selling_price,
                'demand_score': weekly_sales / max(1, weekly_sales + np.random.randint(-5, 6)),
                'base_price': base_price,
                'max_price': max_price,
                'selling_price': selling_price  # Target
            })
    
    return pd.DataFrame(samples)

def train_price_model():
    """Train the dynamic pricing model"""
    print("Preparing training data...")
    df = prepare_training_data()
    
    if df.empty:
        print("No data available for training")
        return
    
    # Define features and target
    feature_columns = [
        'product_id', 'weekly_sales', 'prev_week_sales', 'stock_count', 
        'date', 'current_price', 'demand_score'
    ]
    
    # Ensure all required columns exist
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    
    X = df[feature_columns]
    y = df['selling_price']
    
    print(f"Training with {len(df)} samples and {len(feature_columns)} features")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42
    )
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    # Evaluate model
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    train_mae = mean_absolute_error(y_train, train_pred)
    test_mae = mean_absolute_error(y_test, test_pred)
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)
    
    print(f"Training MAE: {train_mae:.2f}")
    print(f"Testing MAE: {test_mae:.2f}")
    print(f"Training R²: {train_r2:.3f}")
    print(f"Testing R²: {test_r2:.3f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    # Save model
    joblib.dump(model, 'pricing_model.pkl')
    print("Model saved successfully!")
    
    return model