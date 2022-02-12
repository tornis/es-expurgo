# es-expurgo.py

Script de Expurgo de dados usando a API Delete by Query do Elasticsearch

### Como Instalar:

**Requisitos necessários** 

* python-3.8+
* vitualenv 
* git

1. **Passo 1 - Instalando o Virtualenv**

`
pip3 install virtualenv 
`

2. **Passo 2 - Criando o virtualenv**

`cd /opt` 
`virtualenv .venv`


3. **Passo 3 - Carregando o virtualenv**

`
source /opt/.venv/bin/activate
`

4. **Passo 4 - Copiando o es-expurgo do git**

`git clone https://github.com/tornis/es-expurgo.git`

`cd es-expurgo`
 

5. **Passo 5 - Instalando as dependências** 

`pip3 install -r requirements.txt`

6. **Passo 6 - Configurando o es-expurgo.py** 

`vi es-expurgo.py`

`ES_HOSTS = ["http://localhost:9200"]`

`ES_AUTH  = True`

`ES_USER  = "elastic"`

`ES_PASS  = "123456"`

`INDICES = ["*"]`

`PERIODO_RETENCAO = 365`

7. **Passo 7 - Testando o Script**  

`./es-expurgo.py -x` 

8. **Passo 8 - Configurando o crontab** 

`vi /etc/crontab`

`0 1	* * *	root	/opt/.venv/bin/python /opt/es-expurgo/es-expurgo.py -x >> /tmp/es-expurgo.log 2>&1`