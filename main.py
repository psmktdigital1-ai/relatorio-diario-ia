"""
Orquestra o relatório diário: carrega dados -> calcula métricas -> gera resumo
com IA -> monta HTML -> envia por e-mail (ou salva localmente se e-mail não
estiver configurado).

Rodar manualmente: python3 main.py
Rodar automaticamente todo dia: ver .github/workflows/relatorio_diario.yml
"""
from dados import carregar_dados
from metricas import calcular_resumo
from resumo_ia import gerar_resumo
from relatorio import montar_html
from enviar_email import enviar_ou_salvar


def main():
    print("1/5 Carregando dados...")
    df = carregar_dados()

    print("2/5 Calculando métricas e alertas...")
    metricas = calcular_resumo(df)
    print(f"    Dia analisado: {metricas['dia_analisado'].strftime('%d/%m/%Y')}")
    print(f"    Alertas detectados: {len(metricas['alertas'])}")

    print("3/5 Gerando resumo (IA, com fallback automático)...")
    resumo_texto, motor = gerar_resumo(metricas)
    print(f"    Motor usado: {motor}")

    print("4/5 Montando relatório HTML...")
    html = montar_html(metricas, resumo_texto, motor)

    print("5/5 Enviando/salvando...")
    resultado = enviar_ou_salvar(html, assunto=f"Relatório de performance — {metricas['dia_analisado'].strftime('%d/%m/%Y')}")
    print(f"    {resultado}")


if __name__ == "__main__":
    main()
