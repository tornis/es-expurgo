#!/usr/bin/env python3
import sys, re, getopt
import logging
from elasticsearch import Elasticsearch
from datetime import datetime, timedelta

# CONF
# Parametros de conexão com Elastic
ES_HOSTS = ["http://localhost:9200"]
ES_AUTH  = True
ES_USER  = "user"
ES_PASS  = "pass"
# Quais índices serão afetados. Ex: ["index1","index2"] se for todos coloque ["*"]
INDICES = ["*"]
# Periodo de retação em dias
PERIODO_RETENCAO = 365

logging.basicConfig(level=logging.INFO, filename='expurgo.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

class expurgo:
    def __init__(self,es_hosts,es_user,es_pass,es_auth):
        if es_auth == True: 
            self.es = Elasticsearch(hosts=es_hosts,http_auth=(es_user, es_pass))
        else: 
            self.es = Elasticsearch(hosts=es_hosts)

    def getAllIndices(self,indices):
        indices = self.es.cat.indices(index=indices,h='index',s='index:desc').split()
        rx = re.compile(r'^\.')
        return [i for i in indices if not rx.match(i)]

    def getTimeStr(self, dias):
        dias = datetime.today() - timedelta(days=dias)
        return datetime.strftime(dias,"%Y-%m-%d")

    def getTask(self,task_id):
        return self.es.tasks.get(task_id=task_id)

    def remove(self, retencao,indices):
        oldTime = self.getTimeStr(retencao)
        idx = self.getAllIndices(indices)
        results = self.es.delete_by_query(index=idx, opaque_id='expurgo-1', wait_for_completion=False, body={
            "query": {
                "bool": {
                    "should": [
                      {
                        "range": {
                          "startedAt": {
                            "lt": oldTime
                          }
                        }
                      },
                      {
                        "range": {
                          "scheduledTime": {
                            "lt": oldTime
                          }
                        }
                      }
                    ]
                }
            }
        })
        return results.get('task')


lst = sys.argv[1:]
options = "xt:"
long_options = ["expurgo","task"]
try:
    if (len(lst) == 0):
        print("\nes-expurgo: Script para expurgo de dados usando a API Delete By Query do Elasticsearch")
        print("")
        print ('Uso: es-expurgo.py -xt [paramento]')
        print ("\t-x --expurgo - Inicia o processo de expurgo dos dados. Essa opção nao tem paramentros")
        print ("\t-t --task - Consulta o status da task iniciada pelo o expurgo. É necessário ter o id da task retornada pelo expurgo\n")
    else: 
        arguments, value = getopt.getopt(lst, options, long_options)
        for k, v in arguments:
            if k in ("-x", "--expurgo"): 
                try: 
                    logging.info('INICIO DO PROCESSO DE EXPURGO...')
                    ex = expurgo(ES_HOSTS,ES_USER,ES_PASS,ES_AUTH)
                    results = ex.remove(PERIODO_RETENCAO,INDICES)
                    task = str(results)
                    logging.info('TAREFA INICIADA, SEGUE TASK_ID: ' + task)
                    print("\nTask Id Gerada: " + task + '\n')
                except Exception as e:
                    logging.error("TRACE ----> ", exc_info=True)
                    print(e)
                logging.info('FIM DO PROCESSO DE EXPURGO')
            elif k in ("-t","--task"): 
                ex = expurgo(ES_HOSTS,ES_USER,ES_PASS,ES_AUTH)
                print(ex.getTask(v))
except getopt.error as err:
    print("ERROR: Defina um parametro para o script\nUso: es-expurgo [options] [value]\n Exemplo: es-expurgo -t task_id\n")    
