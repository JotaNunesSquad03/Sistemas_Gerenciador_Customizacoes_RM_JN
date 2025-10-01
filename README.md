# Gerenciamento de Customizações no ERP RM TOTVS

## Status Atual
Criar um sistema robusto para gerenciar e auditar customizações no **ERP RM TOTVS**, garantindo:

- Estabilidade do ambiente;
- Otimização da manutenção;
- Facilidade em atualizações;
- Rastreabilidade técnica completa.

---

## Funcionalidades Principais

### 1. Auditoria de Alterações (AUD_ALTERACAO) ✅
- Registra automaticamente todas as modificações (**CREATE, UPDATE, DELETE**) em customizações (Fórmulas Visuais, SQLs, Relatórios).  
- Log detalhado contendo: tabela, chave, ação, valores antes e depois, e descrição.  
- **Status:** Implementado e funcional.

### 2. Espelhamento de Customizações (AUD_FV, AUD_SQL, AUD_REPORT) ✅
- Tabelas "espelho" das customizações no ERP.  
- **Somente leitura**, sem alterar o ERP.  
- **Status:** Implementado.

### 3. Documentação Técnica (AUD_DOCS) ✅
- Permite associar documentação a cada customização.  
- CRUD completo: criar, ler, atualizar, deletar.  
- **Status:** Implementado.

### 4. Mapeamento de Dependências (AUD_DEPENDENCIAS) ✅
- Identificação e registro das relações entre customizações (ex: FV que usa SQL).  
- Scanner automático detecta dependências e popula a tabela sem duplicar e sem interferir no ERP.  
- **Status:** Implementado.

### 5. Notificações e Alertas (via WebSocket) ✅
- Sistema de notificação em tempo real para o frontend.  
- Cada alteração registrada em AUD_ALTERACAO gera uma notificação via WebSocket.  
- **Status:** Implementado.

---

## Tecnologias Utilizadas (Backend)
- **Python** + **FastAPI**  
- **SQLAlchemy** (ORM) + **SQL Server**  
- **WebSockets** para notificações em tempo real  
- **Pydantic** para validação de dados  




