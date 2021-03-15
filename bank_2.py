import random, sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute(
    "CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);")


def add_to_db(acc_num, acc_pin):
    cur.execute(f"INSERT INTO card ('number', 'pin', 'balance') VALUES ('{acc_num}', '{acc_pin}', 0);")
    conn.commit()


used_acc_numbers = set()


def create_account():
    while True:
        account = gen_checksum(gen_card())
        if account not in used_acc_numbers:
            used_acc_numbers.add(account)

            break

    pin = gen_pin()
    print("Your card has been created")
    print(f"Your card number: \n{account}")
    print(f"Your card PIN: \n{pin}\n")
    add_to_db(account, pin)

def card_validator(number):
    card_no = number[:-1]
    card_no = [int(i) for i in card_no]  # string becomes a list of ints
    card_no = [card_no[i] * 2 if i % 2 == 0 else card_no[i] for i in range(0, 15)]  # every other number *2
    card_no = [i - 9 if i > 9 else i for i in card_no]  # numbers over 9, -9
    card_no.append(int(number[-1]))
    total = 0
    for item in card_no:
        total += item
    if total % 10 == 0:
        return True
    else:
        return False


def gen_checksum(card_no) -> str:
    original_number = card_no
    card_no = [int(i) for i in card_no]  # string becomes a list of ints
    card_no = [card_no[i] * 2 if i % 2 == 0 else card_no[i] for i in range(0, 15)]  # every other number *2
    card_no = [i - 9 if i > 9 else i for i in card_no]  # numbers over 9, -9
    total = 0
    for item in card_no:
        total += item
    if total % 10 == 0:
        check_sum = 0
    else:
        check_sum = 10 - int(str(total)[1])

    return original_number + str(check_sum)  # return the number needed to make a multiple of 10


def gen_card() -> str:
    inn = "400000"
    account_card = random.randint(000000000, 999999999)
    account_card = f"{account_card:09d}"
    return inn + account_card


def gen_pin() -> str:
    pin = random.randint(0, 9999)
    return f"{pin:04d}"


def log_in():
    print("\nEnter your card number:")
    account_in = input()
    print("\nEnter your PIN:")
    pass_in = input()

    cur.execute(f"SELECT * FROM card WHERE number = {account_in} AND pin = {pass_in};")
    current = cur.fetchone()

    if current != None:
        print("\nYou have successfully logged in!\n")
        logged_in(current)
    else:
        print("\nWrong card number or PIN!\n")


def logged_in(current):
    
    while True:
        options = {"1" : ["Balance", print_balance], "2": ["Add income", add_income], "3": ["Do transfer", do_transfer], "4": ["Close account"], "5": ["Log out"], "0" : ["Exit", exit_app]}
        for item in options:
            print(f"{item}.", options[item][0])

        user_input = input()

        if user_input not in options:
            print("\nBad input\n")
            continue
        if user_input == "5":
            break
        if user_input == "4":
            close_acc(current)
            break  
        options[user_input][1](current)    

def close_acc(db_row):
    print(db_row)
    cur.execute(f"DELETE FROM card WHERE number = {db_row[1]};")
    conn.commit()
    print("\nThe account has been closed!\n")
    

def do_transfer(db_row):
    print("Transfer\nEnter the card number:")
    transfer_card_no = input()
    while True:
        if card_validator(transfer_card_no) == False:
            print("\nProbably you made a mistake in the card number. Please try again!\n")
            break
        cur.execute(f"SELECT * FROM card WHERE number = {transfer_card_no};")
        transfer_to_row = cur.fetchone()
        if transfer_to_row == None:
            print("\nSuch a card does not exist.\n")
            break
        else:
            print("\nEnter how much money you want to transfer:\n")
            user_input = int(input())
            if enough_for_transfer(db_row, user_input) == False:
                print("\nNot enough money!\n")
                break
            else:
                update_transfer(db_row, transfer_to_row, user_input)
                print("\nSuccess!\n")
                break

def update_transfer(minus_row, plus_row, amount):
    cur.execute(f"SELECT * FROM card WHERE number = {minus_row[1]};")
    current = cur.fetchone()
    increase_total = amount+plus_row[3]
    decrease_total = current[3] - amount
    cur.execute(f"UPDATE card SET balance = {increase_total} WHERE id = {plus_row[0]};")
    conn.commit()
    cur.execute(f"UPDATE card SET balance = {decrease_total} WHERE id = {minus_row[0]};")
    conn.commit()


def enough_for_transfer(db_row, amount):
    cur.execute(f"SELECT * FROM card WHERE number = {db_row[1]};")
    current = cur.fetchone()
    return False if current[3]-amount < 0 else True

def add_income(db_row):
    cur.execute(f"SELECT balance FROM card WHERE id = {db_row[0]};")
    current = cur.fetchone()
    print("\nEnter income:\n")
    user_input = int(input()) + current[0] 
    cur.execute(f"UPDATE card SET balance = {user_input} WHERE id = {db_row[0]};")
    conn.commit()
    print("\nIncome was added!\n")

def print_balance(db_row):
    cur.execute(f"SELECT balance FROM card WHERE id = {db_row[0]};")
    current = cur.fetchone()
    print(f"\nBalance: {current[0]}\n")

def exit_app(current = None):
    print("\nBye!")
    exit()


def main_menu():

    while True:
        options = {'1': ["Create an account", create_account], '2': ["Log into account", log_in], '0': ["Exit", exit_app]}

        for item in options:
            print(f"{item}.", options[item][0])

        user_input = input()

        if user_input not in options:
            print("Bad input\n")
            continue

        options[user_input][1]()

main_menu()
