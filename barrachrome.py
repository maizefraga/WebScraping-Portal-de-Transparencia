from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json

# ABRIR NAVEGADOR HEADLESS
options = webdriver.ChromeOptions()
options.add_argument("--headless")
navegador = webdriver.Chrome(chrome_options=options)
navegador.get(
    'https://www.gp.srv.br/transparencia_barradogarcas/servlet/contrato_servidor_v3?1')
# WINDOW_HANDLES É PARA ADMINISTRAR MÚLTIPLAS JANELAS
navegador.window_handles
print("navegador")

# CLICAR EM PESQUISAR
pesquisar = navegador.find_element(By.ID, "DIV_BTN_PESQUISAR")
pesquisar.click()
print("pesquisar")

# EXIBIR 150 SERVIRES POR PÁGINA
exibir = WebDriverWait(navegador, 40).until(
    EC.element_to_be_clickable((By.ID, "vQTD_POR_PAGINA")))
exibir_paginas = Select(exibir)
exibir_paginas.select_by_value('150')
print("exibir")

# ENCONTRAR BOTÃO DE PRÓXIMO
proximo = "document.querySelector('#TB_PROXIMO_ENABLED').querySelector('a').click()"
print("proximo set")

# ENCONTRAR O TOTAL DE REGISTROS
total_registros_loc = (By.ID, 'span_vTOTAL_REGISTROS')
total_registros_e = WebDriverWait(navegador, 30).until(
    EC.visibility_of_element_located(total_registros_loc))
total_registros = total_registros_e.text
registros = int(total_registros_e.text)

# CALCULAR QUANTAS VEZES SERÁ NECESSÁRIO CLICAR EM "PRÓXIMO"
if (registros % 150 != 0):
    quantidade_paginas = registros//150 + 1
else:
    quantidade_paginas = registros//150

# DECLARAR MAP, SERÁ UM DICIONÁRIO DE DICIONÁRIOS
map = {}

# DECLARAR NOME, SERÁ UMA LISTA COM APENAS O NOME DOS SERVIDORES
# ISSO SERÁ ÚTIL APENAS PARA A COMPARAÇÃO COM A lista_de_nomes
nomes = []


# FUNÇÃO PARA LER A TABELA DENTRO DA LUPA
def ler_tab_interna(map, nomes):
    # O MEU 'tr' NÃO TEM CLASSE ENTÃO PRECISA SER ACESSADO DA SEGUINTE MANEIRA
    table = navegador.find_element(By.ID, 'TABLE3')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    tr = tbody.find_elements(By.TAG_NAME, 'tr')
    
    # 'td' QUE CONTÉM A MATRÍCULA
    td = tr[0].find_elements(By.TAG_NAME, 'td')
    matricula = td[2].get_property('innerText')
 
    # 'td' QUE CONTÉM O NOME
    td = tr[2].find_elements(By.TAG_NAME, 'td')
    nome = td[2].get_property('innerText')
 
    # 'td' QUE CONTÉM O SALÁRIO
    td = tr[6].find_elements(By.TAG_NAME, 'td')
    salario = td[2].get_property('innerText')
 
    # 'td' QUE CONTÉM O CARGO
    td = tr[8].find_elements(By.TAG_NAME, 'td')
    cargo = td[2].get_property('innerText')
 
    # 'td' QUE CONTÉM A LOTAÇÃO
    td = tr[12].find_elements(By.TAG_NAME, 'td')
    lotacao = td[2].get_property('innerText')
 
    # EU PODERIA TER FEITO DA SEGUINTE MANEIRA:
#    map.update({matricula: {'matricula': matricula, 'nome': nome,
#                        'salario': salario, 'cargo': cargo, 'lotacao': lotacao}})
#   nomes.append(nome)
    # MAS PARA MELHOR COMPREENÇÃO VIZUAL DA MINHA PARTE PREFERI FAZER ASSIM:
    aux = {matricula: {'matricula': matricula, 'nome': nome,
                       'salario': salario, 'cargo': cargo, 'lotacao': lotacao}}
    map.update(aux)
    aux = nome
    nomes.append(aux)
    print("tabela interna lida")

    return map, nomes


# FUNÇÃO PARA LER A PÁGINA (ENCONTRAR TODAS AS LUPAS), ENTRAR EM CADA UMA, LER O CONTEÚDO E VOLTAR PARA A PÁGINA DE ORIGEM
def ler_tabela(map, nomes):
    table = navegador.find_element(By.ID, 'grid')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    tr = tbody.find_elements(By.TAG_NAME, 'tr')
    print(len(tr))

    # LER A PÁGINA
    i = 0
    while i < len(tr):

        # CLICAR NA LUPA
        aux = str(i)
        lupa = "document.querySelectorAll('[title=" + \
            '"Visualizar detalhes"]' + "')[" + aux + "].click()"
        navegador.execute_script(lupa)

        # IR PARA PÁGINA DA LUPA
        window_before = navegador.window_handles[0]
        window_after = navegador.window_handles[-1]
        navegador.switch_to.window(window_after)

        # LER A TABELA
        ler_tab_interna(map=map, nomes=nomes)
        print(i)
        
        #VOLTAR PARA PÁGINA DE ORIGEM
        navegador.switch_to.window(window_before)
        i += 1
    return (map, nomes)


sleep(3)

# O RÔLE BASICAMENTE
count = 1
j = 0
while j < quantidade_paginas:

    ler_tabela(map=map, nomes=nomes)
    print("lido")
    navegador.execute_script(proximo)
    count += 1
    print("pag", count)
    j += 1
    sleep(1)

print(map)

navegador.close()

# CRIEI UM ARQUIVO JSON COM TODOS OS DADOS RASPADOS
file = open('map.json', 'w')
json.dump(map, file, ensure_ascii=False)
file.close()

# DECLAREI UMA LISTA DE NOMES ALEATÓRIOS COM ALGUNS NOMES DE SERVIDORES
lista_de_nomes = ['ABADIA BONFIM MARTINS GALLE', 'MAÍZE FRAGA SOUZA',
                  'ALKFJAIGJGJAREJ JAIWEJAO', 'AOIJOAIHGIO', 'LUENE PEREIRA DE SOUZA']

# FIZ A INTERSECÇÃO DESSES NOMES COM OS NOMES DOS SERVIDORES
nomes_inersecao = list(set(nomes).intersection(set(lista_de_nomes)))

# EXTRAÍ DO DICIONÁRIO DE DICIONÁRIOS (O RESULTADO TOTAL DA RASPAGEM) APENAS OS DADOS DOS NOMES RESULTANTES DA INTERSECÇÃO
dict_intersecao = {servidor[0]: servidor[1] for servidor in map.items(
) if servidor[1]['nome'] in nomes_inersecao}
print(dict_intersecao)

# CRIEI UM ARQUIVO JSON COM TODOS OS DADOS DA INTERSECÇÃO
file = open('intersecao.json', 'w')
json.dump(dict_intersecao, file, ensure_ascii=False)
file.close()
