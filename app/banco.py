import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"],
)


def inserir_cofre(cofre: dict) -> None:
    supabase.table("cofres").insert(cofre).execute()


def buscar_cofre(cofre_id: str) -> dict | None:
    resposta = (
        supabase.table("cofres")
        .select("*")
        .eq("id", cofre_id)
        .execute()
    )
    return resposta.data[0] if resposta.data else None


def inserir_segredo(segredo: dict) -> None:
    supabase.table("segredos").insert(segredo).execute()


def listar_segredos(cofre_id: str) -> list[dict]:
    resposta = (
        supabase.table("segredos")
        .select("id, titulo, usuario, url, criado_em, atualizado_em")
        .eq("cofre_id", cofre_id)
        .execute()
    )
    return resposta.data


def buscar_segredo(segredo_id: str, cofre_id: str) -> dict | None:
    resposta = (
        supabase.table("segredos")
        .select("*")
        .eq("id", segredo_id)
        .eq("cofre_id", cofre_id)
        .execute()
    )
    return resposta.data[0] if resposta.data else None


def atualizar_segredo(segredo_id: str, cofre_id: str, dados: dict) -> None:
    (
        supabase.table("segredos")
        .update(dados)
        .eq("id", segredo_id)
        .eq("cofre_id", cofre_id)
        .execute()
    )


def remover_segredo(segredo_id: str, cofre_id: str) -> None:
    (
        supabase.table("segredos")
        .delete()
        .eq("id", segredo_id)
        .eq("cofre_id", cofre_id)
        .execute()
    )
