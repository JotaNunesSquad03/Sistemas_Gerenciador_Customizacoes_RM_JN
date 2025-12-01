Executando o Back-end (API) 

Clonar o repositório: git clone 
https://github.com/JotaNunesSquad03/Sistemas_Gerenciador_Customizacoes_RM_JN.git cd Sistemas_Gerenciador_Customizacoes_RM_JN 
 
Configurar o ambiente virtual e dependências:
python -m venv venv 

Ativar ambiente virtual :
○ Ativar (Windows): venv\Scripts\activate 
○ Ativar (Linux/Mac): source venv/bin/activate 

○ Instalar dependências: 
pip install -r requirements.txt

Executar a API: 
uvicorn app.main:app --reload  (A API rodará em 
http://127.0.0.1:8000) 
