import streamlit as st
import pandas as pd
import google.generativeai as genai
import re

# Configuração da página
st.set_page_config(page_title="Agente Analítico Universal", page_icon="🤖", layout="wide")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
modelo = genai.GenerativeModel('gemini-flash-latest')

st.title("🤖 Agente Analítico Universal")
st.write("Faça o upload de qualquer base de dados. O Agente fará a leitura inicial e aguardará suas instruções.")

arquivo_upload = st.file_uploader("Suba sua planilha (CSV ou Excel)", type=["csv", "xlsx"])

# Função segura para desenhar gráficos baseados no comando da IA
def renderizar_grafico(texto, df):
    # O código procura a etiqueta estruturada gerada pela IA
    match = re.search(r'\|\|GRAFICO\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\|\|', texto)
    if match:
        tipo = match.group(1).strip().upper()
        eixo_x = match.group(2).strip()
        eixo_y = match.group(3).strip()
        
        try:
            st.markdown(f"**Visualização Gerada:** {tipo} ({eixo_x} vs {eixo_y})")
            if "BARRA" in tipo:
                st.bar_chart(df, x=eixo_x, y=eixo_y)
            elif "LINHA" in tipo:
                st.line_chart(df, x=eixo_x, y=eixo_y)
            elif "DISPERS" in tipo:
                st.scatter_chart(df, x=eixo_x, y=eixo_y)
            else:
                st.info(f"O modelo de gráfico sugerido ({tipo}) não possui suporte nativo imediato. Tente barras ou linhas.")
        except Exception as e:
            st.caption("Aviso: Não foi possível desenhar o gráfico. Verifique se os eixos escolhidos possuem dados compatíveis.")

if arquivo_upload is not None:
    try:
        if arquivo_upload.name.endswith('.csv'):
            df = pd.read_csv(arquivo_upload)
        else:
            df = pd.read_excel(arquivo_upload)
            
        # 1. GAVETA DA TABELA (Tabela oculta por padrão para não poluir a tela)
        with st.expander("🔍 Visualizar estrutura dos dados brutos"):
            st.write("Valide se a tabela foi lida corretamente e consulte o nome das colunas:")
            st.dataframe(df.head(5))
        
        st.divider()

        # INICIALIZAÇÃO DA MEMÓRIA DO CHAT
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        if "arquivo_atual" not in st.session_state or st.session_state.arquivo_atual != arquivo_upload.name:
            st.session_state.arquivo_atual = arquivo_upload.name
            st.session_state.chat_history = []
            
            amostra_dados = df.head(3).to_string()
            info_colunas = df.dtypes.to_string()
            
            prompt_reconhecimento = f"""
            Você é um assistente de análise de dados. O usuário fez upload de um arquivo.
            Tipos de colunas detectadas: {info_colunas}
            Amostra das primeiras linhas: {amostra_dados}
            
            Escreva uma mensagem curta em português do Brasil:
            1. Diga do que parece se tratar este arquivo.
            2. Cite os principais tipos de informações.
            3. Pergunte o que ele deseja analisar e avise que você pode sugerir e gerar gráficos interativos sob demanda.
            """
            
            with st.spinner("Lendo a estrutura do arquivo..."):
                resposta = modelo.generate_content(prompt_reconhecimento)
                st.session_state.chat_history.append({"role": "ai", "content": resposta.text})

        # EXIBE O HISTÓRICO DA CONVERSA E OS GRÁFICOS
        for msg in st.session_state.chat_history:
            with st.chat_message("🤖" if msg["role"] == "ai" else "🧑‍💻"):
                # Removemos a etiqueta do texto antes de mostrar ao usuário para ficar invisível
                texto_limpo = re.sub(r'\|\|GRAFICO.*?\|\|', '', msg["content"])
                st.write(texto_limpo)
                
                # Se for mensagem da IA, tenta desenhar o gráfico se a etiqueta existir nos bastidores
                if msg["role"] == "ai":
                    renderizar_grafico(msg["content"], df)

        # CAIXA DE INTERAÇÃO
        user_input = st.chat_input("Digite o que você quer analisar ou peça um gráfico...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("🧑‍💻"):
                st.write(user_input)
                
            with st.chat_message("🤖"):
                with st.spinner("Processando..."):
                    contexto_conversa = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-3:]])
                    resumo_estatistico = df.describe(include='all').to_string()
                    lista_colunas = ", ".join(df.columns)
                    
                    prompt_chat = f"""
                    O usuário está fazendo perguntas sobre uma tabela.
                    Colunas disponíveis: {lista_colunas}
                    Resumo estatístico: {resumo_estatistico}
                    
                    Últimas mensagens:
                    {contexto_conversa}
                    
                    DIRETRIZES DE GRÁFICOS (MUITO IMPORTANTE):
                    1. Se o usuário pedir para visualizar os dados, sugira o gráfico mais adequado, mas pergunte se ele concorda ou se prefere outro modelo. Não gere o comando na primeira sugestão.
                    2. Se o usuário exigir um gráfico específico (mesmo que não seja o ideal), obedeça, mas avise educadamente das limitações matemáticas.
                    3. QUANDO O USUÁRIO CONFIRMAR A CRIAÇÃO DE UM GRÁFICO, inclua EXATAMENTE esta estrutura no final da sua resposta:
                    ||GRAFICO | [TIPO] | [NOME_COLUNA_X] | [NOME_COLUNA_Y]||
                    
                    Tipos suportados: BARRAS, LINHAS, DISPERSAO. 
                    Os nomes das colunas devem ser exatamente os que estão na lista.
                    
                    Responda à dúvida do usuário de forma direta, analítica e em português do Brasil.
                    """
                    resposta_chat = modelo.generate_content(prompt_chat)
                    texto_final = resposta_chat.text
                    
                    # Limpa a etiqueta para não aparecer no balão de texto
                    texto_exibicao = re.sub(r'\|\|GRAFICO.*?\|\|', '', texto_final)
                    st.write(texto_exibicao)
                    
                    # Desenha o gráfico se a etiqueta estiver na resposta
                    renderizar_grafico(texto_final, df)
                    
                    # Salva a resposta completa (com a etiqueta oculta) no histórico
                    st.session_state.chat_history.append({"role": "ai", "content": texto_final})

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
