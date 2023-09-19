import random
from typing import List
import sqlite3


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
# cur.execute('''
# CREATE TABLE card(
#     id INTEGER,
#     number TEXT,
#     pin TEXT,
#     balance INTEGER DEFAULT 0
# )
# ''')
# cur.execute('''
# INSERT INTO card (id, number, pin)
# VALUES (0, '323123132', '231323')
# ''')
# cur.execute('''
# SELECT * FROM card
# ''')
# cur.execute('''
# DELETE FROM card
# ''')
# conn.commit()


def print_in_db():
    cur.execute('''
    SELECT * FROM card
    ''')
    print(cur.fetchall())


def print_options():
    options: List[str] = [
        '1. Create an account',
        '2. Log into account',
        '0. Exit'
    ]
    print('\n'.join(options))


def checksum(num: str):
    sum: int = 0
    for i in range(15):
        if i % 2 == 0:
            sum += int(num[i]) * 2 if int(num[i]) * 2 < 10 else int(num[i]) * 2 - 9
        else:
            sum += int(num[i])
    return str((10 - sum % 10) % 10)


def create_card_number():
    card_number: str = '400000' + ''.join([random.choice('0123456789') for _ in range(9)])
    card_number = card_number + checksum(card_number)
    return card_number


number_of_cards: int = 0


def create():
    card_number: str
    pin_number: str
    while True:
        card_number = create_card_number()
        pin_number = ''.join([random.choice('0123456789') for _ in range(4)])
        cur.execute(f'''
        SELECT * FROM card 
        WHERE number = \'{card_number}\'
        ''')
        if cur.fetchone() is not None:
            continue
        break
    print('Your card has been created',
          'Your card number:',
          card_number,
          'Your card PIN:',
          pin_number,
          sep='\n')
    global number_of_cards
    number_of_cards += 1
    cur.execute(f'''
    INSERT INTO card (id, number, pin)
    VALUES ({number_of_cards}, \'{card_number}\', \'{pin_number}\')
    ''')
    conn.commit()
    # print_in_db()


def log_into_account():
    card_number = input('Enter your card number:')
    pin_number = input('Enter your pin number:')
    cur.execute(f'''
    SELECT * FROM card
    WHERE number = \'{card_number}\'
    ''')
    record = cur.fetchone()
    if record is not None and record[2] == pin_number:
        print('You have successfully logged in!')
        return True, card_number, pin_number
    else:
        print('Wrong card number or PIN!')
        return False, None, None


def print_options_logged():
    options: List[str] = [
        '1. Balance',
        '2. Add income',
        '3. Do transfer',
        '4. Close account',
        '5. Log out',
        '0. Exit'
    ]
    print('\n'.join(options))


def is_valid_card(card_number: str):
    sum: int = 0
    for i in range(len(card_number) - 1):
        sum += int(card_number[i]) if i % 2 == 1 else\
            (int(card_number[i]) * 2 if int(card_number[i]) * 2 < 10 else int(card_number[i]) * 2 - 9)
    sum += int(card_number[-1])
    return sum % 10 == 0


# test: str = str(4000003972196502)
# sum: int = 0
# for i in range(len(test) - 1):
#     sum += int(test[i]) if i % 2 == 1 else (int(test[i]) * 2 if int(test[i]) * 2 < 10 else int(test[i]) * 2 - 9)
#     print(i,
#           test[i],
#           int(test[i]) if i % 2 == 1 else (int(test[i]) * 2 if int(test[i]) * 2 < 10 else int(test[i]) * 2 - 9),
#           sum,)
# print(sum)
# print(checksum('400000397219650'))
# print(is_valid_card(str(4000003972196502)))
# raise BaseException

def get_balance(card_number: str):
    cur.execute(f'''
    SELECT * FROM card
    WHERE number = \'{card_number}\'
    ''')
    card = cur.fetchone()
    return card[3]


def update_balance(card_number: str, delta: int, not_commit: bool = False):
    cur.execute(f'''
    UPDATE card
    SET balance = {get_balance(card_number=card_number) + delta}
    WHERE number = \'{card_number}\'
    ''')
    if not not_commit:
        conn.commit()


def add_income(card_number: str):
    income: int = int(input('Enter income:'))
    cur.execute(f'''
    UPDATE card
    SET balance = {get_balance(card_number=card_number) + income}
    WHERE number = \'{card_number}\'
    ''')
    conn.commit()
    print('Income was added!')


def do_transfer(card_number: str):
    receiver_card = str(input('Transfer\nEnter card number:'))
    if receiver_card == card_number:
        print('You can\'t transfer money to the same account!')
        return
    if not is_valid_card(card_number=receiver_card):
        print('Probably you made a mistake in the card number. Please try again!')
        return
    cur.execute(f'''
    SELECT * FROM card
    WHERE number = \'{receiver_card}\'
    ''')
    record = cur.fetchone()
    if record is None:
        print('Such a card does not exist.')
        return
    money: int = int(input('Enter how much money you want to transfer:'))
    if money > get_balance(card_number):
        print('Not enough money!')
        return
    update_balance(card_number, -money, not_commit=True)
    update_balance(receiver_card, money)
    print('Success!')


def delete_account(card_number: str):
    cur.execute(f'''
    DELETE FROM card
    WHERE number = \'{card_number}\'
    ''')
    conn.commit()
    print('The account has been closed!')


while True:
    print_options()
    option_number = int(input())
    flag: bool = False
    if option_number == 1:
        create()
    elif option_number == 2:
        success: bool
        card_number: str
        pin_number: str
        success, card_number, pin_number = log_into_account()
        if success:
            while True:
                print_options_logged()
                option_number = int(input())
                if option_number == 1:
                    print(f'Balance: {get_balance(card_number=card_number)}')
                elif option_number == 2:
                    add_income(card_number=card_number)
                elif option_number == 3:
                    do_transfer(card_number=card_number)
                elif option_number == 4:
                    delete_account(card_number=card_number)
                    break
                elif option_number == 5:
                    print('You have successfully logged out!')
                    break
                else:
                    flag = True
                    break

    elif option_number == 0:
        print('Bye!')
        break
    else:
        raise BaseException
    if flag:
        break
