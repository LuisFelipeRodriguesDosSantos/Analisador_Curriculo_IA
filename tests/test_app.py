from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

import analisador

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(autouse=True)
def _ambiente(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("GEMINI_API_KEY", "chave-de-teste")
    st.cache_resource.clear()
    yield


def _stream_falso(
    client: Any,
    pdf_bytes: bytes,
    prompt: str,
    modelos: tuple[str, ...],
    estado: dict[str, str],
) -> Iterator[str]:
    estado["modelo"] = "modelo-teste"
    yield "Análise "
    yield "completa."


def _criar_app(
    monkeypatch: pytest.MonkeyPatch,
    chamadas: list[str],
) -> AppTest:
    def gerar(*args: Any, **kwargs: Any) -> Iterator[str]:
        chamadas.append("chamada")
        return _stream_falso(*args, **kwargs)

    monkeypatch.setattr(analisador, "validar_pdf", lambda _: True)
    monkeypatch.setattr(analisador, "gerar_analise_stream", gerar)
    return AppTest.from_file(APP, default_timeout=30).run()


def _preencher(at: AppTest, vaga: str = "Vaga de estágio em dados") -> None:
    at.file_uploader[0].set_value(
        ("curriculo.pdf", b"%PDF-1.4 fake", "application/pdf")
    )
    at.text_area[0].set_value(vaga)


def test_estado_inicial_mostra_limites(monkeypatch: pytest.MonkeyPatch) -> None:
    at = _criar_app(monkeypatch, [])

    assert not at.exception
    captions = " ".join(c.value for c in at.sidebar.caption)
    assert "0/5" in captions
    assert "restantes hoje" in captions


def test_fluxo_completo_e_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas: list[str] = []
    at = _criar_app(monkeypatch, chamadas)

    _preencher(at)
    at.button[0].click().run()

    assert not at.exception
    assert len(chamadas) == 1
    assert at.session_state["resultado"]["texto"] == "Análise completa."
    assert at.session_state["resultado"]["modelo"] == "modelo-teste"
    assert at.session_state["analises_realizadas"] == 1
    assert len(at.session_state["historico"]) == 1
    assert len(at.session_state["cache_analises"]) == 1

    at.button[0].click().run()

    assert len(chamadas) == 1
    assert at.session_state["analises_realizadas"] == 1
    assert len(at.session_state["cache_analises"]) == 1


def test_botao_sem_entradas_mostra_aviso(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas: list[str] = []
    at = _criar_app(monkeypatch, chamadas)

    at.button[0].click().run()

    assert chamadas == []
    assert any("envie o PDF" in aviso.value for aviso in at.warning)


def test_pdf_grande_demais(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas: list[str] = []
    at = _criar_app(monkeypatch, chamadas)
    monkeypatch.setattr(analisador, "TAMANHO_MAX_BYTES", 4)

    _preencher(at)
    at.button[0].click().run()

    assert chamadas == []
    assert any("deve ter no máximo" in erro.value for erro in at.error)


def test_pdf_invalido_mostra_erro(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas: list[str] = []
    at = _criar_app(monkeypatch, chamadas)

    def validar_invalido(_: bytes) -> bool:
        raise ValueError("O arquivo enviado não é um PDF válido.")

    monkeypatch.setattr(analisador, "validar_pdf", validar_invalido)

    _preencher(at)
    at.button[0].click().run()

    assert chamadas == []
    assert any("não é um PDF válido" in erro.value for erro in at.error)


def test_limite_por_sessao_bloqueia(monkeypatch: pytest.MonkeyPatch) -> None:
    chamadas: list[str] = []
    at = _criar_app(monkeypatch, chamadas)

    at.session_state["analises_realizadas"] = 5
    at.run()

    _preencher(at)
    at.button[0].click().run()

    assert chamadas == []
    assert at.session_state["analises_realizadas"] == 5
    assert any("Limite de 5 análises por sessão" in erro.value for erro in at.error)
