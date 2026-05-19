# PDF Extractor & Sanitizer API (LGPD)

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com)

Uma solução completa, robusta e moderna de API e Dashboard Web para **extração de texto, identificação e higienização automática de dados pessoais sensíveis (PII)** em conformidade com as diretrizes da **LGPD (Lei Geral de Proteção de Dados - Lei nº 13.709/2018)**.

O sistema analisa documentos PDF, extrai textos estruturados e tabelas nativas, aplica filtros avançados de expressões regulares validadas via algoritmos matemáticos (para CPFs e CNPJs) e gera relatórios de auditoria interativos em tempo real.

---

## 🚀 Funcionalidades Principais

* **Extração Precisa (pdfplumber)**: Captura de texto mantendo a consistência de páginas e layout do documento, além de reconstrução de tabelas estruturadas nativas.
* **Higienização Inteligente (LGPD/PII)**: Identificação e mascaramento parcial de informações sensíveis, preservando o formato para reconhecimento visual.
* **Validação por Checksum**: Os CPFs e CNPJs são validados através dos algoritmos matemáticos de dígitos verificadores para evitar falsos positivos.
* **Trilha de Auditoria Interativa**: Log detalhado contendo a página, o tipo de dado pessoal detectado, a versão original vs. higienizada e o snippet de contexto real.
* **Exportação Versátil**: Download das tabelas e dados higienizados nos formatos estruturados **CSV** e **JSON**.
* **Dashboard Visual Premium**: Interface web rica em modo escuro (*glassmorphic card design*) construída com HTML5 Semântico, CSS3 Moderno e JavaScript reativo.

---

## 🛡️ Dados Pessoais Higienizados

O motor de sanitização (`sanitizer.py`) realiza buscas e validações detalhadas sobre as seguintes categorias de dados pessoais:

| Categoria | Formato Original | Formato Higienizado | Regra de Mascaramento / Validação |
| :--- | :--- | :--- | :--- |
| **CPF** | `123.456.789-00` | `123.***.***-00` | Validação matemática de checksum dos 2 dígitos verificadores. |
| **CNPJ** | `12.345.678/0001-90` | `12.***.***/0001-90` | Validação matemática de checksum dos 2 dígitos verificadores. |
| **E-mail** | `carlos.alberto@provedor.com` | `c***o@provedor.com` | Ocultamento parcial da caixa de entrada mantendo domínio intacto. |
| **Telefone** | `(11) 98765-4321` | `(11) 9****-4321` | Ocultamento do corpo central do número (celular ou fixo com DDD). |
| **Dados Bancários** | `Agência: 1234-5` | `Agência: ****-*` | Mascaramento de algarismos vinculados a palavras-chave financeiras. |

---

## 🛠️ Tecnologias Utilizadas

### Backend
* **Python 3.10+** como linguagem base.
* **FastAPI** para criação de endpoints assíncronos de alta performance e documentação Swagger automática.
* **pdfplumber** para extração precisa de dados textuais e matriciais de PDFs.
* **ReportLab** para a criação de documentos PDF complexos utilizados no pipeline de validação de testes.
* **Uvicorn** como servidor ASGI de alto desempenho.

### Frontend
* **HTML5 Semântico** para estrutura SEO-friendly.
* **Vanilla CSS3** utilizando propriedades customizadas (variáveis), sistema de grid/flexbox flexível e efeitos de *glassmorphism* (`backdrop-filter`).
* **ES6+ JavaScript** assíncrono para controle do fluxo de uploads, processamento dinâmico de tabelas e geração de downloads via payloads de API.

---

## 📦 Instalação e Execução

Siga os passos abaixo para instalar e rodar o projeto localmente em sua máquina.

### Pré-requisitos
* Python 3.10 ou superior instalado.
* Git configurado.

### 1. Clonar o repositório
```bash
git clone https://github.com/mirydios/PDFSanitizer.git
cd PDFSanitizer
```

### 2. Configurar o ambiente virtual (`.venv`)
Crie e ative um ambiente Python isolado para evitar poluição das dependências globais do seu sistema:

**No Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**No Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 4. Gerar o PDF de testes
O projeto inclui um gerador automatizado de PDF com dados pessoais válidos fictícios para você validar todas as regras do sistema:
```bash
python create_test_pdf.py
```
*Isso gerará o arquivo `test_document.pdf` na raiz do seu projeto.*

### 5. Iniciar o servidor FastAPI
```bash
python -m uvicorn main:app --reload
```

Pronto! Acesse **[http://127.0.0.1:8000](http://127.0.0.1:8000)** no seu navegador para abrir o Dashboard Web interativo.

---

## 🔌 Endpoints da API

A API vem com documentação interativa integrada disponível em `/docs` (Swagger UI). Abaixo estão os endpoints principais:

### 1. Processar e Higienizar PDF
* **Rota**: `/api/process`
* **Método**: `POST`
* **Content-Type**: `multipart/form-data`
* **Payload**: Arquivo binário em formato `.pdf` enviado na chave `file`.
* **Retorno (JSON)**:
  - `metadata`: Metadados do arquivo (autor, título, quantidade de páginas, tamanho em bytes).
  - `original_pages` e `sanitized_pages`: Arrays contendo o texto bruto e sanitizado de cada página.
  - `tables`: Array com todas as tabelas originais e sanitizadas detectadas.
  - `audit_trail`: Log com todas as ocorrências de PII identificadas.
  - `stats`: Estatísticas de higienização agregadas por tipo.

### 2. Baixar Tabela Sanitizada em CSV
* **Rota**: `/api/download/csv`
* **Método**: `POST`
* **Payload (JSON)**:
  ```json
  {
    "table": [["Linha 1 Col 1", "Linha 1 Col 2"]],
    "filename": "tabela_sanitizada.csv"
  }
  ```
* **Retorno**: Arquivo de download CSV codificado em UTF-8 com prefixo BOM para compatibilidade com Microsoft Excel.

### 3. Baixar Dados Higienizados em JSON
* **Rota**: `/api/download/json`
* **Método**: `POST`
* **Payload (JSON)**:
  ```json
  {
    "data": { "chave": "conteudo_higienizado" },
    "filename": "dados_higienizados.json"
  }
  ```
* **Retorno**: Arquivo de download JSON estruturado.

---

## 📂 Estrutura do Repositório

```
PDFSanitizer/
├── requirements.txt       # Arquivo de dependências do Python
├── main.py                # Servidor FastAPI e roteamento de endpoints
├── sanitizer.py           # Core de validação de dados sensíveis e mascaramento
├── pdf_engine.py          # Extrator do pdfplumber (Textos e Tabelas estruturadas)
├── create_test_pdf.py     # Script gerador de PDF de simulação LGPD
├── verify_api.py          # Script de testes automatizados locais
├── static/                # Aplicação web estática (Frontend Dashboard)
│   ├── index.html         # Casca visual do Dashboard e tags SEO
│   ├── style.css          # Estilos de design Glassmorphism e Dark Mode
│   └── app.js             # Controller interativo, uploads, toggles e downloads
└── .gitignore             # Definição de exclusões do controle de versão
```

---

## 📜 Licença

Este projeto é disponibilizado para fins de validação de conformidade com a LGPD e testes de engenharia de software de alta performance. Sinta-se à vontade para expandir as regras de expressões regulares e integrá-las aos seus próprios fluxos corporativos!
