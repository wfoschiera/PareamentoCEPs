import sqlite3
import pandas as pd
from pycep_correios import get_address_from_cep, WebService
import numpy as np


def cep_loader(csv_file='../data/ceps_sem_localidades.csv', db_path='../data/cepsdb.db'):
    '''
    function that verifies if a database already exists,
    if a table already exists on this db and, finally,
    populate the database with ceps and localities.
    csv_file: path to a csv file with index and cep columns
    db_file: path to a database file. If not exists, will be created
    '''
    # if error, rollback automatically, else commit!
    sqlite3.register_adapter(np.int64, lambda val: int(val))
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT SQLITE_VERSION()')
        data = cursor.fetchone()
        print('SQLite version:', data)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Pareamento(cep INTEGER, localidade TEXT)''')
    df = pd.read_csv(csv_file, sep=',')
    count_news = 0
    count_exists = 0
    for index, row in df.iterrows():
        cep = row['CEP']
        cur.execute("SELECT cep FROM Pareamento WHERE cep= ?", (cep,))

        try:
            data = cur.fetchone()[0]
            print("Found in database ", data)
            count_exists += 1
            # continue jumps to next iteration if cep is found in db
            continue
        except:
            pass
        # if len(cep) != 8, its not a valid cep
        if not len(str(cep)) == 8:
            continue

        try:
            address = get_address_from_cep(str(cep), webservice=WebService.CORREIOS)
            localidade = address['bairro']
            count_news += 1
        except:
            localidade = 'Cep nao encontrado'
        print(f'Inserindo registro, CEP: {cep}, Localidade: {localidade}')
        sql = ''' INSERT INTO Pareamento(cep, localidade) 
                VALUES(?,?) '''
        cur.execute(sql, (np.int64(cep), localidade))

        conn.commit()
        #Consulta para saber se os dados estão sendo salvos corretamente
        '''
        cur.execute("SELECT * FROM Pareamento WHERE cep= ?", (cep,))
        data = cur.fetchone()
        print(data)
        '''
    print(f'CEPs existentes no banco: {count_exists}\nCEPs adicionados: {count_news}')

def join_db_with_csv(db_file='../data/cepsdb.db', csv_file='../bdo_csv/bdo_report_16-02-2021-16-55-00.csv'):
    """

    :param db_file: path to database file
    :param csv_file: path to csv file (report exported from BDO)
    :return: None
    """

    # Create your connection.

    conn = sqlite3.connect(db_file)
    df_db = pd.read_sql_query("SELECT * FROM Pareamento", conn, index_col = ['cep'])

    df = pd.read_csv(csv_file,sep=';', parse_dates = ['Data_Alteraçao'])
    pd.set_option('display.float_format', '{:.0f}'.format)
    df.fillna(0)
    df['CEP'] = df['CEP'].astype(str) #cast to string to avoid typeError
    df['CEP'] = df['CEP'].apply(lambda x: x.replace(' ',''))
    df['CEP'] = df.CEP.apply(lambda x: x.split(','))

    ceps_row = []
    nao_localizado = []
    for index, row in df.iterrows():
        for cep in row['CEP']:
            try:
                ceps_row.append(df_db.loc[df_db.index==int(cep)].values[0][0])
            except:
                nao_localizado.append(cep)
        df.at[index, 'Localidade DNE'] = ceps_row

    df = df[['Cod. Pareamento',
     'Cod. UF',
     'Sigla UF',
     'Cod. Subarea',
     'Nome Subarea',
     'Cod. Municipio',
     'Nome Municipio',
     'Codigo Agencia',
     'Nome Agencia',
     'Cod. Setor',
     'Cod. Logradouro CNEFE',
     'Tipo Logradouro CNEFE',
     'Titulo Logradouro CNEFE',
     'Nome Logradouro CNEFE',
     'Nome Tratado CNEFE',
     'Tipo Logradouro DNE',
     'Titulo Logradouro DNE',
     'Nome Logradouro DNE',
     'Nome Tratado DNE',
     'Logradouro Completo DNE',
     'Distancia',
     'Cod. Match',
     'Motivo Match',
     'CEP',
     'Localidade DNE',
     'CEP Logradouro CNEFE',
     'CEPs Face',
     'Localidade Face',
     'Alterar Logradouro para DNE?',
     'Observaçao',
     'SIAPE Alteração',
     'Nome Alteraçao',
     'Data_Alteraçao',
     'Status']]
    return df, nao_localizado