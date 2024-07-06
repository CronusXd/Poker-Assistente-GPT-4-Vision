# Importando as bibliotecas necessárias
import pygetwindow as gw  # Biblioteca para manipular janelas do sistema
import time  # Biblioteca para manipulação de tempo (delays)
import base64  # Biblioteca para codificação e decodificação base64
import json  # Biblioteca para manipulação de dados JSON
import os  # Biblioteca para manipulação de operações do sistema
import requests  # Biblioteca para fazer requisições HTTP
from PIL import ImageGrab  # Biblioteca para captura de tela

# Função para capturar a tela de uma janela específica
def capture_window(window_title):
    """
    Captura a tela de uma janela específica com o título fornecido.

    Args:
    window_title (str): Título da janela a ser capturada.

    Returns:
    str: Caminho do arquivo da captura de tela salva.

    Raises:
    Exception: Se a janela não for encontrada.
    """
    windows = gw.getWindowsWithTitle(window_title)  # Obtém a janela pelo título
    if windows:
        window = windows[0]  # Seleciona a primeira janela encontrada
        window.activate()  # Ativa a janela para garantir que está em foco
        time.sleep(1)  # Aguarda um segundo para garantir que a janela esteja em foco

        # Captura a tela da área delimitada pela janela
        screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.right, window.bottom))
        file_path = 'poker_hand.png'  # Define o caminho do arquivo da captura de tela
        screenshot.save(file_path)  # Salva a captura de tela como um arquivo PNG
        return file_path  # Retorna o caminho do arquivo salvo
    else:
        raise Exception("Janela não encontrada")  # Lança uma exceção se a janela não for encontrada

# Função para codificar a imagem em base64
def encode_image(image_path):
    """
    Codifica a imagem em base64.

    Args:
    image_path (str): Caminho do arquivo da imagem a ser codificada.

    Returns:
    str: Imagem codificada em base64.
    """
    with open(image_path, "rb") as image_file:  # Abre a imagem em modo binário
        return base64.b64encode(image_file.read()).decode('utf-8')  # Codifica a imagem em base64 e retorna como string

# Função para analisar a imagem e obter informações da OpenAI GPT-4 Vision API
def analyze_poker_hand(image_path, api_key):
    """
    Envia a imagem para a API da OpenAI GPT-4 Vision e processa a resposta.

    Args:
    image_path (str): Caminho do arquivo da imagem a ser analisada.
    api_key (str): Chave da API para autenticação.

    Raises:
    Exception: Se a resposta da API for inválida ou se a requisição falhar.
    """
    base64_image = encode_image(image_path)  # Codifica a imagem em base64

    headers = {
        "Content-Type": "application/json",  # Define o tipo de conteúdo como JSON
        "Authorization": f"Bearer {api_key}"  # Adiciona o token de autorização
    }

    # Prompt minimalista para a API responder com a melhor jogada baseada em GTO
    prompt = (
        "Assuma que você é um jogador de poker profissional. "
        "Leve em consideração os seguintes fatores: força da minha mão, tamanho do meu stack, tamanho do pote, tamanho do stack do vilão. "
        "Seja um jogador Tight. "
        "Responda: Quais minhas cartas? "
        "Responda: Qual é minha equidade na mão? "
        "Responda só a ação que você faria: [ação]. "
        "Copas 'h', Ouros 'd', Paus 'c', Espadas 's'. "
        "Exemplo de resposta: "
        "Equit: 55%, Cartas: AhKd, Ação: Raise."
    )

    payload = {
        "model": "gpt-4o-2024-05-13",  # Modelo a ser utilizado
        "messages": [
            {
                "role": "user",  # Define o papel do remetente como usuário
                "content": [
                    {"type": "text", "text": prompt},  # Adiciona o prompt como texto
                    {
                        "type": "image_url",  # Define o tipo de conteúdo como URL de imagem
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"  # Adiciona a imagem codificada em base64
                        }
                    }
                ]
            }
        ],
        "max_tokens": 30  # Limita o número de tokens para uma resposta mais concisa
    }

    # Envia a requisição POST para a API
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()  # Converte a resposta para JSON

        # Verifica se a resposta da API contém informações válidas
        if 'choices' in data and data['choices']:
            # Processa e imprime as informações recebidas da API
            for choice in data['choices']:
                message_content = choice['message']['content']
                print(message_content)  # Imprime o conteúdo da mensagem

            # Imprime o total de tokens usados
            total_tokens = data.get('usage', {}).get('total_tokens', 'N/A')
            print(f"Total de tokens usados: {total_tokens}")

        else:
            raise Exception("Resposta inválida da API")  # Lança uma exceção se a resposta for inválida

    else:
        raise Exception(f"Falha ao analisar a imagem: {response.status_code} - {response.text}")  # Lança uma exceção se a requisição falhar

# Função principal para executar o script
def main():
    """
    Função principal para capturar a janela do Poker, enviar a imagem para análise e imprimir a resposta.
    """
    window_title = "AFH"  # Título da janela a ser capturada
    api_key = "API-Openai"  # Chave da API para autenticação

    try:
        image_path = capture_window(window_title)  # Captura a janela do Poker
        print(f"Procurando Resposta")  # Imprime uma mensagem de status
       
        # Obter análise da OpenAI GPT-4 Vision API
        analyze_poker_hand(image_path, api_key)  # Analisa a imagem e imprime a resposta
       
    except Exception as e:
        print(f"Erro: {e}")  # Imprime o erro se ocorrer uma exceção

# Executa a função principal se o script for executado diretamente
if __name__ == "__main__":
    main()  # Chama a função principal
