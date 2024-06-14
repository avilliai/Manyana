import asyncio
import os

import google.generativeai as genai
async def geminirep(ak,messages,model1="Gemini"):
    # Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
    model1="gemini-1.5-flash"

    GOOGLE_API_KEY=ak
    
    genai.configure(api_key=GOOGLE_API_KEY)

    #model = genai.GenerativeModel('gemini-pro')
    generation_config = {
      "candidate_count": 1,
      "max_output_tokens": 256,
      "temperature": 1.0,
      "top_p": 0.7,
    }

    safety_settings=[
      {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
      },
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
      },
      {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
      },
      {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
      },
      {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
      },
    ]

    model = genai.GenerativeModel(
        model_name=model1,
        generation_config=generation_config,
        safety_settings=safety_settings
    )


    #print(type(messages))

    response = model.generate_content(messages)


    #print(response.text)
    return response.text

