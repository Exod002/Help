import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder, FunctionTransformer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import LogisticRegression


##############################################################################
# 1. Custom Transformer to Concatenate Text Fields (Title + Description)
##############################################################################
class TextConcatTransformer(BaseEstimator, TransformerMixin):
    """
    Concatenates multiple text columns into a single string per row.
    """

    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        # No fitting necessary for this transformer
        return self

    def transform(self, X):
        # Fill missing text with empty strings, then join them
        return X[self.columns].fillna('').agg(' '.join, axis=1)


##############################################################################
# 2. Build Pipelines for Text and Categorical Preprocessing
##############################################################################

# 2.1 Text Pipeline (Title + Description -> HashingVectorizer)
text_pipeline = Pipeline([
    ('concat', TextConcatTransformer(columns=['Title', 'Description'])),
    ('hash', HashingVectorizer(n_features=2 ** 15, alternate_sign=False))
])

# 2.2 Incident Origin Pipeline (one-hot encode)
incident_pipeline = Pipeline([
    ('fillna', FunctionTransformer(lambda X: X.fillna(''))),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# 2.3 Category Pipeline (for Subcategory prediction)
category_pipeline = Pipeline([
    ('fillna', FunctionTransformer(lambda X: X.fillna(''))),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

##############################################################################
# 3. ColumnTransformers for Category vs. Subcategory
##############################################################################

# 3.1 For predicting Category (features: Title, Description, Incident Origin)
category_preprocessor = ColumnTransformer([
    ('text', text_pipeline, ['Title', 'Description']),
    ('incident', incident_pipeline, ['Incident Origin']),
], remainder='drop')

# 3.2 For predicting Subcategory (features: Title, Description, Incident Origin, Category)
subcategory_preprocessor = ColumnTransformer([
    ('text', text_pipeline, ['Title', 'Description']),
    ('incident', incident_pipeline, ['Incident Origin']),
    ('cat', category_pipeline, ['Category']),
], remainder='drop')

##############################################################################
# 4. Load & Prepare the Training Data
##############################################################################
# Use low_memory=False to avoid DtypeWarning on large/mixed-type CSVs
df = pd.read_csv("incident.csv", low_memory=False)

# Split data:
#   - df_cat_train: rows with a known Category (for Category model)
#   - df_sub_train: rows with a known Subcategory (for Subcategory model)
df_cat_train = df[df['Category'].notna()]
df_sub_train = df[df['Subcategory'].notna()]

# Debug prints to ensure these DataFrames are not empty
print("df_cat_train shape:", df_cat_train.shape)
print("df_sub_train shape:", df_sub_train.shape)

##############################################################################
# 5. Define & Fit the Models (One-Time, NOT Incremental)
##############################################################################

# -- 5.1 Category Model (LogisticRegression)
category_model = Pipeline([
    ('preprocessor', category_preprocessor),
    ('clf', LogisticRegression(max_iter=1000, random_state=42))
])

if df_cat_train.empty:
    print("WARNING: df_cat_train is empty! Category model cannot be fitted.")
else:
    category_model.fit(
        df_cat_train[['Title', 'Description', 'Incident Origin']],
        df_cat_train['Category']
    )
    print("Category model fitted successfully.")

# -- 5.2 Subcategory Model (LogisticRegression)
subcategory_model = Pipeline([
    ('preprocessor', subcategory_preprocessor),
    ('clf', LogisticRegression(max_iter=1000, random_state=42))
])

if df_sub_train.empty:
    print("WARNING: df_sub_train is empty! Subcategory model cannot be fitted.")
else:
    subcategory_model.fit(
        df_sub_train[['Title', 'Description', 'Incident Origin', 'Category']],
        df_sub_train['Subcategory']
    )
    print("Subcategory model fitted successfully.")


##############################################################################
# 6. Define Functions for Prediction
##############################################################################

def predict_category_if_missing(row):
    """
    Predicts the Category for a single row (Series) if it's missing.
    Returns the existing Category if present, otherwise predicts one.
    """
    if pd.isna(row['Category']):
        row_df = pd.DataFrame([row])
        # Only predict if the category_model is actually fitted
        return category_model.predict(row_df[['Title', 'Description', 'Incident Origin']])[0]
    else:
        return row['Category']


def predict_subcategory(row):
    """
    Predicts the Subcategory for a single row (Series).
    Steps:
      1) If both Title and Description are missing, return None (no info).
      2) If Category is missing, predict it first.
      3) Then predict Subcategory using the known or predicted Category.
    """
    if pd.isna(row['Title']) and pd.isna(row['Description']):
        return None

    # Ensure Category is filled in (either existing or predicted)
    row['Category'] = predict_category_if_missing(row)

    # Now predict Subcategory (only if subcategory_model is fitted)
    row_df = pd.DataFrame([row])
    return subcategory_model.predict(
        row_df[['Title', 'Description', 'Incident Origin', 'Category']]
    )[0]


##############################################################################
# 7. Predict on New Data
##############################################################################
# Read new data with low_memory=False
new_data = pd.read_csv("new_incident_data.csv", low_memory=False)
print("new_data shape:", new_data.shape)

# Predict subcategory for each row
new_data['Predicted_Subcategory'] = new_data.apply(predict_subcategory, axis=1)

# Save or display results
new_data.to_csv("predicted_incidents.csv", index=False)
print("Predictions saved to predicted_incidents.csv")
