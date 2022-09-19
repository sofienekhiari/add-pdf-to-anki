# pylint: disable=invalid-name
"""Page that batch creates decks"""

import json
import urllib.request
import streamlit as st


def request(action, **params):
    """Basic structure for a HTTP request to Anki Connect"""
    return {"action": action, "params": params, "version": 6}


def invoke(action, **params):
    """Send request to Anki Connect"""
    request_json = json.dumps(request(action, **params)).encode("utf-8")
    response = json.load(
        urllib.request.urlopen(  # pylint: disable=consider-using-with
            urllib.request.Request("http://localhost:8765", request_json)
        )
    )
    if len(response) != 2:
        raise Exception("response has an unexpected number of fields")
    if "error" not in response:
        raise Exception("response is missing required error field")
    if "result" not in response:
        raise Exception("response is missing required result field")
    if response["error"] is not None:
        raise Exception(response["error"])
    return response["result"]


st.write(
    """
# Batch create decks
This page creates multiple decks from a given list.
In said list, deck names must be on a seperate line.
"""
)

with st.form("batch_create_decks"):
    parent_deck = st.text_area(label="Parent deck")
    decks_list_str = st.text_area(label="Decks list")
    form_submitted = st.form_submit_button("Create")

if form_submitted and decks_list_str != "":
    decks_list = decks_list_str.split("\n")
    decks_list = [
        parent_deck + "::" + deck_name if parent_deck != "" else deck_name
        for deck_name in decks_list
    ]
    try:
        for index, deck_name in enumerate(decks_list):
            invoke("createDeck", deck=deck_name)
    except:  # pylint: disable=bare-except
        st.error("🚨 There was a problem creating (one or more of) the decks.")
    else:
        st.success("✅ The decks were successfully created.")
