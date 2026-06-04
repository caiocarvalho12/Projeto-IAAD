import os
import dash
from dash import html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import mysql.connector
from mysql.connector import Error
import pandas as pd
from dotenv import load_dotenv

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


# Execução do Servidor
if __name__ == '__main__':
    app.run(debug=True)