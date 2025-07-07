# grocery_app.py
import csv
import os
import uuid
from datetime import datetime
from colorama import Fore, Style, init
from tabulate import tabulate
from tqdm import tqdm
import time
from tabulate import tabulate

init(autoreset=True)

class GroceryApp:
    def __init__(self, is_admin=False):
        self.products = self.load_products()
        self.cart = {}
        self.saved = {}
        self.user_name = ""
        self.transaction_id = ""
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if is_admin:
            self.admin_menu()

    # ------------------------ Product Handling ------------------------
    def load_products(self, filepath='items.csv'):
        products = {}
        try:
            with open(filepath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    products[int(row['ItemID'])] = {
                        'name': row['ItemName'],
                        'price': float(row['Price'])
                    }
        except FileNotFoundError:
            print(Fore.RED + "❌ items.csv not found!")
        return products

    def save_products(self, filepath='items.csv'):
        with open(filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ItemID', 'ItemName', 'Price'])
            for item_id, data in self.products.items():
                writer.writerow([item_id, data['name'], data['price']])

    def admin_menu(self):
        while True:
            print("\n🔧 Admin Panel")
            print("1. View Products")
            print("2. Add Product")
            print("3. Update Product Price")
            print("4. Delete Product")
            print("5. View CSV Reports")
            print("6. Exit Admin Panel")
            choice = input("Choose an option (1-6 or 'exit'): ").strip().lower()

            if choice in ['6', 'exit']:
                print("👋 Exiting Admin Panel...\n")
                break
            elif choice == '1':
                self.display_products()
            elif choice == '2':
                self.add_product()
            elif choice == '3':
                self.update_price()
            elif choice == '4':
                self.delete_product()
            elif choice == '5':
                self.view_csv_reports()
            else:
                print("❌ Invalid option.")

    def add_product(self):
        name = input("Enter new item name: ").strip()
        price = float(input("Enter price: ").strip())
        new_id = max(self.products.keys(), default=0) + 1
        self.products[new_id] = {'name': name, 'price': price}
        self.save_products()
        print(f"✅ Added {name} with ID {new_id} and price ₹{price}")

    def update_price(self):
        self.display_products()
        try:
            item_id = int(input("Enter ItemID to update: ").strip())
            if item_id in self.products:
                new_price = float(input("New price: ₹").strip())
                self.products[item_id]['price'] = new_price
                self.save_products()
                print(f"✅ Updated {self.products[item_id]['name']} to ₹{new_price}")
            else:
                print("❌ ItemID not found.")
        except:
            print("⚠️ Invalid input.")

    def delete_product(self):
        self.display_products()
        try:
            item_id = int(input("Enter ItemID to delete (or '0' to cancel): ").strip())
            if item_id == 0:
                return
            if item_id in self.products:
                confirm = input(f"Are you sure you want to delete {self.products[item_id]['name']}? (y/n): ").strip().lower()
                if confirm == 'y':
                    del self.products[item_id]
                    self.save_products()
                    print("🗑️ Product deleted.")
            else:
                print("❌ ItemID not found.")
        except:
            print("⚠️ Invalid input.")

    def view_csv_reports(self):
        print(Fore.CYAN + "\n📂 View CSV Data")
        print("1. 📄 Transactions")
        print("2. 🗣️ Feedback")
        print("3. 💾 Saved for Later")

        choice = input("👉 Which file to view? (1/2/3): ").strip()

        file_map = {
            '1': ('transactions.csv', ['TransactionID', 'Name', 'Items', 'Total', 'Timestamp']),
            '2': ('feedback.csv', ['TransactionID', 'Feedback']),
            '3': ('save_for_later.csv', ['Name', 'ItemID', 'Qty'])
        }

        if choice in file_map:
            filename, headers = file_map[choice]
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f)
                    rows = [row for row in reader]

                if rows:
                    print(Fore.YELLOW + f"\n📄 Contents of {filename}:")
                    print(tabulate(rows, headers="keys", tablefmt="fancy_grid", stralign="center", numalign="center"))
                else:
                    print(Fore.YELLOW + "⚠️ File is empty.")
            else:
                print(Fore.RED + "⚠️ File does not exist yet.")
        else:
            print(Fore.RED + "❌ Invalid choice.")

    def display_products(self):
        print("\n📦 Products List:")
        print(f"{'ItemID':<8} {'Item':<12} {'Price'}")
        print("-" * 30)
        for i, p in self.products.items():
            print(f"{i:<8} {p['name']:<12} ₹{p['price']}")

    # ------------------------ Customer Flow ------------------------

    def start_session(self):
        self.user_name = input("👤 Enter your name: ").strip().lower()
        self.transaction_id = f"TRX{str(uuid.uuid4())[:6].upper()}"
        self.retrieve_saved()
        print(f"\n🧾 Welcome, {self.user_name.title()}! Transaction ID: {self.transaction_id}")
        self.display_products()

        if self.saved:
            print(Fore.BLUE + "\n💾 Items Saved for Later:")
            self.print_saved_summary()
        else:
            print(Fore.YELLOW + "\n💾 No items saved for later.")

        self.collect_items()
        self.review_and_edit()

    def retrieve_saved(self, filepath='save_for_later.csv'):
        if not os.path.isfile(filepath):
            return
        with open(filepath, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Name'] == self.user_name:
                    self.saved[int(row['ItemID'])] = int(row['Qty'])

    def overwrite_saved_file(self, filepath='save_for_later.csv'):
        all_data = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Name'] != self.user_name:
                        all_data.append(row)
        for item_id, qty in self.saved.items():
            all_data.append({'Name': self.user_name, 'ItemID': item_id, 'Qty': qty})
        with open(filepath, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['Name', 'ItemID', 'Qty'])
            writer.writeheader()
            for row in all_data:
                writer.writerow(row)

    def collect_items(self):
        print("\n🛒 Add items:")
        print("▶ item_id,qty         → cart")
        print("▶ item_id,qty,save    → save for later")
        print("▶ done                → finish")
        print("▶ exit                → exit now\n")

        while True:
            entry = input("> ").strip().lower()
            if entry == 'done':
                break
            if entry == 'exit':
                print("👋 Exiting current transaction.")
                exit()
            parts = [p.strip() for p in entry.split(',')]
            if len(parts) < 2:
                print("⚠️ Invalid input.")
                continue
            try:
                item_id = int(parts[0])
                qty = int(parts[1])
                if item_id not in self.products:
                    print("❌ ItemID not found.")
                    continue
            except:
                print("❌ Use numbers.")
                continue

            if len(parts) == 2:
                self.cart[item_id] = qty
                print(Fore.GREEN + f"🛒 Added {qty} x {self.products[item_id]['name']} to cart.")
            elif parts[2] == 'save':
                self.saved[item_id] = qty
                print(Fore.BLUE + f"💾 Saved {qty} x {self.products[item_id]['name']} for later.")
            else:
                print("⚠️ Invalid format.")

    def review_and_edit(self):
        while True:
            total = self.print_summary()
            choice = input("\n🔄 Type 'edit' or 'proceed': ").strip().lower()
            if choice == 'proceed':
                self.overwrite_saved_file()
                self.save_transaction(total)
                self.generate_invoice(total)
                self.simulate_payment()
                self.get_feedback()
                break
            elif choice == 'edit':
                self.edit_items()
            elif choice == 'exit':
                print("👋 Exiting current transaction.")
                exit()
            else:
                print("❌ Choose 'edit' or 'proceed'.")

    def print_summary(self):
        print("\n🧾 Transaction Summary:")

        if self.cart:
            print(Fore.GREEN + "\n🛒 Cart Items:")
            cart_data = []
            total = 0
            for item_id, qty in self.cart.items():
                name = self.products[item_id]['name']
                price = self.products[item_id]['price']
                item_total = qty * price
                cart_data.append([item_id, name, qty, f"₹{price}", f"₹{item_total}"])
                total += item_total
            print(tabulate(cart_data, headers=["ItemID", "Item", "Qty", "Unit Price", "Total"], tablefmt="fancy_grid"))
        else:
            print(Fore.YELLOW + "🛒 Cart is empty.")

        if self.saved:
            print(Fore.BLUE + "\n💾 Saved for Later:")
            self.print_saved_summary()
        return total

    def print_saved_summary(self):
        data = []
        for i, q in self.saved.items():
            data.append([i, self.products[i]['name'], q])
        print(tabulate(data, headers=["ItemID", "Item", "Qty"], tablefmt="fancy_grid"))

    def edit_items(self):
        print("\n🔧 Edit:")
        print("▶ item_id,qty        → update cart")
        print("▶ item_id,qty,save   → cart → saved")
        print("▶ item_id,qty,cart   → saved → cart")
        print("▶ edit_done          → finish")
        print("▶ exit               → exit now\n")

        while True:
            entry = input("> ").strip().lower()
            if entry == 'edit_done':
                break
            if entry == 'exit':
                print("👋 Exiting current transaction.")
                exit()

            parts = [p.strip() for p in entry.split(',')]
            if len(parts) < 2:
                print(Fore.RED + "⚠️ Invalid input. Please enter at least item_id and qty.")
                continue

            try:
                item_id = int(parts[0])
                qty = int(parts[1])
                if qty <= 0:
                    print(Fore.RED + "❌ Quantity must be greater than 0.")
                    continue
            except:
                print(Fore.RED + "❌ Invalid format. ItemID and Qty must be numbers.")
                continue

            if len(parts) == 2:
                if item_id in self.products:
                    self.cart[item_id] = qty
                    print(Fore.GREEN + f"🛒 Cart updated: {self.products[item_id]['name']} → Qty: {qty}")
                else:
                    print(Fore.RED + "❌ ItemID not found.")

            elif parts[2] == 'save':
                if item_id in self.cart:
                    if qty >= self.cart[item_id]:
                        self.saved[item_id] = self.saved.get(item_id, 0) + self.cart[item_id]
                        print(Fore.BLUE + f"💾 Moved all {self.products[item_id]['name']} from cart to saved.")
                        del self.cart[item_id]
                    else:
                        self.saved[item_id] = self.saved.get(item_id, 0) + qty
                        self.cart[item_id] -= qty
                        print(Fore.BLUE + f"💾 Moved {qty} of {self.products[item_id]['name']} from cart to saved.")
                else:
                    print(Fore.RED + "❌ Item not found in cart.")

            elif parts[2] == 'cart':
                if item_id in self.saved:
                    if qty >= self.saved[item_id]:
                        self.cart[item_id] = self.cart.get(item_id, 0) + self.saved[item_id]
                        print(Fore.GREEN + f"🛒 Moved all {self.products[item_id]['name']} from saved to cart.")
                        del self.saved[item_id]
                    else:
                        self.cart[item_id] = self.cart.get(item_id, 0) + qty
                        self.saved[item_id] -= qty
                        print(Fore.GREEN + f"🛒 Moved {qty} of {self.products[item_id]['name']} from saved to cart.")
                else:
                    print(Fore.RED + "❌ Item not found in saved list.")

            else:
                print(Fore.RED + "⚠️ Invalid third value. Use 'save' or 'cart' only.")

        print(Fore.MAGENTA + "\n📋 Summary after Editing:")
        self.print_summary()

    def save_transaction(self, total, filepath='transactions.csv'):
        file_exists = os.path.isfile(filepath)
        with open(filepath, 'a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["TransactionID", "Name", "Items", "Total", "Timestamp"])
            items_str = ','.join([f"{i}:{q}" for i, q in self.cart.items()])
            writer.writerow([self.transaction_id, self.user_name, items_str, total, self.timestamp])

    def generate_invoice(self, total):
        print(Fore.CYAN + "\n" + "=" * 50)
        print(Fore.CYAN + Style.BRIGHT + f"{'🧾 FINAL INVOICE':^50}")
        print(Fore.CYAN + "=" * 50)
        print(f"👤 Customer     : {Fore.YELLOW}{self.user_name.title()}")
        print(f"🆔 Transaction  : {self.transaction_id}")
        print(f"📅 Date & Time  : {self.timestamp}")
        print(Fore.CYAN + "-" * 50)

        invoice_data = []
        for i, q in self.cart.items():
            name = self.products[i]['name']
            price = self.products[i]['price']
            line_total = q * price
            invoice_data.append([name, q, f"₹{price}", f"₹{line_total}"])

        print(tabulate(invoice_data, headers=["Item", "Qty", "Unit Price", "Total"], tablefmt="rounded_grid"))
        print(Fore.GREEN + f"{'TOTAL':>43}: ₹{total}")
        print(Fore.CYAN + "=" * 50)

    def simulate_payment(self):
        print("\n💳 Processing payment...")
        for _ in tqdm(range(30), desc="💳 Verifying Card", bar_format="{l_bar}{bar} | {percentage:3.0f}%"):
            time.sleep(0.05)
        print(Fore.GREEN + Style.BRIGHT + "\n✅ Payment Successful! Thank you for your purchase.")

    def get_feedback(self, filepath='feedback.csv'):
        ans = input("\n🗣️  Leave feedback? (y/n): ").strip().lower()
        if ans == 'y':
            msg = input("✍️  Your feedback: ")
            file_exists = os.path.isfile(filepath)
            with open(filepath, 'a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["TransactionID", "Feedback"])
                writer.writerow([self.transaction_id, msg])
            print("🙏 Thanks for your feedback!")
