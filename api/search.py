from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import openai
import os

openai.api_key = os.environ["OPENAI_API_KEY"]
app = FastAPI()

@app.post("/api/search")
async def search(request: Request):
    data = await request.json()
    prompt = f"""
    You're a fashion assistant. A user is looking for clothes matching:
    - Size: {data['shirtSize']}
    - Gender: {data['gender']}
    - Country: {data['country']}
    - Preference: {data['channel']}
    - Price Range: ${data['minPrice']} to ${data['maxPrice']}
    - Item Query: {data['query']}

    Give 20 online product links matching these filters. Each result must have:
    - name
    - size
    - price
    - link (must be valid)

    If 20 not available, fill extras with similar items. Format as:
    [{"name": "...", "size": "...", "price": ..., "link": "..."}, ...]
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    try:
        results = eval(response.choices[0].message['content'])
        return JSONResponse({"results": results})
    except:
        return JSONResponse({"results": []})
