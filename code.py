import sqlite3

class RestaurantManagementSystem:
    def __init__(self):
        self.orders = []
        self.reservations = []
        self.menu = {}
        self.customer_address = ""
        self.create_connection()
        self.setup_database()
        self.load_menu()

    def create_connection(self):
        self.connection = sqlite3.connect('restaurant_management.db')
        self.cursor = self.connection.cursor()

    def setup_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT UNIQUE,
                price REAL,
                rating REAL DEFAULT 0,
                rating_count INTEGER DEFAULT 0,
                comments TEXT DEFAULT ''
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                items TEXT,
                total REAL,
                address TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_number INTEGER,
                name TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT
            )
        ''')
        self.connection.commit()

    def load_menu(self):
        self.cursor.execute('SELECT item, price, rating, rating_count, comments FROM menu')
        rows = self.cursor.fetchall()
        for row in rows:
            item, price, rating, rating_count, comments = row
            self.menu[item] = {
                "price": price,
                "rating": rating,
                "rating_count": rating_count,
                "comments": comments.split(',') if comments else []
            }

    def start(self):
        auth_system = self.UserAuthentication(self.cursor)  # Pass the cursor here
        role = auth_system.run()

        if role == "admin":
            self.admin_dashboard()
        elif role == "customer":
            self.customer_dashboard()

    class UserAuthentication:
        def __init__(self, cursor):
            self.cursor = cursor

        def register(self):
            print("\n--- Register ---")
            username = input("Enter a username: ")
            self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            if self.cursor.fetchone():
                print("Username already exists. Please choose a different username.")
                return
            password = input("Enter a password: ")
            print("Roles: [admin, customer]")  # Removed staff role
            role = input("Enter your role: ").lower()
            if role not in ["admin", "customer"]:  # Updated role check
                print("Invalid role. Please register again.")
                return
            self.cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                                (username, password, role))
            self.cursor.connection.commit()  # Commit the changes
            print(f"User  '{username}' registered successfully as '{role}'!")

        def login(self):
            print("\n--- Login ---")
            username = input("Enter your username: ")
            self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = self.cursor.fetchone()
            if not user:
                print("Username not found. Please register first.")
                return
            password = input("Enter your password: ")
            if user[2] == password:  # Assuming password is the third column
                role = user[3]  # Assuming role is the fourth column
                print(f"Welcome, {username}! You are logged in as '{role}'.")
                return role
            else:
                print("Incorrect password. Please try again.")
                return None

        def run(self):
            while True:
                print("\n--- User Authentication System ---")
                print("1. Register")
                print("2. Login")
                print("3. Exit")
                choice = input("Enter your choice: ")

                if choice == "1":
                    self.register()
                elif choice == "2":
                    role = self.login()
                    if role:
                        return role
                elif choice == "3":
                    print("Exiting the system. Goodbye!")
                    return None
                else:
                    print("Invalid choice. Please try again.")

    def admin_dashboard(self):
        while True:
            print("\n--- Admin Dashboard ---")
            print("1. Update Menu")
            print("2. Check Total Orders Today")
            print("3. See Feedback on Each Item")
            print("4. View Pending Online Orders")
            print("5. Exit")
            choice = input ("Enter your choice: ").strip()

            if choice == "1":
                self.update_menu()
            elif choice == "2":
                self.check_total_orders()
            elif choice == "3":
                self.view_feedback()
            elif choice == "4":
                self.view_pending_orders()
            elif choice == "5":
                print("See you soon, Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def customer_dashboard(self):
        while True:
            print("\n--- Customer Dashboard ---")
            print("1. Online Ordering")
            print("2. Table Reservations")
            print("3. View Menu")
            print("4. Give Feedback")
            print("5. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.online_ordering()
            elif choice == "2":
                self.manage_reservations()
            elif choice == "3":
                self.view_menu()
            elif choice == "4":
                self.feedback_system()
            elif choice == "5":
                print("See you soon, Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def online_ordering(self):
        while True:
            print("\n--- Online Ordering ---")
            print("Choose the option:")
            print("1. See the Menu")
            print("2. Order Food")
            print("3. My Orders")
            print("4. My Address")
            print("5. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.view_menu()
            elif choice == "2":
                self.place_order()
            elif choice == "3":
                self.view_my_orders()
            elif choice == "4":
                self.manage_address()
            elif choice == "5":
                print("Exiting Online Ordering. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def view_menu(self):
        print("\n--- Menu ---")
        for item, details in self.menu.items():
            rating = details.get('rating', 'N/A')  # Default to 'N/A' if rating is missing
            price = details.get('price', 'N/A')   # Default to 'N/A' if price is missing
            comments = details.get('comments', [])
            print(f"{item}: Price: ${price if price != 'N/A' else 'N/A'}, Rating: {rating:.1f}, Comments: {comments}")

    def place_order(self):
        print("\n--- Place Your Order ---")
        order = {}
        while True:
            item = input("Enter the item you want to order (or type 'done' to finish): ")
            if item.lower() == 'done':
                break
            if item in self.menu:
                quantity = int(input(f"Enter the quantity for {item}: "))
                order[item] = quantity
                print(f"Added {quantity} x {item} to your order.")
            else:
                print("Item not found in the menu. Please try again.")

        if order:
            total = sum(self.menu[item]["price"] * quantity for item, quantity in order.items())
            payment_method = input("Choose payment method (1: Cash on Delivery): ")
            if payment_method == "1":
                if not self.customer_address:
                    print("Please provide your address before placing the order.")
                    return
                self.insert_order({"items": order, "total": total, "address": self.customer_address})
                print(f"Your order has been placed! Total amount: ${total:.2f}.")
            else:
                print("Invalid payment method. Please try again.")
        else:
            print("No items ordered.")

    def view_my_orders(self):
        print("\n--- My Orders ---")
        self.cursor.execute('SELECT * FROM orders')
        rows = self.cursor.fetchall()
        if not rows:
            print("You have no previous orders.")
            return
        for index, order in enumerate(rows, start=1):
            items, total, address = order[1], order[2], order[3]
            print(f"Order {index}: {items} | Total: ${total:.2f} | Address: {address}")

    def manage_address(self):
        print("\n--- Manage My Address ---")
        if self.customer_address:
            print(f"Current Address: {self.customer_address}")
            update = input("Do you want to update your address? (yes/no): ").lower()
            if update == 'yes':
                self.customer_address = input("Enter your new address: ")
                print("Address updated successfully.")
        else:
            self.customer_address = input("Enter your address: ")
            print("Address saved successfully.")

    def feedback_system(self):
        print("\n--- Feedback System ---")
        while True:
            print("1. Give Feedback")
            print("2. View Menu with Feedback")
            print("3. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                self.get_feedback()
            elif choice == "2":
                self.display_feedback_menu()
            elif choice == "3":
                print("Exiting Feedback System.")
                break
            else:
                print("Invalid choice. Please try again.")

    def display_feedback_menu(self):
        print("\n--- Menu with Feedback ---")
        for item, details in self.menu.items():
            print(
                f"{item}: ${details['price']:.2f} | Rating: {details['rating']:.1f} | Comments: {details['comments']}"
            )

    def get_feedback(self):
        item = input("\nEnter the menu item you want to provide feedback on: ").strip()
        if item not in self.menu:
            print("Item not found in the menu.")
            return

        try:
            rating = int(input("Enter your rating (1-10): ").strip())
            if rating < 1 or rating > 10:
                print("Rating must be between 1 and 10.")
                return
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 10.")
            return

        remark = input("Enter your remark (optional): ").strip()
        self.update_feedback(item, rating, remark)

    def update_feedback(self, item, rating, remark):
        current_rating = self.menu[item]["rating"]
        rating_count = self.menu[item]["rating_count"]
        new_rating = (current_rating * rating_count + rating) / (rating_count + 1)
        self.menu[item]["rating"] = new_rating
        self.menu[item]["rating_count"] += 1

        if remark:
            self.menu[item]["comments"].append(remark)

        self.cursor.execute('''
            UPDATE menu SET rating = ?, rating_count = ?, comments = ?
            WHERE item = ?
        ''', (new_rating, rating_count + 1, ','.join(self.menu[item]["comments"]), item))
        self.connection.commit()

        print(f"\nFeedback updated for {item}. New rating: {new_rating:.1f}")
        if remark:
            print(f"Remark added: {remark}")

    def update_menu(self):
        self.view_menu()
        print("\n--- Update Menu ---")
        item = input("Enter the name of the menu item to update (or 'add' to create a new item): ").strip()
        if item == "add":
            new_item = input("Enter the name of the new menu item: ").strip()
            if new_item in self.menu:
                print("Item already exists in the menu.")
                return
            try:
                price = float(input(f"Enter the price for {new_item}: ").strip())
                self.menu[new_item] = {"price": price, "rating": 0, "rating_count": 0, "comments": []}
                self.cursor.execute('''
                    INSERT INTO menu (item, price, rating, rating_count, comments) VALUES (?, ?, 0, 0, '')
                ''', (new_item, price))
                self.connection.commit()
                print(f"{new_item} has been added to the menu with a price of ${price:.2f}.")
            except ValueError:
                print("Invalid price entered. Please try again.")
        elif item in self.menu:
            try:
                new_price = float(input(f"Enter the new price for {item}: ").strip())
                self.menu[item]["price"] = new_price
                self.cursor.execute('''
                    UPDATE menu SET price = ? WHERE item = ?
                ''', (new_price, item))
                self.connection.commit()
                print(f"The price for {item} has been updated to ${new_price:.2f}.")
            except ValueError:
                print("Invalid price entered. Please try again.")
        else:
            print("Item not found in the menu.")

    def check_total_orders(self):
        print("\n--- Total Orders Today ---")
        self.cursor.execute('SELECT COUNT(*) FROM orders')
        total_orders = self.cursor.fetchone()[0]
        if total_orders == 0:
            print("No orders placed today.")
        else:
            print(f"Total orders placed today: {total_orders}")

    def view_feedback(self):
        print("\n--- Feedback on Each Menu Item ---")
        if not self.menu:
            print("No menu items available.")
            return
        for item, details in self.menu.items():
            rating = details.get("rating", "N/A")
            comments = details.get("comments", [])
            print(f"\n{item}:")
            print(f"  - Rating: {rating:.1f}")
            if comments:
                print(f"  - Comments: {', '.join(comments)}")
            else:
                print("  - Comments: No comments yet.")

    def view_pending_orders(self):
        print("\n--- Pending Online Orders ---")
        self.cursor.execute('SELECT * FROM orders')
        rows = self.cursor.fetchall()
        if not rows:
            print("No pending orders.")
            return
        for index, order in enumerate(rows, start=1):
            items, total, address = order[1], order[2], order[3]
            print(f"\nOrder {index}:")
            print(f"  - Items: {items}")
            print(f"  - Total: ${total:.2f}")
            print(f"  - Address: {address}")

    def insert_order(self, order):
        items = ', '.join(f"{item} x {quantity}" for item, quantity in order["items"].items())
        self.cursor.execute('''
            INSERT INTO orders (items, total, address) VALUES (?, ?, ?)
        ''', (items, order["total"], order["address"]))
        self.connection.commit()

    def close_connection(self):
        self.connection.close()

if __name__ == "__main__":
    system = RestaurantManagementSystem()
    try:
        system.start()
    finally:
        system.close_connection()
