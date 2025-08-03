from src.agent.assistant_manager import Assistant
from fastapi import FastAPI, HTTPException, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from fastapi import UploadFile, Form,APIRouter
from fastapi.responses import JSONResponse
from pyngrok import ngrok
import nest_asyncio
import uvicorn
from typing import Optional

router = APIRouter()
nest_asyncio.apply()

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
        phone_thrd_id = client.beta.threads.create()
        phone_thread_id = phone_thrd_id.id
        phone_no_tracking[phone_no]=phone_thread_id
        print("thread id.>>>>>>>>>>")
        print(phone_thread_id)
      if NumMedia > 0 and MediaUrl0:
        stored_img_path = await download_image(media_url=MediaUrl0,phone_no=phone_no)
        doc_data= await extract_doc_info(stored_img_path)
        if Body!="":
          doc_data= doc_data + f"User message: {Body}"
        print(f"doc data>>>>>>{doc_data}")
        ai_response = await run_assistant(assistant_id,phone_thread_id,doc_data)
      else:
        ai_response = await run_assistant(assistant_id,phone_thread_id,Body)
      print(f"AI response>>>>>>>>{ai_response}")
      message_id = await send_twilio(msg=str(ai_response),sender=phone_no)
      if message_id:
        return JSONResponse({"status":"message forwared successfully"})
      else:
        return JSONResponse({"status":"not success"})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Start ngrok tunnel
# ngrok.kill()
public_url = ngrok.connect(4001)
print("Public URL:", public_url)

# Run server in background
uvicorn.run(app, host='0.0.0.0', port=4001)
