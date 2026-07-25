import argparse
import os
import requests
import time

def create_instance(mode, instance_name, business_id=None, token=None):
    evolution_url = os.environ.get("EVOLUTION_API_URL", "http://localhost:8080")
    api_key = os.environ.get("EVOLUTION_API_KEY", "super_secret_key")
    
    headers = {
        "apikey": api_key,
        "Content-Type": "application/json"
    }

    print(f"[*] Creating instance '{instance_name}' in {mode} mode...")
    
    payload = {
        "instanceName": instance_name
    }

    if mode == "baileys":
        payload["integration"] = "WHATSAPP-BAILEYS"
        payload["qrcode"] = True
    elif mode == "cloud_api":
        if not business_id or not token:
            print("[!] Error: business_id and token are required for cloud_api mode.")
            return
        payload["integration"] = "WHATSAPP-BUSINESS"
        payload["businessId"] = business_id
        payload["token"] = token
    
    try:
        response = requests.post(f"{evolution_url}/instance/create", json=payload, headers=headers)
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"[+] Instance {instance_name} created successfully!")
            
            if mode == "baileys" and data.get("qrcode"):
                base64_str = data["qrcode"].get("base64", "")
                if base64_str.startswith("data:image/png;base64,"):
                    base64_str = base64_str.replace("data:image/png;base64,", "")
                
                import base64
                with open("qr.png", "wb") as f:
                    f.write(base64.b64decode(base64_str))
                print("[!] Le code QR a été sauvegardé dans le fichier 'qr.png'.")
                print("[!] Ouvrez ce fichier (qr.png) et scannez-le rapidement avec WhatsApp (il expire vite).")
            elif mode == "cloud_api":
                print("[+] Cloud API connected successfully.")
        else:
            print(f"[-] Failed to create instance. Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[-] Error connecting to Evolution API at {evolution_url}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage Evolution API Instances")
    parser.add_argument("--mode", choices=["baileys", "cloud_api"], required=True, help="Mode of integration")
    parser.add_argument("--instance", required=True, help="Name of the instance")
    parser.add_argument("--business-id", help="Meta Business ID (for cloud_api)")
    parser.add_argument("--token", help="Meta Permanent Token (for cloud_api)")

    args = parser.parse_args()
    create_instance(args.mode, args.instance, args.business_id, args.token)
