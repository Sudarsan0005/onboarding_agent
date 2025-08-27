import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.agent_router import router
from constant import PORT

app = FastAPI(docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

# Start ngrok tunnel
# ngrok.kill()
# public_url = ngrok.connect(4001)
# print("Public URL:", public_url)
#
# # Run server in background
# uvicorn.run(app, host='0.0.0.0', port=4001)
