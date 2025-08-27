from src.agent.assistant_manager import Assistant
from fastapi import FastAPI, HTTPException, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from fastapi import UploadFile, Form,APIRouter
from fastapi.responses import JSONResponse
from twillio_manager.twillio_manager import download_image,send_twilio
from pyngrok import ngrok
import nest_asyncio
import uvicorn
from typing import Optional

router = APIRouter()
assistant_client = Assistant()
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
      phone_thread_id=phone_no_tracking.get(phone_no,"")
      if phone_thread_id=="":
        phone_thrd_id = assistant_client.create_thread()
        phone_thread_id = phone_thrd_id.id
        phone_no_tracking[phone_no]=phone_thread_id
        print("thread id.>>>>>>>>>>")
        print(phone_thread_id)
      if NumMedia > 0 and MediaUrl0:
        stored_img_path = await download_image(media_url=MediaUrl0,phone_no=phone_no)
        # doc_data= await extract_doc_info(stored_img_path)
        if Body!="":
            doc_data= f"User message: {Body}" + '\n' + f"Doc path: {stored_img_path}"
            ai_response = await assistant_client.run_assistant(phone_thread_id,doc_data)
      else:
        ai_response = await assistant_client.run_assistant(phone_thread_id,Body)
      print(f"AI response>>>>>>>>{ai_response}")
      message_id = await send_twilio(msg=str(ai_response),sender=phone_no)
      if message_id:
        return JSONResponse({"status":"message forwared successfully"})
      else:
        return JSONResponse({"status":"not success"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

