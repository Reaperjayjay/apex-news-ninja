import os

print("-" * 30)
print("DIAGNOSING .ENV FILE")
print("-" * 30)

# 1. Check current folder
cwd = os.getcwd()
print(f"Current Folder: {cwd}")

# 2. List all files
files = os.listdir(cwd)
if ".env" in files:
    print("STATUS: Found file '.env'")
    
    # 3. Read the file to check for typos
    with open(".env", "r") as f:
        lines = f.readlines()
        found_key = False
        for i, line in enumerate(lines):
            clean_line = line.strip()
            # Skip empty lines or comments
            if not clean_line or clean_line.startswith("#"):
                continue
            
            # Check for the key
            if "GEMINI_API_KEY" in clean_line:
                found_key = True
                print(f"Line {i+1}: Found entry.")
                print(f"Raw Content: '{clean_line}'")
                
                # Check for common errors
                if ":" in clean_line and "=" not in clean_line:
                    print("ERROR: You used a COLON (:) instead of EQUALS (=).")
                    print("FIX: Change it to: GEMINI_API_KEY=AIza...")
                elif " = " in clean_line:
                    print("WARNING: You have spaces around the equals sign.")
                    print("FIX: Remove spaces: GEMINI_API_KEY=AIza...")
                elif "=" in clean_line:
                    print("FORMAT LOOKS GOOD: Variable=Value")
                else:
                    print("ERROR: No equals sign found.")

        if not found_key:
            print("ERROR: .env file exists, but 'GEMINI_API_KEY' is missing from it.")

elif ".env.txt" in files:
    print("ERROR: Found '.env.txt'. Windows added a hidden extension.")
    print("FIX: Rename the file and remove '.txt'.")

else:
    print("ERROR: No .env file found in this folder.")
    print("Did you create it inside the 'app' folder? Move it here.")

print("-" * 30)