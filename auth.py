import bcrypt
import os

USER_DATA_FILE = "users.txt"

# Step 4: Password Hashing
def hash_password(plain_text_password):
    password_bytes = plain_text_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# Step 5: Password Verification
def verify_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Step 7: Register User
def register_user(username, password):
    if user_existence(username):
        return False
    hashed = hash_password(password)
    with open(USER_DATA_FILE, "a") as file:
        file.write(f"{username},{hashed}\n")
    return True

# Step 8: Check User Existence
def user_existence(username):
    try:
        with open(USER_DATA_FILE, "r") as file:
            for line in file:
                if line.startswith(username + ","):
                    return True
    except FileNotFoundError:
        print("File not found")
    return False

# Step 9: Login User
def login_user(username, password):
    try:
        with open(USER_DATA_FILE, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if parts[0] == username:
                    return verify_password(password, parts[1])
    except FileNotFoundError:
        print("File doesn't exist")
    return False

# Step 10: Input Validation
def validate_username(username):
    if len(username) < 3:
        print("Username is too short")
        return False, "Too short"
    if not username.isalnum():
        print("Only letters and numbers allowed")
        return False, "Invalid characters"
    return True, "Valid username"

def validate_password(password):
    if len(password) < 8:
        print("Password is too short")
        return False, "Too short"
    if not any(char.isupper() for char in password):
        print("Add uppercase letters")
        return False, "Missing uppercase"
    if not any(char.islower() for char in password):
        print("Add lowercase letters")
        return False, "Missing lowercase"
    if not any(char.isdigit() for char in password):
        print("Add a number")
        return False, "Missing number"
    return True, "Valid password"

# Step 11: Main Menu
def display_menu():
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    print("\nWelcome to the Week 7 Authentication System!")
    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()
            is_valid, msg = validate_username(username)
            if not is_valid:
                print(f"Error: {msg}")
                continue

            password = input("Enter a password: ").strip()
            is_valid, msg = validate_password(password)
            if not is_valid:
                print(f"Error: {msg}")
                continue

            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            if register_user(username, password):
                print("User registered successfully.")
            else:
                print("Username already exists.")

        elif choice == '2':
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()
            if login_user(username, password):
                print("\nYou are now logged in.")
                print("In a real application, you would now access the dashboard or secure features.")
            else:
                print("Login failed. Please check your credentials.")
            input("\nPress Enter to return to main menu...")

        elif choice == '3':
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()