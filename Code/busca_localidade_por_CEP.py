# ### Usando pacote [PyCEPCorreios](https://github.com/mstuttgart/pycep-correios)

try:
    from pycep_correios import get_address_from_cep, WebService
except:
    pipenv install pycep-correios
    from pycep_correios import get_address_from_cep, WebService 
import pandas as pd
import numpy as np
import re
import csv

#Teste pyCEPCorreios
address = get_address_from_cep('78550045', webservice=WebService.CORREIOS)
print(address)

# Ler arquivo xls e converter para pandas dataframe
df = pd.read_csv('pareamento_logradouro_relatorio_12_02_2021_09_00_00.csv',sep=';', parse_dates = ['Data_Alteraçao'])
pd.set_option('display.float_format', '{:.0f}'.format)

df = df.drop(columns = ['Cod.UF', 'SiglaUF',
                  'Cod.Municipio', 'NomeMunicipio', 
                  'CodigoAgencia', 'NomeAgencia','Cod.LogradouroCNEFE', 
                  'TipoLogradouroCNEFE','TituloLogradouroCNEFE',
                  'TipoLogradouroDNE', 'TituloLogradouroDNE',
                  'LogradouroCompletoDNE', 'Distancia', 'Cod.Match', 'MotivoMatch', 
                  'Observaçao', 'NomeAlteraçao', 'Status', 'Unnamed: 33'])

#df.columns

# filtrar por subárea, neste caso, eliminando a subárea que já foi trabalhada
df = df.loc[df['Cod.Subarea'] != '510790900']
#df.head(50)

# Preencher campos nulos com 0, cast do CEP_CNEFE para string
df = df.fillna(0)
df.CEP_CNEFE = df.CEP_CNEFE.astype(str)

#remover o ponto do float
df['CEP_CNEFE'] = df['CEP_CNEFE'].apply(lambda x: x.split('.')[0])

# Remover espaços em branco, depois converter a string para uma lista de strings, usando função lambda
df['CEP'] = df['CEP'].astype(str) #cast to string to avoid typeError
df['CEP'] = df['CEP'].apply(lambda x: x.replace(' ',''))
df['CEP'] = df.CEP.apply(lambda x: x.split(','))
#df.head(50)

# ## Regras de negócio:
# ### Regra 2
# * Retornar casos onde o 'CEP Logradouro CNEFE' **não** está contido na lista do campo 'CEP' (DNE) e o campo "Alterar Logradouro para DNE?" == SIM
#df.info()

#Uma maneira prática de entender qual o tipo do objeto de um dataframe é usando o método iterrows()
#e analisar a saída usando print
'''
localidades = dict()
for index, rowStr in df.iterrows():
    print(index, type(rowStr['CEP']))
'''

# ### Criando a mascara que será utilizada como filtro
mask = dict()
for index, row in df.iterrows():
    #print(index, row['CEP_CNEFE'], row['CEP'])
    mask[index] = row['CEP_CNEFE'] in row['CEP']
filtro = pd.Series(mask)
#print(filtro.loc[50:70])


# In[13]:


df['Filtro'] = filtro
print(df.loc[50:70])


# In[14]:


df_NaoContemCepCnefe = df.loc[df['Filtro'] == False]


# In[15]:


df_alteraDNE_Sim = df_NaoContemCepCnefe.loc[df_NaoContemCepCnefe['AlterarLogradouroparaDNE?'] == 'SIM']


# In[16]:


df_alteraDNE_Sim


# In[17]:


df_alteraDNE_Sim.info()


# In[18]:


df_alteraDNE_Sim.to_csv('MT_-_CEPCNEFE_dif_CEPDNE_&_AlteraDNE_SIM.csv')


# In[ ]:


#cria arquivo csv localmente para ir adicionando os CEPs obtidos
with open('CEP_e_localidades_pareamento.csv', 'w', newline='') as csvfile:
    fieldnames = ['index', 'logradouro', 'CEPsDNE', 'localidades']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    
    cep_temp = {}
    localidades = dict()
    i = 0
    total = len(df_alteraDNE_Sim)
    for index, rowStr in df_alteraDNE_Sim.iterrows():
        localidade = []
        for cep in rowStr['CEP']:
            cep = re.sub('[^0-9]', '', cep)
            if not cep in cep_temp.keys():
                #se o cep não existir na base local, consulta localidade a partir do CEP e grava CEP e Localidade
                try:
                    address = get_address_from_cep(cep, webservice=WebService.CORREIOS)
                    #popula um dicionário dos CEPs já consultados, assim não repito as consultas
                    cep_temp[cep] = cep_temp.get(cep, address['bairro'])
                except:
                    cep_temp[cep] = cep_temp.get(cep, 'cep nao encontrado')
                
            else:
                address['bairro'] = cep_temp[cep]
                print('existente')
            if address['bairro']=='':
                localidade.append(cep)
            else:
                localidade.append(address['bairro'])
        print(localidade)
        localidades[index] = localidade
        
        
        writer.writerow({'index': index, 'logradouro':rowStr['NomeTratadoCNEFE'], 'CEPsDNE': rowStr['CEP'], 'localidades':localidade})

        print('\n')
        print(f'Apurados {i} / {total}')
        
        i += 1


# In[ ]:


df_alteraDNE_Sim.to_csv('MT_-_CEPCNEFE_dif_CEPDNE_&_AlteraDNE_SIM_COM_LOCALIDADES_DNE.csv')

