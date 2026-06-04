# Projeto-IAAD

# 🏆 Sistema de Gestão — Copa do Mundo 2026

Este sistema computacional web foi desenvolvido como parte da avaliação da 2ª VA da disciplina **Introdução ao Armazenamento e Análise de Dados (IAAD) — 2026.1**, no curso de Bacharelado em Sistemas de Informação da **Universidade Federal Rural de Pernambuco (UFRPE)**.

O projeto consiste em uma interface gráfica moderna desenvolvida em Python (utilizando o framework Dash e componentes Bootstrap) totalmente integrada a um banco de dados relacional MySQL.

---

## 🚀 Funcionalidades Principais

* **Automação de Infraestrutura:** O sistema possui uma rotina automática que verifica, cria e popula a base de dados, as tabelas e os gatilhos (triggers) necessários no primeiro momento em que é executado.
* **CRUD Completo de Seleções:** Interface visual para inserção (Create), listagem/leitura (Read), atualização (Update) e remoção (Delete) de registros de seleções.
* **Processamento de Partidas & Trigger:** Painel de simulação de confrontos onde o campo `vencedor` é calculado e preenchido automaticamente por um gatilho (*Before Insert Trigger*) diretamente no MySQL.
* **Validação de Regras de Negócio:** Restrição automática que impede a alocação de árbitros que não possuam a função "Principal" nas partidas disputadas.

---

## 📋 Pré-requisitos

Antes de iniciar a execução do programa, certifique-se de ter instalado em sua máquina:
1. **Python 3.10 ou superior**
2. **MySQL Server** (com o serviço/servidor ativo em segundo plano)

---

## 🛠️ Passo a Passo para Configuração e Execução

Siga as etapas abaixo sequencialmente para preparar o ambiente e rodar a aplicação:

### Passo 1: Preparar o Arquivo de Credenciais (`.env`)
Por motivos de segurança e portabilidade, o sistema gerencia as credenciais locais do banco através de variáveis de ambiente.
1. Na raiz do projeto, crie um arquivo de texto e nomeie-o exatamente como `.env` (sem extensões como `.txt`).
2. Abra o arquivo e adicione as suas configurações locais do MySQL Server, preenchendo as senhas do seu usuário administrador:

```env
DB_ROOT_PASSWORD=sua_senha_do_mysql_root
DB_PASSWORD=sua_senha_do_mysql_root
DB_HOST=localhost
DB_NAME=copa_do_mundo
DB_USER=root