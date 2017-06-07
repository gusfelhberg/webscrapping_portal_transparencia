import pandas as pd
import requests
from bs4 import BeautifulSoup
from splinter import Browser
import pickle


url_base = 'http://transparencia.gov.br/servidores/Servidor-ListaServidores.asp'

def buscar_dados_cpf(cpf):

    browser = Browser('chrome')

    browser.visit(url_base)
    browser.fill('Pesquisa',cpf)
    button = browser.find_by_value('ok')
    button.click()
    link = browser.find_link_by_partial_href('DetalhaServidor')

    if len(link) == 0:
        print('Servidor não encontrado')
    else:
        link.first.click()

    html_content = requests.get(browser.url)
    soup = BeautifulSoup(html_content.content,'html.parser')
    browser.quit()
    table = soup.find_all('table')
    tabela_vinculos = soup.find_all('div',{"id":"listagemConvenios"})
    # tabela_externa = tabela_vinculos[0].find('table')
    tabelas_vinculos = tabela_externa.find_all('table')

    for vinculo_bruto in tabelas_vinculos:

        vinculo = tabelas_vinculos[0].find('tbody')

        lista = []
        lst = []
        for linha in vinculo:
            prop = linha.find("td")
            valor = linha.find("strong")
            lst.append(prop)
            lst.append(valor)
            lista.append(lst)
            lst=[]

        lista_vinculos = []
        vinculo_limpo = []
        lst = []
        lst.append('cpf')
        lst.append(cpf)
        vinculo_limpo.append(lst)
        lst = []
        for item in lista:
            if item != [-1, -1] and len(item) > 0:

                try:
                    prop = item[0].text.replace(':','').replace('\xa0 ','').strip()
                    value = item[1].text.replace(':','').replace('\xa0 ','').strip()
                    lst.append(prop)
                    lst.append(value)
                    vinculo_limpo.append(lst)
                    lst = []
                except AttributeError:
                    prop = item[0].text.replace(':','').replace('\xa0 ','').strip()
                    value = ''
                    lst.append(prop)
                    lst.append(value)
                    vinculo_limpo.append(lst)
                    lst = []
            else:
                pass

    return vinculo_limpo

def carregar_dados_cpf_pickle():
    file = open("vinculos.pickle",'rb')
    object_file = pickle.load(file)
    file.close()
    return object_file

def salvar_dados_cpf_pickle(lista_vinculos):
    filehandler = open("vinculos.pickle","wb")
    pickle.dump(lista_vinculos,filehandler)
    filehandler.close()

lista_vinculos = buscar_dados_cpf('09713437721')
#salvar_dados_cpf_pickle(lista_vinculos)

#lista_vinculos = carregar_dados_cpf_pickle()
print(lista_vinculos)
