import sqlite3
import pandas as pd
from pycep_correios import get_address_from_cep, WebService

def cep_loader(csv_file='../data/ceps_sem_localidades.csv', db_path='../data/cepsdb.db'):
    '''
    function that verifies if a database already exists,
    if a table already exists on this db and, finally,
    populate the database with ceps and localities.
    csv_file: path to a csv file with index and cep columns
    db_file: path to a database file. If not exists, will be created
    '''
    # if error, rollback automatically, else commit!
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT SQLITE_VERSION()')
        data = cursor.fetchone()
        print('SQLite version:', data)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Pareamento (cep TEXT, localidade TEXT)''')
    df = pd.read_csv(csv_file, sep=',')
    count_news = 0
    count_exists = 0
    for index, row in df.iterrows():
        cep = row['CEP']
        cur.execute("SELECT cep FROM Pareamento WHERE cep= ?", (cep,))

        try:
            data = cur.fetchone()[0]
            #print("Found in database ", cep)
            # continue jumps to next iteration if cep is found in db
            count_exists += 1
            continue
        except:
            pass
        # if len(cep) != 8, its not a valid cep
        if not len(str(cep)) == 8:
            continue

        try:
            address = get_address_from_cep(cep, webservice=WebService.CORREIOS)
            localidade = address['bairro']
            count_news += 1
        except:
            localidade = 'Cep nao encontrado'

        cur.execute('''INSERT INTO Pareamento (cep, localidade) 
                VALUES ( ?, ? )''', (cep, localidade))

        conn.commit()
    print(f'CEPs existentes no banco: {count_exists}\nCEPs adcionados: {count_news}')