import os
import dash
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import mysql.connector
from mysql.connector import Error
import pandas as pd
import plotly.express as px          # Gráficos interativos (barras, scatter, etc.)
import plotly.graph_objects as go    # Controle fino de layout e traces
from dotenv import load_dotenv
load_dotenv()

# --- NOVA FUNÇÃO DE AUTOMAÇÃO AUTOMÁTICA ---
# --- FUNÇÃO DE AUTOMAÇÃO AUTOMÁTICA COMPLETA ---
def init_db():
    """Liga-se como root para garantir que a base de dados, o utilizador, 
    as tabelas e os triggers do sistema existem."""
    root_password = os.getenv('DB_ROOT_PASSWORD', '')
    custom_user = os.getenv('DB_USER', 'root')
    custom_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'copa_do_mundo')

    try:
        # 1. Liga-se temporariamente como ROOT
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user='root',
            password=root_password
        )
        cursor = conn.cursor()

        # 2. Cria a base de dados se não existir
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name};")

        # 3. Configura o utilizador customizado (se não for o root)
        if custom_user != 'root':
            try:
                cursor.execute(f"CREATE USER '{custom_user}'@'localhost' IDENTIFIED BY '{custom_password}';")
            except mysql.connector.Error:
                # Se o utilizador já existir, apenas atualiza a senha
                cursor.execute(f"ALTER USER '{custom_user}'@'localhost' IDENTIFIED BY '{custom_password}';")
            
            # Garante permissões totais na base de dados do projeto
            cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{custom_user}'@'localhost';")
            cursor.execute("FLUSH PRIVILEGES;")

        # 4. Entra na base de dados para criar a estrutura de tabelas
        cursor.execute(f"USE {db_name};")

        # TABELA: Seleções
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS selecoes (
                id_selecao INT AUTO_INCREMENT PRIMARY KEY,
                nome_selecao VARCHAR(100) NOT NULL,
                continente VARCHAR(100) NOT NULL,
                tecnico VARCHAR(100) NOT NULL,
                titulos INT DEFAULT 0
            );
        """)

        # TABELA: Jogadores (depende de selecoes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jogadores (
                id_jogador INT AUTO_INCREMENT PRIMARY KEY,
                nome_jogador VARCHAR(60) NOT NULL,
                posicao VARCHAR(30) NOT NULL,
                numero_camisa INT NOT NULL,
                data_nascimento DATE NOT NULL,
                id_selecao INT NOT NULL,
                FOREIGN KEY (id_selecao) REFERENCES selecoes(id_selecao)
                    ON DELETE CASCADE ON UPDATE CASCADE
            );
        """)

        # TABELA: Estádios (Necessária para o JOIN do histórico de partidas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estadios (
                id_estadio INT AUTO_INCREMENT PRIMARY KEY,
                nome_estadio VARCHAR(100) NOT NULL
            );
        """)

        # Insere um estádio padrão (ID 1) para o formulário não falhar no início
        cursor.execute("""
            INSERT IGNORE INTO estadios (id_estadio, nome_estadio) 
            VALUES (1, 'Estádio Nacional de Demonstração');
        """)

        # TABELA: Árbitros (necessária antes de Partidas por causa da FK)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS arbitros (
                id_arbitro INT AUTO_INCREMENT PRIMARY KEY,
                nome_arbitro VARCHAR(50) NOT NULL,
                nacionalidade VARCHAR(30) NOT NULL,
                funcao ENUM('Principal', 'Assistente', 'VAR') NOT NULL
            );
        """)

        # Insere um árbitro padrão (ID 1, função Principal) para o formulário funcionar no início
        cursor.execute("""
            INSERT IGNORE INTO arbitros (id_arbitro, nome_arbitro, nacionalidade, funcao)
            VALUES (1, 'Árbitro Padrão', 'Brasil', 'Principal');
        """)

        # TABELA: Partidas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS partidas (
                id_partida INT AUTO_INCREMENT PRIMARY KEY,
                data_partida DATE NOT NULL,
                id_estadio INT NOT NULL,
                id_arbitro INT NOT NULL,
                id_selecao_1 INT NOT NULL,
                id_selecao_2 INT NOT NULL,
                quantidade_gols_selecao_1 INT DEFAULT 0,
                quantidade_gols_selecao_2 INT DEFAULT 0,
                vencedor INT NULL,
                FOREIGN KEY (id_estadio) REFERENCES estadios(id_estadio),
                FOREIGN KEY (id_arbitro) REFERENCES arbitros(id_arbitro),
                FOREIGN KEY (id_selecao_1) REFERENCES selecoes(id_selecao),
                FOREIGN KEY (id_selecao_2) REFERENCES selecoes(id_selecao)
            );
        """)

        # 5. Criação Automática do TRIGGER para definir o Vencedor
        cursor.execute("DROP TRIGGER IF EXISTS trg_definir_vencedor;")
        cursor.execute("""
            CREATE TRIGGER trg_definir_vencedor
            BEFORE INSERT ON partidas
            FOR EACH ROW
            BEGIN
                IF NEW.quantidade_gols_selecao_1 > NEW.quantidade_gols_selecao_2 THEN
                    SET NEW.vencedor = NEW.id_selecao_1;
                ELSEIF NEW.quantidade_gols_selecao_2 > NEW.quantidade_gols_selecao_1 THEN
                    SET NEW.vencedor = NEW.id_selecao_2;
                ELSE
                    SET NEW.vencedor = NULL; -- Empate
                END IF;
            END;
        """)

        # 6. Trigger: valida que apenas árbitros 'Principal' podem ser alocados
        cursor.execute("DROP TRIGGER IF EXISTS trg_valida_arbitro_principal;")
        cursor.execute("""
            CREATE TRIGGER trg_valida_arbitro_principal
            BEFORE INSERT ON partidas
            FOR EACH ROW
            BEGIN
                DECLARE v_funcao VARCHAR(30);
                SELECT funcao INTO v_funcao
                FROM arbitros
                WHERE id_arbitro = NEW.id_arbitro;
                IF v_funcao != 'Principal' THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Apenas árbitros com função Principal podem ser alocados na partida.';
                END IF;
            END;
        """)

        print(f"[OK] Estrutura completa de '{db_name}' verificada/criada com sucesso!")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"[AVISO] Erro na automacao da base de dados: {e}")

# Executa a configuração antes de iniciar o servidor Dash
init_db()

# Configurações Dinâmicas Continuam Iguais aqui para baixo
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'copa_do_mundo'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Carrega as variáveis do arquivo .env local (se ele existir)
load_dotenv()

# Configurações Dinâmicas (Lê do ambiente ou usa um padrão seguro se não configurado)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'copa_do_mundo'),
    'user': os.getenv('DB_USER', 'root'),       # Padrão universal 'root'
    'password': os.getenv('DB_PASSWORD', '')    # Padrão sem senha
}

# Inicialização do App Dash com tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Sistema Copa do Mundo 2026"

# ----------------------------------------------------------------------
# Funções Auxiliares de Banco de Dados (CRUD)
# ----------------------------------------------------------------------
def query_db(query, params=None):
    """Executa consultas de leitura (SELECT) e retorna (dados, erro)"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return result, None  # Retorna os dados e nenhum erro
    except Error as e:
        print(f"Erro detectado no terminal: {e}")
        return None, str(e)  # Retorna None e a mensagem do erro
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def mutate_db(query, params=None):
    """Executa alterações no banco (INSERT, UPDATE, DELETE)"""
    conn = None
    success = False
    msg = ""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        success = True
        msg = "Operação realizada com sucesso!"
    except Error as e:
        success = False
        msg = f"Erro no Banco de Dados: {e.msg}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return success, msg

# ----------------------------------------------------------------------
# Layout da Interface Gráfica
# ----------------------------------------------------------------------
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("🏆 Sistema de Gestão - Copa do Mundo 2026", className="text-center my-4 text-primary"), width=12)
    ]),
    
    dbc.Tabs([
        # ABA 1: GERENCIAR SELEÇÕES (CRUD COMPLETO)
        dbc.Tab(label="⚽ Seleções (CRUD)", children=[
            dbc.Row([
                # Formulário Lateral esquerdo (Create / Update)
                dbc.Col([
                    html.H4("Formulário da Seleção", className="mt-3"),
                    html.Div([
                        dbc.Label("ID da Seleção (Apenas para Atualizar/Excluir):"),
                        dbc.Input(id="sel-id", type="number", placeholder="ID gerado automaticamente no Create", readonly=False),
                        
                        dbc.Label("Nome da Seleção:", className="mt-2"),
                        dbc.Input(id="sel-nome", type="text", placeholder="Ex: Brasil"),
                        
                        dbc.Label("Continente:", className="mt-2"),
                        dbc.Input(id="sel-continente", type="text", placeholder="Ex: América do Sul"),
                        
                        dbc.Label("Técnico:", className="mt-2"),
                        dbc.Input(id="sel-tecnico", type="text", placeholder="Ex: Dorival Júnior"),
                        
                        dbc.Label("Títulos:", className="mt-2"),
                        dbc.Input(id="sel-titulos", type="number", value=0),
                    ], className="mb-3"),
                    
                    # Botões de Ações CRUD
                    dbc.Button("✨ Cadastrar (Create)", id="btn-create-sel", color="success", className="me-2 mb-2"),
                    dbc.Button("🔄 Atualizar (Update)", id="btn-update-sel", color="warning", className="me-2 mb-2"),
                    dbc.Button("❌ Excluir (Delete)", id="btn-delete-sel", color="danger", className="mb-2"),
                    
                    html.Div(id="alert-sel", className="mt-2")
                ], md=4),
                
                # Tabela de Visualização à direita (Read)
                dbc.Col([
                    html.H4("Seleções Registradas (Read)", className="mt-3"),
                    dbc.Button("🔄 Atualizar Tabela", id="btn-refresh-sel", color="info", size="sm", className="mb-2"),
                    html.Div(id="tabela-selecoes-container")
                ], md=8)
            ])
        ]),
        
        # ABA 2: PARTIDAS (Demonstração do Trigger de Vencedor)
        dbc.Tab(label="📅 Partidas & Trigger", children=[
            dbc.Row([
                dbc.Col([
                    html.H4("Simular Nova Partida", className="mt-3"),
                    html.P("O campo 'vencedor' será calculado automaticamente pelo Trigger 'trg_definir_vencedor' do MySQL.", className="text-muted"),
                    
                    dbc.Label("Data da Partida:"),
                    dbc.Input(id="part-data", type="date", value="2026-06-25"),
                    
                    dbc.Label("ID Estádio:", className="mt-2"),
                    dbc.Input(id="part-estadio", type="number", value=1),
                    
                    dbc.Label("ID Árbitro (Deve ser Principal):", className="mt-2"),
                    dbc.Input(id="part-arbitro", type="number", value=1),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("ID Seleção 1:"),
                            dbc.Input(id="part-sel1", type="number", value=1),
                            dbc.Label("Gols Sel. 1:", className="mt-1"),
                            dbc.Input(id="part-gols1", type="number", value=0),
                        ], width=6),
                        dbc.Col([
                            dbc.Label("ID Seleção 2:"),
                            dbc.Input(id="part-sel2", type="number", value=2),
                            dbc.Label("Gols Sel. 2:", className="mt-1"),
                            dbc.Input(id="part-gols2", type="number", value=0),
                        ], width=6),
                    ], className="mt-2"),
                    
                    dbc.Button("🚀 Agendar e Processar Partida", id="btn-create-partida", color="primary", className="mt-3"),
                    html.Div(id="alert-partida", className="mt-2")
                ], md=4),
                
                dbc.Col([
                    html.H4("Histórico de Partidas", className="mt-3"),
                    dbc.Button("🔄 Atualizar Partidas", id="btn-refresh-part", color="info", size="sm", className="mb-2"),
                    html.Div(id="tabela-partidas-container")
                ], md=8)
            ])
        ]),

        # ABA 3: DASHBOARD DE VISUALIZAÇÕES GRÁFICAS (Bonificação Extra)
        dbc.Tab(label="📊 Dashboard", children=[
            dbc.Row([
                dbc.Col([
                    html.H4("📊 Dashboard Analítico", className="mt-3"),
                    html.P(
                        "Visualizações geradas por consultas SQL não-triviais (JOIN, GROUP BY, SUM, COUNT).",
                        className="text-muted"
                    ),
                    dbc.Button("🔄 Carregar / Atualizar Gráficos", id="btn-refresh-dash",
                               color="primary", className="mb-3"),
                ], width=12)
            ]),

            # Linha 1: Gráfico de Ranking de Vitórias (largura total)
            dbc.Row([
                dbc.Col([
                    # dcc.Graph é o componente Dash que renderiza qualquer gráfico Plotly
                    dcc.Graph(id="grafico-vitorias")
                ], width=12)
            ], className="mb-4"),

            # Linha 2: Dois gráficos lado a lado
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="grafico-gols")
                ], md=6),
                dbc.Col([
                    dcc.Graph(id="grafico-scatter")
                ], md=6)
            ])
        ])
    ])
], fluid=True)


# ----------------------------------------------------------------------
# Callbacks - Lógica de Funcionamento
# ----------------------------------------------------------------------

# 1. CALLBACK: Gerenciamento de Seleções (CRUD: Create, Update, Delete)
@app.callback(
    Output("alert-sel", "children"),
    Input("btn-create-sel", "n_clicks"),
    Input("btn-update-sel", "n_clicks"),
    Input("btn-delete-sel", "n_clicks"),
    State("sel-id", "value"),
    State("sel-nome", "value"),
    State("sel-continente", "value"),
    State("sel-tecnico", "value"),
    State("sel-titulos", "value"),
    prevent_initial_call=True
)
def gerenciar_selecoes(c_clicks, u_clicks, d_clicks, id_sel, nome, continente, tecnico, titulos):
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Operação: CREATE
    if button_id == "btn-create-sel":
        if not nome or not continente or not tecnico:
            return dbc.Alert("Preencha todos os campos obrigatórios para cadastrar!", color="danger")
        query = "INSERT INTO selecoes (nome_selecao, continente, tecnico, titulos) VALUES (%s, %s, %s, %s)"
        success, msg = mutate_db(query, (nome, continente, tecnico, titulos))
        return dbc.Alert(msg, color="success" if success else "danger")
        
    # Operação: UPDATE
    elif button_id == "btn-update-sel":
        if not id_sel:
            return dbc.Alert("Você precisa informar o ID da Seleção que deseja atualizar!", color="danger")
        query = "UPDATE selecoes SET nome_selecao=%s, continente=%s, tecnico=%s, titulos=%s WHERE id_selecao=%s"
        success, msg = mutate_db(query, (nome, continente, tecnico, titulos, id_sel))
        return dbc.Alert(msg, color="success" if success else "danger")
        
    # Operação: DELETE
    elif button_id == "btn-delete-sel":
        if not id_sel:
            return dbc.Alert("Você precisa informar o ID da Seleção que deseja excluir!", color="danger")
        query = "DELETE FROM selecoes WHERE id_selecao = %s"
        success, msg = mutate_db(query, (id_sel,))
        return dbc.Alert(msg, color="success" if success else "danger")

    return ""


# 2. CALLBACK: Visualização de Seleções (READ)
@app.callback(
    Output("tabela-selecoes-container", "children"),
    Input("btn-refresh-sel", "n_clicks"),
    Input("alert-sel", "children")
)
def renderizar_tabela_selecoes(n_clicks, alert):
    dados, erro = query_db("SELECT id_selecao AS ID, nome_selecao AS Seleção, continente AS Continente, tecnico AS Técnico, titulos AS Títulos FROM selecoes")
    
    # Se houver um erro de conexão real, exibe o alerta vermelho com o motivo técnico
    if erro:
        return dbc.Alert(f"❌ Erro de Conexão com o Banco: {erro}", color="danger", className="mt-2")
    
    # Se a conexão deu certo mas não há registros na tabela
    if not dados:
        return html.P("A tabela 'selecoes' está conectada, mas encontra-se vazia no momento.", className="text-muted mt-2")
    
    df = pd.DataFrame(dados)
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#f4f6f9', 'fontWeight': 'bold'}
    )


# 3. CALLBACK: Inserção de Partidas (Ação disparando o TRIGGER)
@app.callback(
    Output("alert-partida", "children"),
    Input("btn-create-partida", "n_clicks"),
    State("part-data", "value"),
    State("part-estadio", "value"),
    State("part-arbitro", "value"),
    State("part-sel1", "value"),
    State("part-sel2", "value"),
    State("part-gols1", "value"),
    State("part-gols2", "value"),
    prevent_initial_call=True
)
def cadastrar_partida(n_clicks, data, estadio, arbitro, sel1, sel2, gols1, gols2):
    if not data or not estadio or not arbitro or not sel1 or not sel2:
        return dbc.Alert("Preencha todos os campos da partida.", color="danger")
        
    query = """
        INSERT INTO partidas (data_partida, id_estadio, id_arbitro, id_selecao_1, id_selecao_2, quantidade_gols_selecao_1, quantidade_gols_selecao_2)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    success, msg = mutate_db(query, (data, estadio, arbitro, sel1, sel2, gols1, gols2))
    return dbc.Alert(msg, color="success" if success else "danger")


# 4. CALLBACK: Visualização de Partidas (Mostrando o Vencedor calculado pelo Trigger)
@app.callback(
    Output("tabela-partidas-container", "children"),
    Input("btn-refresh-part", "n_clicks"),
    Input("alert-partida", "children")
)
def renderizar_tabela_partidas(n_clicks, alert):
    query = """
        SELECT 
            p.id_partida AS ID, 
            p.data_partida AS Data, 
            e.nome_estadio AS Estádio,
            s1.nome_selecao AS `Time 1`, 
            p.quantidade_gols_selecao_1 AS `Gols 1`,
            p.quantidade_gols_selecao_2 AS `Gols 2`, 
            s2.nome_selecao AS `Time 2`,
            COALESCE(sv.nome_selecao, 'Empate') AS `Vencedor (via Trigger)`
        FROM partidas p
        JOIN estadios e ON p.id_estadio = e.id_estadio
        JOIN selecoes s1 ON p.id_selecao_1 = s1.id_selecao
        JOIN selecoes s2 ON p.id_selecao_2 = s2.id_selecao
        LEFT JOIN selecoes sv ON p.vencedor = sv.id_selecao
    """
    dados, erro = query_db(query)
    
    if erro:
        return dbc.Alert(f"❌ Erro de Conexão com o Banco: {erro}", color="danger", className="mt-2")
        
    if not dados:
        return html.P("Nenhuma partida registrada.", className="text-muted mt-2")
        
    df = pd.DataFrame(dados)
    if 'Data' in df.columns:
        df['Data'] = df['Data'].astype(str)
        
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center', 'padding': '10px'},
        style_header={'backgroundColor': '#e9ecef', 'fontWeight': 'bold'}
    )


# 5. CALLBACK: Dashboard de Visualizações Gráficas
# Um único callback retorna 3 gráficos ao mesmo tempo (múltiplos Outputs)
@app.callback(
    Output("grafico-vitorias", "figure"),   # Ranking de vitórias
    Output("grafico-gols", "figure"),        # Gols por seleção
    Output("grafico-scatter", "figure"),     # Scatter: gols marcados vs sofridos
    Input("btn-refresh-dash", "n_clicks"),
    prevent_initial_call=True
)
def atualizar_dashboard(n_clicks):
    # Função auxiliar: figura vazia com mensagem quando não há dados
    def figura_vazia(mensagem):
        fig = go.Figure()
        fig.add_annotation(
            text=mensagem, showarrow=False,
            font=dict(size=16, color="gray"),
            xref="paper", yref="paper", x=0.5, y=0.5
        )
        fig.update_layout(
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            plot_bgcolor="white", paper_bgcolor="white"
        )
        return fig

    # ------------------------------------------------------------------
    # GRÁFICO 1: Ranking de Vitórias por Seleção
    # Técnicas SQL: COUNT(*), INNER JOIN, GROUP BY, ORDER BY
    # Aliases simples (sem acento) para garantir compatibilidade com mysql-connector
    # ------------------------------------------------------------------
    query_vitorias = """
        SELECT
            s.nome_selecao AS selecao,
            COUNT(*)       AS vitorias
        FROM partidas p
        INNER JOIN selecoes s ON p.vencedor = s.id_selecao
        WHERE p.vencedor IS NOT NULL
        GROUP BY s.nome_selecao
        ORDER BY vitorias DESC
    """
    dados_vitorias, _ = query_db(query_vitorias)

    if dados_vitorias:
        df_v = pd.DataFrame(dados_vitorias)
        # Renomeia para exibição legível no gráfico
        df_v = df_v.rename(columns={"selecao": "Seleção", "vitorias": "Vitórias"})
        # Barras horizontais: fácil de comparar rankings
        fig_vitorias = px.bar(
            df_v,
            x="Vitórias", y="Seleção",
            orientation="h",
            color="Vitórias",
            color_continuous_scale="Viridis",
            title="🏅 Ranking de Vitórias por Seleção",
            text="Vitórias"
        )
        fig_vitorias.update_traces(textposition="outside")
        fig_vitorias.update_layout(
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            plot_bgcolor="#f8f9fa",
            title_font_size=18
        )
    else:
        fig_vitorias = figura_vazia("⚠️ Nenhuma partida com vencedor registrada ainda.")

    # ------------------------------------------------------------------
    # GRÁFICO 2: Total de Gols Marcados por Seleção
    # Técnicas SQL: SUM(), UNION ALL, LEFT JOIN, GROUP BY
    # Soma gols como time 1 + gols como time 2 para cada seleção
    # ------------------------------------------------------------------
    query_gols = """
        SELECT
            s.nome_selecao   AS selecao,
            SUM(gols_totais) AS gols_marcados
        FROM (
            SELECT id_selecao_1 AS id_sel, quantidade_gols_selecao_1 AS gols_totais FROM partidas
            UNION ALL
            SELECT id_selecao_2 AS id_sel, quantidade_gols_selecao_2 AS gols_totais FROM partidas
        ) AS todos_gols
        LEFT JOIN selecoes s ON todos_gols.id_sel = s.id_selecao
        GROUP BY s.nome_selecao
        ORDER BY gols_marcados DESC
    """
    dados_gols, _ = query_db(query_gols)

    if dados_gols:
        df_g = pd.DataFrame(dados_gols)
        df_g = df_g.rename(columns={"selecao": "Seleção", "gols_marcados": "Gols Marcados"})
        fig_gols = px.bar(
            df_g,
            x="Seleção", y="Gols Marcados",
            color="Gols Marcados",
            color_continuous_scale="OrRd",
            title="⚽ Total de Gols Marcados por Seleção",
            text="Gols Marcados"
        )
        fig_gols.update_traces(textposition="outside")
        fig_gols.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="#f8f9fa",
            title_font_size=16
        )
    else:
        fig_gols = figura_vazia("⚠️ Nenhuma partida registrada ainda.")

    # ------------------------------------------------------------------
    # GRÁFICO 3: Scatter — Gols Feitos vs Gols Sofridos por Seleção
    # Técnicas SQL: SUM(), UNION ALL, LEFT JOIN, GROUP BY, HAVING
    # Cada "bolha" = uma seleção. Tamanho = nº de partidas jogadas.
    # Seleções abaixo da diagonal = saldo de gols positivo!
    # ------------------------------------------------------------------
    query_scatter = """
        SELECT
            s.nome_selecao AS selecao,
            SUM(feitos)    AS gols_feitos,
            SUM(sofridos)  AS gols_sofridos,
            COUNT(*)       AS num_partidas
        FROM (
            SELECT id_selecao_1 AS id_sel,
                   quantidade_gols_selecao_1 AS feitos,
                   quantidade_gols_selecao_2 AS sofridos
            FROM partidas
            UNION ALL
            SELECT id_selecao_2 AS id_sel,
                   quantidade_gols_selecao_2 AS feitos,
                   quantidade_gols_selecao_1 AS sofridos
            FROM partidas
        ) AS desempenho
        LEFT JOIN selecoes s ON desempenho.id_sel = s.id_selecao
        GROUP BY s.nome_selecao
        HAVING SUM(feitos) IS NOT NULL
    """
    dados_scatter, _ = query_db(query_scatter)

    if dados_scatter and len(dados_scatter) > 0:
        df_s = pd.DataFrame(dados_scatter)
        df_s = df_s.rename(columns={
            "selecao":       "Seleção",
            "gols_feitos":   "Gols Feitos",
            "gols_sofridos": "Gols Sofridos",
            "num_partidas":  "Partidas"
        })
        # Garante que as colunas numéricas não tenham NaN (substitui por 0)
        df_s["Gols Feitos"]   = pd.to_numeric(df_s["Gols Feitos"],   errors="coerce").fillna(0)
        df_s["Gols Sofridos"] = pd.to_numeric(df_s["Gols Sofridos"], errors="coerce").fillna(0)
        df_s["Partidas"]      = pd.to_numeric(df_s["Partidas"],      errors="coerce").fillna(1)

        fig_scatter = px.scatter(
            df_s,
            x="Gols Feitos", y="Gols Sofridos",
            size="Partidas",
            color="Seleção",
            hover_name="Seleção",
            text="Seleção",
            title="🔵 Gols Feitos vs Sofridos (Análise de Desempenho)",
            size_max=40
        )
        fig_scatter.update_traces(textposition="top center")
        fig_scatter.update_layout(
            plot_bgcolor="#f8f9fa",
            title_font_size=16,
            showlegend=False
        )
        # Linha diagonal de referência: abaixo = saldo positivo, acima = saldo negativo
        max_val = float(max(df_s["Gols Feitos"].max(), df_s["Gols Sofridos"].max())) + 1
        if max_val > 0:
            fig_scatter.add_shape(
                type="line", line=dict(dash="dot", color="gray", width=1),
                x0=0, y0=0, x1=max_val, y1=max_val
            )
            fig_scatter.add_annotation(
                x=max_val * 0.75, y=max_val * 0.85,
                text="Saldo Neutro", showarrow=False,
                font=dict(color="gray", size=10)
            )
    else:
        fig_scatter = figura_vazia("⚠️ Dados insuficientes para o gráfico de desempenho.")

    return fig_vitorias, fig_gols, fig_scatter


# Execução do Servidor
if __name__ == '__main__':
    app.run(debug=True)