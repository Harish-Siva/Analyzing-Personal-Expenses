import pymysql
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

mydb = pymysql.connect(
  host="localhost",
  user="root",
  password="sql_1234h",
  database="expenses_tracker"
)

mycursor = mydb.cursor()

# Query the database to fetch data
mycursor.execute("SELECT DISTINCT * FROM expenses")
myresult = mycursor.fetchall()

# Get column names from the cursor description
columns = [col[0] for col in mycursor.description]
# Close the cursor and connection
mycursor.close()

# Convert the data to a pandas DataFrame
df = pd.DataFrame(myresult, columns=columns)

# Display the first few rows of the DataFrame
print(df.tail())

# 1.Number of Observations and Variables
print(f"Observations (Rows): {df.shape[0]}")
print(f"Variables (Columns): {df.shape[1]}")

# Data Types of Each Column
print("\nData Types:")
print(df.dtypes)

# Basic Statistics
print("\nBasic Statistics:")
print(df.describe(include='all'))

#2. Categorize variables into categorical and numerical
categorical_columns = df.select_dtypes(include=['object']).columns
numerical_columns = df.select_dtypes(include=['float64', 'int64']).columns

print(f"Categorical Columns: {list(categorical_columns)}")
print(f"Numerical Columns: {list(numerical_columns)}")

# Check distributions
for col in numerical_columns:
    sns.histplot(df[col], kde=True)
    plt.title(f'Distribution of {col}')
    plt.show()

for col in categorical_columns:
    print(f"\n{col} Value Counts:")
    print(df[col].value_counts())

#3. Pairplot for relationships
sns.pairplot(df)
plt.show()

# Correlation heatmap
correlation_matrix = df[numerical_columns].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title("Correlation Between Numerical Variables")
plt.show()

from scipy.stats import zscore

#4. Calculate Z-scores for numerical columns
z_scores = df[numerical_columns].apply(zscore)

# Identify outliers based on Z-scores (>3 or <-3)
outliers = (z_scores > 3) | (z_scores < -3)
print("\nOutliers Detected (Per Column):")
print(outliers.sum())

# Visualize outliers using boxplots
for col in numerical_columns:
    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df, x=col)
    plt.title(f'Boxplot for {col}')
    plt.show()

#5. Check for missing values
print("\nMissing Values Per Column:")
print(df.isnull().sum())

# Visualize missing values
plt.figure(figsize=(8, 6))
sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
plt.title('Heatmap of Missing Values')
plt.show()

#6. Check for duplicate rows
duplicate_count = df.duplicated().sum()
print("\nNumber of Duplicate Rows:", duplicate_count)

# Remove duplicates if necessary
df = df.drop_duplicates()
print("Duplicates removed. Updated row count:", df.shape[0])

#7. Ensure 'date' column is in datetime format
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])

    # Extract year and month
    df['year_month'] = df['date'].dt.to_period('M')

    # Plot trends over time
    if 'amount' in df.columns:
        monthly_expenses = df.groupby('year_month')['amount'].sum()
        monthly_expenses.plot(kind='line', marker='o', figsize=(10, 6))
        plt.title("Monthly Expense Trends")
        plt.xlabel("Year-Month")
        plt.ylabel("Total Amount")
        plt.grid()
        plt.show()

#8. Variability (standard deviation) in numerical columns
print("\nVariability (Standard Deviation) for Numerical Columns:")
print(df[numerical_columns].std())

# Coefficient of variation (CV) for numerical columns
cv = (df[numerical_columns].std() / df[numerical_columns].mean()) * 100
print("\nCoefficient of Variation (%):")
print(cv)

#9. Example: Compare actual expenses with expected budget (if applicable)
if 'amount' in df.columns and 'budget' in df.columns:
    df['difference'] = df['amount'] - df['budget']
    print("\nDifferences Between Actual and Budgeted Amounts:")
    print(df[['amount', 'budget', 'difference']].head())
    
    # Visualize discrepancies
    plt.figure(figsize=(8, 6))
    sns.histplot(df['difference'], kde=True, color='red')
    plt.title("Distribution of Differences (Actual vs. Budget)")
    plt.show()

#10. Grouping by 'category' and calculating the mean of 'amount_paid'
if 'category' in df.columns and 'amount_paid' in df.columns:
    category_summary = df.groupby('category')['amount_paid'].mean()
    print("\nAverage Amount Paid by Category:")
    print(category_summary)

    # Visualize the average amount paid by category
    category_summary.plot(kind='bar', figsize=(10, 6), color='teal')
    plt.title("Average Expense by Category")
    plt.xlabel("Category")
    plt.ylabel("Average Amount Paid")
    plt.xticks(rotation=45)
    plt.show()
else:
    print("Either 'category' or 'amount_paid' column is missing.")
