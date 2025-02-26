import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os

# Função para criar um gradiente de cores mais claras e transparentes
def gradient_fill(ax, x, y1, y2, color1, color2, **kwargs):
    z = np.empty((100, 1, 4), dtype=float)
    rgb1 = np.array(mcolors.to_rgba(color1))
    rgb2 = np.array(mcolors.to_rgba(color2))
    for i in range(100):
        z[i, 0, :] = (i * rgb2 + (99 - i) * rgb1) / 99
        z[i, 0, 3] = 0.3  # Ajustar a transparência aqui
    x = np.array([x[0], x[-1]])
    im = ax.imshow(z, aspect='auto', extent=[x.min(), x.max(), y1.min(), y2.max()], origin='lower', **kwargs)
    return im

# Função para adicionar uma imagem ao gráfico
def add_image(ax, image_path, zoom=0.2, xy=(0.85, 0.15)):
    if os.path.exists(image_path):
        image = plt.imread(image_path)
        imagebox = OffsetImage(image, zoom=zoom)
        ab = AnnotationBbox(imagebox, xy, frameon=False, xycoords='axes fraction')
        ax.add_artist(ab)
    else:
        st.error(f"Arquivo de imagem '{image_path}' não encontrado.")

# Interface do Streamlit
st.title("Análise de Textura")

# Seleção entre 1 ou 2 gráficos
grafico_opcao = st.radio("Selecione o número de gráficos", ('1 gráfico', '2 gráficos'))

# Campo de entrada comum para todos os gráficos
modelos_input = st.text_input("Digite os modelos separados por vírgula:").strip()
perda_agua_input = st.text_input("Digite as perdas de água separadas por vírgula:").strip()
crocancia_input = st.text_area("Digite os valores das crocâncias separadas por vírgula (os valores serão usados para calcular a crocância média):").strip()

# Se 1 gráfico for selecionado, adicionar campo para Tensão
tensao_input = None
if grafico_opcao == '1 gráfico':
    tensao_input = st.text_input("Digite a tensão do produto:")

# Função para gerar gráfico
def gerar_grafico(df, produto, tensao=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['Perda água'], df['Crocância med'], color='b', label='Dados')

    # Adicionar título e rótulos aos eixos
    ax.set_title(f'{produto}')
    ax.set_xlabel('Water loss (%)')
    ax.set_ylabel('Hardness (N)')

    # Definir intervalos dos eixos
    ax.set_xticks([i for i in range(0, 71, 2)])
    ax.set_yticks(range(0, 26, 1))

    # Definir limites dos eixos
    ax.set_xlim(0, 70)
    ax.set_ylim(0, 25)

    # Adicionar linhas dos eixos x e y mais fracas e atrás dos outros elementos
    ax.axhline(0, color='gray', linewidth=0.2, zorder=0)
    ax.axvline(0, color='gray', linewidth=0.2, zorder=0)
    ax.grid(color='gray', linestyle='-', linewidth=0.2, zorder=0)

    # Marcar um ponto no ponto de encontro (média dos valores)
    mean_perda_agua = df['Perda água'].mean()
    mean_crocancia_med = df['Crocância med'].mean()
    ax.scatter(mean_perda_agua, mean_crocancia_med, color='r', marker='o', s=100, label='Ponto de Encontro', zorder=5)

    # Adicionar tensão ao lado do ponto de encontro, se fornecido
    if tensao:
        ax.text(mean_perda_agua, mean_crocancia_med, f' Tensão: {tensao}', color='black', fontsize=12, ha='left')

    # Preencher com um degradê do verde para o laranja (mais claro e transparente)
    gradient_fill(ax, [20, 60], np.array([5]), np.array([24.8]), 'lightgreen', 'lightcoral')

    # Adicionar linhas vermelhas
    ax.plot([20, 60], [5, 5], color='red', zorder=3)
    ax.plot([20, 20], [0.5, 24.8], color='red', zorder=3)
    ax.plot([60, 60], [0.5, 24.8], color='red', zorder=3)

    # Adicionar linha cinza
    ax.plot([20, 60], [10, 10], color='gray', zorder=3)

    # Adicionar palavras no eixo X, alinhadas com a linha do eixo y = 13
    ax.text(10, 13, 'Uncooked', color='black', ha='center', va='center', fontsize=20, zorder=15)
    ax.text(65, 13, 'Dry', color='black', ha='center', va='center', fontsize=20, zorder=15)
    ax.text(40, 2, 'Indefinite', color='black', ha='center', va='center', fontsize=20, zorder=15)

    # Remover a legenda de pontos
    ax.legend().set_visible(False)

    # Adicionar imagem ao gráfico
    add_image(ax, 'foto.png', zoom=0.25, xy=(0.9, -0.1))

    # Exibir o gráfico
    st.pyplot(fig)

# Lógica de visualização
if grafico_opcao == '1 gráfico':
    if modelos_input and perda_agua_input and crocancia_input:
        try:
            # Conversão para listas de dados
            modelos = modelos_input.split(',')
            perda_agua = list(map(float, perda_agua_input.split(',')))
            crocancia = list(map(float, crocancia_input.split(',')))

            # Calcular a média da crocância
            crocancia_media = np.mean(crocancia)
            crocancia_med = [crocancia_media] * len(modelos)  # Atribuir a mesma média a todos os modelos

            # Criar um DataFrame com os dados fornecidos
            data = {
                'Modelo': modelos,
                'Perda água': perda_agua,
                'Crocância med': crocancia_med
            }
            df = pd.DataFrame(data)

            # Gerar gráfico
            for produto in modelos:
                df_produto = df[df['Modelo'] == produto]
                gerar_grafico(df_produto, produto, tensao_input)
        except ValueError:
            st.error("Por favor, insira valores numéricos válidos para perdas de água e crocâncias.")
    else:
        st.warning("Por favor, insira os dados necessários.")

elif grafico_opcao == '2 gráficos':
    # Solicitar as informações para o segundo gráfico
    modelos_input_2 = st.text_input("Digite os modelos para o segundo gráfico separados por vírgula:").strip()
    perda_agua_input_2 = st.text_input("Digite as perdas de água para o segundo gráfico separados por vírgula:").strip()
    crocancia_input_2 = st.text_area("Digite os valores das crocâncias para o segundo gráfico separados por vírgula:").strip()

    if modelos_input_2 and perda_agua_input_2 and crocancia_input_2 and modelos_input and perda_agua_input and crocancia_input:
        try:
            # Conversão para listas de dados
            modelos_1 = modelos_input.split(',')
            perda_agua_1 = list(map(float, perda_agua_input.split(',')))
            crocancia_1 = list(map(float, crocancia_input.split(',')))

            modelos_2 = modelos_input_2.split(',')
            perda_agua_2 = list(map(float, perda_agua_input_2.split(',')))
            crocancia_2 = list(map(float, crocancia_input_2.split(',')))

            # Calcular a média da crocância
            crocancia_media_1 = np.mean(crocancia_1)
            crocancia_med_1 = [crocancia_media_1] * len(modelos_1)

            crocancia_media_2 = np.mean(crocancia_2)
            crocancia_med_2 = [crocancia_media_2] * len(modelos_2)

            # Criar DataFrame para os dois gráficos
            data_1 = {
                'Modelo': modelos_1,
                'Perda água': perda_agua_1,
                'Crocância med': crocancia_med_1
            }
            df_1 = pd.DataFrame(data_1)

            data_2 = {
                'Modelo': modelos_2,
                'Perda água': perda_agua_2,
                'Crocância med': crocancia_med_2
            }
            df_2 = pd.DataFrame(data_2)

            # Gerar os gráficos
            for produto in modelos_1:
                df_produto_1 = df_1[df_1['Modelo'] == produto]
                gerar_grafico(df_produto_1, produto)

            for produto in modelos_2:
                df_produto_2 = df_2[df_2['Modelo'] == produto]
                gerar_grafico(df_produto_2, produto)

        except ValueError:
            st.error("Por favor, insira valores numéricos válidos para perdas de água e crocâncias.")
    else:
        st.warning("Por favor, insira todos os dados necessários para ambos os gráficos.")
