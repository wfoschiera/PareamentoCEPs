# PareamentoCEPs
Repositorio para hospedagem do código utilizado para pareamento das bases IBGE_CNEFE x DNE
Estes scripts manipulam um csv extraído da base do BDO criando, a partir deste, uma lista de CEPs únicos a partir das bases do CNEFE e DNE.
A partir da lista de CEPs únicos, é populado um banco de dados identificando para cada CEP, sua localidade.
Essa informação servirá de insumo para a revisão do pareamento.

Além disso, existem dois scripts que avaliam as 'regras de negócio' do pareamento. As regras utilizadas são:
1. Campo *CEP Localidade CNEFE* **contido** entre os valores do campo *CEP DNE* & campo *Alterar Logradouro para DNE?* **igual** a *Não*.
1. Campo *CEP Localidade CNEFE* **não está contido** entre os valores do campo *CEP DNE* & campo *Alterar Logradouro para DNE?* **igual** a *Sim*.

Com isso, busca-se facilitar a busca da supervisão por falsos negativos (1) e falsos positivos (2).


# Como utilizar estes scripts
Caso seja usuário Windows, recomendo a instação do pacote *Anaconda*, disponível [aqui](https://docs.anaconda.com/anaconda/install/windows/). Para instalar os pacotes, utilizar o gerenciar de pacotes *conda*.

A forma mais fácil é clonando este repositório. Em sua máquina local, assegure-se de que o pipenv esteja instalado, ou instale-o usando o comando:
```
pip install pipenv
```
Então, execute o comando:
```
pipenv sync
```
Com isso, todos os pacotes necessários serão instalados.
Em seguida, no ```Terminal```, navegue até a pasta do projeto e abra o Jupyter Notebook, executando o comando:
```
../pareamento$ jupyter notebook 
```
Na célula 1, altere o caminho (path) onde está localizado o arquivo csv extraído do bdo, para isso, edite o campo ```caminho_do_csv``` com o valor apropriado.
```python
from utils.csv_manager import csv_loader
caminho_do_csv = '../bdo_csv/bdo_report_16-02-2021-16-55-00.csv'
ceps_csv = csv_loader(caminho_do_csv)
```
Depois, é possível realizar todo o processamento de forma automatiza. No menu bar, selecione Kernel >> Restart & Run All.

Em caso de dúvidas ou bugs, entre em contato.

Ideias, sugestões e contribuições são bem vindas.
