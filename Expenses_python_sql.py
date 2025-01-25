import pandas as pd
import random
from faker import Faker
import calendar

# Initialize the Faker instance
fake = Faker()

# Define categories with corresponding plausible descriptions
category_descriptions = {
    'Food': [
        'Pizza order',
        'Grocery shopping at local market',
        'Dinner at Italian restaurant',
        'Coffee at cafe',
        'Bakery purchase'
    ],
    'Transportation': [
        'Taxi fare',
        'Monthly bus pass',
        'Train ticket to downtown',
        'Gas station refill',
        'Ride-sharing service payment'
    ],
    'Bills': [
        'Electricity bill payment',
        'Water utility bill',
        'Internet service provider charge',
        'Mobile phone bill',
        'Cable TV subscription'
      ],
    'Entertainment': [
        'Movie theater ticket',
        'Concert ticket purchase',
        'Streaming service subscription',
        'Amusement park entry fee',
        'Bookstore purchase'
    ],
    'Healthcare': [
        'Pharmacy medication purchase',
        'Doctor consultation fee',
        'Dental clinic payment',
        'Health insurance premium',
        'Optician eyewear purchase'
    ],
    'Groceries': [
        'Dairy products',
        'Meat and fish',
        'Kitchen items',
        'Snacks and Drinks',
        'Cooking Essentials'
    ],
    'Subscriptions': [
        'Amazon Prime Membership',
        'Netflix',
        'Spotify',
        'LinkedIn',
        'Disney Hotstar'
    ]
}

# Define cashback rates based on payment mode
cashback_rates = {
    'UPI': 0.05,     # 5% cashback for UPI
    'Online': 0.10,  # 10% cashback for Online
    # Other payment modes can have 0% cashback or specified rates
    'Cash': 0.15,
    'CardTransaction': 0.05,
    'Netbanking': 0.05
}

# Function to generate random dates within a specific month and year
def generate_random_dates(year, month, num_records):
    # Determine the number of days in the month
    num_days = pd.Period(year=year, month=month, freq='M').days_in_month
    
    if num_records <= num_days:
        # Generate unique random days within the month
        days = random.sample(range(1, num_days + 1), num_records)
    else:
        # Allow duplicates if num_records exceeds num_days
        days = [random.randint(1, num_days) for _ in range(num_records)]
    
    # Create dates for the specified month and year
    dates = [f"{year}-{month:02d}-{day:02d}" for day in days]
    return dates

# Function to generate monthly expense data
def generate_monthly_data(year, month, num_records):
    dates = generate_random_dates(year, month, num_records)
    categories = list(category_descriptions.keys())
    payment_modes = list(cashback_rates.keys())
    
    data = {
        'Date': dates,
        'Category': [],
        'Payment Mode': [],
        'Description': [],
        'Amount Paid': [],
        'Cashback': []
    }
    
    for _ in range(num_records):
        category = random.choice(categories)
        payment_mode = random.choice(payment_modes)
        description = random.choice(category_descriptions[category])
        amount_paid = round(random.uniform(10, 500), 2)
        cashback = round(amount_paid * cashback_rates[payment_mode], 2)
        
        data['Category'].append(category)
        data['Payment Mode'].append(payment_mode)
        data['Description'].append(description)
        data['Amount Paid'].append(amount_paid)
        data['Cashback'].append(cashback)
    
    return pd.DataFrame(data)

# Dictionary to store DataFrames for each month
monthly_dataframes = {}

# Generate and store data for each month
for month in range(1, 13):
    # Generate data for the current month
    monthly_data = generate_monthly_data(2023, month, num_records=180)
    
    # Add the month name column for clarity
    monthly_data['Month'] = calendar.month_name[month]
    
    # Store the DataFrame in the dictionary using the month name as the key
    monthly_dataframes[calendar.month_name[month]] = monthly_data

# Example: Accessing and displaying the first few rows of January's data
print(monthly_dataframes['January'].head())

import os

# Ensure the directory to save CSV files exists
output_dir = 'expense_data'
os.makedirs(output_dir, exist_ok=True)

# Iterate over each month's DataFrame in the dictionary
for month_name, month_data in monthly_dataframes.items():
    # Define the file path for the CSV file
    file_path = os.path.join(output_dir, f'{month_name}_2023.csv')
    
    # Save the DataFrame to a CSV file
    month_data.to_csv(file_path, index=False, encoding='utf-8')
    
    print(f'Saved {month_name} data to {file_path}')

import mysql.connector

# Create a new database and table if they do not exist
def create_database_and_table():
    connection = create_mysql_connection()
    cursor = connection.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS expenses_db")
    cursor.execute("USE expenses_db")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            date DATE,
            category VARCHAR(255),
            payment_mode VARCHAR(255),
            description VARCHAR(255),
            amount_paid FLOAT,
            cashback FLOAT,
            month VARCHAR(255)
        )
    ''')

    connection.commit()
    cursor.close()
    connection.close()

# Function to insert data into MySQL database
def insert_data_into_mysql(month_data):
    try:
        import pymysql
        
        mydb=pymysql.connect(
        host="localhost",         # Your MySQL server host (use 'localhost' if running locally)
        user="root",     # Your MySQL username
        password="sql_1234h", # Your MySQL password
        database="expenses_tracker" # The database name to connect to (you can create one before)
    )
        cursor = mydb.cursor()

        insert_query = '''
        INSERT INTO expenses (date, category, payment_mode, description, amount_paid, cashback, month)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''

        for _, row in month_data.iterrows():
            cursor.execute(insert_query, (
                row['Date'], row['Category'], row['Payment Mode'], row['Description'],
                row['Amount Paid'], row['Cashback'], row['Month']
            ))

        mydb.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
# Insert all monthly data into the database
for month_name, month_data in monthly_dataframes.items():
    insert_data_into_mysql(month_data)
    print(f'Data for {month_name} inserted into MySQL database')