#!/usr/bin/env python3
"""
VIS Maintenance & Deployment Utility
-----------------------------------
Fungsi:
1. Re-index otomatis seluruh folder & gambar PNG di CWD menjadi `data.js` dan `index.html`.
2. Commit & Push otomatis ke GitHub secara bertahap (batch-safe) agar tidak timeout / crash.

Penggunaan:
  python update.py               -> Reindex + Push perubahan ke GitHub
  python update.py --reindex     -> Hanya reindex data.js & index.html (tanpa push)
  python update.py --push        -> Hanya commit & push ke GitHub
  python update.py -m "pesan"    -> Kustom pesan commit
"""

import os
import sys
import re
import json
import subprocess
import time
import argparse

# Ensure UTF-8 output encoding across Windows terminals
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CWD = os.path.dirname(os.path.abspath(__file__))

THEME_METADATA = {
    "E1": {
        "themeCode": "E1",
        "themeTitle": "History of Computing & Tech Culture",
        "themeShortTitle": "Computing & Tech History",
        "chipTitle": "💻 E1 • History & Tech",
        "theme": {"bg": "#EFF6FF", "border": "#BFDBFE", "accent": "#2563EB", "icon": "💻"}
    },
    "E2": {
        "themeCode": "E2",
        "themeTitle": "Artificial Intelligence & Machine Learning",
        "themeShortTitle": "AI & Machine Learning",
        "chipTitle": "🤖 E2 • AI & Machine Learning",
        "theme": {"bg": "#F5F3FF", "border": "#DDD6FE", "accent": "#7C3AED", "icon": "🤖"}
    },
    "E3": {
        "themeCode": "E3",
        "themeTitle": "Computer Science & Programming",
        "themeShortTitle": "Computer Science & Dev",
        "chipTitle": "⚡ E3 • Computer Science",
        "theme": {"bg": "#ECFEFF", "border": "#A5F3FC", "accent": "#0891B2", "icon": "⚡"}
    },
    "E4": {
        "themeCode": "E4",
        "themeTitle": "Statistics & Data Science",
        "themeShortTitle": "Statistics & Data Science",
        "chipTitle": "📊 E4 • Data & Statistics",
        "theme": {"bg": "#ECFDF5", "border": "#A7F3D0", "accent": "#059669", "icon": "📊"}
    },
    "E5": {
        "themeCode": "E5",
        "themeTitle": "Cybersecurity & Cryptography",
        "themeShortTitle": "Cybersecurity & Privacy",
        "chipTitle": "🛡️ E5 • Cybersecurity",
        "theme": {"bg": "#FEF2F2", "border": "#FECACA", "accent": "#DC2626", "icon": "🛡️"}
    },
    "E6": {
        "themeCode": "E6",
        "themeTitle": "Space Exploration & Rocketry",
        "themeShortTitle": "Space Exploration & Flight",
        "chipTitle": "🚀 E6 • Space & Exploration",
        "theme": {"bg": "#FFFBEB", "border": "#FDE68A", "accent": "#D97706", "icon": "🚀"}
    }
}

FOLDER_DISPLAY_NAMES = {
    "E1-01-history-computing": "History of Computing",
    "E1-02-internet-web": "Internet & Web",
    "E1-03-iconic-devices-products": "Iconic Devices & Products",
    "E1-04-tech-companies": "Tech Companies",
    "E1-05-figures": "Computing Pioneers & Figures",
    "E1-06-concepts-future": "Concepts & Future Tech",
    "E1-07-digital-culture": "Digital Culture",

    "E2-01-core-concepts": "AI Core Concepts",
    "E2-02-architectures": "Neural Architectures",
    "E2-03-ml-algorithms": "Machine Learning Algorithms",
    "E2-04-ai-ethics-bias": "AI Ethics & Bias",
    "E2-05-history-ai": "History of AI",
    "E2-06-figures": "AI Pioneers & Figures",
    "E2-07-applications-future": "AI Applications & Future",

    "E3-01-algorithms-data-structures": "Algorithms & Data Structures",
    "E3-02-programming-paradigms": "Programming Paradigms",
    "E3-03-concepts": "Computer Science Concepts",
    "E3-04-networks-systems": "Networks & Systems",
    "E3-05-programming-languages": "Programming Languages",
    "E3-06-cs-figures": "Computer Science Figures",

    "E4-01-statistical-concepts": "Statistical Concepts",
    "E4-02-probability": "Probability & Distributions",
    "E4-03-data-visualization": "Data Visualization",
    "E4-04-ml-basics": "Data & ML Basics",
    "E4-05-data-bias": "Data Bias & Cognitive Errors",
    "E4-06-figures-studies": "Figures & Landmark Studies",

    "E5-01-attacks-threats": "Attacks & Security Threats",
    "E5-02-cryptography": "Cryptography & Protocols",
    "E5-03-defense": "Defense & Security Architecture",
    "E5-04-legendary-hacks": "Legendary Hacks & Incidents",
    "E5-05-privacy-figures": "Privacy & Security Figures",

    "E6-01-historic-missions": "Historic Space Missions",
    "E6-02-rockets-technology": "Rockets & Space Technology",
    "E6-03-astronauts": "Astronauts & Cosmonauts",
    "E6-04-space-agencies": "Space Agencies & Aerospace",
    "E6-05-future": "Future Space Exploration",
    "E6-06-spaceflight-environment-phenomena": "Spaceflight Environment & Phenomena",
}

SPECIAL_WORD_MAP = {
    "ai": "AI",
    "ml": "ML",
    "cs": "CS",
    "cv": "CV",
    "gpu": "GPU",
    "gpus": "GPUs",
    "cpu": "CPU",
    "cpus": "CPUs",
    "ram": "RAM",
    "rom": "ROM",
    "pc": "PC",
    "bios": "BIOS",
    "os": "OS",
    "arpanet": "ARPANET",
    "eniac": "ENIAC",
    "edvac": "EDVAC",
    "univac": "UNIVAC",
    "altair": "Altair",
    "ibm": "IBM",
    "dec": "DEC",
    "pdp": "PDP",
    "vax": "VAX",
    "cray": "Cray",
    "apple": "Apple",
    "macintosh": "Macintosh",
    "amiga": "Amiga",
    "atari": "Atari",
    "commodore": "Commodore",
    "sinclair": "Sinclair",
    "zx": "ZX",
    "spectrum": "Spectrum",
    "xerox": "Xerox",
    "parc": "PARC",
    "gui": "GUI",
    "html": "HTML",
    "html5": "HTML5",
    "http": "HTTP",
    "https": "HTTPS",
    "css": "CSS",
    "js": "JS",
    "javascript": "JavaScript",
    "json": "JSON",
    "xml": "XML",
    "sql": "SQL",
    "nosql": "NoSQL",
    "ajax": "AJAX",
    "tcp": "TCP",
    "ip": "IP",
    "udp": "UDP",
    "dns": "DNS",
    "url": "URL",
    "uri": "URI",
    "api": "API",
    "apis": "APIs",
    "rest": "REST",
    "rpc": "RPC",
    "grpc": "gRPC",
    "ftp": "FTP",
    "ssh": "SSH",
    "tls": "TLS",
    "ssl": "SSL",
    "vpn": "VPN",
    "vpns": "VPNs",
    "dmz": "DMZ",
    "lan": "LAN",
    "wan": "WAN",
    "wifi": "Wi-Fi",
    "bluetooth": "Bluetooth",
    "rfid": "RFID",
    "nfc": "NFC",
    "gps": "GPS",
    "iot": "IoT",
    "vr": "VR",
    "ar": "AR",
    "3d": "3D",
    "2d": "2D",
    "4k": "4K",
    "llm": "LLM",
    "llms": "LLMs",
    "gpt": "GPT",
    "bert": "BERT",
    "cnn": "CNN",
    "cnns": "CNNs",
    "rnn": "RNN",
    "rnns": "RNNs",
    "lstm": "LSTM",
    "lstms": "LSTMs",
    "gru": "GRU",
    "grus": "GRUs",
    "gan": "GAN",
    "gans": "GANs",
    "vae": "VAE",
    "rl": "RL",
    "rlhf": "RLHF",
    "svm": "SVM",
    "svms": "SVMs",
    "knn": "k-NN",
    "pca": "PCA",
    "sgd": "SGD",
    "adam": "Adam",
    "relu": "ReLU",
    "gelu": "GELU",
    "softmax": "Softmax",
    "sigmoid": "Sigmoid",
    "ocr": "OCR",
    "nlp": "NLP",
    "alexnet": "AlexNet",
    "resnet": "ResNet",
    "vgg": "VGG",
    "transformer": "Transformer",
    "transformers": "Transformers",
    "alphago": "AlphaGo",
    "alphazero": "AlphaZero",
    "alphafold": "AlphaFold",
    "deepmind": "DeepMind",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google": "Google",
    "microsoft": "Microsoft",
    "meta": "Meta",
    "amazon": "Amazon",
    "netflix": "Netflix",
    "nvidia": "NVIDIA",
    "intel": "Intel",
    "amd": "AMD",
    "arm": "ARM",
    "risc": "RISC",
    "cisc": "CISC",
    "asic": "ASIC",
    "fpga": "FPGA",
    "tpu": "TPU",
    "rsa": "RSA",
    "aes": "AES",
    "des": "DES",
    "sha": "SHA",
    "md5": "MD5",
    "ecc": "ECC",
    "pki": "PKI",
    "ca": "CA",
    "pgp": "PGP",
    "gpg": "GPG",
    "otp": "OTP",
    "2fa": "2FA",
    "mfa": "MFA",
    "sso": "SSO",
    "saml": "SAML",
    "oauth": "OAuth",
    "jwt": "JWT",
    "rbac": "RBAC",
    "abac": "ABAC",
    "tpm": "TPM",
    "ddos": "DDoS",
    "dos": "DoS",
    "mitm": "MitM",
    "xss": "XSS",
    "csrf": "CSRF",
    "sqli": "SQLi",
    "rce": "RCE",
    "apt": "APT",
    "soc": "SOC",
    "siem": "SIEM",
    "edr": "EDR",
    "ids": "IDS",
    "ips": "IPS",
    "gdpr": "GDPR",
    "ccpa": "CCPA",
    "hipaa": "HIPAA",
    "fbi": "FBI",
    "cia": "CIA",
    "nsa": "NSA",
    "kgb": "KGB",
    "gchq": "GCHQ",
    "cp-m": "CP/M",
    "ms-dos": "MS-DOS",
    "unix": "UNIX",
    "linux": "Linux",
    "bsd": "BSD",
    "posix": "POSIX",
    "gnu": "GNU",
    "mit": "MIT",
    "cern": "CERN",
    "ansi": "ANSI",
    "iso": "ISO",
    "ieee": "IEEE",
    "ietf": "IETF",
    "w3c": "W3C",
    "rfc": "RFC",
}

POSSESSIVES = {
    "holleriths": "Hollerith's",
    "napiers": "Napier's",
    "moores": "Moore's",
    "shannons": "Shannon's",
    "turings": "Turing's",
    "babbages": "Babbage's",
    "conways": "Conway's",
    "netscapes": "Netscape's",
    "cuckoos": "Cuckoo's",
    "anscombes": "Anscombe's",
    "simpsons": "Simpson's",
    "markovs": "Markov's",
    "poissons": "Poisson's",
    "bayes": "Bayes'",
    "zipfs": "Zipf's",
}

LOWERCASE_WORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in",
    "into", "nor", "of", "off", "on", "onto", "or", "over", "per",
    "the", "to", "up", "upon", "via", "with", "without", "versus", "vs", "v"
}

def clean_title(fn):
    base = re.sub(r'\.pngx?$', '', fn, flags=re.IGNORECASE)
    
    if base == "a-search":
        return "A* Search"
    if base == "the-cuckoos-egg":
        return "The Cuckoo's Egg"
    if base == "anscombes-quartet":
        return "Anscombe's Quartet"
    if base == "cp-m":
        return "CP/M"
    if base == "the-414s":
        return "The 414s"
    if base == "the-3-2-1-rule":
        return "The 3-2-1 Rule"

    tokens = base.split('-')
    words = []
    
    for i, token in enumerate(tokens):
        t_low = token.lower()
        if t_low in SPECIAL_WORD_MAP:
            words.append(SPECIAL_WORD_MAP[t_low])
        elif t_low in POSSESSIVES:
            words.append(POSSESSIVES[t_low])
        elif i > 0 and t_low in LOWERCASE_WORDS:
            words.append(t_low)
        elif re.match(r'^(i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv)$', t_low):
            words.append(token.upper())
        elif re.match(r'^\d+[a-z]?$', t_low):
            words.append(token.upper())
        else:
            words.append(token.capitalize())
            
    title = " ".join(words)
    for k, v in SPECIAL_WORD_MAP.items():
        title = re.sub(rf'\b{k}\b', v, title, flags=re.IGNORECASE)
        
    return title

def format_size(bytes_size):
    if bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    return f"{bytes_size / (1024 * 1024):.1f} MB"

def escape_html(text):
    if not text:
        return ""
    return (str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

def reindex():
    print("[1/2] Menjalankan Re-Indexing Folder dan Gambar...")
    folders = sorted([d for d in os.listdir(CWD) if os.path.isdir(os.path.join(CWD, d)) and d.startswith("E") and not d.startswith(".")])
    
    library_data = []
    total_all_images = 0
    
    for global_idx, f in enumerate(folders, 1):
        theme_prefix = f.split('-')[0]
        theme_info = THEME_METADATA.get(theme_prefix, {
            "themeCode": theme_prefix,
            "themeTitle": "Technology & Science",
            "themeShortTitle": "Technology",
            "chipTitle": f"📁 {theme_prefix}",
            "theme": {"bg": "#EFF6FF", "border": "#BFDBFE", "accent": "#2563EB", "icon": "📁"}
        })
        
        code_match = re.match(r'^(E\d+-\d+)', f)
        code_str = code_match.group(1) if code_match else f
        number_str = f"{global_idx:02d}"
        display_name = FOLDER_DISPLAY_NAMES.get(f, f.replace('-', ' ').title())
        
        fpath = os.path.join(CWD, f)
        files = sorted([img for img in os.listdir(fpath) if img.lower().endswith(".png")])
        
        folder_images = []
        for file in files:
            full_p = os.path.join(fpath, file)
            sz = os.path.getsize(full_p)
            title = clean_title(file)
            folder_images.append({
                "name": file,
                "cleanTitle": title,
                "subtitle": "",
                "ext": "png",
                "url": f"{f}/{file}",
                "size": format_size(sz)
            })
            
        total_all_images += len(folder_images)
        
        library_data.append({
            "rawName": f,
            "number": number_str,
            "code": code_str,
            "themeCode": theme_prefix,
            "themeTitle": theme_info["themeTitle"],
            "themeShortTitle": theme_info["themeShortTitle"],
            "displayName": display_name,
            "subtitle": "",
            "imageCount": len(folder_images),
            "theme": theme_info["theme"],
            "images": folder_images
        })

    # Write data.js
    data_js_path = os.path.join(CWD, "data.js")
    with open(data_js_path, "w", encoding="utf-8") as out:
        out.write("/** VIS Computer Science & Tech Dataset */\n")
        out.write("window.libraryData = ")
        json.dump(library_data, out, ensure_ascii=False)
        out.write(";\n")

    total_topics = len(library_data)
    print(f"[OK] Re-Index Sukses: {total_topics} topik, {total_all_images} poster visual.")
    return library_data

def run_cmd(cmd, retries=3, delay=5):
    for attempt in range(1, retries + 1):
        res = subprocess.run(cmd, cwd=CWD, shell=isinstance(cmd, str), capture_output=True, text=True)
        if res.returncode == 0:
            return True, res.stdout
        if attempt < retries:
            time.sleep(delay)
    return False, res.stderr

def git_sync(custom_msg=None):
    print("\n[2/2] Memeriksa & Mengunggah Perubahan ke GitHub...")
    run_cmd(["git", "config", "http.postBuffer", "524288000"])
    
    res = subprocess.run(["git", "status", "--porcelain"], cwd=CWD, capture_output=True, text=True)
    status_out = res.stdout.strip()
    
    if not status_out:
        print("[INFO] Repositori sudah bersih (up-to-date), tidak ada perubahan baru.")
        return

    print("[INFO] Ditemukan perubahan file:")
    for line in status_out.splitlines()[:15]:
        print(f"  {line}")
    if len(status_out.splitlines()) > 15:
        print(f"  ... dan {len(status_out.splitlines()) - 15} perubahan lainnya.")

    # Step A: Push base web files if modified
    base_files = ["index.html", "data.js", "update.py"]
    staged_base = False
    for bf in base_files:
        if bf in status_out:
            run_cmd(["git", "add", bf])
            staged_base = True
            
    if staged_base:
        msg = custom_msg or f"Update dataset & web configuration ({time.strftime('%Y-%m-%d %H:%M')})"
        run_cmd(["git", "commit", "-m", msg])
        print("[PUSH] Mengunggah web config & dataset...")
        ok, out = run_cmd(["git", "push", "origin", "main"], retries=5, delay=5)
        if ok:
            print("  [OK] Web config & dataset berhasil diunggah.")
        else:
            print(f"  [ERROR] Gagal push config: {out[:200]}")

    # Step B: Scan any modified or untracked folders starting with E
    folders = sorted([d for d in os.listdir(CWD) if os.path.isdir(os.path.join(CWD, d)) and d.startswith("E") and not d.startswith(".")])
    
    for folder in folders:
        st_res = subprocess.run(["git", "status", "--porcelain", folder], cwd=CWD, capture_output=True, text=True)
        if st_res.stdout.strip():
            print(f"[BATCH] Mengunggah folder: {folder}...")
            run_cmd(["git", "add", folder])
            run_cmd(["git", "commit", "-m", f"Update {folder} poster content"])
            ok, err = run_cmd(["git", "push", "origin", "main"], retries=5, delay=7)
            if ok:
                print(f"  [OK] {folder} berhasil di-push.")
            else:
                print(f"  [ERROR] Gagal push {folder}: {err[:200]}")
                
    print("\n[OK] Sinkronisasi ke GitHub selesai dengan sukses!")

def main():
    parser = argparse.ArgumentParser(description="VIS Maintenance & GitHub Deployment Utility")
    parser.add_argument("--reindex", action="store_true", help="Hanya jalankan re-index")
    parser.add_argument("--push", action="store_true", help="Hanya jalankan commit & push ke GitHub")
    parser.add_argument("-m", "--message", type=str, help="Pesan kustom commit git")
    args = parser.parse_args()

    if args.push:
        git_sync(args.message)
    elif args.reindex:
        reindex()
    else:
        reindex()
        git_sync(args.message)

if __name__ == "__main__":
    main()
