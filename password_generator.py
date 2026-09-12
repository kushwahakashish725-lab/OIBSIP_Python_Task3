import random
import string

MIN_LENGTH = 8


def get_length() -> int:
    while True:
        raw = input(f"Enter desired password length (minimum {MIN_LENGTH}): ").strip()
        if not raw.isdigit():
            print(f"  ⚠ Please enter a whole number.\n")
            continue
        length = int(raw)
        if length < MIN_LENGTH:
            print(f"  ⚠ Length must be at least {MIN_LENGTH}. Try again.\n")
            continue
        return length


def get_character_types() -> dict:
    print("\nWhich character types should the password include?")
    print("(Answer y/n for each — at least 2 types must be selected)\n")

    while True:
        choices = {
            "upper": input("  Include UPPERCASE letters? (y/n): ").strip().lower() == "y",
            "lower": input("  Include lowercase letters? (y/n): ").strip().lower() == "y",
            "digits": input("  Include numbers (0-9)? (y/n): ").strip().lower() == "y",
            "symbols": input("  Include symbols (!@#$...)? (y/n): ").strip().lower() == "y",
        }
        selected_count = sum(choices.values())
        if selected_count < 2:
            print("\n  ⚠ Please select at least 2 character types.\n")
            continue
        return choices


def build_character_pool(choices: dict) -> str:
    pool = ""
    if choices["upper"]:
        pool += string.ascii_uppercase
    if choices["lower"]:
        pool += string.ascii_lowercase
    if choices["digits"]:
        pool += string.digits
    if choices["symbols"]:
        pool += string.punctuation
    return pool


def generate_password(length: int, choices: dict) -> str:
    pool = build_character_pool(choices)

    guaranteed = []
    if choices["upper"]:
        guaranteed.append(random.choice(string.ascii_uppercase))
    if choices["lower"]:
        guaranteed.append(random.choice(string.ascii_lowercase))
    if choices["digits"]:
        guaranteed.append(random.choice(string.digits))
    if choices["symbols"]:
        guaranteed.append(random.choice(string.punctuation))

    remaining_length = length - len(guaranteed)
    rest = [random.choice(pool) for _ in range(remaining_length)]

    password_chars = guaranteed + rest
    random.shuffle(password_chars)
    return "".join(password_chars)


def main():
    print("=" * 45)
    print("        RANDOM PASSWORD GENERATOR")
    print("=" * 45)

    while True:
        length = get_length()
        choices = get_character_types()
        password = generate_password(length, choices)

        print("\n" + "-" * 45)
        print(f"  Generated password: {password}")
        print("-" * 45)

        again = input("\nGenerate another password? (y/n): ").strip().lower()
        print()
        if again != "y":
            print("Goodbye! Stay secure.")
            break


if __name__ == "__main__":
    main()
