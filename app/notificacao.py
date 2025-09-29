from datetime import datetime

def notificar_console(change):
    """
    Imprime no console uma 'notificação' formatada sobre a alteração registrada.
    'change' deve ser um objeto do modelo AUD_ALTERACAO já preenchido.
    """
    acao = (change.ACAO or "").upper()

    nomes_tabela = {
        "AUD_FV": "Fórmula Visual",
        "AUD_SQL": "Consulta SQL",
        "AUD_REPORT": "Relatório"
    }
    tipo_obj = nomes_tabela.get(change.TABELA, change.TABELA)

    print("\n" + "="*70)
    print(f"NOTIFICAÇÃO — {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*70)
    print(f"Objeto: {tipo_obj}")
    print(f"Chave: {change.CHAVE}")
    print(f"Ação: {acao}")
    print(f"Usuário: {change.USUARIO or 'Sistema'}")
    print(f"Data/Hora: {change.DATA_HORA}")
    if change.DESCRICAO:
        print(f"Descrição: {change.DESCRICAO}")
    print("-"*70)

    if acao == "CREATE":
        print("Valor Novo:")
        print(change.VALOR_NOVO or "(vazio)")
    elif acao == "UPDATE":
        print("Valor Anterior:")
        print(change.VALOR_ANTERIOR or "(vazio)")
        print("\nValor Novo:")
        print(change.VALOR_NOVO or "(vazio)")
    elif acao == "DELETE":
        print("Registro Excluído (anterior):")
        print(change.VALOR_ANTERIOR or "(vazio)")
    else:
        if change.VALOR_ANTERIOR:
            print("Valor Anterior:")
            print(change.VALOR_ANTERIOR)
        if change.VALOR_NOVO:
            print("\nValor Novo:")
            print(change.VALOR_NOVO)

    print("="*70 + "\n")


# Opcional: teste rápido se rodar diretamente este arquivo
if __name__ == "__main__":
    # Mock simples de um objeto com os mesmos atributos de AUD_ALTERACAO
    class _Fake:
        ID_AUD = 999
        TABELA = "AUD_SQL"
        CHAVE = "1|2202"
        ACAO = "UPDATE"
        USUARIO = "TESTE_USER"
        DATA_HORA = datetime.now()
        DESCRICAO = "Alteração de exemplo"
        VALOR_ANTERIOR = '{"CONSULTA": "SELECT * FROM FUNC"}'
        VALOR_NOVO = '{"CONSULTA": "SELECT * FROM FUNC WHERE ATIVO=1"}'

    notificar_console(_Fake())