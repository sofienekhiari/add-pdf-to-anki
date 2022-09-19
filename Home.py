# pylint: disable=invalid-name
"""App that adds pdf files to Anki among other things"""

import streamlit as st
from pta_processing import add_pta

# Write the introduction text
st.write(
    """
# Add PDF to Anki
This script allows you to add a **PDF** file to **Anki** as a deck of cards.
In this case, each card contains one page of the PDF file.
The cards are _marked_ and _suspended_ by default.
That way, they are not taken into account in the study routine until they are edited and made ready.
"""
)

# Create the form
with st.form("pta-form"):
    st.write(
        """
    ### Data entry
    Use the following form to enter the necessary details for the script to run.
    """
    )
    deck_name = st.text_area(
        "Deck Name",
        help="The deck name may include parents, for more information see syntax for nested decks.",
    )
    pdf_full_path = st.text_area(
        "File Full Path", help="The full path must include the file name and extension."
    )
    st.write("_Please verify the entered information before running the script._")
    submitted = st.form_submit_button("Add file to Anki")

# Run the script on submission
if submitted:
    add_pta(deck_name, pdf_full_path)
