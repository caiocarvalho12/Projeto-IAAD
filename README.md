# 🏆 Sistema de Gestão e Business Intelligence — Copa do Mundo 2026

Este sistema computacional web foi desenvolvido como parte da avaliação da 2ª VA da disciplina **Introdução ao Armazenamento e Análise de Dados (IAAD) — 2026.1**, no curso de Bacharelado em Sistemas de Informação da **Universidade Federal Rural de Pernambuco (UFRPE)**.

A plataforma consiste em uma aplicação de gerenciamento transacional e análise estatística de Business Intelligence (BI) desenvolvida em Python (utilizando o framework Dash, componentes Bootstrap e gráficos Plotly) totalmente integrada a um banco de dados relacional MySQL.

---

## 🚀 Funcionalidades Principais por Módulos (Abas)

O sistema organiza o controle do torneio de forma modular através de uma interface gráfica web intuitiva, dividida em seis abas operacionais:

* **⚽ Seleções (CRUD Completo):** Painel operacional para inserção (Create), listagem dinâmica em tempo real (Read), atualização de dados cadastrais (Update) e remoção permanente (Delete) de registros de seleções na base de dados.
* **🏃 Jogadores:** Controle cadastral de atletas vinculados às seleções por chaves estrangeiras, apresentando uma visualização avançada com junção de tabelas (`JOIN`) para exibir o nome da delegação na grade de leitura.
* **⚖️ Árbitros:** Módulo de gerenciamento de profissionais com controle de integridade de domínio, utilizando um componente de seleção de dados restrito às funções do tipo `ENUM` do banco de dados ('Principal', 'Assistente', 'VAR').
* **🏟️ Estádios:** Cadastro e monitoramento das sedes oficiais da competição, permitindo o gerenciamento de capacidades de público e localizações geográficas.
* **📅 Partidas & Trigger:** Painel de simulação de confrontos que demonstra a inteligência e as regras de negócio aplicadas diretamente no motor do banco de dados:
  * **Cálculo Automático de Resultados:** O preenchimento da coluna `vencedor` é processado de forma 100% autônoma pelo gatilho `trg_definir_vencedor` (*Before Insert Trigger*) no MySQL.
  * **Validação de Arbitragem:** Atuação do gatilho `trg_valida_arbitro_principal`, que bloqueia a inserção e ejeta uma exceção controlada caso o usuário tente alocar um árbitro com função de "Assistente" ou "VAR" para apitar a partida principal.
* **📊 Dashboard Analítico:** Painel gerencial avançado contendo componentes gráficos interativos do Plotly que extraem métricas estratégicas da competição em tempo real através de conexões otimizadas com o SGBD.

---

## 📊 Engenharia de Dados: Consultas Não-Triviais Utilizadas

A aba de Dashboard analítico é alimentada diretamente por três consultas relacionais complexas mapeadas nos callbacks da aplicação:

1. **Ranking de Vitórias:** Contagem agregada de triunfos por delegação obtida através de funções `COUNT(*)`, interligação via `INNER JOIN`, agrupamento por `GROUP BY` e ordenação decrescente (`ORDER BY DESC`), filtrando resultados de empate.
2. **Volumetria de Gols Marcados:** Consolidação do total de gols de cada país combinando dados estatísticos paralelos por meio da cláusula `UNION ALL` (unificando gols marcados como mandante e como visitante) associada a funções de soma (`SUM`) e `LEFT JOIN`.
3. **Análise de Desempenho (Scatter):** Dispersão bidimensional que correlaciona os gols feitos versus os gols sofridos por seleção, aplicando agrupamentos avançados e filtragem de registros agregados pós-agrupamento por meio da cláusula restritiva `HAVING SUM(feitos) IS NOT NULL`.

---

## 📋 Pré-requisitos do Sistema

Antes de iniciar a execução do programa, certifique-se de ter instalado em seu ambiente:
1. **Python 3.10 ou superior**
2. **MySQL Server** (com o serviço ativo e rodando localmente em segundo plano)

---

## 🛠️ Guia de Instalação, Povoamento e Execução (Passo a Passo)

Siga rigorosamente as etapas ordenadas abaixo para integrar a infraestrutura de dados no MySQL Workbench e executar a aplicação transacional.

### 📌 PASSO 1: Configurar o Arquivo de Credenciais (`.env`)
O sistema gerencia as chaves de acesso locais de forma isolada por meio de variáveis de ambiente para garantir a portabilidade do código.
1. Na raiz do projeto (mesma pasta onde encontra-se o arquivo `sistema.py`), crie um arquivo de texto e renomeie-o exatamente como **`.env`** (certifique-se de que o sistema operacional não adicione a extensão oculta `.txt`).
2. Abra o arquivo em seu editor de código e configure os acessos locais da sua máquina:
```env
DB_ROOT_PASSWORD=sua_senha_do_mysql_root
DB_PASSWORD=sua_senha_do_mysql_root
DB_HOST=localhost
DB_NAME=copa_do_mundo
DB_USER=root

3. No MySQL Workbench, vá no menu superior e clique em File > Open SQL Script... e selecione o arquivo copa_do_mundo.sql.

4. Clique no ícone do Raio no menu superior. O motor do MySQL processará o arquivo DDL e DML.
Como o Workbench não atualiza a lista sozinho, vá até a barra lateral esquerda na aba SCHEMAS e clique no botão de Refresh (ícone de duas setas circulares). O esquema copa_do_mundo aparecerá na lista.
Caso queira auditar se os dados entraram, dê dois cliques em copa_do_mundo para ativá-lo e execute a query abaixo para visualizar as seleções base inseridas:
SELECT * FROM selecoes;

5. Abrir o Terminal: No VS Code, abra o terminal integrado na pasta raiz do projeto.

Ativar o Ambiente Virtual: Certifique-se de que o seu ambiente virtual (.venv) está ativo no terminal (exibindo a tag (.venv) no início da linha de comando).

Iniciar o Servidor: Digite o comando abaixo para executar o programa:

python sistema.py

Acessar o Navegador: O terminal informará que o servidor Dash está ativo em modo de depuração (Debug mode: on). Abra o seu navegador e acesse a URL:

Plaintext
http://127.0.0.1:8050/

