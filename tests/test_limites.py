import limites


def test_consumir_permite_dentro_dos_limites() -> None:
    controle = limites.ControleDeUso(
        max_por_sessao=2, max_por_ip=2, max_diarias=5
    )

    assert controle.consumir("1.1.1.1", 0, agora=0) is None
    assert controle.restantes_diarias(agora=0) == 4


def test_limite_por_sessao_bloqueia_sem_consumir_cota() -> None:
    controle = limites.ControleDeUso(
        max_por_sessao=1, max_por_ip=5, max_diarias=5
    )

    mensagem = controle.consumir("1.1.1.1", 1, agora=0)

    assert mensagem is not None
    assert "sessão" in mensagem
    assert controle.restantes_diarias(agora=0) == 5


def test_limite_por_ip_entre_sessoes() -> None:
    controle = limites.ControleDeUso(
        max_por_sessao=5, max_por_ip=1, max_diarias=5
    )

    assert controle.consumir("1.1.1.1", 0, agora=0) is None

    mensagem = controle.consumir("1.1.1.1", 0, agora=0)

    assert mensagem is not None
    assert "rede" in mensagem
    assert controle.consumir("2.2.2.2", 0, agora=0) is None


def test_sem_ip_nao_aplica_limite_por_rede() -> None:
    controle = limites.ControleDeUso(
        max_por_sessao=5, max_por_ip=1, max_diarias=5
    )

    assert controle.consumir(None, 0, agora=0) is None
    assert controle.consumir(None, 0, agora=0) is None


def test_limite_diario_global() -> None:
    controle = limites.ControleDeUso(
        max_por_sessao=5, max_por_ip=5, max_diarias=2
    )

    assert controle.consumir("1.1.1.1", 0, agora=0) is None
    assert controle.consumir("2.2.2.2", 0, agora=0) is None

    mensagem = controle.consumir("3.3.3.3", 0, agora=0)

    assert mensagem is not None
    assert "24 horas" in mensagem
    assert controle.restantes_diarias(agora=0) == 0


def test_janela_expira() -> None:
    controle = limites.ControleDeUso(
        max_por_sessao=5, max_por_ip=1, max_diarias=1, janela_segundos=10
    )

    assert controle.consumir("1.1.1.1", 0, agora=0) is None
    assert controle.consumir("1.1.1.1", 0, agora=5) is not None
    assert controle.consumir("1.1.1.1", 0, agora=11) is None


def test_restantes_na_sessao() -> None:
    assert limites.restantes_na_sessao(2, 5) == 3
    assert limites.restantes_na_sessao(5, 5) == 0
    assert limites.restantes_na_sessao(9, 5) == 0
