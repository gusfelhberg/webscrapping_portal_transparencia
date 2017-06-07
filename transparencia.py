import pandas as pd
import requests
from bs4 import BeautifulSoup
from splinter import Browser
import pickle


url_base = 'http://transparencia.gov.br/servidores/Servidor-ListaServidores.asp'

def buscar_dados_cpf(lista_cpfs):

    browser = Browser('chrome')
    lista_vinculos = []
    cpfs_nao_encontrados = []
    for cpf in lista_cpfs:
        browser.visit(url_base)
        browser.fill('Pesquisa',cpf)
        button = browser.find_by_value('ok')
        button.click()
        link = browser.find_link_by_partial_href('DetalhaServidor')

        if len(link) == 0:
            # print('{} - Servidor não encontrado'.format(cpf))
            cpfs_nao_encontrados.append(cpf)
        else:
            link.first.click()

            html_content = requests.get(browser.url)
            soup = BeautifulSoup(html_content.content,'html.parser')

            #busca o nome do pesquisado
            nome = soup.find('td',{"class":"colunaValor"})
            # print(nome)
            # if nome is not None:
            nome = nome.string.strip()

            table = soup.find_all('table')
            tabela_vinculos = soup.find_all('div',{"id":"listagemConvenios"})
            tabela_externa = tabela_vinculos[0].find('table')
            tabelas_vinculos = tabela_externa.find_all('table')



            for vinculo_bruto in tabelas_vinculos:

                vinculo = vinculo_bruto.find('tbody')

                lista_bruta = []
                lst = []
                for linha in vinculo:
                    prop = linha.find("td")
                    valor = linha.find("strong")
                    lst.append(prop)
                    lst.append(valor)
                    lista_bruta.append(lst)
                    lst=[]

                vinculo_limpo = []
                lst = []
                lst.append('cpf')
                lst.append(cpf)
                vinculo_limpo.append(lst)
                lst = []
                lst.append('Nome')
                lst.append(nome)
                vinculo_limpo.append(lst)
                lst = []
                for item_bruto in lista_bruta:
                    if item_bruto != [-1, -1] and len(item_bruto) > 0:

                        try:
                            prop = item_bruto[0].text.replace(':','').replace('\xa0 ','').strip()
                            value = item_bruto[1].text.replace(':','').replace('\xa0 ','').strip()
                            lst.append(prop)
                            lst.append(value)
                            vinculo_limpo.append(lst)
                            lst = []
                        except AttributeError:
                            prop = item_bruto[0].text.replace(':','').replace('\xa0 ','').strip()
                            value = ''
                            lst.append(prop)
                            lst.append(value)
                            vinculo_limpo.append(lst)
                            lst = []
                        except IndexError:
                            pass
                    else:
                        pass

                lista_vinculos.append(vinculo_limpo)
    browser.quit()
    print("Lista de CPFs não encontrados:")
    for i in cpfs_nao_encontrados:
        print(i)

    return lista_vinculos

def carregar_dados_cpf_pickle():
    file = open("vinculos.pickle",'rb')
    object_file = pickle.load(file)
    file.close()
    return object_file

def salvar_dados_cpf_pickle(lista_vinculos):
    filehandler = open("vinculos.pickle","wb")
    pickle.dump(lista_vinculos,filehandler)
    filehandler.close()

def migrar_lista_para_dataframe(lista_vinculos):

    lista_dicts = []


    for i in range(len(lista_vinculos)):
            lista_dicts.append(dict(lista_vinculos[i]))

    df = pd.DataFrame.from_dict(lista_dicts)
    colunas = ['cpf','Nome','Atividade', 'Ato de Ingresso no Órgão', 'Ato de nomeação/contratação', 'Cargo Emprego', 'Classe', 'Data da Última Alteração no Cargo', 'Data da última alteração na função', 'Data da última alteração no Órgão', 'Data de nomeação/contratação', 'Data de publicação', 'Documento Legal', 'Função', 'Ingresso no Serviço Público', 'Jornada de Trabalho', 'Local de Exercício - Localização', 'Matrícula', 'Nível', 'Número Doc. Legal', 'Ocorrência de Afastamento/Licença', 'Opção parcial', 'Padrão', 'Referência', 'Regime Jurídico', 'Sigla - Descrição', 'Situação Vínculo', 'UF', 'UORG', 'Órgão', 'Órgão Origem - Lotação', 'Órgão Superior']
    df = df[colunas].set_index('cpf')

    return df

def carrega_lista_cpfs():

    cpfs_completo = pd.read_excel('lista_cpfs.xlsx',sheet_name=0)
    cpfs = cpfs_completo['cpfs'].tolist()
    cpfs = list(map(lambda x: str(x).zfill(11),cpfs))
    return cpfs

lista_cpfs = carrega_lista_cpfs()

lista_vinculos = buscar_dados_cpf(lista_cpfs)
#salvar_dados_cpf_pickle(lista_vinculos)

# lista_vinculos = carregar_dados_cpf_pickle()
df = migrar_lista_para_dataframe(lista_vinculos)

writer = pd.ExcelWriter('dados_portal_transparencia.xlsx', engine='xlsxwriter')

df.to_excel(writer, sheet_name='Dados')
writer.save()
