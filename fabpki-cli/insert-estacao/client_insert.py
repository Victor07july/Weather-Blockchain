import requests
import sys
from hfc.fabric import Client as client_fabric
import asyncio
from datetime import datetime
import time
#from get_previsao import getPrevisao
from get_estacao import getEstacao

domain = ["inmetro.br"]
channel_name = "nmi-channel"
cc_name = "fabpki"
cc_version = "1.0"
callpeer = []

URL = "http://alertario.rio.rj.gov.br/upload/TempoReal.html"

# arrays para receber os dados
arrayPrecipitacao = []
arrayDados = []

# inicializando variáveis
horaLeituraP = "Indisponível"
totalUltimaHora = "Indisponível"
situacao = "Indisponível"

horaLeituraD = "Indisponível"
direcaoVentoGraus = "Indisponível"
velocidadeVento = "Indisponível"
temperatura = "Indisponível"
pressao = "Indisponível"
umidade = "Indisponível"

# ------ VERIFICAÇÃO E EXECUÇÃO --------

if __name__ == "__main__":

    #test if the city name was informed as argument
    if len(sys.argv) != 2: # o primeiro  argumento sempre vai ser o chamado do python
        print("Usage:",sys.argv[0], "<\"ID da Estação \"> ")
        exit(1)

    # recebe o id da estação como variavel
    idEstacao = str(sys.argv[1])

    # envia o id inserido para a função de verificar estações
    arrayPrecipitacao, arrayDados, ultimaAtualizacaoE = getEstacao(URL, idEstacao)

    # ------ PEGANDO O HORÁRIO DE EXECUÇÃO DO CLIENTE --------
    # Horário de execução do cliente em unix
    timestampCliente = time.time()
    print(f'Horário de execução do cliente em UNIX: {timestampCliente}')

    # ------ PEGANDO O HORÁRIO DE ULTIMA ATUALIZAÇÃO DOS DADOS DAS ESTAÇÕES -------
    # Extrair a hora e a data da string
    hora_data = ultimaAtualizacaoE.split(": ")[-1]  # "10:23 - 18/07/2023"
    
    # Separar a hora e a data da ultima atualização
    hora, data = hora_data.split(" - ")
    
    # Converter para o formato UNIX
    formato = "%H:%M - %d/%m/%Y"
    data_hora = datetime.strptime(hora_data, formato)
    timestampEstacao = int(data_hora.timestamp())
    print(f'Última atualização dos dados das estações em UNIX: {timestampEstacao}')

    # pode ser que uma das estações tenha apenas um dos dados disponiveis (ou nenhum)
    # verifica se pelo menos um dos dados estão disponíveis
    situacao = ""

    if arrayPrecipitacao or arrayDados:
        print("Sucesso! Uma ou ambas as arrays possui os dados necessários")

        if arrayPrecipitacao:
            horaLeitura = arrayPrecipitacao[2]
            totalUltimaHora = arrayPrecipitacao[4]
            situacao = "Somente precipitacao disponivel"

        if arrayDados:
            direcaoVentoGraus = arrayDados[3]
            velocidadeVento = arrayDados[4]
            temperatura = arrayDados[5]
            pressao = arrayDados[6]
            umidade = arrayDados[7]
            if situacao == "Somente precipitacao disponivel":
                situacao = "Precipitacao e dados disponiveis"
            else:
                situacao = "Somente dados disponiveis"

        
        print(situacao)
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
        #   cc_version=cc_version,
            fcn='insertStationData',
            args=[
                idEstacao,
                horaLeitura, 
                totalUltimaHora, 
                situacao, 
                direcaoVentoGraus, 
                velocidadeVento, 
                temperatura, 
                pressao, 
                umidade, 
                str(timestampEstacao), 
                str(timestampCliente),
                ],
            cc_pattern=None))

        #so far, so good
        print("Successo ao registrar dados")
    
    else:
        print("Falha! Ambas as arrays estão vazias! Você escolheu um ID válido?")

