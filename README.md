# 🤖 Agente Analítico Universal (Dashboard Analítico)

Um *dashboard* interativo construído em Python que permite analisar e conversar com as suas bases de dados em segundos. Este projeto foi criado para eliminar a barreira técnica da análise de dados, automatizando a limpeza preliminar de planilhas (*Data Quality*) e utilizando Inteligência Artificial para gerar informações e gráficos através de linguagem natural.

## ✨ Funcionalidades Principais

- **Auditoria de Dados em Tempo Real:** Ao fazer o upload de um arquivo (CSV ou Excel), o sistema realiza um diagnóstico automático, detectando anomalias como células vazias e linhas duplicadas.
- **Assepsia e Limpeza Automática:** Com um simples clique, o programa utiliza o Pandas para limpar a planilha nos bastidores, preenchendo os dados que faltam e removendo repetições.
- **Interface Conversacional:** O usuário dialoga com a tabela, fazendo perguntas em português estruturado diretamente para a IA.
- **Geração Dinâmica de Gráficos:** Através do processamento da IA, o sistema interpreta a lógica matemática dos pedidos e desenha instantaneamente gráficos interativos (barras, linhas ou dispersão) na tela.

## 🛠️ Tecnologias e Ferramentas

- **Linguagem:** Python
- **Interface Web:** Streamlit
- **Manipulação de Dados:** Pandas
- **Inteligência Artificial:** Integração via API da Groq (motor LLM otimizado de alta velocidade)

## 🚀 Como rodar este projeto localmente

Para testar o Agente Analítico na sua própria máquina, siga os passos abaixo:

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/sinhozinhotarantino-prog/dashboard-analitico.git](https://github.com/sinhozinhotarantino-prog/dashboard-analitico.git)
cd dashboard-analitico
pip install -r requirements.txt
Configure a chave de segurança da API (Groq):

Crie uma pasta chamada .streamlit na raiz do seu projeto.

Dentro dessa pasta, crie um arquivo com o nome secrets.toml.

Insira a sua chave de acesso no arquivo com o seguinte formato:
GROQ_API_KEY = "cole_a_sua_chave_da_groq_aqui"
Inicie a aplicação:
streamlit run app.py
