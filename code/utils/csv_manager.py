import pandas as pd


def csv_loader(csv_file):
    """
    Parses a BDO CSV file, select unique CEPs and return a pd.Series of CEPs.
    Tip: Can be saved using pd.Series.to_csv(path, sep=',', header=['CEP'], index=False)

        :parameter
            csv_file (str): A str path to csv file

        :return
            pd.Series (pd.Series): pd.Series list of all unique CEPs
    """
    df = pd.read_csv(csv_file, sep=';', parse_dates=['Data_Alteraçao'])
    pd.set_option('display.float_format', '{:.0f}'.format)

    df = df.fillna(0)
    df = df.drop(columns=['Cod. Pareamento', 'Cod. UF', 'Sigla UF', 'Cod. Subarea',
                          'Nome Subarea', 'Cod. Municipio', 'Nome Municipio', 'Codigo Agencia',
                          'Nome Agencia', 'Cod. Setor', 'Cod. Logradouro CNEFE',
                          'Tipo Logradouro CNEFE', 'Titulo Logradouro CNEFE',
                          'Nome Logradouro CNEFE', 'Nome Tratado CNEFE', 'Tipo Logradouro DNE',
                          'Titulo Logradouro DNE', 'Nome Logradouro DNE', 'Nome Tratado DNE',
                          'Logradouro Completo DNE', 'Distancia', 'Cod. Match', 'Motivo Match',
                          'CEPs Face', 'Localidade Face',
                          'Alterar Logradouro para DNE?', 'Observaçao', 'SIAPE Alteração',
                          'Nome Alteraçao', 'Data_Alteraçao', 'Status', 'Unnamed: 33'])

    # df.astype({'CEP Logradouro CNEFE': 'int32'}).dtypes

    df['CEP'] = df['CEP'].str.replace(' ', '', regex=False)

    ceps_dne = []
    for index, row in df.iterrows():
        if type(row.CEP) == str:
            for cep in row.CEP.split(','):
                # print(index, cep)
                ceps_dne.append(int(cep))

    ceps_cnefe = df['CEP Logradouro CNEFE'].astype(int).tolist()
    ceps = ceps_dne + ceps_cnefe
    ceps = list(set(ceps))
    return pd.Series(ceps)
