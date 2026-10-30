# Roteiro passo a passo - Sistema da Assistência Técnica de Celulares

## 1. Pré-requisitos
Python 3.10+, MySQL 8+ em execução e um terminal aberto na pasta do projeto.

## 2. Ambiente virtual e dependências
```
cd sistema
python -m venv venv
venv\Scripts\activate          (Windows)   |   source venv/bin/activate   (Linux/Mac)
pip install -r requirements.txt
```
Esperado: Flask, bcrypt e mysql-connector-python instalados sem erro.

## 3. Criar e popular o banco
```
mysql -u root -p < ../saep_db.sql
mysql -u root -p -e "USE saep_db; SELECT COUNT(*) FROM usuarios; SELECT COUNT(*) FROM clientes; SELECT COUNT(*) FROM aparelhos; SELECT COUNT(*) FROM servicos; SELECT COUNT(*) FROM agendamentos;"
```
Esperado: cada tabela com 3 registros.

## 4. Configurar a conexão (variáveis de ambiente)
Linux/Mac: `export DB_USER=root DB_PASSWORD=suasenha SECRET_KEY=uma-chave-longa`
Windows (PowerShell): `$env:DB_USER="root"; $env:DB_PASSWORD="suasenha"; $env:SECRET_KEY="uma-chave-longa"`

## 5. Testar a conexão
`python testar_conexao.py`  ->  esperado: `Conexão OK: {'banco': 'saep_db', 'versao': '8.x'}`
Se falhar: confira se o MySQL está ativo, usuário/senha e se o banco foi criado (passo 3).

## 6. Subir o servidor
`python app.py` e abrir http://localhost:5000

## 7. Testar o login
| Teste | Ação | Esperado |
|---|---|---|
| Falha | usuário `admin`, senha `errada` | mensagem "Usuário ou senha inválidos." |
| Vazio | enviar sem preencher | "Informe usuário e senha." |
| Sucesso | `admin` / `admin123` | vai para a tela principal |
| Proteção | abrir /clientes sem login | redireciona para /login |

## 8. Tela principal
Deve mostrar "Usuário: Administrador", links (Clientes, Aparelhos, Agendamentos) e o botão **Sair** (volta ao login e invalida a sessão).

## 9. Clientes
1. Cadastrar: nome, use um CPF novo e válido (ex.: `123.456.789-09`; o `529.982.247-25` já existe no banco). Esperado: aparece na lista.
2. CPF sem 11 dígitos (ex.: `123`) -> "CPF deve conter 11 dígitos."
3. CPF repetido -> "Já existe cliente com este CPF."
4. Buscar por "maria" e Buscar com CPF completo: a lista é atualizada.
5. Editar: clique em Editar, altere o telefone, Salvar, busque de novo e confirme a alteração.
6. Criptografia: `mysql -u root -p -e "SELECT nome, cpf_hash FROM saep_db.clientes;"` -> o CPF aparece como hash iniciado por `$2b$10$`.

## 10. Aparelhos
1. Cadastrar com cliente selecionado + IMEI novo (ex.: `352099001761481`), marca, modelo e defeito -> sucesso.
2. Sem selecionar cliente -> o navegador bloqueia; via API retorna "Selecione o cliente...".
3. IMEI inválido (ex.: `12345`) -> "IMEI inválido (informe os 15 dígitos)."; IMEI repetido (com ou sem espaços/hífens) -> "IMEI já cadastrado."
4. Editar e excluir (excluir aparelho com agendamento é bloqueado).

## 11. Agendamentos
1. A listagem vem ordenada por data (o de 01/11 aparece antes do de 03/11), com dados do cliente e do aparelho.
2. Criar novo agendamento escolhendo aparelho, serviço (reparo) e data.
3. Reagendar: clique em Reagendar, mude a data, salve; a lista reordena.
4. Conferir no banco: `SELECT id, data_agendamento FROM saep_db.agendamentos ORDER BY 2;`

## 12. Expiração da sessão
Tempo: 30 min (`EXPIRACAO_SEGUNDOS` em `autenticacao.py`). Para testar rápido, troque para 60, faça login, espere 1 min e clique em qualquer ação: volta ao login com "Sessão expirada".

## 13. Testes por API (opcional)
```
curl -c c.txt -H "Content-Type: application/json" -d '{"login":"admin","senha":"admin123"}' localhost:5000/api/login
curl -b c.txt localhost:5000/api/teste-conexao
curl -b c.txt "localhost:5000/api/clientes?q=maria"
```

## 14. Entrega
Crie `SeuNomeCompleto.zip` na área de trabalho com: documentacao.pdf, der.png/der.pdf, saep_db.sql e a pasta `sistema`.
