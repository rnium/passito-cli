from typing import List
import random
from . import settings, db
from .security import encrypt, decrypt
from .db import add_account
import json
import sys
import typer


setup_dir = settings.setup_dir


def pass_generator(length=12):
    special_characters = ('@', '#', '$', '%', '&', '*', '?', '!')
    lowercases = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                  'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                  'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                  'z'
                  )
    uppercases = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                  'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                  'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                  'Z'
                  )
    numbers = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
    all_chars = (special_characters + lowercases + uppercases + numbers)

    rand_special = random.choice(special_characters)
    rand_lower = random.choice(lowercases)
    rand_upper = random.choice(uppercases)
    rand_number = random.choice(numbers)

    temp_pass = rand_special + rand_upper + rand_lower + rand_number

    for i in range(length-4):
        anything = random.choice(all_chars)
        temp_pass = temp_pass + anything

    result_password = ''.join(random.sample(temp_pass, len(temp_pass)))
    return result_password


def initialize_config():
    if not setup_dir.exists():
        try:
            setup_dir.mkdir(parents=True, exist_ok=True)
            security_key = pass_generator(35)
            sysdata = {
                'gall_interval': 5,
                'gp_length': 12, 
                'security_key': security_key,
                'getall_posx': 0,
                'getall_posy': 0,
                'backup_dir': str(settings.backup_dir),
            }
            sysfile = setup_dir / 'config.json'
            with sysfile.open('w') as f:
                json.dump(sysdata, f, indent=4)
        
        except Exception as exc:
            print(f'An unexpected error occurred. Error info: {exc}')
            sys.exit("Exiting due to setup error.")
            
            
def raise_for_typer_error(msg: str):
    error_message = typer.style(
        msg,
        fg=typer.colors.RED
    )
    typer.echo(error_message)
    raise typer.Exit(1)


def show_success(msg: str):
    error_message = typer.style(
        msg,
        fg=typer.colors.GREEN
    )
    typer.echo(error_message)


def add_account(conn, all_id: List[str], id_name, email, password, r_password):
    if len(id_name) == 0 or len(email) == 0 or len(password) == 0 or len(r_password) == 0:
        raise_for_typer_error('Some empty argument')
    if id_name.isdigit():
        raise_for_typer_error('invalid name, ID name cannot be an integer!')
    if id_name in all_id:
        raise_for_typer_error(f"{id_name} is already in the database.")
    if password != r_password:
        raise_for_typer_error('Passwords doesn\'t match')
    else:
        e_email = encrypt(email)
        e_password = encrypt(password)
        add_account(conn, id_name=id_name, usernaname=e_email, password=e_password)


def update_account(conn, all_id: List[str], id_name, email, password, r_password):
    if not all([bool(len(item)) for item in [id_name, password, r_password]]):
        raise_for_typer_error('(426) Some empty argument')
    elif id_name not in all_id:
        raise_for_typer_error('(404) Account not found')
    if password != r_password:
        raise_for_typer_error('Passwords doesn\'t match')
    if not email:
        credential = db.get_credential(conn, id_name)
        e_prev_mail = credential['username']
        e_password = encrypt(password)
        db.update_credential_by_name(conn, id_name, e_prev_mail, e_password)
    else:
        e_user = encrypt(email)
        e_pass = encrypt(password)
        db.update_credential_by_name(conn, id_name, e_user, e_pass)


def delete_account(conn, all_id: List[str], id_name):
    if id_name not in all_id:
        raise_for_typer_error('(404) Account not found')
    db.delete_by_name(conn, id_name)


