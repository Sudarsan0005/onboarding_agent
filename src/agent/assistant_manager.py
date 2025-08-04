import json

from openai import OpenAI
from constant import (DB_Manager,doc_extraction_prompt)
from src.mcpServer.mcpclient import (tool_configuration,call_mcp_tools)
import os
import time
client = OpenAI()

class Assistant:
    def create_assistant(self,assistant_name:str,model:str)->str:
        try:
            assistant_id = DB_Manager.get_assistant_id()['assistant_id']
            if assistant_id is not None:
                assistant = client.beta.assistants.create(
              name=assistant_name,
              model=model
            )
                assistant_id = assistant.id
                DB_Manager.update_mod_setting(assistant_id=assistant.id)
            return assistant_id
        except Exception as e:
            raise Exception(f"Error while creating assistant {e}")
    def update_assistant(self, assistant_prompt):
        try:
            assistant_id = DB_Manager.get_assistant_id()['assistant_id']
            tools = tool_configuration()
            updated_assistant = client.beta.assistants.update(assistant_id=assistant_id,
                                      instructions=assistant_prompt,
                                      temperature=0.6,tools=tools)
            DB_Manager.update_mod_setting(assistant_prompt=assistant_prompt)
            return updated_assistant.id
        except Exception as e:
            raise Exception(f"Error while updating assistant {e}")
    def create_thread(self):
        try:
            thread = client.beta.threads.create()
            return thread.id
        except Exception as e:
            raise Exception(f"Error while creating thread {e}")

    async def run_assistant(self,thread_id:str, user_response:str):
        try:
            assistant_id = DB_Manager.get_assistant_id()['assistant_id']
            message = client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_response,

            )
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            while True:
                time.sleep(2)
                if run.status == "requires_action":
                    tool_outputs=[]
                    for tool in run.required_action.submit_tool_outputs.tool_calls:
                        if tool.function.name == "validate_dealer":
                            tool_name = tool.function.name
                            tool_args = tool.function.arguments
                            tool_args = json.loads(tool_args)
                            # Execute tool call
                            result = await call_mcp_tools(tool_name,tool_args)

                            tool_outputs.append({
                                "tool_call_id": tool.id,
                                "output": result
                            })
                    if tool_outputs:
                        try:
                            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                                thread_id=thread_id,
                                run_id=run.id,
                                tool_outputs=tool_outputs
                            )
                            print("Tool outputs submitted successfully.")
                        except Exception as e:
                            print("Failed to submit tool outputs:", e)
                    else:
                        print("No tool outputs to submit.")
                    print(run.status)
                elif run.status == 'completed':
                    messages = client.beta.threads.messages.list(
                        thread_id=thread_id
                    )
                    print("Assistant response::::")
                    print(messages.data[0].content[0].text.value)
                    print(
                        f"Token useage::: \n Total token : {run.usage.total_tokens}\n Prompt token : {run.usage.prompt_tokens}\n completion token : {run.usage.completion_tokens}")
                    return messages.data[0].content[0].text.value
                else:
                    print(run.status)
        except Exception as e:
            print(e)


import base64
@staticmethod
async def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
async def extract_doc_info(image_path:str):
  try:
    base64_image = await encode_image(image_path)
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": doc_extraction_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "image_url",
                      "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
    )
    print(f"prompt token::: {response.usage.prompt_tokens}")
    print(f"completion_tokens::: {response.usage.completion_tokens}")
    print(f"total_tokens::: {response.usage.total_tokens}")
    print(f"Openai text>>>>> {response.choices[0].message.content}")
    return json.loads(response.choices[0].message.content.replace("```","").replace("json",""))
  except Exception as e:
    print(e)

