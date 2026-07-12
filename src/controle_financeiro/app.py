from __future__ import annotations

from pathlib import Path

import streamlit as st


def main() -> None:
    st.set_page_config(page_title="controle-financeiro", layout="wide")
    st.title("Controle Financeiro")
    st.caption("Setup inicial com workflow orientado à IA.")

    st.info("Nesta etapa o projeto foca em estrutura, processo e documentação. A modelagem vem depois.")

    col1, col2 = st.columns(2)
    col1.subheader("O que já está preparado")
    col1.write("- Entrypoint Streamlit")
    col1.write("- README do setup inicial")
    col1.write("- Templates de IA e SDD")

    col2.subheader("Próximos passos")
    col2.write("- Criar a primeira spec")
    col2.write("- Definir o modelo de dados")
    col2.write("- Implementar a primeira funcionalidade")

    st.caption(f"Workspace: {Path(__file__).resolve().parent.parent.parent.name}")


if __name__ == "__main__":
    main()
