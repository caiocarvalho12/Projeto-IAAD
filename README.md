# 🏆 Sistema de Gestão e Business Intelligence — Copa do Mundo 2026

Este sistema computacional web foi desenvolvido como parte da avaliação da 2ª VA da disciplina **Introdução ao Armazenamento e Análise de Dados (IAAD) — 2026.1**, no curso de Bacharelado em Sistemas de Informação da **Universidade Federal Rural de Pernambuco (UFRPE)**.

O projeto consiste em uma plataforma de gerenciamento e análise de dados desenvolvida em Python (utilizando o framework Dash, componentes Bootstrap e gráficos Plotly) totalmente integrada a um banco de dados relacional MySQL.

---

## 🚀 Funcionalidades Principais

* **Automação de Infraestrutura:** O sistema possui uma rotina automática interna (`init_db()`) que se conecta ao servidor, verifica e cria de forma transparente o esquema, as tabelas estruturadas (`selecoes`, `jogadores`, `estadios`, `arbitros`, `partidas`) e as cargas iniciais básicas no primeiro instante em que o arquivo é executado.
* **CRUD Completo de Seleções:** Interface visual para inserção (Create), listagem dinâmica em tempo real (Read), atualização cadastral (Update) e remoção (Delete) de registros.
* **Processamento de Partidas via Trigger:** Painel de simulação de confrontos onde o campo `vencedor` é calculado e populado de forma 100% autônoma por um gatilho (*Before Insert Trigger*) diretamente no motor do MySQL.
* **Restrições de Integridade e Validação:** Presença de gatilhos físicos no banco que impedem alocações inválidas (como árbitros assistentes atuando como juiz principal) e chaves estrangeiras com ações em cascata (`ON DELETE CASCADE`).
* **📊 Dashboard de Business Intelligence:** Painel analítico avançado com gráficos interativos que extraem estatísticas do torneio em tempo real por meio de consultas relacionais complexas.

---

## 📊 Engenharia de Dados: Consultas Não-Triviais Utilizadas

O Dashboard analítico é alimentado por três consultas SQL avançadas mapeadas nos callbacks da aplicação:

1. **Ranking de Vitórias:** Agrupamento e contagem de vitórias por delegação utilizando `COUNT(*)`, `INNER JOIN`, `GROUP BY` e ordenação decrescente (`ORDER BY DESC`).
2. **Volumetria de Gols Marcados:** Agregação de gols marcados combinando estatísticas de mandante e visitante por meio da técnica de união de tabelas virtuais com `SUM()`, `UNION ALL` e `LEFT JOIN`.
3. **Análise de Desempenho (Scatter):** Mapeamento bidimensional de gols feitos versus gols sofridos por seleção, aplicando agrupamentos complexos e filtragem de agregações pós-agrupamento por meio da cláusula `HAVING`.

---

## 📋 Pré-requisitos do Sistema

Antes de iniciar a execução do programa, certifique-se de ter instalado no ambiente:
1. **Python 3.10 ou superior**
2. **MySQL Server** (com o serviço ativo e rodando em segundo plano no Windows)

---

## 🛠️ Passo a Passo para Configuração e Execução

### Passo 1: Configurar o Arquivo de Credenciais (`.env`)
O sistema gerencia as chaves de acesso locais de forma isolada por meio de variáveis de ambiente.
1. Na raiz do projeto, crie um arquivo e nomeie-o exatamente como `.env`.
2. Cole a estrutura abaixo e substitua pelos seus dados de autenticação locais do MySQL:

```env
DB_ROOT_PASSWORD=sua_senha_do_mysql_root
DB_PASSWORD=sua_senha_do_mysql_root
DB_HOST=localhost
DB_NAME=copa_do_mundo
DB_USER=root