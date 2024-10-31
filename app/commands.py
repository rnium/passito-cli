import time
import typer
import sqlite3
from . import settings, db, utils
import pyperclip
from .security import encrypt, decrypt, get_sysdata
import cryptography


app = typer.Typer()
conn = sqlite3.connect(str(settings.DB_FILE))
all_accounts = db.get_id_name_list(conn)
utils.initialize_config()

def autocomplete_ac(incomplete: str):
    return [ac for ac in all_accounts if ac.startswith(incomplete)]


@app.command()
def ls():
    for i, ac in enumerate(all_accounts):
        print(f"[{i}] {ac}")


@app.command()
def get_pass(ac_name: str = typer.Argument(autocompletion=autocomplete_ac)):
    if ac_name not in all_accounts:
        utils.raise_for_typer_error('(404) Account not found')
    credential = db.get_credential(conn, ac_name)
    e_password = credential['password']
    try:
        password = decrypt(e_password)
    except cryptography.fernet.InvalidToken:
        print("Invalid token")
        return None
    pyperclip.copy(password)
    utils.show_success('Password copied to clipboard')


@app.command()
def get_all(ac_name: str = typer.Argument(autocompletion=autocomplete_ac)):
    if ac_name not in all_accounts:
        utils.raise_for_typer_error('(404) Account not found')
    credential = db.get_credential(conn, ac_name)
    interval = get_sysdata('gall_interval')
    e_username = credential['username']
    username = decrypt(e_username)
    pyperclip.copy(username)
    utils.show_success(f'Username/Email copied to clipboard, wait for {interval} sec')
    e_password = credential['password']
    try:
        password = decrypt(e_password)
    except cryptography.fernet.InvalidToken:
        print("Invalid token")
        return None
    time.sleep(interval)
    pyperclip.copy(password)
    utils.show_success('Password copied to clipboard')


@app.command()
def add_ac(ac_title, email, password, re_password):
    utils.add_account(conn, all_accounts, ac_title,
                      email, password, re_password)
    utils.show_success('Account added')


@app.command()
def update_ac(ac_title, password, re_password, email=None):
    utils.update_account(conn, all_accounts, ac_title,
                         email, password, re_password)
    utils.show_success('Account updated')


@app.command()
def delete_ac(ac_title):
    utils.delete_account(conn, all_accounts, ac_title)
    utils.show_success('Account updated')
