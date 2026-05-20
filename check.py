import os
from dotenv import load_dotenv

# This looks for the .env file
load_dotenv()

# This pulls the key from the .env file
key = os.getenv("GROQ_API_KEY")

if key:
    print("✅ Success! Your .env file is set up correctly.")
    print(f"Your key starts with: {key[:5]}...")
else:
    print("❌ Error: Could not find GROQ_API_KEY in the .env file.")