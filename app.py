from grocery_app import GroceryApp
from pyfiglet import figlet_format
from colorama import Fore, Style


if __name__ == "__main__":
    print(Fore.CYAN + Style.BRIGHT + "\n======== Grocery Store System ========\n")


    while True:
        print(Fore.YELLOW + "\n🔐 Welcome to Grocery System")
        print("Select Role:")
        print("1. 👨‍💼 Admin")
        print("2. 🛒 Customer")
        print("3. 🚪 Exit")

        choice = input("👉 Enter your choice (1/2/3): ").strip()
        if choice == '1':
            GroceryApp(is_admin=True)
        elif choice == '2':
            while True:
                app = GroceryApp()
                app.start_session()
                again = input("\n🌀 Start a new transaction? (y/n): ").strip().lower()
                if again != 'y':
                    print(Fore.GREEN + "👋 Thank you for shopping. Goodbye!")
                    break
        elif choice == '3':
            print(Fore.CYAN + "🚪 Exiting system. Goodbye!")
            break
        else:
            print(Fore.RED + "❌ Invalid input. Please choose 1, 2, or 3.")
