# Relatório Diário de Performance (com IA)

Automação que gera e envia, todo dia, um briefing de performance de mídia paga em português — sem precisar abrir dashboard. Calcula métricas, detecta quedas/altas relevantes por regra automática e usa IA (Gemini, com fallback Groq) pra transformar os números num resumo em linguagem natural.

Exemplo de saída real: [`exemplo_relatorio.html`](exemplo_relatorio.html) (baixe e abra no navegador pra ver o layout do e-mail gerado).

## Por que existe

Serviço de automação pra agências e e-commerces: em vez do cliente entrar num dashboard todo dia, ele recebe por e-mail um resumo pronto — com alerta automático quando algum canal foge do padrão. Complementa o [dashboard-performance-ads](https://github.com/psmktdigital1-ai/dashboard-performance-ads) (mesmo formato de dados) para quem quer automação de ponta a ponta: dashboard pra explorar, relatório pra ser avisado.

## Como funciona

1. **`dados.py`** — carrega os dados (por padrão, gera dados sintéticos; troque por CSV real, planilha ou API da plataforma de mídia)
2. **`metricas.py`** — compara o último dia com a média dos 7 dias anteriores, por canal, e aplica regras simples pra detectar alertas (ROAS caiu, CPA subiu, canal investiu e não converteu)
3. **`resumo_ia.py`** — manda os números pra um LLM (Gemini, fallback Groq) escrever um briefing curto em português; sem nenhuma API key configurada, cai num resumo gerado por template (sem IA) — o projeto roda de qualquer jeito
4. **`relatorio.py`** — monta o HTML final, pronto pra e-mail
5. **`enviar_email.py`** — envia por SMTP; sem SMTP configurado, salva o HTML em `saida/` em vez de falhar
6. **`main.py`** — orquestra os passos acima
7. **`.github/workflows/relatorio_diario.yml`** — roda tudo automaticamente todo dia às 8h (horário de Brasília) via GitHub Actions

## Como rodar

```bash
pip install -r requirements.txt
python3 main.py
```

Sem nenhuma variável de ambiente configurada, gera dados de exemplo, calcula métricas, escreve o resumo com um template (sem IA) e salva o relatório em `saida/`. Dá pra abrir o HTML gerado direto no navegador.

### Ativar IA no resumo

```bash
export GEMINI_API_KEY="sua-chave"     # ou GROQ_API_KEY como alternativa
python3 main.py
```

### Ativar envio por e-mail de verdade

```bash
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="seu-email@gmail.com"
export SMTP_PASS="sua-senha-de-app"
export EMAIL_DESTINO="cliente@empresa.com"
python3 main.py
```

### Automatizar no GitHub Actions

Configure os mesmos nomes de variável acima como *Secrets* do repositório (Settings → Secrets and variables → Actions) e o workflow em `.github/workflows/relatorio_diario.yml` roda sozinho, todo dia — sem precisar de servidor próprio ligado.

## Usar com dados reais

Troque a chamada em `main.py`:

```python
# de:
df = carregar_dados()
# para:
from dados import carregar_de_csv
df = carregar_de_csv("meus_dados.csv")
```

O CSV precisa das colunas `Data, Canal, Campanha, Investimento, Impressões, Cliques, Conversões, Receita` — o mesmo formato usado no dashboard-performance-ads.

## Stack

Python, Pandas, Google Generative AI (Gemini) com fallback Groq, GitHub Actions (agendamento).

## Status

Funcional e testado de ponta a ponta localmente: geração de dados, cálculo de métricas e alertas, resumo (modo template e caminho de IA), montagem de HTML e o fallback de salvar em disco quando SMTP não está configurado. O workflow do GitHub Actions ainda não rodou em produção — a lógica YAML foi validada, mas o agendamento real só é confirmado depois de configurar os secrets e deixar rodar.
