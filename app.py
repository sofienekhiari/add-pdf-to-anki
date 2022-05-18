import streamlit as st
import json
import urllib.request
from uuid import uuid4
import os
import pathlib
import PyPDF2


# Wrapper to catch errors in case commands not installed
def run_command(command):
    command_exit_code = os.system(command)
    if command_exit_code !=0:
        raise Exception(f"There was an error while running the following command: {command}")


# Anki Connect Boilerplate (1/2)
def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


# Anki Connect Boilerplate (2/2)
def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


# Function that creates a single note
def add_pta_note(deck_name, slide_path):
    # Create the basic structure for the note
    slide_note = {
        "deckName": deck_name,
        "modelName": "Khiari Basic",
        "fields": {"Question": "TODO"},
        "options": {"allowDuplicate": True},
        "tags": ["marked"],
        "picture": {
            "path": slide_path,
            "filename": f"add-pta-{uuid4()}.png",
            "fields": ["Answer"]
            }
        }
    # Add the note
    note_id = invoke('addNote', note=slide_note)
    # Print the result
    print(f"Note {note_id} created.")


# Write the introduction text
st.write("""
# Add PDF file to Anki
This script allows you to add a **PDF** file to **Anki** as a deck of cards where each card contains one page of the PDF file. The cards are _marked_ and _suspended_ by default to not be taken into account in the study routine until they are edited and made ready.
""")

# Create the form
with st.form("pta-form"):
    st.write("""
    ### Data entry
    Use the following form to enter the necessary details for the script to run.
    """)
    deck_name = st.text_area("Deck Name", help="The deck name may include parents, for more information see syntax for nested decks.")
    pdf_full_path = st.text_area("File Full Path", help="The full path must include the file name and extension.")
    st.write("_Please verify the entered information before running the script._")
    submitted = st.form_submit_button("Add file to Anki")

# Run the script on submission
if submitted:

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
        
        # Create the PDF page
        run_command(f"cd {tmp_folder} && pdftoppm '{pdf_full_path}' pta -png -progress -f {pdf_page_nb} -l {pdf_page_nb}")
        
        # Create the associated note
        for filename in os.listdir(tmp_folder):
            parent_folder=pathlib.Path(filename).parent.absolute()
            filepath = f"{parent_folder}/{tmp_folder}/{filename}"
            add_pta_note(deck_name, filepath)
        
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
