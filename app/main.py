from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, status

from app import banco
from app.cripto import (
	ITERACOES_PADRAO,
	aad_segredo,
	criar_verificador,
	decifrar,
	de_b64,
	derivar_chave,
	cifrar,
	gerar_sal,
	para_b64,
	senha_mestra_correta,
)
from app.modelos import NovoCofre, NovoSegredo


app = FastAPI(title="Cofre de Senhas")


def obter_chave(cofre_id: str, senha_mestra: str) -> tuple[dict, bytes]:
	cofre = banco.buscar_cofre(cofre_id)
	if cofre is None:
		raise HTTPException(status_code=404, detail="cofre nao encontrado")

	chave = derivar_chave(
		senha_mestra,
		de_b64(cofre["kdf_sal"]),
		cofre["kdf_iteracoes"],
	)
	if not senha_mestra_correta(
		chave,
		cofre["verificador_nonce"],
		cofre["verificador_criptograma"],
		cofre["verificador_etiqueta"],
		cofre_id,
	):
		raise HTTPException(status_code=401, detail="senha-mestra incorreta")
	return cofre, chave


@app.post("/cofres", status_code=status.HTTP_201_CREATED)
def criar_cofre(dados: NovoCofre) -> dict[str, str]:
	cofre_id = str(uuid4())
	sal = gerar_sal()
	chave = derivar_chave(dados.senha_mestra, sal, ITERACOES_PADRAO)
	nonce, criptograma, etiqueta = criar_verificador(chave, cofre_id)

	banco.inserir_cofre({
		"id": cofre_id,
		"nome": dados.nome,
		"kdf_sal": para_b64(sal),
		"kdf_iteracoes": ITERACOES_PADRAO,
		"verificador_nonce": nonce,
		"verificador_criptograma": criptograma,
		"verificador_etiqueta": etiqueta,
	})
	return {"id": cofre_id}


@app.post("/cofres/{cofre_id}/abrir")
def abrir_cofre(
	cofre_id: str,
	x_senha_mestra: str = Header(...),
) -> dict[str, str]:
	obter_chave(cofre_id, x_senha_mestra)
	return {"mensagem": "cofre aberto"}


@app.post("/cofres/{cofre_id}/segredos", status_code=status.HTTP_201_CREATED)
def criar_segredo(
	cofre_id: str,
	dados: NovoSegredo,
	x_senha_mestra: str = Header(...),
) -> dict[str, str]:
	_, chave = obter_chave(cofre_id, x_senha_mestra)
	segredo_id = str(uuid4())
	nonce, criptograma, etiqueta = cifrar(
		chave,
		dados.senha,
		aad_segredo(cofre_id, segredo_id),
	)

	banco.inserir_segredo({
		"id": segredo_id,
		"cofre_id": cofre_id,
		"titulo": dados.titulo,
		"usuario": dados.usuario,
		"url": dados.url,
		"nonce": nonce,
		"criptograma": criptograma,
		"etiqueta": etiqueta,
	})
	return {"id": segredo_id}


@app.get("/cofres/{cofre_id}/segredos")
def listar_segredos(
	cofre_id: str,
	x_senha_mestra: str = Header(...),
) -> list[dict]:
	obter_chave(cofre_id, x_senha_mestra)
	return banco.listar_segredos(cofre_id)


@app.get("/cofres/{cofre_id}/segredos/{segredo_id}")
def ler_segredo(
	cofre_id: str,
	segredo_id: str,
	x_senha_mestra: str = Header(...),
) -> dict:
	_, chave = obter_chave(cofre_id, x_senha_mestra)
	segredo = banco.buscar_segredo(segredo_id, cofre_id)
	if segredo is None:
		raise HTTPException(status_code=404, detail="segredo nao encontrado")

	try:
		senha = decifrar(
			chave,
			segredo["nonce"],
			segredo["criptograma"],
			segredo["etiqueta"],
			aad_segredo(cofre_id, segredo_id),
		)
	except ValueError:
		raise HTTPException(status_code=500, detail="registro adulterado")

	return {
		"id": segredo["id"],
		"titulo": segredo["titulo"],
		"usuario": segredo["usuario"],
		"url": segredo["url"],
		"senha": senha,
	}


@app.put("/cofres/{cofre_id}/segredos/{segredo_id}")
def atualizar_segredo(
	cofre_id: str,
	segredo_id: str,
	dados: NovoSegredo,
	x_senha_mestra: str = Header(...),
) -> dict[str, str]:
	_, chave = obter_chave(cofre_id, x_senha_mestra)
	if banco.buscar_segredo(segredo_id, cofre_id) is None:
		raise HTTPException(status_code=404, detail="segredo nao encontrado")

	nonce, criptograma, etiqueta = cifrar(
		chave,
		dados.senha,
		aad_segredo(cofre_id, segredo_id),
	)
	banco.atualizar_segredo(segredo_id, cofre_id, {
		"titulo": dados.titulo,
		"usuario": dados.usuario,
		"url": dados.url,
		"nonce": nonce,
		"criptograma": criptograma,
		"etiqueta": etiqueta,
	})
	return {"id": segredo_id}


@app.delete("/cofres/{cofre_id}/segredos/{segredo_id}")
def excluir_segredo(
	cofre_id: str,
	segredo_id: str,
	x_senha_mestra: str = Header(...),
) -> dict[str, str]:
	obter_chave(cofre_id, x_senha_mestra)
	if banco.buscar_segredo(segredo_id, cofre_id) is None:
		raise HTTPException(status_code=404, detail="segredo nao encontrado")
	banco.remover_segredo(segredo_id, cofre_id)
	return {"mensagem": "segredo removido"}
