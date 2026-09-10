from datetime import date, timedelta
from collections import defaultdict
import csv
import html


# ============================================================
# CONFIGURAÇÕES
# ============================================================

COLABORADORES = [
    "Nome_do_colaborador", #Preencher com os nomes dos colaboradores no lugar de Nome_do_colaborador
    "Nome_do_colaborador",
    "Nome_do_colaborador",
]

DATA_INICIO = date(2026, 1, 1) #aqui é a configuração de colocar a data inicial
DATA_FIM = date(2026, 12, 31) #aqui é a configuração da data final

ARQUIVO_CSV = "escala_2026.csv"
ARQUIVO_HTML = "index.html"


DIAS_SEMANA = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo",
}


MESES = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}


# ============================================================
# VALIDAÇÕES
# ============================================================

def validar_colaboradores(colaboradores):
    """
    A lógica atual da escala foi criada especificamente
    para 3 colaboradores.
    """

    if len(colaboradores) != 3:
        raise ValueError(
            "A escala precisa ter exatamente 3 colaboradores."
        )

    if len(set(colaboradores)) != 3:
        raise ValueError(
            "Os nomes dos colaboradores não podem estar repetidos."
        )


# ============================================================
# GERADOR DA ESCALA
# ============================================================

def gerar_escala(data_inicio, data_fim, colaboradores=None):
    if colaboradores is None:
        colaboradores = COLABORADORES

    validar_colaboradores(colaboradores)

    if data_inicio > data_fim:
        raise ValueError(
            "A data inicial não pode ser maior que a data final."
        )

    escala = []

    estatisticas = {
        pessoa: {
            "entregas": 0,
            "compras": 0,
            "sextas": 0,
            "sabados": 0,
            "total": 0,
        }
        for pessoa in colaboradores
    }

    # Descobre a segunda-feira da semana da data inicial.
    #
    # Isso torna o gerador mais preparado caso no futuro
    # você escolha outro período que não comece numa segunda.
    inicio_semana = (
        data_inicio
        - timedelta(days=data_inicio.weekday())
    )

    numero_semana = 0
    semana_atual = inicio_semana

    while semana_atual <= data_fim:

        # ----------------------------------------------------
        # ROTAÇÃO DOS 3 COLABORADORES (nomes de exemplo) (obs: os reis do minecraft ai)
        # ----------------------------------------------------
        #
        # Semana 1:
        # A = Gilverson
        # B = Elly
        # C = Erick
        #
        # Semana 2:
        # A = Elly
        # B = Erick
        # C = Gilverson
        #
        # Semana 3:
        # A = Erick
        # B = Gilverson
        # C = Elly
        #
        # Semana 4:
        # volta ao começo
        # ----------------------------------------------------

        pessoa_a = colaboradores[numero_semana % 3]
        pessoa_b = colaboradores[(numero_semana + 1) % 3]
        pessoa_c = colaboradores[(numero_semana + 2) % 3]

        # ----------------------------------------------------
        # REGRA OFICIAL DA SEMANA
        # ----------------------------------------------------
        #
        # Segunda = A -> Entrega
        # Terça   = C -> Compras
        # Quarta  = B -> Entrega
        # Sexta   = C -> Entrega
        # Sábado  = A + B -> Presencial
        #
        # A pessoa da sexta:
        # - também faz a compra de terça
        # - não trabalha sábado
        # ----------------------------------------------------

        atividades_semana = [
            {
                "data": semana_atual,
                "atividade": "Entrega",
                "pessoas": [pessoa_a],
            },
            {
                "data": semana_atual + timedelta(days=1),
                "atividade": "Compras",
                "pessoas": [pessoa_c],
            },
            {
                "data": semana_atual + timedelta(days=2),
                "atividade": "Entrega",
                "pessoas": [pessoa_b],
            },
            {
                "data": semana_atual + timedelta(days=4),
                "atividade": "Entrega",
                "pessoas": [pessoa_c],
            },
            {
                "data": semana_atual + timedelta(days=5),
                "atividade": "Presencial",
                "pessoas": [pessoa_a, pessoa_b],
            },
        ]

        for atividade in atividades_semana:

            data_atividade = atividade["data"]

            # Não adiciona datas fora do período escolhido.
            if not (data_inicio <= data_atividade <= data_fim):
                continue

            registro = {
                "data": data_atividade,
                "dia": DIAS_SEMANA[data_atividade.weekday()],
                "atividade": atividade["atividade"],
                "pessoas": atividade["pessoas"],
                "semana": numero_semana + 1,
            }

            escala.append(registro)

            # ------------------------------------------------
            # ESTATÍSTICAS
            # ------------------------------------------------

            for pessoa in atividade["pessoas"]:

                if atividade["atividade"] == "Entrega":
                    estatisticas[pessoa]["entregas"] += 1

                    if data_atividade.weekday() == 4:
                        estatisticas[pessoa]["sextas"] += 1

                elif atividade["atividade"] == "Compras":
                    estatisticas[pessoa]["compras"] += 1

                elif atividade["atividade"] == "Presencial":
                    estatisticas[pessoa]["sabados"] += 1

                estatisticas[pessoa]["total"] += 1

        numero_semana += 1
        semana_atual += timedelta(days=7)

    escala.sort(key=lambda item: item["data"])

    return escala, estatisticas


# ============================================================
# MOSTRAR ESCALA NO TERMINAL
# ============================================================

def mostrar_escala(escala):
    print()
    print("=" * 65)
    print("ESCALA EMPADINHAS BARNABÉ")
    print("=" * 65)

    semana_anterior = None

    for registro in escala:

        if registro["semana"] != semana_anterior:
            print()
            print(
                f"---------------- SEMANA "
                f"{registro['semana']:02d} ----------------"
            )

            semana_anterior = registro["semana"]

        data_formatada = registro["data"].strftime("%d/%m/%Y")

        pessoas = " + ".join(registro["pessoas"])

        print(
            f"{data_formatada} | "
            f"{registro['dia']:<13} | "
            f"{registro['atividade']:<10} | "
            f"{pessoas}"
        )

    print()


# ============================================================
# MOSTRAR ESTATÍSTICAS
# ============================================================

def mostrar_estatisticas(estatisticas):
    print()
    print("=" * 65)
    print("ESTATÍSTICAS")
    print("=" * 65)

    for pessoa, dados in estatisticas.items():

        print()
        print(pessoa)

        print(
            f"  Entregas:              "
            f"{dados['entregas']}"
        )

        print(
            f"  Compras:               "
            f"{dados['compras']}"
        )

        print(
            f"  Entregas de sexta:     "
            f"{dados['sextas']}"
        )

        print(
            f"  Sábados presenciais:   "
            f"{dados['sabados']}"
        )

        print(
            f"  Total de participações:"
            f" {dados['total']}"
        )

    print()


# ============================================================
# SALVAR CSV
# ============================================================

def salvar_csv(escala, nome_arquivo):
    with open(
        nome_arquivo,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        escritor = csv.writer(
            arquivo,
            delimiter=";"
        )

        escritor.writerow([
            "Data",
            "Dia",
            "Atividade",
            "Colaboradores",
        ])

        for registro in escala:

            escritor.writerow([
                registro["data"].strftime("%d/%m/%Y"),
                registro["dia"],
                registro["atividade"],
                " + ".join(registro["pessoas"]),
            ])


# ============================================================
# SALVAR HTML
# ============================================================

def salvar_html(escala, nome_arquivo):

    # Separa os registros por mês.
    registros_por_mes = defaultdict(list)

    for registro in escala:
        chave_mes = (
            registro["data"].year,
            registro["data"].month,
        )

        registros_por_mes[chave_mes].append(registro)

    partes_html = []

    partes_html.append(
        """<!DOCTYPE html>
<html lang="pt-BR">

<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <meta
        name="theme-color"
        content="#063b79"
    >

    <title>Escala 2026 | Empadinhas Barnabé</title>

    <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family:
                Arial,
                Helvetica,
                sans-serif;

            background-color: #f5c928;
            background-image: url("bg_pattern.png");
            background-repeat: repeat;
            background-size: 420px auto;

            color: #152033;

            min-height: 100vh;
        }

        .cabecalho {
            background: #063b79;
            color: white;

            padding: 28px 20px;

            box-shadow:
                0 4px 15px
                rgba(0, 0, 0, 0.18);
        }

        .cabecalho-conteudo {
            max-width: 1100px;
            margin: auto;

            display: flex;
            align-items: center;
            gap: 24px;
        }

        .logo {
            width: 120px;
            max-height: 100px;

            object-fit: contain;
        }

        .titulo-area h1 {
            font-size: 34px;
            margin-bottom: 6px;
        }

        .titulo-area p {
            color: #e9f1ff;
            font-size: 15px;
        }

        .conteudo {
            width: calc(100% - 32px);
            max-width: 1100px;

            margin: 28px auto 50px;
        }

        .aviso {
            background: white;

            padding: 18px 20px;

            border-left: 6px solid #063b79;
            border-radius: 12px;

            margin-bottom: 25px;

            line-height: 1.55;

            box-shadow:
                0 4px 14px
                rgba(0, 0, 0, 0.12);
        }

        .mes {
            background: white;

            border-radius: 15px;

            margin-bottom: 25px;

            overflow: hidden;

            box-shadow:
                0 5px 18px
                rgba(0, 0, 0, 0.14);
        }

        .titulo-mes {
            background: #063b79;
            color: white;

            padding: 15px 20px;

            font-size: 21px;
            font-weight: bold;
        }

        .tabela-container {
            width: 100%;
            overflow-x: auto;
        }

        table {
            width: 100%;

            border-collapse: collapse;

            min-width: 650px;
        }

        th {
            background: #eef3f8;

            color: #063b79;

            text-align: left;

            padding: 14px 16px;

            font-size: 13px;

            text-transform: uppercase;

            letter-spacing: 0.5px;
        }

        td {
            padding: 15px 16px;

            border-top: 1px solid #e9edf2;

            vertical-align: middle;
        }

        tbody tr:hover {
            background: #f7f9fc;
        }

        .linha-sabado {
            background: #fff7cc;
        }

        .linha-sabado:hover {
            background: #fff0a8;
        }

        .data {
            font-weight: bold;
            white-space: nowrap;
        }

        .pessoas {
            font-weight: bold;
        }

        .etiqueta {
            display: inline-block;

            padding: 6px 11px;

            border-radius: 30px;

            font-size: 12px;

            font-weight: bold;

            white-space: nowrap;
        }

        .entrega {
            background: #dceaff;
            color: #064b96;
        }

        .compras {
            background: #fff0a8;
            color: #785900;
        }

        .presencial {
            background: #dff4e4;
            color: #276338;
        }

        .rodape {
            text-align: center;

            padding: 22px;

            color: #17375e;

            font-size: 13px;

            font-weight: bold;
        }

        /* ================================================
           CELULAR
           ================================================ */

        @media (max-width: 680px) {

            .cabecalho {
                padding: 22px 16px;
            }

            .cabecalho-conteudo {
                flex-direction: column;

                text-align: center;

                gap: 12px;
            }

            .logo {
                width: 105px;
            }

            .titulo-area h1 {
                font-size: 28px;
            }

            .titulo-area p {
                line-height: 1.4;
            }

            .conteudo {
                width: calc(100% - 20px);

                margin-top: 18px;
            }

            .aviso {
                font-size: 14px;

                padding: 16px;

                border-left-width: 5px;
            }

            .mes {
                border-radius: 12px;
            }

            .titulo-mes {
                font-size: 19px;

                padding: 14px 16px;
            }

            .tabela-container {
                overflow: visible;
            }

            table {
                min-width: 0;
            }

            thead {
                display: none;
            }

            tbody,
            tr,
            td {
                display: block;
                width: 100%;
            }

            tbody tr {
                padding: 13px 15px;

                border-bottom:
                    1px solid #e3e8ee;
            }

            tbody tr:last-child {
                border-bottom: none;
            }

            td {
                display: flex;

                justify-content: space-between;
                align-items: center;

                gap: 14px;

                padding: 6px 0;

                border: none;

                text-align: right;
            }

            td::before {
                content: attr(data-label);

                color: #687386;

                font-size: 11px;

                font-weight: bold;

                text-transform: uppercase;

                text-align: left;
            }

            .pessoas {
                font-size: 15px;
            }
        }

    </style>
</head>

<body>

<header class="cabecalho">

    <div class="cabecalho-conteudo">

        <img
            src="logo.png"
            alt="Empadinhas Barnabé"
            class="logo"
        >

        <div class="titulo-area">

            <h1>Escala 2026</h1>

            <p>
                Empadinhas Barnabé •
                Entregas, Compras e Sábados
            </p>

        </div>

    </div>

</header>


<main class="conteudo">

    <div class="aviso">

        <strong>Aviso:</strong>

        Cada colaborador realiza uma entrega por semana.
        A pessoa da sexta-feira também fica responsável
        pelas compras de terça-feira e folga no sábado.

    </div>
"""
    )

    for (ano, mes), registros in registros_por_mes.items():

        nome_mes = MESES[mes]

        partes_html.append(
            f"""
<section class="mes">

    <div class="titulo-mes">
        {nome_mes} de {ano}
    </div>

    <div class="tabela-container">

        <table>

            <thead>

                <tr>
                    <th>Data</th>
                    <th>Dia</th>
                    <th>Atividade</th>
                    <th>Colaborador(es)</th>
                </tr>

            </thead>

            <tbody>
"""
        )

        for registro in registros:

            data_formatada = (
                registro["data"].strftime("%d/%m/%Y")
            )

            dia = html.escape(registro["dia"])

            atividade = html.escape(
                registro["atividade"]
            )

            pessoas = html.escape(
                " + ".join(registro["pessoas"])
            )

            if registro["atividade"] == "Entrega":
                classe_etiqueta = "entrega"

            elif registro["atividade"] == "Compras":
                classe_etiqueta = "compras"

            else:
                classe_etiqueta = "presencial"

            classe_linha = ""

            if registro["data"].weekday() == 5:
                classe_linha = "linha-sabado"

            partes_html.append(
                f"""
<tr class="{classe_linha}">

    <td
        class="data"
        data-label="Data"
    >
        {data_formatada}
    </td>

    <td data-label="Dia">
        {dia}
    </td>

    <td data-label="Atividade">

        <span
            class="etiqueta {classe_etiqueta}"
        >
            {atividade}
        </span>

    </td>

    <td
        class="pessoas"
        data-label="Colaborador(es)"
    >
        {pessoas}
    </td>

</tr>
"""
            )

        partes_html.append(
            """
            </tbody>

        </table>

    </div>

</section>
"""
        )

    partes_html.append(
        """
</main>


<footer class="rodape">
    Empadinhas Barnabé • Escala de colaboradores
</footer>


</body>
</html>
"""
    )

    conteudo_html = "".join(partes_html)

    with open(
        nome_arquivo,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(conteudo_html)


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

if __name__ == "__main__":

    escala, estatisticas = gerar_escala(
        DATA_INICIO,
        DATA_FIM,
    )

    mostrar_escala(escala)

    mostrar_estatisticas(estatisticas)

    salvar_csv(
        escala,
        ARQUIVO_CSV,
    )

    salvar_html(
        escala,
        ARQUIVO_HTML,
    )

    print(
        f"Arquivo CSV gerado com sucesso: "
        f"{ARQUIVO_CSV}"
    )

    print(
        f"Arquivo HTML gerado com sucesso: "
        f"{ARQUIVO_HTML}"
    )
