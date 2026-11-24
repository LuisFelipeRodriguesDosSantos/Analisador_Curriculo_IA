# Conteúdos para saber — Analisador de Currículo IA

Mapa das habilidades necessárias para construir um projeto como este do zero.
Legenda: **[essencial]** você precisa dominar; **[importante]** precisa conhecer bem;
**[desejável]** aprofunda qualidade e manutenção.

> Importante: este projeto **usa** um modelo de IA via API. Você não precisa saber
> treinar modelos, machine learning ou matemática de redes neurais.

## 1. Fundamentos de Python **[essencial]**

- Sintaxe, variáveis, tipos (`str`, `int`, `float`, `bool`, `None`), operadores e f-strings.
- Estruturas de dados: `list`, `tuple`, `dict`, `set` e quando usar cada uma.
- Controle de fluxo: `if/elif/else`, `for`, `while`, `break`, `continue`.
- Funções: parâmetros, valores padrão, retorno, escopo e funções aninhadas.
- Módulos e pacotes: `import`, imports relativos, `if __name__ == "__main__"`.
- Tratamento de exceções: `try/except/else/finally`, `raise`, exceções customizadas.
- Comprehensions, iteradores e geradores (`yield`) — usados no streaming da IA.
- Tipagem: type hints (`str | None`, `list[dict[str, str]]`) e por que ajudam.
- Arquivos e bytes: `open`, `pathlib`, `io.BytesIO`, leitura binária de PDF.
- Context managers (`with`) e noções de classes/dataclasses.
- Ambientes virtuais (`venv`), `pip`, `requirements.txt` com versões fixadas.
- Variáveis de ambiente e arquivos `.env` com `python-dotenv`.

## 2. Streamlit **[essencial]**

- Modelo de execução: o script inteiro roda de novo a cada interação (rerun).
- Widgets: `file_uploader`, `text_area`, `button`, `selectbox`, `download_button`.
- Layout: `st.columns`, `st.sidebar`, `st.container`, `st.expander`, `st.divider`.
- Estado da sessão com `st.session_state` (resultado, histórico, cache, contadores).
- Cache: `@st.cache_data` vs `@st.cache_resource` e quando usar cada um.
- Streaming de respostas com `st.write_stream`.
- Secrets em produção (`st.secrets`) e fallback para `.env` no local.
- `st.set_page_config` e personalização com CSS/HTML (`unsafe_allow_html`).
- Mensagens de feedback: `st.error`, `st.warning`, `st.info`, `st.spinner`.
- Testes de interface com `streamlit.testing.v1.AppTest`.

## 3. Integração com LLM (Google Gemini) **[essencial]**

- Conceitos: prompt, tokens, contexto, temperatura, streaming, multimodalidade.
- Chave de API: criação no Google AI Studio, proteção e rotação.
- SDK `google-genai`: `Client`, `models.generate_content_stream`, `types.Part`.
- Enviar PDF como entrada multimodal (`types.Part.from_bytes` com `application/pdf`).
- Prompt engineering: instruções claras, formato de saída, delimitação da vaga.
- Mitigação de **prompt injection** (não obedecer instruções vindas do texto do usuário).
- Truncamento de entrada e limites de contexto.
- Erros comuns: `429 RESOURCE_EXHAUSTED`, `503 UNAVAILABLE`, timeout e retry.
- Fallback entre modelos e registro do modelo que respondeu.
- Cotas, limites de requisições e custo por token (free tier x pago).

## 4. PDF e validação de arquivos **[essencial]**

- Arquivo binário e "magic number" (`%PDF`) para validar extensão real.
- `pypdf`: `PdfReader`, `pages`, `extract_text()`, `is_encrypted`.
- Limites de tamanho e de páginas para evitar abuso e consumo excessivo.
- Diferença entre PDF com texto e PDF escaneado (imagem) — implicações para a IA.
- Tratamento de PDFs corrompidos/protegidos com mensagens amigáveis.

## 5. Segurança e privacidade **[essencial]**

- Nunca versionar segredos: `.env` e `.streamlit/secrets.toml` no `.gitignore`.
- Separar configuração local (`.env`) de produção (Secrets do Streamlit).
- Validar toda entrada do usuário (tipo, tamanho, formato, páginas).
- Limites de uso: por sessão, por IP/rede e global (proteção de cota/custo).
- Rate limiting e por que contagem por sessão é apenas "best-effort".
- LGPD/privacidade: transparência, minimização de dados e não retenção de arquivos.
- Não registrar conteúdo sensível em logs; sanitizar o que é exibido.

## 6. Testes e qualidade **[importante]**

- `pytest`: `assert`, `pytest.raises`, `pytest.mark.parametrize`, fixtures.
- `monkeypatch` para variáveis de ambiente e substituição de funções.
- Fakes/mocks: simular cliente da IA sem chamar a API de verdade.
- Testar regras puras (validação, prompt, limites) separadas da interface.
- Testar a UI com `AppTest` (clique, upload, session_state, mensagens).
- Cobertura de testes (`pytest-cov`) e definição de meta mínima.
- `ruff` para lint/estilo e `mypy` para tipagem estática.
- Configuração centralizada em `pyproject.toml`.

## 7. Git, GitHub e CI/CD **[importante]**

- `git status`, `diff`, `add`, `commit`, `push`, `branch`, `log`.
- Commits pequenos e mensagens claras; revisar antes de enviar.
- `.gitignore` e verificação de que segredos não foram commitados.
- GitHub Actions: workflow YAML, `on`, jobs, steps e matriz de versões.
- Cache de dependências (`actions/setup-python` com `cache: pip`).
- Dependabot para atualizações automáticas de dependências e actions.
- Deploy no Streamlit Community Cloud: repositório, branch, arquivo, Secrets, logs e reboot.

## 8. Arquitetura e boas práticas **[importante]**

- Separar interface (`app.py`) da lógica de negócio (`analisador.py`, `limites.py`).
- Funções pequenas, puras e testáveis; injetar dependências (cliente da IA como parâmetro).
- Tratamento de erros por camada, com mensagens distintas para o usuário e logs técnicos.
- Cache e estado: o que guardar, por quanto tempo e o que nunca persistir.
- Logging estruturado sem dados sensíveis.
- UX: feedback de progresso, mensagens acionáveis, responsividade e acessibilidade.
- Documentação: README com instalação, configuração, deploy, limites e limitações.

## 9. Frontend básico **[desejável]**

- HTML e CSS suficientes para personalizar o tema via `st.markdown`.
- Layout responsivo com `flex`, media queries e boas práticas de contraste.
- Limites do Streamlit e quando faria sentido migrar para outro framework.

## Roteiro sugerido de estudo

1. Python básico (tipos, funções, exceções, dict/list) + Git.
2. Ambiente virtual, `pip install`, `requirements.txt` e `.env`.
3. Testes com `pytest` em funções simples.
4. Streamlit: widgets, layout, `session_state` e rerun.
5. `pypdf`: abrir PDF, extrair texto, detectar criptografia.
6. Gemini: primeira chamada, depois streaming e PDF multimodal.
7. Prompt engineering + mitigação de prompt injection.
8. Cache, histórico, tratamento de erros e fallback de modelos.
9. Testes de UI com `AppTest`, `ruff`, `mypy` e cobertura.
10. CI com GitHub Actions e deploy no Streamlit Cloud.
11. Limites de uso, privacidade e monitoramento de custos.

## Exercícios práticos (mini entregas)

- CLI que recebe um PDF e imprime o texto extraído.
- App Streamlit que recebe dois números e mostra a soma (entender rerun/estado).
- Script que envia um texto ao Gemini e imprime a resposta em streaming.
- Unir PDF + prompt + streaming em uma única tela.
- Adicionar cache, histórico, testes, lint e CI ao projeto anterior.
- Adicionar limite de uso por sessão e mensagens de erro amigáveis.

## Referências oficiais

- Python: https://docs.python.org/3/tutorial/
- Streamlit: https://docs.streamlit.io/
- AppTest: https://docs.streamlit.io/develop/api-reference/app-testing
- Gemini API: https://ai.google.dev/gemini-api/docs
- Preços: https://ai.google.dev/pricing
- pypdf: https://pypdf.readthedocs.io/
- pytest: https://docs.pytest.org/
- ruff: https://docs.astral.sh/ruff/
- mypy: https://mypy.readthedocs.io/
- Git: https://git-scm.com/book/pt-br/v2
- GitHub Actions: https://docs.github.com/actions
