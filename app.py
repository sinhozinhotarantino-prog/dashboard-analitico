import streamlit as st
import pandas as pd
from groq import Groq
import re

# Configuração da página
st.set_page_config(page_title="Agente Analítico Universal", page_icon="🤖", layout="wide")

# Inicializa o motor Llama 3 via Groq
try:
    cliente_groq = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Configure a GROQ_API_KEY nos secrets do Streamlit.")
    st.stop()

st.title("🤖 Agente Analítico Universal")
st.write("Faça o upload de qualquer base de dados. O Agente fará a leitura inicial e aguardará suas instruções.")

arquivo_upload = st.file_uploader("Suba sua planilha (CSV ou Excel)", type=["csv", "xlsx"])

def renderizar_grafico(texto, df):
    match = re.search(r'\|\|GRAFICO\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\|\|', texto)
    if match:
        tipo = match.group(1).strip().upper()
        eixo_x = match.group(2).strip()
        eixo_y = match.group(3).strip()
        col_filtro = match.group(4).strip()
        val_filtro = match.group(5).strip()
        
        df_plot = df.copy()
        
        try:
            if col_filtro.upper() != "NENHUM" and val_filtro.upper() != "NENHUM" and col_filtro in df.columns:
                df_plot = df_plot[df_plot[col_filtro].astype(str).str.contains(val_filtro, case=False, na=False)]
                st.markdown(f"**📊 Visualização Gerada:** {tipo} ({eixo_x} vs {eixo_y}) - *Filtrado por: {col_filtro} = {val_filtro}*")
            else:
                st.markdown(f"**📊 Visualização Gerada:** {tipo} ({eixo_x} vs {eixo_y})")
                
            if "BARRA" in tipo:
                st.bar_chart(df_plot, x=eixo_x, y=eixo_y)
            elif "LINHA" in tipo:
                st.line_chart(df_plot, x=eixo_x, y=eixo_y)
            elif "DISPERS" in tipo:
                st.scatter_chart(df_plot, x=eixo_x, y=eixo_y)
            else:
                st.info(f"O modelo de gráfico sugerido ({tipo}) não possui suporte nativo imediato.")
        except Exception as e:
            st.caption(f"Aviso: Não foi possível desenhar o gráfico. (Erro: {e})")

def consultar_ia(prompt):
    resposta = cliente_groq.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-70b-versatile",
        temperature=0.3
    )
    return resposta.choices[0].message.content

if arquivo_upload is not None:
    try:
        if arquivo_upload.name.endswith('.csv'):
            df = pd.read_csv(arquivo_upload)
        else:
            df = pd.read_excel(arquivo_upload)
            
        with st.expander("🔍 Visualizar estrutura dos dados brutos"):
            st.dataframe(df.head(5))
        
        st.divider()

        resumo_categorias = ""
        colunas_texto = df.select_dtypes(include=['object', 'string']).columns
        for col in colunas_texto:
            unicos = df[df[col].notna()][col].unique()
            if len(unicos) < 15:
                resumo_categorias += f"- {col}: {', '.join(map(str, unicos))}\n"

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
        if "arquivo_atual" not in st.session_state or st.session_state.arquivo_atual != arquivo_upload.name:
            st.session_state.arquivo_atual = arquivo_upload.name
            st.session_state.chat_history = []
            
            amostra_dados = df.head(3).to_string()
            info_colunas = df.dtypes.to_string()
            
            prompt_reconhecimento = f"""
            Você é um assistente de análise de dados universal. O usuário fez upload de um arquivo.
            Tipos de colunas detectadas: {info_colunas}
            Valores categóricos identificados automaticamente:
            {resumo_categorias}
            Amostra das primeiras linhas: {amostra_dados}
            
            Escreva uma mensagem curta em português do Brasil:
            1. Diga do que parece se tratar este arquivo.
            2. Cite os principais tipos de informações e categorias disponíveis para filtro.
            3. Pergunte o que ele deseja analisar, sugerindo gráficos.
            """
            
            with st.spinner("Lendo a estrutura universal do arquivo..."):
                resposta_texto = consultar_ia(prompt_reconhecimento)
                st.session_state.chat_history.append({"role": "ai", "content": resposta_texto})

        for msg in st.session_state.chat_history:
            with st.chat_message("🤖" if msg["role"] == "ai" else "🧑‍💻"):
                texto_limpo = re.sub(r'\|\|GRAFICO.*?\|\|', '', msg["content"])
                st.write(texto_limpo)
                if msg["role"] == "ai":
                    renderizar_grafico(msg["content"], df)

        user_input = st.chat_input("Digite o que você quer analisar ou peça um gráfico...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("🧑‍💻"):
                st.write(user_input)
                
            with st.chat_message("🤖"):
                with st.spinner("Processando análises..."):
                    contexto_conversa = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history[-3:]])
                    resumo_estatistico = df.describe(include='all').to_string()
                    lista_colunas = ", ".join(df.columns)
                    
                    prompt_chat = f"""
                    O usuário está fazendo perguntas sobre uma tabela.
                    Colunas disponíveis: {lista_colunas}
                    Valores categóricos para filtros:
                    {resumo_categorias}
                    Resumo estatístico: {resumo_estatistico}
                    
                    Últimas mensagens:
                    {contexto_conversa}
                    
                    DIRETRIZES DE GRÁFICOS:
                    1. Recomende o gráfico adequado e peça aprovação.
                    2. SE O USUÁRIO CONFIRMAR A CRIAÇÃO DE UM GRÁFICO, inclua EXATAMENTE esta estrutura no final:
                    ||GRAFICO | [TIPO] | [EIXO_X] | [EIXO_Y] | [COLUNA_FILTRO] | [VALOR_FILTRO]||
                    
                    - Tipos suportados: BARRAS, LINHAS, DISPERSAO.
                    - Exemplo sem filtro: ||GRAFICO | BARRAS | Vendedor | Faturamento | NENHUM | NENHUM||
                    - Exemplo com filtro: ||GRAFICO | BARRAS | Nome | Nota | Turma | 6º Ano A||
                    
                    Responda à dúvida de forma analítica e em português do Brasil.
                    """
                    
                    texto_final = consultar_ia(prompt_chat)
                    
                    texto_exibicao = re.sub(r'\|\|GRAFICO.*?\|\|', '', texto_final)
                    st.write(texto_exibicao)
                    
                    renderizar_grafico(texto_final, df)
                    st.session_state.chat_history.append({"role": "ai", "content": texto_final})

    except Exception as e:
        erro_str = str(e).lower()
        if "429" in erro_str or "rate limit" in erro_str or "quota" in erro_str:
            st.warning("""
            ⚠️️ **Olá! Muitos recrutadores estão testando esta ferramenta hoje e o limite da API de demonstração foi atingido.**
            
            Enquanto a cota se renova (leva apenas alguns segundos), você pode conferir o vídeo de demonstração completa desta aplicação funcionando no meu repositório.
            
            👉 [Clique aqui para assistir ao vídeo no GitHub](SUBSTITUA_PELO_SEU_LINK_AQUI)
            """)
        else:
            st.error(f"Ocorreu um erro inesperado ao processar os dados: {e}")
