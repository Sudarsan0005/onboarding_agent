from src.agent.assistant_manager import Assistant
from fastapi import FastAPI, HTTPException, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from fastapi import UploadFile, Form,APIRouter
from fastapi.responses import JSONResponse
from twillio_manager.twillio_manager import download_image,send_twilio
from db_manager.db_manager import DatabaseManager
from pyngrok import ngrok
import nest_asyncio
import uvicorn
from typing import Optional

router = APIRouter()
assistant_client = Assistant()
db_manager = DatabaseManager()
nest_asyncio.apply()
phone_no_tracking={}

@router.post("/enrollment_qa")
async def enrollment_qa(
        phone_no: str = Form(...,alias="From"),
        Body: str = Form(""),
        NumMedia: int = Form(0),
        MediaUrl0: Optional[str] = Form(None),
        MessageSid: str = Form(...)
):
    try:
      phone_no=phone_no.replace("whatsapp:","")
      # phone_thread_id=phone_no_tracking.get(phone_no,"")
      phone_thread_id = db_manager.get_user_setting(phone_no=phone_no)
      if phone_thread_id=="":
        phone_thrd_id = assistant_client.create_thread()
        phone_thread_id = phone_thrd_id.id
        db_manager.insert_user_setting(phone_no=phone_no,thread_id=phone_thread_id)
        # phone_no_tracking[phone_no]=phone_thread_id
        print("thread id.>>>>>>>>>>")
        print(phone_thread_id)
      if NumMedia > 0 and MediaUrl0:
        stored_img_path = await download_image(media_url=MediaUrl0,phone_no=phone_no)
        # doc_data= await extract_doc_info(stored_img_path)
        if Body!="":
            doc_data= f"User message: {Body}" + '\n' + f"Doc path: {stored_img_path}"
            db_manager.insert_user_conversation(actor="user", phone_no=phone_no, message=Body, doc_type="", doc_path=stored_img_path)
            ai_response = await assistant_client.run_assistant(phone_thread_id,doc_data)
            db_manager.insert_user_conversation(actor="ai", phone_no=phone_no, message=ai_response, doc_type="",
                                                doc_path="")
      else:
        db_manager.insert_user_conversation(actor="user",phone_no=phone_no,message=Body,doc_type="",doc_path="")
        ai_response = await assistant_client.run_assistant(phone_thread_id,Body)
        db_manager.insert_user_conversation(actor="ai", phone_no=phone_no, message=ai_response, doc_type="", doc_path="")
      print(f"AI response>>>>>>>>{ai_response}")
      message_id = await send_twilio(msg=str(ai_response),sender=phone_no)
      if message_id:
        return JSONResponse({"status":"message forwared successfully"})
      else:
        return JSONResponse({"status":"not success"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/create_assistant")
async def create_assistant(
assistant_prompt: str = Form(...,alias="assistant_prompt"),
assistant_name:str = Form(...,alias="assistant_name"),
model:str=Form(...,alias="model")
):
    try:
        assistant_id = assistant_client.create_assistant(assistant_name=assistant_name,model=model)
        updated_assistant_id = assistant_client.update_assistant(assistant_prompt=assistant_prompt)
        return updated_assistant_id
    except Exception as e:
        print(f"Error>> {e}")
        return ''
