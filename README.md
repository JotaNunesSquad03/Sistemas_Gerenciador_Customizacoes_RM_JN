# Gerenciamento de Customizações no ERP RM TOTVS

## Status Atual
Sistema para gerenciar e auditar customizações no ERP RM TOTVS, garantindo:  

- Estabilidade do ambiente  
- Otimização da manutenção  
- Facilidade em atualizações  
- Rastreabilidade técnica completa  

## Funcionalidades Principais

### 1. Espelhamento de Customizações (`AUD_FV`, `AUD_SQL`, `AUD_REPORT`) ✅
- Tabelas "espelho" das customizações no ERP  
- Somente leitura, sem alterar o ERP  
- Status: Implementado  

### 2. Mapeamento de Dependências (`AUD_DEPENDENCIA`) ✅
- Identifica relações entre customizações (ex.: FV que usa SQL)  
- Preenche automaticamente a tabela de dependências sem duplicar dados e sem interferir no ERP  
- Status: Implementado  

### 3. Monitoramento e Logs Simplificados ✅
- Auditoria simplificada diretamente nos espelhos (`AUD_SQL`, `AUD_FV`, `AUD_REPORT`)  
- Detecta criação e atualização de registros  
- Inclui campo `LIDA` apenas no `REPORT`, se necessário  
- Status: Implementado  

### 4. Gestão de Usuários (`USUÁRIOS`) ✅
- Gerencia usuários do sistema, incluindo autenticação e associação de permissões  
- Status: Implementado  

## Tecnologias Utilizadas (Backend)
- Python + FastAPI  
- SQLAlchemy (ORM) + SQL Server  
- WebSockets para monitoramento em tempo real  
- Pydantic para validação de dados
