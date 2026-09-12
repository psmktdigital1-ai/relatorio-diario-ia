"""
Transforma o dicionário de métricas (metricas.py) num resumo em português,
escrito por IA (Gemini, com fallback pra Groq — mesmo esquema usado no chatbot-ia).

Sem GEMINI_API_KEY nem GROQ_API_KEY configuradas, cai num resumo gerado por
template (sem IA) — assim o projeto roda e mostra resultado mesmo sem chave,
só que num nível de qualidade mais baixo que o modo com IA.
"""
import os
import json


def _formatar_moeda(v):
    return f"R$ {v:,.0f}".replace(",", ".")


def _montar_prompt(metricas: dict) -> str:
    total = metricas["total"]
    dia = metricas["dia_analisado"].strftime("%d/%m/%Y")

    linhas_canal = []
    for c in metricas["por_canal"]:
        var_roas = f"{c['var_roas']*100:+.0f}%" if c["var_roas"] is not None else "n/d"
        var_cpa = f"{c['var_cpa']*100:+.0f}%" if c["var_cpa"] is not None else "n/d"
        linhas_canal.append(
            f"- {c['canal']}: investimento {_formatar_moeda(c['investimento'])}, "
            f"receita {_formatar_moeda(c['receita'])}, ROAS {c['roas']:.2f}x (var. {var_roas}), "
            f"CPA {_formatar_moeda(c['cpa']) if c['cpa'] else 'n/d'} (var. {var_cpa}), "
            f"{c['conversoes']} conversões"
        )

    alertas_txt = "\n".join(f"- {a}" for a in metricas["alertas"]) if metricas["alertas"] else "- Nenhum alerta relevante hoje."

    return f"""Você é um analista de mídia paga escrevendo um briefing matinal curto para um gestor de e-commerce.
Data analisada: {dia}

RESUMO TOTAL DO DIA:
- Investimento: {_formatar_moeda(total['investimento'])}
- Receita: {_formatar_moeda(total['receita'])}
- ROAS: {total['roas']:.2f}x
- Conversões: {total['conversoes']}

POR CANAL:
{chr(10).join(linhas_canal)}

ALERTAS DETECTADOS (regras automáticas, comparando com a média dos últimos 7 dias):
{alertas_txt}

Escreva um briefing em português brasileiro, direto, sem enrolação, em no máximo 6 frases:
1. Comece com o resultado geral do dia (bom, neutro ou ruim, e por quê).
2. Destaque o canal com melhor e o com pior desempenho, se relevante.
3. Se houver alertas, explique o que provavelmente está acontecendo e sugira UMA ação concreta.
4. Não invente números que não foram passados acima. Não use bullet points — escreva em parágrafo corrido.
"""


def _resumo_gemini(prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash-preview-04-17")
    return model.generate_content(prompt).text.strip()


def _resumo_groq(prompt: str) -> str:
    import requests
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4, "max_tokens": 400,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _resumo_template(metricas: dict) -> str:
    """Fallback sem IA: um resumo gerado por regras, não por LLM."""
    total = metricas["total"]
    situacao = "positivo" if total["roas"] >= 3 else ("neutro" if total["roas"] >= 1.5 else "abaixo do esperado")
    partes = [
        f"Ontem o investimento total foi de {_formatar_moeda(total['investimento'])}, "
        f"gerando {_formatar_moeda(total['receita'])} em receita (ROAS de {total['roas']:.2f}x) — "
        f"um resultado {situacao}."
    ]
    if metricas["por_canal"]:
        melhor = max(metricas["por_canal"], key=lambda c: c["roas"])
        pior = min(metricas["por_canal"], key=lambda c: c["roas"])
        if melhor["canal"] != pior["canal"]:
            partes.append(
                f"{melhor['canal']} foi o canal com melhor retorno (ROAS {melhor['roas']:.2f}x), "
                f"enquanto {pior['canal']} teve o pior desempenho (ROAS {pior['roas']:.2f}x)."
            )
    if metricas["alertas"]:
        partes.append("Pontos de atenção: " + " ".join(metricas["alertas"]))
    else:
        partes.append("Nenhum alerta relevante — operação dentro do padrão dos últimos 7 dias.")
    return " ".join(partes)


def gerar_resumo(metricas: dict) -> tuple[str, str]:
    """Retorna (texto_resumo, motor_usado) — motor é 'gemini', 'groq' ou 'template'."""
    prompt = _montar_prompt(metricas)

    if os.getenv("GEMINI_API_KEY"):
        try:
            return _resumo_gemini(prompt), "gemini"
        except Exception:
            pass
    if os.getenv("GROQ_API_KEY"):
        try:
            return _resumo_groq(prompt), "groq"
        except Exception:
            pass
    return _resumo_template(metricas), "template"
