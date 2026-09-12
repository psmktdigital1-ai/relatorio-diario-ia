"""Monta o relatório final (HTML, pronto pra e-mail) a partir das métricas + resumo em texto."""


def _fmt_moeda(v):
    return f"R$ {v:,.0f}".replace(",", ".")


def _fmt_pct(v):
    if v is None:
        return "—"
    return f"{v*100:+.0f}%"


def montar_html(metricas: dict, resumo_texto: str, motor_ia: str) -> str:
    dia = metricas["dia_analisado"].strftime("%d/%m/%Y")
    total = metricas["total"]

    linhas_canal = ""
    for c in metricas["por_canal"]:
        cor_roas = "#16a34a" if (c["var_roas"] or 0) >= 0 else "#dc2626"
        linhas_canal += f"""
        <tr>
          <td style="padding:8px 10px;border-bottom:1px solid #eee">{c['canal']}</td>
          <td style="padding:8px 10px;border-bottom:1px solid #eee;text-align:right">{_fmt_moeda(c['investimento'])}</td>
          <td style="padding:8px 10px;border-bottom:1px solid #eee;text-align:right">{_fmt_moeda(c['receita'])}</td>
          <td style="padding:8px 10px;border-bottom:1px solid #eee;text-align:right;color:{cor_roas}">{c['roas']:.2f}x ({_fmt_pct(c['var_roas'])})</td>
          <td style="padding:8px 10px;border-bottom:1px solid #eee;text-align:right">{c['conversoes']}</td>
        </tr>"""

    alertas_html = ""
    if metricas["alertas"]:
        itens = "".join(f"<li style='margin-bottom:4px'>{a}</li>" for a in metricas["alertas"])
        alertas_html = f"""
        <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:14px 18px;margin:16px 0">
          <div style="font-weight:600;color:#991b1b;margin-bottom:6px">⚠️ Pontos de atenção</div>
          <ul style="margin:0;padding-left:18px;color:#7f1d1d;font-size:0.9rem">{itens}</ul>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:Arial,Helvetica,sans-serif;color:#18181b">
  <div style="max-width:640px;margin:0 auto;padding:24px 20px">
    <div style="background:#ffffff;border-radius:14px;padding:28px 26px;border:1px solid #e4e4e7">
      <div style="font-size:0.8rem;color:#71717a;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px">Relatório diário de performance</div>
      <div style="font-size:1.5rem;font-weight:700;margin-bottom:18px">{dia}</div>

      <div style="background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;padding:16px 18px;margin-bottom:18px;font-size:0.95rem;line-height:1.6">
        {resumo_texto}
      </div>

      {alertas_html}

      <table style="width:100%;border-collapse:collapse;font-size:0.88rem;margin-top:8px">
        <thead>
          <tr style="background:#f4f4f5">
            <th style="padding:8px 10px;text-align:left">Canal</th>
            <th style="padding:8px 10px;text-align:right">Investimento</th>
            <th style="padding:8px 10px;text-align:right">Receita</th>
            <th style="padding:8px 10px;text-align:right">ROAS (var.)</th>
            <th style="padding:8px 10px;text-align:right">Conversões</th>
          </tr>
        </thead>
        <tbody>{linhas_canal}
          <tr style="font-weight:700;background:#fafafa">
            <td style="padding:8px 10px">Total</td>
            <td style="padding:8px 10px;text-align:right">{_fmt_moeda(total['investimento'])}</td>
            <td style="padding:8px 10px;text-align:right">{_fmt_moeda(total['receita'])}</td>
            <td style="padding:8px 10px;text-align:right">{total['roas']:.2f}x ({_fmt_pct(total.get('var_roas'))})</td>
            <td style="padding:8px 10px;text-align:right">{total['conversoes']}</td>
          </tr>
        </tbody>
      </table>

      <div style="font-size:0.72rem;color:#a1a1aa;margin-top:20px">
        Gerado automaticamente · resumo escrito por {"IA (" + motor_ia + ")" if motor_ia != "template" else "template (sem IA configurada)"} · comparação vs. média dos últimos 7 dias
      </div>
    </div>
  </div>
</body>
</html>"""
