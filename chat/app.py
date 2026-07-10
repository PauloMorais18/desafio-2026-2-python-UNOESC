"""Initial Streamlit chat shell."""

import streamlit as st


def main() -> None:
    """Render a placeholder chat UI until it consumes the questions API."""
    st.set_page_config(page_title="Academic Assistant Chat")
    st.title("Academic Assistant Chat")
    st.info("TODO: This interface will send questions to the API endpoint.")


if __name__ == "__main__":
    main()

