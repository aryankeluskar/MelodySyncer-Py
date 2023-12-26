import uvicorn
from os import getenv

if __name__ == "__main__":
   print("Starting server...")
   uvicorn.run("index:app", host="0.0.0.0", port=int(getenv("PORT", 3000)), reload=True)