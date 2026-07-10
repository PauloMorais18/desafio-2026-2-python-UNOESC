"""Initial Streamlit dashboard shell."""

import streamlit as st


def main() -> None:
    """Render a placeholder dashboard until it consumes the API."""
    st.set_page_config(page_title="Academic Assistant Dashboard", layout="wide")
    st.title("Academic Assistant Dashboard")
    st.info("TODO: This dashboard will consume the statistics API endpoint.")


if __name__ == "__main__":
    main()

