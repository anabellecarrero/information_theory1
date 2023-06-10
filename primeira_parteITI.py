import time
import struct
import matplotlib.pyplot as plt

def salvar_graficos(rc, rc_k, tempos, local): 
    fig1, ax1 = plt.subplots()
    ax1.set_title('Tempo - K')
    ax1.set_ylabel('Tempo (segundos)')
    ax1.set_xlabel('K')
    ax1.scatter(list(range(9, 17)), tempos)
    fig1.savefig(f"{local}/tempo_k.png")

    fig2, ax2 = plt.subplots()
    ax2.set_title('RC(tamArqOriginal/tamArqComprimido) - K')
    ax2.set_ylabel('RC')
    ax2.set_xlabel('K')
    ax2.scatter(list(range(9, 17)), rc)
    fig2.savefig(f"{local}/rc.png")

    fig3, ax3 = plt.subplots()
    ax3.set_title('RC(tamArqOriginal/((totalIndices*K)/8)) - K')
    ax3.set_ylabel('RC')
    ax3.set_xlabel('K')
    ax3.scatter(list(range(9, 17)), rc_k)
    fig3.savefig(f"{local}/rc_k.png")


def ler_arquivo(nome_arquivo): 
    with open (nome_arquivo, "rb") as arquivo: #lê como binário
        texto = arquivo.read()
        texto = texto.decode('ISO-8859-1')   #decodifica em ISO-8859-1 para deixar texto em string
    return texto

def escrever_arquivo(nome_arquivo, mensagem_compactada, formato):
    outFile = open(nome_arquivo , "wb")
    for i in mensagem_compactada:
        if formato == 'H':
            outFile.write(struct.pack(formato, i))
        else: 
            outFile.write(struct.pack(formato, ord(i)))
    outFile.close()

def ler_arquivo_compactado(nome_arquivo):
    mensagem = open(nome_arquivo, "rb").read()
    mensagem_compactada = [] 
    for i in range(0,len(mensagem),2):
        arr = bytearray([mensagem[i],mensagem[i+1]])
        mensagem_compactada.append(struct.unpack('H', arr)[0])
    return mensagem_compactada


def compactar(mensagem, k): 
    dicionario = {}       

    for i in range(256):   #iniciando o dicionário com o alfabeto
        dicionario[i.to_bytes(1, 'big')]=i

    #variáveis que serão usadas no LZD
    tamanho_dicionario = 256  # tam do dicionário + 1 (indica o próx local livre a ser inserido)
    mensagem_compactada = [] 
    char_atual =''
    char_anterior =''

    for char in mensagem: #percorre toda a mensagem
        char_atual=char_anterior+char

        if char_atual.encode('ISO-8859-1') not in dicionario: #verifica se já existe o símbolo do dicionário
            if len(dicionario)<2**k:
                dicionario[char_atual.encode('ISO-8859-1')]=tamanho_dicionario
                tamanho_dicionario+=1
            codigo_dic=dicionario[char_anterior.encode('ISO-8859-1')] 
            mensagem_compactada.append(codigo_dic) #adiciona o novo código na mensagem
            char_anterior=char
        else:
            char_anterior=char_atual

    codigo_dic = dicionario[char_anterior.encode('ISO-8859-1')]
    mensagem_compactada.append(codigo_dic)
    return mensagem_compactada, tamanho_dicionario

def descompactar(mensagem, k):
    dicionario = {}
    tamanho_dicionario = 256
    mensagem_descompactada = ''
    
    for i in range(256): #iniciando o dicionário com o alfabeto
        dicionario[i] = chr(i) 
   
    for i in mensagem:   #tradução
        if len(dicionario) <= 2**k:
            if tamanho_dicionario > 256:   
                dicionario[tamanho_dicionario-1] += dicionario[i][0]
        mensagem_descompactada += dicionario[i]
        dicionario[tamanho_dicionario] = dicionario[i]  
        tamanho_dicionario += 1
    return mensagem_descompactada, tamanho_dicionario




mensagem = ler_arquivo("corpus16MB.txt")
rc = []
rc_k = []
tempos = []
for i in range(9,17):
    tempo_inicial = time.time()
    mensagem_compactada, tamanho_dicionario = compactar(mensagem, i) #compacta a mensagem 
    tempo_final = time.time()

    #printa os resultados
    escrever_arquivo(f"texto_compactado/texto{i}.txt", mensagem_compactada, 'H')
    
    print(f"Tempo para compactar K = {i}: {tempo_final-tempo_inicial}")
    tempos.append(tempo_final-tempo_inicial)
    print(f"Quantidade de índices do dicionário: {tamanho_dicionario}")
    print(f"Tamanho mensagem original: {len(mensagem)}")
    print(f"Tamanho mensagem compactada: {len(mensagem_compactada)}")
    print(f"Razão de compressão (tamArqOriginal/tamArqComprimido): {len(mensagem)/ len(mensagem_compactada)}")
    rc.append(len(mensagem)/ len(mensagem_compactada))
    print(f"Razão de compressão (tamArqOriginal/((totalIndices*K)/8)): {len(mensagem)/ ((tamanho_dicionario*i)/8)}\n\n\n")
    rc_k.append(len(mensagem)/ ((tamanho_dicionario*i)/8))
    
    
    mensagem_compactada = ler_arquivo_compactado(f"texto_compactado/texto{i}.txt")
    
    mensagem_descompactada, tamanho_dicionario = descompactar(mensagem_compactada, i)
    
    escrever_arquivo(f"texto_descompactado/texto{i}.txt", mensagem_descompactada, 'B')

#salva os gráficos
salvar_graficos(rc, rc_k, tempos, "graficos_texto")

