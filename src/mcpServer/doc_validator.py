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
def aadhar_otp_generator(aadhar_no:str):
    try:
        url = "https://bpilmobile.bergerindia.com/DIGITALSTAGING/api/v1.0/DigitalStaging/aadhaar-otp-request"

        payload = json.dumps({
            "user_id": "0",
            "aadhaar_no":aadhar_no
        })
        headers = {
            'Content-Type': 'application/json',
            'AuthKey': 'DbZ6ddxltpijv5r3g5g5umrxodzh3qbvey'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        jresponse = json.loads(response.text)
        return jresponse
    except Exception as e:
        return {}

def aadhar_otp_validator(client_id:str,otp:str):
    try:
        url = "https://bpilmobile.bergerindia.com/DIGITALSTAGING/api/v1.0/DigitalStaging/aadhaar-otp-validate"

        payload = json.dumps({
            "user_id": "0",
            "client_id": client_id,
            "otp": otp
        })
        headers = {
            'Content-Type': 'application/json',
            'AuthKey': 'DbZ6ddxltpijv5r3g5g5umrxodzh3qbvey'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)

        jresponse = json.loads(response.text)
        return jresponse
    except Exception as e:
        return {}

def pan_validator(pan_no:str):
    try:
        url = "https://bpilmobile.bergerindia.com/DIGITALSTAGING/api/v1.0/DigitalStaging/pan-validate"

        payload = json.dumps({
            "pan": pan_no
        })
        headers = {
            'Content-Type': 'application/json',
            'AuthKey': 'DbZ6ddxltpijv5r3g5g5umrxodzh3qbvey'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

        jresponse = json.loads(response.text)
        return jresponse
    except Exception as e:
        return {}

def ifsc_validator(ifsc_no:str):
    try:
        url = f"https://ifsc.razorpay.com/{ifsc_no}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.text != "Not Found":
            return {"status": 0, "message": "Validation failed: IFSC code Invalid"}
        else:
            return json.loads(response.text)
    except Exception as e:
        return {"status":0,"message":"Please provide valid document"}

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
@mcp.tool()
def aadhar_otp_generator(doc_path:str):
    '''
    send otp to phone number linked with aadhar card by extracting data from document
    Args:
        doc_path: document path
    '''
    try:
        data = extract_doc_info(image_path=doc_path)
        if data["type"]=="aadhar":
            otp_generation_status = aadhar_otp_generator(aadhar_no=data["aadhar_no"])
            return otp_generation_status
        return {"status":"docuemnt is not valid please provide a valid aadhar card"}
    except Exception:
        return {"status":"Failed"}

@mcp.tool()
def aadhar_otp_validator(client_id:str, otp:str):
    '''
    validating opt if it is correct or not
    Args:
        client_id: unique id generated while generating otp from Aadhar
        otp: otp
    '''
    try:
        status = aadhar_otp_validator(client_id=client_id,otp=otp)
        return status
    except Exception:
        return {"status":"Failed"}

@mcp.tool()
def pan_validator(doc_path:str):
    '''
    extracting pancard details from document and return validation status
    Args:
        doc_path: document path
    '''
    try:
        data = extract_doc_info(image_path=doc_path)
        if data["type"]=="pan":
            pan_validation_status = pan_validator(pan_no=data["pan_no"])
            return pan_validation_status
        return {"status":"docuemnt is not valid please provide a valid pan card"}
    except Exception:
        return {"status":"Failed"}

@mcp.tool()
def ifscCodeValidator(doc_path:str):
    '''
    extracting ifsc code details from document and return validation status
    Args:
        doc_path: document path
    '''
    try:
        data = extract_doc_info(image_path=doc_path)
        if data["type"]=="Passbook":
            ifsc_validation_status = ifsc_validator(ifsc_no=data["ifsc_code"])
            return ifsc_validation_status
        return {"status":"document is not valid please provide a valid pan card"}
    except Exception:
        return {"status":"Failed"}


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

