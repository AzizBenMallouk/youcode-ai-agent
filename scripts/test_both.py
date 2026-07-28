import urllib.request
import json
import base64
import time

def run_evolution():
    print("Testing Evolution API...")
    url = "http://localhost:8090/instance/create"
    data = json.dumps({
        "instanceName": "youcode-ai",
        "token": "youcode-token",
        "qrcode": True
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "apikey": "super_secret_key"
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            qr = res_data.get("qrcode", {}).get("base64", "")
            if qr:
                # Save base64 QR to artifact
                with open("/home/bucketlister/.gemini/antigravity/brain/c1139cad-ee1f-4c58-af13-3840b33da408/whatsapp_qr.md", "w") as f:
                    f.write("# WhatsApp Evolution API QR Code\n\n")
                    f.write(f"![QR Code]({qr})\n\n")
                    f.write("Scan this with your WhatsApp app to connect your number to the system.")
                print("QR code artifact created successfully.")
            else:
                print("Instance created, but no QR code found in response.")
    except Exception as e:
        print(f"Failed to create Evolution instance: {e}")

def run_newsletter():
    print("Testing Newsletter MCP...")
    url = "http://localhost:8010/api/v1/invoke"
    
    # Step 1: Request
    data1 = json.dumps({
        "user_id": "212600000031@s.whatsapp.net",
        "message": "Salut ! J aimerais m abonner à la newsletter sur Intelligence Artificielle, voici mon email : ahmed@dev.ma"
    }).encode("utf-8")
    req1 = urllib.request.Request(url, data=data1, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req1) as response:
            print("Response 1:", json.loads(response.read().decode()))
    except Exception as e:
        print("Failed Request 1:", e)
        return
        
    time.sleep(2)
    
    # Step 2: Consent
    data2 = json.dumps({
        "user_id": "212600000031@s.whatsapp.net",
        "message": "Oui j accepte"
    }).encode("utf-8")
    req2 = urllib.request.Request(url, data=data2, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req2) as response:
            print("Response 2:", json.loads(response.read().decode()))
    except Exception as e:
        print("Failed Request 2:", e)

if __name__ == "__main__":
    run_evolution()
    run_newsletter()
