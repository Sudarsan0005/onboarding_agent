import logging

from mcp.server.fastmcp import FastMCP
import sys
import json
import os
from typing import Dict,Any,Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.agent.assistant_manager import extract_doc_info
mcp = FastMCP("doc validator")

import requests
import json




def d_codeValidator(code:str)->Dict[str,Any]:
    try:
        url = "https://bpilmobile.bergerindia.com/DIGITALSTAGING/api/v1.0/DigitalStaging/GetDealerCodeValidation"

        payload = json.dumps({
            "dlr_code": code
        })
        headers = {
            'Content-Type': 'application/json',
            'AuthKey': 'DbZ6ddxltpijv5r3g5g5umrxodzh3qbvey'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        jresponse = json.loads(response.text)
        return jresponse
    except Exception as e:
        return {}
@mcp.tool()
def validate_dealer(dealer_code:str)->Dict[str,Any]:
    '''
    Validate Dealer Code
    Args:
        dealer_code: dealer's code
    '''
    try:
        response = d_codeValidator(dealer_code)
        return response
    except Exception:
        return {}
# @mcp.tool()
# def aadhar_validator(doc_path:str):
#     '''
#     Validating aadhar card using card number
#     :return:
#     '''
#     try:
#         data = extract_doc_info(image_path=doc_path)
#
#     pass
#
@mcp.tool()
def pan_validator(doc_path:str):
    '''
    validating pan card using pan number
    :return:
    '''
    pass
# @mcp.tool()
# def ifsc_validator(doc_path:str):
#     '''
#     validating bank ifsc code return valid or not
#     :return:
#     '''
#     pass

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

