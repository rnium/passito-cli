import sqlite3
import json
import time
import pathlib


def create_passito(conn:sqlite3.Connection):
    cur = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS passito (
        pk INTEGER PRIMARY KEY AUTOINCREMENT,
        id_name TEXT,
        username TEXT,
        password TEXT
    )
    """
    cur.execute(sql)
    conn.commit()


def add_account(conn:sqlite3.Connection, id_name, usernaname, password):
    cur = conn.cursor()

    sql = f"""
    INSERT INTO passito (id_name, username, password)
    VALUES ("{id_name}", "{usernaname}", "{password}")
    """

    cur.execute(sql)
    conn.commit()


def update_credential_by_name(conn:sqlite3.Connection, id_name, usernaname, password):
    cur = conn.cursor()
    sql = f"""
    UPDATE passito
    SET username = "{usernaname}",
        password = "{password}"
    WHERE id_name = "{id_name}"
    """
    cur.execute(sql)
    conn.commit()


def delete_by_name(conn:sqlite3.Connection, id_name):
    cur = conn.cursor()
    sql = f"""
    DELETE FROM passito
    WHERE id_name = "{id_name}"
    """
    cur.execute(sql)
    conn.commit()


def get_id_name_list(conn:sqlite3.Connection):
    cur = conn.cursor()
    sql = f"""
    SELECT id_name FROM passito
    """
    queryset = cur.execute(sql).fetchall()
    id_names = [i[0] for i in queryset]
    id_names.sort()
    return id_names


def get_credential(conn:sqlite3.Connection, id_name):
    cur = conn.cursor()
    sql = f"""
    SELECT username, password FROM passito
    WHERE id_name="{id_name}"
    """
    queryset = cur.execute(sql).fetchone()
    credential = {'username': queryset[0], 'password': queryset[1]}
    return credential


def rename_id(conn:sqlite3.Connection, old_name, new_name):
    # getting pk of the id
    cur = conn.cursor()
    pk_queryset = cur.execute(f"""SELECT pk FROM passito WHERE id_name="{old_name}" """).fetchone()
    pk = pk_queryset[0]
    # rename the id
    cur.execute(f"""
    UPDATE passito
    SET id_name = "{new_name}"
    WHERE pk = {pk}
    """)
    conn.commit()


def backup_passito(conn:sqlite3.Connection, path:pathlib.Path):
    cur = conn.cursor()
    queryset = cur.execute("SELECT * FROM passito").fetchall()
    accounts = list()
    for query in queryset:
        account = {
            'pk': query[0],
            'id_name': query[1],
            'username': query[2],
            'password': query[3]
        }
        accounts.append(account)
    backup_filename = 'passito_backup '+time.strftime('%m-%d-%Y %H.%M')
    file = str(path/f"{backup_filename}.json")
    with open(file, 'w') as f:
        json.dump(accounts, f, indent=4)
    

def restore_passito(conn:sqlite3.Connection, filepath:pathlib.Path):
    if not filepath.exists():
        raise ValueError('file does not exists!')
    create_passito(conn)
    with open(filepath, 'r') as f:
        accounts = json.loads(f.read())
    cur = conn.cursor()
    # Deleting all existing credentials
    cur.execute("DELETE FROM passito")

    # Restoring each account credential
    for account in accounts:
        sql = f"""
        INSERT INTO passito (pk, id_name, username, password)
        VALUES ({account['pk']},"{account['id_name']}", "{account['username']}", "{account['password']}")
        """
        cur.execute(sql)
    conn.commit()

    