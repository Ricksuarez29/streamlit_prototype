import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
import joblib

# Load the dataset
df = pd.read_csv('car_price_dataset.csv')

# I define numerical and categorical features
numerical_features = ['Year', 'Engine_Size', 'Mileage', 'Doors', 'Owner_Count']
categorical_features_onehot = ['Brand', 'Model', 'Fuel_Type']
categorical_features_ordinal = ['Transmission']

# Define transformers
numerical_transformer = StandardScaler()
categorical_transformer_onehot = OneHotEncoder(handle_unknown='ignore')
categorical_transformer_ordinal = OrdinalEncoder(categories=[['Manual', 'Semi-Automatic', 'Automatic']])

# Combine the preprocessing steps
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numerical_transformer, numerical_features),
        ('cat_onehot', categorical_transformer_onehot, categorical_features_onehot),
        ('cat_ordinal', categorical_transformer_ordinal, categorical_features_ordinal)
    ]
)

# Create the pipeline
pipeline = Pipeline(steps=[('preprocessor', preprocessor)])
X = df.drop(columns='Price')
y = df['Price']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# This hyperparameters were tuned using GridSearchCV.
best_rf_model = RandomForestRegressor(
    max_depth=20,
    min_samples_leaf=2,
    min_samples_split=2,
    n_estimators=150,
    random_state=42
)

# Create a pipeline with the preprocessor and the model
rf_pipeline = Pipeline(steps=[
    ('preprocessor', pipeline.named_steps['preprocessor']),
    ('model', best_rf_model)
])

# Fit the pipeline on the training data
rf_pipeline.fit(X_train, y_train)

# Make predictions on the test set
y_pred_rf = rf_pipeline.predict(X_test)

# Calculate RMSE and R-squared
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
r2_rf = r2_score(y_test, y_pred_rf)

# Save the trained pipeline to a file
joblib.dump(rf_pipeline, 'rf_model.pkl')