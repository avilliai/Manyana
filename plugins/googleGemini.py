import asyncio
import os

import google.generativeai as genai
async def geminirep(ak,messages):
    # Or use `os.getenv('GOOGLE_API_KEY')` to fetch an environment variable.
    GOOGLE_API_KEY=ak

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel('gemini-pro')



    #print(type(messages))

    response = model.generate_content(messages)


    print(response.text)
    return response.text

