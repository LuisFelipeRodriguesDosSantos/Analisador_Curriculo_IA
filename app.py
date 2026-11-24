import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Carrega a chave API do arquivo .env
load_dotenv()

st.set_page_config(
    page_title="Analisador de Currículo IA",
    page_icon="📄",
    layout="centered",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, .stApp, button, input, textarea,
    [data-testid="stMarkdownContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
            Roboto, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(900px 500px at 12% -10%, rgba(99, 102, 241, 0.16), transparent 60%),
            radial-gradient(800px 450px at 95% 0%, rgba(56, 189, 248, 0.14), transparent 55%),
            linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
        background-attachment: fixed;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    footer {
        display: none;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: 920px;
        padding-top: 3rem;
        padding-bottom: 2rem;
    }

    h1 {
        text-align: center;
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.03em;
        color: #1e1b4b;
        margin-bottom: 0.35rem;
    }

    .subtitulo {
        text-align: center;
        color: #64748b;
        font-size: 1.02rem;
        line-height: 1.6;
        max-width: 620px;
        margin: 0 auto 2rem !important;
    }

    .st-key-formulario,
    .st-key-resultado {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 24px 48px -34px rgba(30, 27, 75, 0.45);
    }

    .st-key-resultado {
        margin-top: 1.5rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: #ffffff;
        border: 1.5px dashed #c7d2fe;
        border-radius: 16px;
        padding: 2.2rem 1rem;
        min-height: 165px;
        align-items: center;
        transition: border-color 0.2s ease, background 0.2s ease;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #6366f1;
        background: #f5f3ff;
    }

    [data-testid="stFileUploaderDropzone"] button {
        border-radius: 10px;
        border-color: #c7d2fe;
        background: #eef2ff;
        color: #4338ca;
        font-weight: 600;
    }

    [data-baseweb="textarea"],
    [data-testid="stTextArea"] textarea {
        background: #ffffff;
        border-radius: 14px;
    }

    [data-testid="stTextArea"] textarea {
        padding: 0.85rem 1rem;
        font-size: 0.95rem;
    }

    [data-testid="stTextArea"] label p,
    [data-testid="stFileUploader"] label p {
        font-weight: 600;
        color: #334155;
    }

    [data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #6366f1, #4f46e5);
        border: none;
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        color: #ffffff;
        box-shadow: 0 12px 24px -12px rgba(79, 70, 229, 0.8);
        transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
    }

    [data-testid="stBaseButton-primary"]:hover {
        filter: brightness(1.05);
        transform: translateY(-1px);
        box-shadow: 0 16px 30px -12px rgba(79, 70, 229, 0.85);
    }

    [data-testid="stBaseButton-primary"]:active {
        transform: translateY(0);
    }

    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 {
        color: #312e81;
    }

    [data-testid="stMarkdownContainer"] strong {
        color: #4338ca;
    }

    [data-testid="stMarkdownContainer"] hr {
        border-color: #e2e8f0;
    }

    [data-testid="stAlert"] {
        border-radius: 14px;
    }

    .rodape {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 2.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📄 Analisador de Currículo para Estágios")
st.markdown(
    '<p class="subtitulo">Compare seu currículo com a vaga de estágio e descubra '
    "o que destacar, o que falta e como passar pelos filtros ATS.</p>",
    unsafe_allow_html=True,
)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error(
        "Chave GEMINI_API_KEY não encontrada. Crie um arquivo .env na raiz do "
        "projeto com a linha: GEMINI_API_KEY=sua_chave"
    )
    st.stop()


MODELOS = (
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
)


@st.cache_resource
def obter_cliente():
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                attempts=2,
                initial_delay=1.0,
                max_delay=5.0,
            )
        ),
    )


client = obter_cliente()


def gerar_analise(pdf_bytes, prompt):
    ultimo_erro = None
    for modelo in MODELOS:
        try:
            return client.models.generate_content(
                model=modelo,
                contents=[
                    types.Part.from_bytes(
                        data=pdf_bytes,
                        mime_type="application/pdf",
                    ),
                    prompt,
                ],
            )
        except Exception as erro:
            ultimo_erro = erro
    raise ultimo_erro


# Entrada do usuário
with st.container(key="formulario"):
    col_curriculo, col_vaga = st.columns(2, gap="large")

    with col_curriculo:
        arquivo_pdf = st.file_uploader("Envie seu currículo (PDF)", type=["pdf"])
        st.caption("Formato aceito: PDF, até 20 MB.")

    with col_vaga:
        descricao_vaga = st.text_area(
            "Descrição da vaga de estágio",
            height=200,
            placeholder="Cole aqui os requisitos e atividades da vaga...",
        )

analisar = st.button(
    "Analisar Currículo",
    type="primary",
    use_container_width=True,
)

if analisar:
    if not arquivo_pdf or not descricao_vaga.strip():
        st.warning("Por favor, envie o PDF e cole a descrição da vaga.")
    elif arquivo_pdf.size > 20 * 1024 * 1024:
        st.error("O PDF deve ter no máximo 20 MB.")
    else:
        with st.spinner("Analisando compatibilidade..."):
            try:
                pdf_bytes = arquivo_pdf.read()

                prompt = f"""Você é um recrutador técnico especializado em vagas de estágio em tecnologia.
Analise o currículo em PDF anexado comparando-o com a descrição da vaga abaixo.

Descrição da Vaga:
{descricao_vaga.strip()}

Forneça uma resposta estruturada em Markdown com:
1. **Nota de Compatibilidade (0 a 100%)** e justificativa breve.
2. **Pontos Fortes:** o que já alinha bem com a vaga.
3. **O que está faltando (Lacunas):** habilidades, projetos ou experiências pedidas na vaga e ausentes no currículo.
4. **Palavras-chave Sugeridas:** termos importantes da vaga para incluir no currículo (foco em filtros ATS).
5. **Dica Prática:** uma melhoria rápida que o candidato pode fazer hoje."""

                response = gerar_analise(pdf_bytes, prompt)

                if response.text:
                    with st.container(key="resultado"):
                        st.markdown(response.text)
                else:
                    st.warning(
                        "A IA não retornou conteúdo. O PDF pode estar protegido "
                        "ou a solicitação foi bloqueada. Tente novamente."
                    )
            except Exception as erro:
                mensagem = str(erro)
                if "503" in mensagem or "UNAVAILABLE" in mensagem:
                    st.error(
                        "O modelo de IA está com alta demanda no momento. "
                        "Aguarde alguns instantes e tente novamente."
                    )
                elif "429" in mensagem or "RESOURCE_EXHAUSTED" in mensagem:
                    st.error(
                        "Limite de uso da API atingido. "
                        "Aguarde alguns minutos e tente novamente."
                    )
                else:
                    st.error(f"Não foi possível analisar o currículo: {erro}")

st.markdown(
    '<p class="rodape">Análise gerada por IA — use como apoio, não como veredito final.</p>',
    unsafe_allow_html=True,
)
