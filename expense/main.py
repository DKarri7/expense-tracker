import mysql.connector
import datetime

#creating database connection

def database_connection():
    return mysql.connector.connect(
        host = '127.0.0.1',
        user = 'root',
        password = 'deepak123',
        database = 'expensedb'
    )

# creating user table in database

def create_user_table():
    conn = database_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
        ) 
    ''')
    conn.commit()
    conn.close()

# creating expense table

def create_expense_table():
    conn = database_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DROP TABLE IF EXISTS expenses')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    amount FLOAT,
                    category VARCHAR(255),
                    description VARCHAR(255),
                    datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
    except Exception as e:
        print(f"Error creating expenses table: {e}")

    conn.commit()
    conn.close()


### expense tracker main code

class ExpenseTracker:
    def __init__(self, user_id):
        self.user_id = user_id
        self.expense = []

    def add_expense(self, amount, category, description):
        conn = database_connection()
        cursor = conn.cursor()

        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        #to insert new expense
        cursor.execute('INSERT INTO expenses (user_id, amount, category, description, datetime) VALUES (%s, %s, %s, %s, %s)', 
                       (self.user_id, amount, category, description, current_datetime,))
        
        conn.commit()
        conn.close()

        print(f"Expense added successfully on {current_datetime}!")



    def view_expenses_bycategory(self):
        conn = database_connection()
        cursor = conn.cursor()

        # Retrieve distinct categories
        cursor.execute('SELECT DISTINCT category FROM expenses WHERE user_id = %s', (self.user_id,))
        categories = cursor.fetchall()

        conn.close()

        if not categories:
            print("No categories found.")
            return

        print("Available Categories:")
        for index, category in enumerate(categories, start=1):
            print(f"{index}. {category[0]}")

        choice = input("Enter the number corresponding to the category you want to view (Enter 'all' to view all categories): ")

        if choice.lower() == 'all':
            self.display_expenses('all')
        elif choice.isdigit() and 1 <= int(choice) <= len(categories):
            selected_category = categories[int(choice) - 1][0]
            self.display_expenses(selected_category)
        else:
            print("Invalid choice. Please enter a valid number or 'all'.")

    def display_expenses(self, selected_category):
        conn = database_connection()
        cursor = conn.cursor()

        if selected_category == 'all':
            # Retrieve all expenses
            cursor.execute('SELECT * FROM expenses WHERE user_id = %s', (self.user_id,))
        else:
            # Retrieve expenses for the selected category
            cursor.execute('SELECT * FROM expenses WHERE user_id = %s AND category = %s', (self.user_id, selected_category))

        expenses = cursor.fetchall()

        conn.close()

        if not expenses:
            print("No expenses to display.")
            return

        print("\nExpense Details:")
        for expense in expenses:
            print(f"Category: {expense[2]}, Amount: ${expense[3]}, Description: {expense[4]}, Added on Date: {expense[5]}")

# ... (other parts of your code)

 


    def view_summary(self):
        conn = database_connection()
        cursor = conn.cursor()

        # Retrieve distinct categories
        cursor.execute('SELECT DISTINCT category FROM expenses WHERE user_id = %s', (self.user_id,))
        categories = cursor.fetchall()

        print("\nExpense Summary:")
        total_expense = 0

        for category in categories:
            cursor.execute('SELECT SUM(amount) FROM expenses WHERE user_id = %s AND category = %s', (self.user_id, category[0]))
            category_total_amount = cursor.fetchone()[0] or 0
            total_expense += category_total_amount

            print(f"{category[0]}: ${category_total_amount}")

        print(f"Total Expense: ${total_expense}")

        conn.close()


#user authentication ---- user ID

def get_userID(username):
    conn = database_connection()
    cursor = conn.cursor()

    query = 'SELECT id FROM users WHERE LOWER(username) = LOWER(%s)'
    # print(f"DEBUG: SQL Query: {query}, Parameters: ({username},)")

    cursor.execute(query, (username,))
    rows = cursor.fetchall()
    #print(f"DEBUG: Rows Returned: {rows}")

    user_id = rows[0][0] if rows else None

    #print(f"DEBUG: Username: {username}, User ID: {user_id}")

    conn.close()

    return user_id


#user sign up function

def user_signup():
    create_user_table()
    create_expense_table()

    conn = database_connection()
    cursor = conn.cursor()

    username = input("Enter your Username: ")
    password = input("Enter your password: ")

    #to check if the username already exists
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        print("Username already exists. Please choose a different username.")
    else:
        #to insert new user in database
        cursor.execute('INSERT INTO users (username, password) VALUE (%s, %s)', (username, password))
        print("Account created successfully")

    conn.commit()
    conn.close()

    #to login after signup
    login_choice = input("Do you want to log in now? (yes/no); ")
    if login_choice == 'yes':
        tracker = user_login()
    else:
        print("Goodbye!")

#user login function

def user_login():
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    user_id = get_userID(username)

    # print(f"DEBUG: Username: {username}, Password: {password}, User ID: {user_id}")

    if user_id:
        print("Login successful")
        tracker = ExpenseTracker(user_id)
        return tracker
    else:
        print('Login failed. Please check your username and password')


#main code

print("Welcome to Expense Tracker")
print("1. Sign UP")
print("2. Login ")

choice = int(input("Enter your choice: "))

if choice == 1:
    user_signup()
elif choice == 2:
    tracker = user_login()
    if tracker:
        while True:
            print("\nExpense Tracker Menu")
            print("1. Add Expense")
            print("2. View Expenses by Category")
            print("3. View Summary")
            print("4. Exit")

            menu_choice = int(input("Enter your choice: "))

            if menu_choice == 1:
                amount = float(input("Enter the Expense Amount: "))
                category = input("Enter the Expense Category: ")
                description = input("Enter a brief description: ")
                tracker.add_expense(amount, category, description)

            elif menu_choice == 2:
                tracker.view_expenses_bycategory()

            elif menu_choice == 3:
                tracker.view_summary()

            elif menu_choice == 4:
                print("Exiting the Expense Tracker. Goodbye!")
                break

            else:
                print("Invalid choice. Please enter a number between 1 and 4.")