import hashlib
import logging
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

import analisador
import limites

# Carrega a chave API do arquivo .env
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("analisador_curriculo")

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

    @media (max-width: 700px) {
        .st-key-formulario [data-testid="stHorizontalBlock"] {
            flex-direction: column;
        }

        .st-key-formulario [data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        h1 {
            font-size: 2rem !important;
        }
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


def carregar_api_key() -> str | None:
    try:
        chave = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        chave = None
    return chave or os.getenv("GEMINI_API_KEY")


api_key = carregar_api_key()
if not api_key:
    st.error(
        "Chave GEMINI_API_KEY não encontrada. Configure um arquivo .env na raiz "
        "do projeto (local) ou os Secrets do Streamlit (deploy)."
    )
    st.stop()


@st.cache_resource
def obter_cliente() -> genai.Client:
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=analisador.TEMPO_LIMITE_MS,
            retry_options=types.HttpRetryOptions(
                attempts=2,
                initial_delay=1.0,
                max_delay=5.0,
            ),
        ),
    )


client = obter_cliente()


def carregar_limite(nome: str, padrao: int) -> int:
    valor: object = None
    try:
        valor = st.secrets.get(nome)
    except Exception:
        valor = None
    if valor is None:
        valor = os.getenv(nome)
    try:
        return max(1, int(valor))
    except (TypeError, ValueError):
        return padrao


@st.cache_resource
def obter_controle_uso() -> limites.ControleDeUso:
    return limites.ControleDeUso(
        max_por_sessao=carregar_limite(
            "LIMITE_ANALISES_SESSAO", limites.MAX_ANALISES_POR_SESSAO
        ),
        max_por_ip=carregar_limite(
            "LIMITE_ANALISES_IP", limites.MAX_ANALISES_POR_IP
        ),
        max_diarias=carregar_limite(
            "LIMITE_ANALISES_DIARIO", limites.MAX_ANALISES_DIARIAS
        ),
    )


def obter_ip() -> str | None:
    try:
        endereco = st.context.ip_address
    except Exception:
        return None
    return endereco or None


controle_uso = obter_controle_uso()

with st.sidebar:
    st.subheader("Configurações")
    modelo_escolhido = st.selectbox(
        "Modelo de IA",
        ("Automático", *analisador.MODELOS),
        help=(
            "No modo Automático, a aplicação tenta os modelos em sequência "
            "até obter uma resposta."
        ),
    )

    analises_realizadas = st.session_state.get("analises_realizadas", 0)
    restantes_sessao = limites.restantes_na_sessao(
        analises_realizadas, controle_uso.max_por_sessao
    )
    st.divider()
    st.caption(
        f"Análises nesta sessão: {analises_realizadas}/"
        f"{controle_uso.max_por_sessao} — restam {restantes_sessao}."
    )
    st.caption(f"Análises restantes hoje: {controle_uso.restantes_diarias()}.")

modelos = (
    analisador.MODELOS
    if modelo_escolhido == "Automático"
    else (modelo_escolhido,)
)


def calcular_chave(
    pdf_bytes: bytes,
    descricao_vaga: str,
    modelos_escolhidos: tuple[str, ...],
) -> str:
    hash_pdf = hashlib.sha256(pdf_bytes).hexdigest()
    assinatura = f"{hash_pdf}:{descricao_vaga}:{'|'.join(modelos_escolhidos)}"
    return hashlib.sha256(assinatura.encode("utf-8")).hexdigest()


def registrar_resultado(resultado: dict[str, str], descricao_vaga: str) -> None:
    st.session_state["resultado"] = resultado
    historico: list[dict[str, str]] = st.session_state.setdefault("historico", [])
    historico.insert(
        0,
        {
            "texto": resultado["texto"],
            "modelo": resultado["modelo"],
            "vaga": descricao_vaga.strip()[:80],
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        },
    )
    del historico[5:]


def exibir_resultado(resultado: dict[str, str]) -> None:
    st.caption(f"Análise gerada com o modelo {resultado['modelo']}.")
    st.download_button(
        "Baixar análise (.md)",
        data=resultado["texto"],
        file_name="analise_curriculo.md",
        mime="text/markdown",
        key="download_resultado",
        width="stretch",
    )


def exibir_erro(erro: Exception) -> None:
    st.session_state.pop("resultado", None)

    if isinstance(erro, ValueError):
        st.error(str(erro))
        return

    logger.error("Erro ao analisar currículo", exc_info=erro)
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
        st.error(
            "Não foi possível analisar o currículo. Tente novamente em instantes."
        )


# Entrada do usuário
with st.container(key="formulario"):
    col_curriculo, col_vaga = st.columns(2, gap="large")

    with col_curriculo:
        arquivo_pdf = st.file_uploader("Envie seu currículo (PDF)", type=["pdf"])
        st.caption(
            f"Formato aceito: PDF, até {analisador.TAMANHO_MAX_MB} MB e "
            f"{analisador.MAX_PAGINAS} páginas."
        )

    with col_vaga:
        descricao_vaga = st.text_area(
            "Descrição da vaga de estágio",
            height=200,
            placeholder="Cole aqui os requisitos e atividades da vaga...",
        )

analisar = st.button(
    "Analisar Currículo",
    type="primary",
    width="stretch",
)

if analisar:
    if not arquivo_pdf or not descricao_vaga.strip():
        st.warning("Por favor, envie o PDF e cole a descrição da vaga.")
    elif arquivo_pdf.size > analisador.TAMANHO_MAX_BYTES:
        st.error(f"O PDF deve ter no máximo {analisador.TAMANHO_MAX_MB} MB.")
    else:
        try:
            pdf_bytes = arquivo_pdf.read()
            tem_texto = analisador.validar_pdf(pdf_bytes)
            if not tem_texto:
                st.info(
                    "O PDF não possui texto extraível. A IA tentará "
                    "interpretá-lo como imagem."
                )

            descricao = descricao_vaga.strip()
            chave = calcular_chave(pdf_bytes, descricao, modelos)
            cache: dict[str, dict[str, str]] = st.session_state.setdefault(
                "cache_analises", {}
            )

            if chave in cache:
                registrar_resultado(cache[chave], descricao)
            elif analises_realizadas >= controle_uso.max_por_sessao:
                st.error(
                    limites.MENSAGEM_LIMITE_SESSAO.format(
                        maximo=controle_uso.max_por_sessao
                    )
                )
            else:
                st.session_state["pendente"] = {
                    "pdf_bytes": pdf_bytes,
                    "descricao": descricao,
                    "modelos": modelos,
                    "chave": chave,
                }
                st.session_state.pop("resultado", None)
        except ValueError as erro:
            exibir_erro(erro)

pendente = st.session_state.pop("pendente", None)

if pendente:
    bloqueio = controle_uso.consumir(
        obter_ip(), st.session_state.get("analises_realizadas", 0)
    )

    if bloqueio:
        st.session_state.pop("resultado", None)
        st.error(bloqueio)
    else:
        st.session_state["analises_realizadas"] = (
            st.session_state.get("analises_realizadas", 0) + 1
        )
        with st.container(key="resultado"):
            estado: dict[str, str] = {}
            try:
                with st.spinner("Analisando compatibilidade..."):
                    texto = st.write_stream(
                        analisador.gerar_analise_stream(
                            client,
                            pendente["pdf_bytes"],
                            analisador.montar_prompt(pendente["descricao"]),
                            pendente["modelos"],
                            estado,
                        )
                    )

                texto = texto if isinstance(texto, str) else "".join(texto)
                if not texto.strip():
                    raise ValueError(analisador.MENSAGEM_SEM_CONTEUDO)

                resultado = {
                    "texto": texto,
                    "modelo": estado.get("modelo", pendente["modelos"][0]),
                }
                registrar_resultado(resultado, pendente["descricao"])
                st.session_state.setdefault("cache_analises", {})[
                    pendente["chave"]
                ] = resultado
                exibir_resultado(resultado)
            except Exception as erro:
                exibir_erro(erro)

elif st.session_state.get("resultado"):
    resultado = st.session_state["resultado"]
    with st.container(key="resultado"):
        st.markdown(resultado["texto"])
        exibir_resultado(resultado)

historico = st.session_state.get("historico", [])
if historico:
    with st.expander("Análises anteriores nesta sessão"):
        rotulos = [
            f"{indice + 1}. {item['data']} — {item['vaga']}"
            for indice, item in enumerate(historico)
        ]
        escolha = st.selectbox(
            "Revisar análise",
            rotulos,
            index=None,
            placeholder="Selecione uma análise",
            key="historico_analises",
        )
        if escolha is not None:
            item = historico[rotulos.index(escolha)]
            st.markdown(item["texto"])
            st.caption(f"Análise gerada com o modelo {item['modelo']}.")

st.markdown(
    '<p class="rodape">Análise gerada por IA — use como apoio, não como veredito final.</p>',
    unsafe_allow_html=True,
)
