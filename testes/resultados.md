# Resultados dos testes obrigatorios

Os testes foram executados com a API conectada ao Supabase e pela interface Swagger em `http://127.0.0.1:8001/docs`. As evidencias devem ser salvas em `testes/evidencias/` sem expor a senha-mestra ou a chave do Supabase.

## Preparacao validada - Criacao do cofre

- Procedimento: executar `POST /cofres` pelo Swagger em `http://127.0.0.1:8001/docs`.
- Resultado esperado: HTTP `201` com o identificador do cofre.
- Resultado observado: aprovado. A API retornou HTTP `201` e um identificador UUID, confirmando a gravacao na tabela `cofres`.
- Evidencia: captura da resposta `201` do Swagger, usada na documentacao da execucao.

## Teste 1 - Nonces distintos

- Procedimento: cadastrar os segredos `teste 1` e `teste 1-2` no mesmo cofre usando a mesma senha.
- Resultado esperado: `nonce` e `criptograma` diferentes.
- Resultado observado: aprovado. A consulta retornou `nonces_diferentes = true` e `criptogramas_diferentes = true`.
- Consulta usada: comparacao dos campos `nonce` e `criptograma` entre os titulos `teste 1` e `teste 1-2`.
- Evidencia: `testes/evidencias/Teste1/teste1-1.png` e `testes/evidencias/Teste1/teste1-2.png`

## Teste 2 - Senha-mestra incorreta

- Procedimento: ler o segredo `e7768eea-c949-4b4d-990e-b959541c183f` usando senha-mestra incorreta.
- Resultado esperado: HTTP `401`, sem senha no corpo.
- Resultado observado: aprovado. A API retornou HTTP `401 Unauthorized` com a mensagem `senha-mestra incorreta`, sem expor o segredo.
- Evidencia: `testes/evidencias/Teste2/Teste2.png`

## Teste 3 - Dados armazenados

- Procedimento: consultar diretamente `public.segredos` no Supabase usando o filtro do cofre testado.
- Resultado esperado: apenas campos Base64 e metadados, sem senha legivel.
- Resultado observado: aprovado. A consulta exibiu titulo, usuario e URL, além de nonce, criptograma e etiqueta; nenhuma senha foi armazenada ou exibida.
- Consulta usada: `select id, titulo, usuario, url, nonce, criptograma, etiqueta from public.segredos` filtrada pelo `cofre_id` testado.
- Evidencia: `testes/evidencias/Teste3/Teste3.png`

## Teste 4 - Registro adulterado

- Procedimento: alterar um caractere de `criptograma` no segredo `66821e72-ce72-4037-b956-a9d6ba326c82` e realizar a leitura com a senha-mestra correta.
- Resultado esperado: HTTP `500`, sem texto claro.
- Resultado observado: aprovado. A API retornou HTTP `500` com a mensagem `registro adulterado`, sem expor o texto claro.
- Operacao usada: alteracao de um caractere do campo `criptograma` no Supabase antes da leitura.
- Evidencia: `testes/evidencias/Teste4/Teste4.png`

## Teste 5 - Troca de criptogramas

- Procedimento: copiar `nonce`, `criptograma` e `etiqueta` do segredo `b81210c6-d0ba-40ee-b53e-9c8d9f4d6f72` para o segredo `e7768eae-c949-4b4d-990e-b959541c183f`.
- Resultado esperado: leitura recusada por AAD invalido, com HTTP `500`.
- Resultado observado: aprovado. A leitura do segredo de destino retornou HTTP `500` com a mensagem `registro adulterado`, confirmando que o AAD impediu a troca entre registros.
- Operacao usada: copia de `nonce`, `criptograma` e `etiqueta` do registro de origem para o registro de destino.
- Evidencia: `testes/evidencias/Teste5/Teste5.png`

## Identificadores usados

- Cofre: `00412cc2-318c-4001-8592-c67ef94d1758`.
- Segredo usado no Teste 4: `66821e72-ce72-4037-b956-a9d6ba326c82`.
- Segredo de origem no Teste 5: `b81210c6-d0ba-40ee-b53e-9c8d9f4d6f72`.
- Segredo de destino no Teste 5: `e7768eea-c949-4b4d-990e-b959541c183f`.

Os identificadores nao sao credenciais. A senha-mestra e os valores do arquivo `.env` nao devem ser incluidos neste relatorio ou nas capturas.
