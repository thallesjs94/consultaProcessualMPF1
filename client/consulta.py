from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pathlib import Path
import json
import time

class Consulta:
    def __init__(self):
        self.diretorio_atual = Path.cwd()
        self.diretorio_pai = self.diretorio_atual.parent
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.browser = Chrome(options=self.chrome_options)  # Inicializar o Chrome diretamente

    def consulta(self, codigoProcesso):
        #Tempo maximo de espera do elemento em segundos
        timeout = 10

        #Abrindo o navegador
        self.browser.get('https://apps.mpf.mp.br/aptusmpf/portal')

        #Consultando processo
        campoProcesso = WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(@title,"Informe o nº processo")]'))
        )
        campoProcesso.send_keys(codigoProcesso)

        buttonPesquisar = self.browser.find_element(By.XPATH, '//*[@id="btnPesquisar"]')
        buttonPesquisar.click()

        #Seleciona o primeiro item com espera explícita
        primeiroItem = WebDriverWait(self.browser, timeout).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@class="table"]/tbody/tr[1]/td[2]/div/div/div/a'))
        )
        primeiroItem.click()

        #Navega para a aba nova
        self.browser.switch_to.window(self.browser.window_handles[1])

        #Espera todos os elementos da pagina estarem carregados
        WebDriverWait(self.browser, timeout).until(EC.visibility_of_element_located((By.XPATH, '//*[text()="NUP:"]')))

        # Localizar a tabela
        table = self.browser.find_element(By.XPATH, '//*[@id="tab_proc"]')

        # Extrair todas as linhas da tabela
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Inicializar o dicionário para armazenar os dados
        table_data = {}
        last_key = ''
        # Percorrer as linhas e colunas
        for row in rows:
            # Extrair as colunas de cada linha
            cols = row.find_elements(By.TAG_NAME, 'td')

            #Trata a descrição que tem mais de uma linha
            if cols[0].text == '':
                table_data[last_key] = table_data[last_key] +' '+ cols[1].text
                continue
            else:
                last_key = cols[0].text
            if len(cols) >= 2:  # Verificar se a linha tem pelo menos 2 colunas
                key = cols[0].text  # Primeira coluna como chave
                if cols[1].text == '':
                    value = cols[2].text  # Terceira coluna como valor
                else:
                    value = cols[1].text  # Segunda coluna como valor
                table_data[key] = value  # Adicionar ao dicionário

        # Localizar a tabela de tramitação
        table = self.browser.find_element(By.XPATH, '//*[@id="tab_mov"]')

        # Extrair todas as linhas da tabela de tramitação
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Inicializar a lista de tramitação e o dicionário para armazenar os dados
        table_data['tramitacao'] = []

        # Percorrer as linhas e colunas de tramitação
        for row in rows:
            # Extrair as colunas de cada linha
            cols = row.find_elements(By.TAG_NAME, 'td')

            if len(cols) >= 2:  # Verificar se a linha tem pelo menos 2 colunas
                dict_tramitacao = {}  # Mover a criação do dicionário para dentro do loop
                data = cols[0].text  # Primeira coluna como chave
                descricao = cols[2].text  # Terceira coluna como valor
                dict_tramitacao['data'] = data  # Adicionar ao dicionário a data da tramitação
                dict_tramitacao['descricao'] = descricao # Adicionar ao dicionário a descrição da tramitação
                table_data['tramitacao'].append(dict_tramitacao)

        # Salvar os dados extraídos no arquivo JSON
        with open(self.diretorio_pai / 'result.json', 'w', encoding='utf-8') as arquivo_json:
            json.dump(table_data, arquivo_json, ensure_ascii=False, indent=4)

        print("Arquivo gerado em: " + str({self.diretorio_pai / 'result.json'}))

        # Fecha a aba aberta e volta para a tela anterior
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[0])

