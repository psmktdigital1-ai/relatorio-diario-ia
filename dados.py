"""
Camada de dados do relatório diário.

Por padrão gera dados sintéticos (mesmo formato usado no dashboard-performance-ads,
pra manter os dois projetos compatíveis). Pra usar dados reais, troque a função
`carregar_dados()` por uma leitura de CSV, planilha do Google ou API da plataforma de mídia —
a única exigência é devolver um DataFrame com estas colunas:

Data, Canal, Campanha, Investimento, Impressões, Cliques, Conversões, Receita
"""
import pandas as pd
import numpy as np

COLUNAS = ["Data", "Canal", "Campanha", "Investimento", "Impressões", "Cliques", "Conversões", "Receita"]

CANAIS = {
    "Google Ads": {"campanhas": ["Pesquisa - Marca", "Pesquisa - Genérico", "Performance Max"], "cpc_base": 1.8, "ctr_base": 0.045},
    "Meta Ads":   {"campanhas": ["Prospecção - Lookalike", "Remarketing - Carrinho", "Catálogo - Dinâmico"], "cpc_base": 1.1, "ctr_base": 0.018},
    "Amazon Ads": {"campanhas": ["Sponsored Products", "Sponsored Brands", "Sponsored Display"], "cpc_base": 1.4, "ctr_base": 0.032},
}


def carregar_dados(dias: int = 15, seed: int = None) -> pd.DataFrame:
    """Gera `dias` dias de dados sintéticos (hoje incluso).
    seed=None -> dados variam a cada execução (simulando um dia novo de verdade);
    passe um seed fixo pra reproduzir o mesmo cenário em testes."""
    rng = np.random.default_rng(seed)
    dias_periodo = pd.date_range(end=pd.Timestamp.today().normalize(), periods=dias, freq="D")

    linhas = []
    for canal, cfg in CANAIS.items():
        for campanha in cfg["campanhas"]:
            for dia in dias_periodo:
                fator_fds = 0.75 if dia.weekday() >= 5 else 1.0
                fator_ruido = max(0.3, rng.normal(1, 0.18))
                investimento = round(rng.uniform(80, 420) * fator_fds * fator_ruido, 2)
                cpc = max(0.25, rng.normal(cfg["cpc_base"], cfg["cpc_base"] * 0.15))
                cliques = max(0, int(investimento / cpc))
                ctr = max(0.003, rng.normal(cfg["ctr_base"], cfg["ctr_base"] * 0.2))
                impressoes = int(cliques / ctr) if ctr > 0 else 0
                taxa_conv = rng.uniform(0.015, 0.06)
                conversoes = int(cliques * taxa_conv)
                ticket_medio = rng.uniform(90, 340)
                receita = max(0, round(conversoes * ticket_medio * rng.normal(1, 0.25), 2))
                linhas.append({
                    "Data": dia.strftime("%Y-%m-%d"), "Canal": canal, "Campanha": campanha,
                    "Investimento": investimento, "Impressões": impressoes, "Cliques": cliques,
                    "Conversões": conversoes, "Receita": receita,
                })

    df = pd.DataFrame(linhas)
    df["Data"] = pd.to_datetime(df["Data"])
    return df


def carregar_de_csv(caminho: str) -> pd.DataFrame:
    """Lê um CSV real no mesmo formato do dashboard-performance-ads."""
    df = pd.read_csv(caminho)
    faltando = [c for c in COLUNAS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas faltando no CSV: {', '.join(faltando)}")
    df["Data"] = pd.to_datetime(df["Data"])
    for col in ["Investimento", "Impressões", "Cliques", "Conversões", "Receita"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
