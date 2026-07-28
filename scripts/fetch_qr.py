import urllib.request
import json
import base64

def get_qr():
    url = "http://localhost:8090/instance/connect/youcode-ai"
    req = urllib.request.Request(url, headers={
        "apikey": "super_secret_key"
    })
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode())
            qr_base64 = res_data.get("base64", "")
            if qr_base64:
                qr_base64 = qr_base64.replace("data:image/png;base64,", "")
                
                # Save base64 QR to artifact
                with open("/home/bucketlister/.gemini/antigravity/brain/c1139cad-ee1f-4c58-af13-3840b33da408/whatsapp_qr.md", "w") as f:
                    f.write("# WhatsApp Evolution API QR Code\n\n")
                    f.write(f"![QR Code](data:image/png;base64,{qr_base64})\n\n")
                    f.write("Scan this QR Code with your WhatsApp mobile app to connect your number to the system.")
                print("QR code artifact created successfully.")
            else:
                print("No QR code found in response. The instance might already be connected.")
    except Exception as e:
        print(f"Failed to fetch QR code: {e}")

if __name__ == "__main__":
    get_qr()
