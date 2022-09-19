"""Boiletplate for Anki Connect"""

import json
import urllib.request


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
