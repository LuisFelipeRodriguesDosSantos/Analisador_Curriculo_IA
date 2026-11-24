import threading
import time
from collections import defaultdict, deque

JANELA_SEGUNDOS = 24 * 60 * 60
MAX_ANALISES_POR_SESSAO = 5
MAX_ANALISES_POR_IP = 20
MAX_ANALISES_DIARIAS = 100

MENSAGEM_LIMITE_SESSAO = (
    "Limite de {maximo} análises por sessão atingido. "
    "Aguarde alguns minutos antes de tentar novamente."
)
MENSAGEM_LIMITE_IP = (
    "Limite de {maximo} análises nas últimas 24 horas para esta rede atingido. "
    "Tente novamente mais tarde."
)
MENSAGEM_LIMITE_DIARIO = (
    "O limite de {maximo} análises da aplicação nas últimas 24 horas foi "
    "atingido. Tente novamente mais tarde."
)


class ControleDeUso:
    """Aplica limites de uso em uma janela móvel de tempo."""

    def __init__(
        self,
        *,
        max_por_sessao: int = MAX_ANALISES_POR_SESSAO,
        max_por_ip: int = MAX_ANALISES_POR_IP,
        max_diarias: int = MAX_ANALISES_DIARIAS,
        janela_segundos: float = JANELA_SEGUNDOS,
    ) -> None:
        self.max_por_sessao = max_por_sessao
        self.max_por_ip = max_por_ip
        self.max_diarias = max_diarias
        self.janela_segundos = janela_segundos
        self._lock = threading.Lock()
        self._uso_por_ip: dict[str, deque[float]] = defaultdict(deque)
        self._uso_global: deque[float] = deque()

    def _descartar_antigos(self, registro: deque[float], agora: float) -> None:
        limite = agora - self.janela_segundos
        while registro and registro[0] <= limite:
            registro.popleft()

    def consumir(
        self,
        ip: str | None,
        analises_na_sessao: int,
        agora: float | None = None,
    ) -> str | None:
        """Registra uma análise ou retorna a mensagem do limite atingido."""
        momento = time.monotonic() if agora is None else agora

        with self._lock:
            if analises_na_sessao >= self.max_por_sessao:
                return MENSAGEM_LIMITE_SESSAO.format(maximo=self.max_por_sessao)

            self._descartar_antigos(self._uso_global, momento)
            if len(self._uso_global) >= self.max_diarias:
                return MENSAGEM_LIMITE_DIARIO.format(maximo=self.max_diarias)

            if ip is not None:
                registro_ip = self._uso_por_ip[ip]
                self._descartar_antigos(registro_ip, momento)
                if len(registro_ip) >= self.max_por_ip:
                    return MENSAGEM_LIMITE_IP.format(maximo=self.max_por_ip)

            self._uso_global.append(momento)
            if ip is not None:
                self._uso_por_ip[ip].append(momento)
            return None

    def restantes_diarias(self, agora: float | None = None) -> int:
        momento = time.monotonic() if agora is None else agora

        with self._lock:
            self._descartar_antigos(self._uso_global, momento)
            return max(0, self.max_diarias - len(self._uso_global))


def restantes_na_sessao(
    analises_realizadas: int,
    maximo: int = MAX_ANALISES_POR_SESSAO,
) -> int:
    return max(0, maximo - analises_realizadas)
