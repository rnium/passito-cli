from pathlib import Path
import os


if os.name == 'nt':
    setup_dir = Path.home()/'AppData/Roaming/passito/appsys'
    data_dir = Path.home()/'AppData/Roaming/passito/database'
    backup_dir = Path.home() / 'Documents/passito_backup'
else:
    setup_dir = Path.home() / '.config/passito/appsys'
    data_dir = Path.home() / '.config/passito/database'
    backup_dir = Path.home() / 'passito/backup'
    

DB_FILE = data_dir/'passito.db'
