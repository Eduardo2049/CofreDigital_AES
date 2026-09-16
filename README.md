# CofreDigital_AES

API de cofre de credenciais desenvolvida para a disciplina de Criptografia Aplicada.

## Equipe

Preencher com os nomes dos integrantes antes da entrega.

## Objetivo e modelo de ameacas

O sistema armazena credenciais em PostgreSQL por meio do Supabase. As senhas sao cifradas antes de serem gravadas e o banco nunca recebe a senha-mestra nem a chave derivada.

O projeto protege contra copia integral do banco, consulta SQL direta e adulteracao dos campos criptograficos. Ele nao protege um servidor de aplicacao comprometido durante o uso, senha-mestra fraca ou divulgada, nem oferece auditoria de acessos. Essas limitacoes fazem parte do escopo definido no PDF.

## Arquitetura

| Arquivo | Responsabilidade |
| --- | --- |
| `app/cripto.py` | PBKDF2, AES-GCM, Base64, verificador e AAD. |
| `app/banco.py` | Operacoes de leitura e escrita no Supabase. |
| `app/modelos.py` | Modelos Pydantic das requisicoes. |
| `app/main.py` | Rotas, respostas HTTP e orquestracao. |
| `sql/esquema.sql` | Tabelas, indice e politicas do Supabase. |
| `testes/resultados.md` | Procedimentos, resultados e evidencias. |

## Parametros criptograficos

- PBKDF2 com HMAC-SHA-256.
- Chave derivada de 32 bytes, equivalente ao AES-256.
- Sal aleatorio de 16 bytes por cofre.
- Minimo de 210.000 iteracoes, armazenadas em `kdf_iteracoes`.
- AES em modo GCM.
- Nonce aleatorio de 12 bytes a cada cifragem, inclusive nas atualizacoes.
- Etiqueta de autenticacao de 16 bytes.
- Campos binarios armazenados em Base64.
- AAD do verificador: `cofre_id`.
- AAD dos segredos: `cofre_id|segredo_id`.

O verificador cifra a frase fixa `cofre-ok`. Se ele falhar, a API responde `401`. Se o verificador funcionar e um segredo falhar na etiqueta, a API responde `500`, indicando possivel adulteracao.

## Instalacao

Requer Python 3.10 ou superior.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crie o arquivo `.env` na raiz. Use a URL do projeto Supabase e a chave publica `anon` ou `publishable`. Nunca use `service_role`, secret key, senha do banco ou JWT secret.

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-publica
```

O arquivo `.env` esta no `.gitignore`. O arquivo `.env.exemplo` documenta os nomes das variaveis sem conter credenciais reais.

## Banco de dados

No SQL Editor do Supabase, execute uma vez o conteudo de [sql/esquema.sql](sql/esquema.sql). O script cria as tabelas `cofres` e `segredos`, a chave estrangeira, o indice e as politicas RLS usadas neste laboratorio.

Os campos `titulo`, `usuario` e `url` ficam em texto claro para permitir listagem sem a senha-mestra. Os campos `nonce`, `criptograma` e `etiqueta` sao os dados protegidos do AES-GCM. A chave derivada e a senha-mestra nunca sao persistidas.

## Execucao

Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

A documentacao interativa fica em <http://127.0.0.1:8001/docs>. A rota `/` nao foi definida; portanto, acessar a raiz pode retornar `{"detail":"Not Found"}` sem indicar falha da API.

Se a porta `8000` estiver ocupada no Windows, use `8001` ou outra porta livre. A porta usada nas evidencias deste projeto foi `8001`.

## Rotas

Todas as rotas, exceto `POST /cofres`, exigem o cabecalho `X-Senha-Mestra`.

| Metodo | Rota | Comportamento |
| --- | --- | --- |
| POST | `/cofres` | Cria o cofre e retorna seu UUID. |
| POST | `/cofres/{id}/abrir` | Valida a senha-mestra pelo verificador. |
| POST | `/cofres/{id}/segredos` | Cifra e grava uma credencial. |
| GET | `/cofres/{id}/segredos` | Lista somente metadados. |
| GET | `/cofres/{id}/segredos/{sid}` | Decifra e retorna uma credencial. |
| PUT | `/cofres/{id}/segredos/{sid}` | Atualiza metadados e senha com novo nonce. |
| DELETE | `/cofres/{id}/segredos/{sid}` | Remove a credencial. |

Exemplo de criacao:

```http
POST /cofres
Content-Type: application/json

{
    "nome": "Equipe de suporte",
    "senha_mestra": "senha forte da equipe"
}
```

Resposta `201`:

```json
{"id": "id-do-cofre"}
```

Exemplo de criacao de segredo:

```http
POST /cofres/id-do-cofre/segredos
X-Senha-Mestra: senha forte da equipe
Content-Type: application/json

{
    "titulo": "Banco de dados",
    "usuario": "equipe",
    "url": "https://exemplo.test",
    "senha": "senha protegida"
}
```

Exemplo de leitura:

```http
GET /cofres/id-do-cofre/segredos/id-do-segredo
X-Senha-Mestra: senha forte da equipe
```

## Codigos de resposta

- `200`: abertura, leitura ou atualizacao concluida.
- `201`: cofre ou segredo criado.
- `401`: senha-mestra incorreta.
- `404`: cofre ou segredo inexistente.
- `422`: corpo ou campos invalidos, gerado pelo FastAPI.
- `500`: verificador aprovado, mas o registro do segredo falhou na autenticacao.

## Verificacao e evidencias

A criacao do cofre retornou `201` com UUID. Os cinco testes obrigatorios foram executados e aprovados:

1. Nonces e criptogramas diferentes para duas cifragens da mesma senha.
2. Senha-mestra incorreta rejeitada com `401`.
3. Consulta direta ao banco sem senha legivel.
4. Criptograma adulterado rejeitado com `500`.
5. Troca de criptograma entre registros rejeitada pelo AAD com `500`.

Os procedimentos, identificadores usados e resultados estao em [testes/resultados.md](testes/resultados.md). As capturas devem ser mantidas em `testes/evidencias/` com os nomes indicados nesse arquivo.

## Restricoes de seguranca

Nao armazenar ou registrar em logs:

- senha-mestra;
- chave derivada;
- senha de qualquer segredo em texto claro;
- valores de credenciais do `.env`.

O nonce nunca deve ser reutilizado com a mesma chave. Atualizacoes sempre geram uma nova cifragem e um novo nonce.

## Referencias

- NIST SP 800-38D, Galois/Counter Mode (GCM) and GMAC.
- NIST SP 800-132, Password-Based Key Derivation.
- OWASP Password Storage Cheat Sheet.
- Documentacao do PyCryptodome: <https://pycryptodome.readthedocs.io>.
- Documentacao do FastAPI: <https://fastapi.tiangolo.com>.
