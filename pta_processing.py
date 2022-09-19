"""Central processing for the PTA process"""

import streamlit as st
from uuid import uuid4
import os
import pathlib
import PyPDF2
from ac_boilerplate import invoke
from wrappers import run_command

# DEFAULT PTA NOTES PARAMETERS
# The following parameters are the author's
# default preferences. You can change them
# to better suit your preferences.
NOTE_MODEL_NAME = "ClozeSK"
EVALUATION_FIELD = "Evaluation"
EVALUATION_TEMPLATE = "[[START]]<br>QUESTION<br>{{c1::ANSWER}}<br>[[END]]"
TAGS = ["marked"]
NOTES_FIELD = "Notes"
TEXT_FIELD = "Text"

def add_pta_note(deck_name, slide_path, slide_text):
    """Create a single PTA note"""
    # Create the basic structure for the note
    pta_note = {
        "deckName": deck_name,
        "modelName": NOTE_MODEL_NAME,
        "fields": {EVALUATION_FIELD: EVALUATION_TEMPLATE, TEXT_FIELD: slide_text},
        "options": {"allowDuplicate": True},
        "tags": TAGS,
        "picture": {
            "path": slide_path,
            "filename": f"add-pta-{uuid4()}.png",
            "fields": [NOTES_FIELD]
            }
        }
    # Add the note
    invoke('addNote', note=pta_note)

def add_pta(deck_name, pdf_full_path):
    """Add a PTA file"""
    # Add a message that the script is running
    st.write("""
    ### Progress details
    Running the script...
    """)
    # Add an empty progress bar
    pta_progress_bar = st.progress(0)
    # Create the deck
    invoke('createDeck', deck=deck_name)
    # Create a temporary folder
    tmp_folder = f".add-pta-{uuid4()}"
    run_command(f"mkdir {tmp_folder}")
    # Get the number of pages in the PDF
    with open(pdf_full_path, 'rb') as pdf_file:
        pdf_read = PyPDF2.PdfFileReader(pdf_file)
        pdf_pages_count = pdf_read.numPages
    # Iterate through the pages
    for pdf_page_index in range(pdf_pages_count):
        # Set the PDF page number
        pdf_page_nb = pdf_page_index + 1
        # Extract the text from the PDF page
        with open(pdf_full_path, 'rb') as pdf_file:
            pdf_read = PyPDF2.PdfFileReader(pdf_file)
            slide_text = pdf_read.pages[pdf_page_index].extract_text()
        # Create the PDF page
        run_command(f"cd {tmp_folder} && pdftoppm '{pdf_full_path}' pta -png -progress -f {pdf_page_nb} -l {pdf_page_nb}")
        # Create the associated note
        for filename in os.listdir(tmp_folder):
            parent_folder=pathlib.Path(filename).parent.absolute()
            filepath = f"{parent_folder}/{tmp_folder}/{filename}"
            add_pta_note(deck_name, filepath, slide_text)
        # Delete the PDF page
        run_command(f"rm -f {tmp_folder}/*")
        pta_progress = round(float(pdf_page_nb) * 100 / pdf_pages_count)
        pta_progress_bar.progress(pta_progress)
    # Delete the temporary folder
    run_command(f"rm -rf {tmp_folder}")
    # Suspend cards
    with st.spinner('Suspending newly created cards...'):
        # Get the cards ids
        cards_ids = invoke('findCards', query=f'"deck:{deck_name}"')
        # Suspend the cards by their ids
        invoke('suspend', cards=cards_ids)
    # Print a success message
    st.success('File added!')
