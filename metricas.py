"""
Calcula métricas do dia mais recente comparado com a média dos 7 dias anteriores
(baseline), por canal e no total. Também detecta alertas com regras simples de
variação percentual — sem IA, sem ML, só threshold. A IA (resumo_ia.py) entra
depois, pra transformar esses números em texto.
"""
import pandas as pd

# limites que disparam alerta (variação percentual vs. baseline)
LIMITE_QUEDA_ROAS = -0.15      # ROAS caiu mais de 15%
LIMITE_ALTA_CPA = 0.20         # CPA subiu mais de 20%
LIMITE_QUEDA_CONVERSOES = -0.30  # conversões caíram mais de 30%


def _agregar(df: pd.DataFrame) -> dict:
    investimento = df["Investimento"].sum()
    receita = df["Receita"].sum()
    conversoes = df["Conversões"].sum()
    cliques = df["Cliques"].sum()
    return {
        "investimento": investimento,
        "receita": receita,
        "conversoes": conversoes,
        "cliques": cliques,
        "roas": (receita / investimento) if investimento > 0 else 0.0,
        "cpa": (investimento / conversoes) if conversoes > 0 else None,
    }


def _variacao(atual, base):
    if base in (0, None) or atual is None:
        return None
    return (atual - base) / base


def calcular_resumo(df: pd.DataFrame) -> dict:
    """Retorna um dicionário com:
    - dia_analisado: data do último dia disponível nos dados
    - total: métricas do dia + variação vs baseline
    - por_canal: lista de métricas por canal + variação vs baseline
    - alertas: lista de strings descrevendo quedas/altas relevantes
    """
    dia_analisado = df["Data"].max()
    inicio_baseline = dia_analisado - pd.Timedelta(days=7)

    df_dia = df[df["Data"] == dia_analisado]
    df_baseline = df[(df["Data"] >= inicio_baseline) & (df["Data"] < dia_analisado)]

    total_dia = _agregar(df_dia)
    total_baseline = _agregar(df_baseline)
    n_dias_baseline = max(1, df_baseline["Data"].nunique())

    total = {
        **total_dia,
        "var_investimento": _variacao(total_dia["investimento"], total_baseline["investimento"] / n_dias_baseline),
        "var_receita": _variacao(total_dia["receita"], total_baseline["receita"] / n_dias_baseline),
        "var_roas": _variacao(total_dia["roas"], total_baseline["roas"]),
        "var_cpa": _variacao(total_dia["cpa"], total_baseline["cpa"]),
        "var_conversoes": _variacao(total_dia["conversoes"], total_baseline["conversoes"] / n_dias_baseline),
    }

    por_canal = []
    alertas = []
    for canal in sorted(df["Canal"].unique()):
        dia_c = _agregar(df_dia[df_dia["Canal"] == canal])
        base_c = _agregar(df_baseline[df_baseline["Canal"] == canal])

        media_investimento_base = base_c["investimento"] / n_dias_baseline
        media_conversoes_base = base_c["conversoes"] / n_dias_baseline

        linha = {
            "canal": canal,
            **dia_c,
            "var_roas": _variacao(dia_c["roas"], base_c["roas"]),
            "var_cpa": _variacao(dia_c["cpa"], base_c["cpa"]),
            "var_conversoes": _variacao(dia_c["conversoes"], media_conversoes_base),
        }
        por_canal.append(linha)

        if dia_c["investimento"] > 0 and linha["var_roas"] is not None and linha["var_roas"] <= LIMITE_QUEDA_ROAS:
            alertas.append(f"ROAS de {canal} caiu {abs(linha['var_roas']) * 100:.0f}% vs. média dos últimos 7 dias.")
        if linha["var_cpa"] is not None and linha["var_cpa"] >= LIMITE_ALTA_CPA:
            alertas.append(f"CPA de {canal} subiu {linha['var_cpa'] * 100:.0f}% vs. média dos últimos 7 dias.")
        if linha["var_conversoes"] is not None and linha["var_conversoes"] <= LIMITE_QUEDA_CONVERSOES and dia_c["investimento"] > 0:
            alertas.append(f"Conversões de {canal} caíram {abs(linha['var_conversoes']) * 100:.0f}% vs. média dos últimos 7 dias.")
        if dia_c["investimento"] > media_investimento_base * 0.3 and dia_c["conversoes"] == 0:
            alertas.append(f"{canal} investiu R$ {dia_c['investimento']:,.0f} ontem e não teve nenhuma conversão.")

    return {
        "dia_analisado": dia_analisado,
        "total": total,
        "por_canal": por_canal,
        "alertas": alertas,
    }
