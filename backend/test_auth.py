
from getpass import getpass

from services.auth_service import register_user, login_user


if __name__ == "__main__":

    print("===== EduStream Authentication Test =====")

    name = input("Enter test user name: ")
    email = input("Enter test email: ").strip()
    password = getpass("Enter test password: ")

    print("\n1. Testing registration...")

    try:
        user = register_user(
            full_name=name,
            email=email,
            password=password,
            role="student"
        )

        print("Registration successful!")
        print("User ID:", user["user_id"])
        print("Name:", user["full_name"])
        print("Email:", user["email"])
        print("Role:", user["role"])

    except ValueError as error:
        print("Registration failed:", error)
        raise SystemExit

    print("\n2. Testing login...")

    login_result = login_user(email, password)

    if login_result:
        print("Login successful!")
        print("Welcome,", login_result["full_name"])
        print("Role:", login_result["role"])
    else:
        print("Login failed!")

    print("\n3. Testing incorrect password...")

    incorrect_login = login_user(email, "WrongPassword123")

    if incorrect_login is None:
        print("Incorrect password rejected successfully!")
    else:
        print("Security test failed!")
