# 📄 Analisador de Currículo para Estágios

Aplicação web em [Streamlit](https://streamlit.io/) que usa a API **Google Gemini** para comparar um currículo em PDF com a descrição de uma vaga de estágio. A IA calcula a compatibilidade, aponta pontos fortes, lacunas e palavras-chave relevantes para passar pelos filtros **ATS** (Applicant Tracking Systems).

## Funcionalidades

- Upload de currículo em **PDF** (até 20 MB).
- Análise do PDF diretamente pelo modelo, sem extração manual de texto.
- Nota de compatibilidade de **0 a 100%** com justificativa.
- Listagem de **pontos fortes** e **lacunas** em relação à vaga.
- Sugestão de **palavras-chave** para otimizar o currículo para ATS.
- Dica prática de melhoria rápida.
- Fallback automático entre múltiplos modelos Gemini e mensagens amigáveis para erros de demanda (`503`) e limite de uso (`429`).

## Tecnologias

- Python 3.10+
- [Streamlit](https://streamlit.io/)
- [google-genai](https://github.com/googleapis/python-genai) (SDK oficial do Gemini)
- [python-dotenv](https://github.com/theskumar/python-dotenv)

## Pré-requisitos

- Python 3.10 ou superior instalado.
- Uma chave de API do Google Gemini. Obtenha a sua em [Google AI Studio](https://aistudio.google.com/apikey).

## Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd Analisador_Curriculo_IA

# Crie e ative o ambiente virtual (Windows)
python -m venv venv
venv\Scripts\activate

# Linux/macOS
# python3 -m venv venv
# source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com a sua chave:

```env
GEMINI_API_KEY=sua_chave_aqui
```

> O arquivo `.env` já está no `.gitignore` e não deve ser versionado.

## Execução

```bash
streamlit run app.py
```

A aplicação abre em `http://localhost:8501`.

## Como usar

1. Envie o currículo em **PDF** no painel esquerdo.
2. Cole a descrição da vaga de estágio no painel direito.
3. Clique em **Analisar Currículo**.
4. Aguarde o processamento e confira o relatório gerado.

## Estrutura do projeto

```
Analisador_Curriculo_IA/
├── app.py              # Aplicação Streamlit (interface + integração com Gemini)
├── requirements.txt    # Dependências do projeto
├── .env                # Chave da API (não versionado)
├── .gitignore
└── README.md
```

## Como funciona

1. O usuário envia o PDF do currículo e a descrição da vaga.
2. O PDF é lido em bytes e enviado ao Gemini junto com um prompt estruturado de recrutador técnico.
3. A aplicação tenta os modelos em sequência (`gemini-3.5-flash-lite`, `gemini-3.5-flash`, `gemini-3.1-flash-lite`, `gemini-3.8-flash`) até obter uma resposta válida.
4. O relatório em Markdown é renderizado na tela.

## Limitações

- A análise é gerada por IA e deve ser usada como **apoio**, não como veredito final.
- PDFs protegidos por senha ou com texto não processável podem não ser analisados.
- O uso da API está sujeito às cotas e à disponibilidade do Google Gemini.

## Licença

Este projeto é de uso livre para fins de estudo e portfólio.
