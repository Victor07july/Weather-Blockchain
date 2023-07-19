import requests
import sys
from hfc.fabric import Client as client_fabric
import asyncio
from datetime import datetime
import time
from get_previsao import getPrevisao
from get_estacao import getEstacao

domain = ["inmetro.br"]
channel_name = "nmi-channel"
cc_name = "fabpki"
cc_version = "1.0"
callpeer = []

URL = "http://alertario.rio.rj.gov.br/upload/TempoReal.html"

# arrays com os dados
arrayPrecipitacao = []
arrayDados = []

#arrayPrevisao = []
# arrayPrevisao = getPrevisao(print_output=False)

# ------ VERIFICAÇÃO E EXECUÇÃO --------

if __name__ == "__main__":

    #test if the city name was informed as argument
    if len(sys.argv) != 2: # o primeiro  argumentosempre vai ser o chamado do python
        print("Usage:",sys.argv[0], "<\"ID da Estação \"> ")
        exit(1)

    # recebe o id da estação como variavel
    idEstacao = sys.argv[1]

    # envia o id inserido para a função de verificar estações
    arrayPrecipitacao, arrayDados, ultimaAtualizacaoE = getEstacao(URL, idEstacao)


    # ------ PEGANDO O HORÁRIO DE EXECUÇÃO DO CLIENTE --------
    # Horário de execução do cliente em unix
    timestampCliente = time.time()
    print(f'Horário de execução do cliente em UNIX: {timestampCliente}')

    # ------ PEGANDO O HORÁRIO DE ULTIMA ATUALIZAÇÃO DA PREVISÃO --------
    # ultimaAtualizacaoP = arrayPrevisao[8] # Usar isso como base na hora de verificar a cada 5 minutos

    # # Extrair a hora e a data da string
    # hora_data = ultimaAtualizacaoP.split(": ")[-1]  # "10:23 - 18/07/2023"

    # # Separar a hora e a data da ultima atualização
    # hora, data = hora_data.split(" - ")
    # # Converter para o formato UNIX
    # formato = "%H:%M - %d/%m/%Y"
    # data_hora = datetime.strptime(hora_data, formato)
    # timestampPrevisao = int(data_hora.timestamp())
    # print(f'Horário de ultima atualização da previsão em UNIX: {timestampPrevisao}')

    # ------ PEGANDO O HORÁRIO DE ULTIMA ATUALIZAÇÃO DOS DADOS DAS ESTAÇÕES --------
    # Extrair a hora e a data da string
    hora_data = ultimaAtualizacaoE.split(": ")[-1]  # "10:23 - 18/07/2023"

    # Separar a hora e a data da ultima atualização
    hora, data = hora_data.split(" - ")

    # Converter para o formato UNIX
    formato = "%H:%M - %d/%m/%Y"
    data_hora = datetime.strptime(hora_data, formato)
    timestampEstacao = int(data_hora.timestamp())
    print(f'Última atualização dos dados das estações em UNIX: {timestampEstacao}')

    if arrayDados or arrayPrecipitacao:
        print("Sucesso! Uma ou ambas as arrays possui os dados necessários")
        print("Iniciando o chaincode...")

        #creates a loop object to manage async transactions
        loop = asyncio.get_event_loop()

        #instantiate the hyperledeger fabric client
        c_hlf = client_fabric(net_profile=(domain[0] + ".json"))

        #get access to Fabric as Admin user
        admin = c_hlf.get_user(domain[0], 'Admin')
        for i in domain:
            callpeer.append("peer0." + i)

        #the Fabric Python SDK do not read the channel configuration, we need to add it mannually'''
        c_hlf.new_channel(channel_name)

        #invoke the chaincode to register the meter
        response = loop.run_until_complete(c_hlf.chaincode_invoke(
            requestor=admin, 
            channel_name=channel_name, 
            peers=callpeer,
            cc_name=cc_name, 
          # cc_version=cc_version,
            fcn='registerWeatherFromWeb',
            args=[cidade, situacao, temperaturaString],
            cc_pattern=None))

        #so far, so good
        print("Success on register climate")
    
    else:
        print("Falha! Ambas as arrays estão vazias! Você escolheu um ID válido?")

