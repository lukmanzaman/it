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
    print("[1/2] Menjalankan Re-Indexing Folder & Gambar...")
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
        code = code_match.group(1) if code_match else f
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
            "code": code,
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

    # Build HTML Cards
    cards_html_list = []
    for folder in library_data:
        raw_name = folder["rawName"]
        theme_code = folder["themeCode"]
        theme_accent = folder["theme"]["accent"]
        theme_icon = folder["theme"]["icon"]
        num = folder["number"]
        code = folder["code"]
        short_theme = folder["themeShortTitle"]
        title = folder["displayName"]
        count = folder["imageCount"]
        
        items_html = []
        for i, img in enumerate(folder["images"], 1):
            item_title = escape_html(img["cleanTitle"])
            items_html.append(
                f'<div class="card-dropdown-item" onclick="event.stopPropagation(); openReader(\'{raw_name}\', {i});">'
                f'<span class="picker-item-num">#{i}</span>'
                f'<span class="picker-item-title">{item_title}</span>'
                f'</div>'
            )
        items_joined = "".join(items_html)
        
        card_html = f"""    <div class="folder-card" data-rawname="{raw_name}" data-theme="{theme_code}" style="--theme-accent: {theme_accent};">
        <div class="card-click-area" onclick="openReader('{raw_name}');">
            <div class="card-top">
                <div class="folder-icon-box">{theme_icon}</div>
                <div class="folder-info">
                    <div style="display: flex; gap: 0.35rem; align-items: center; margin-bottom: 0.25rem;">
                        <span class="number-badge">#{num}</span>
                        <span class="theme-badge" style="color: {theme_accent};">{code} • {escape_html(short_theme)}</span>
                    </div>
                    <h2 class="folder-title">{escape_html(title)}</h2>
                </div>
            </div>
        </div>
        <div class="card-bottom-row">
            <div class="card-dropdown-wrapper">
                <button type="button" class="btn-card-list" onclick="event.stopPropagation(); toggleCardDropdown(this);">
                    <span>Daftar Materi ({count})</span>
                    <span class="picker-arrow">▾</span>
                </button>
                <div class="card-dropdown-menu">
                    <div class="card-dropdown-header">
                        <span>{escape_html(title)}</span>
                        <span>{count} Poster</span>
                    </div>
                    <div class="card-dropdown-list">
                        {items_joined}
                    </div>
                </div>
            </div>
            <button type="button" class="btn-read" onclick="openReader('{raw_name}');">
                <span>Buka Stream</span>
            </button>
        </div>
    </div>"""
        cards_html_list.append(card_html)

    all_cards_html = "\n".join(cards_html_list)

    # Active theme codes
    theme_codes = sorted(list(set(f["themeCode"] for f in library_data)))
    chips_html_list = [f'<button class="chip active" data-theme="">Semua Tema ({len(library_data)})</button>']
    for code in theme_codes:
        count_in_theme = sum(1 for f in library_data if f["themeCode"] == code)
        info = THEME_METADATA.get(code, {"chipTitle": f"{code}"})
        chip_title = info.get("chipTitle", f"{code}")
        chips_html_list.append(f'<button class="chip" data-theme="{code}">{chip_title} ({count_in_theme})</button>')
    theme_chips_html = "".join(chips_html_list)

    total_themes = len(theme_codes)
    total_topics = len(library_data)

    index_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <title>VIS Computer Science &amp; Technology • Vertical Infographic Stream</title>
    <meta name="description" content="Eksplorasi visual {total_all_images}+ konsep sains komputer, AI, algoritma, data science, dan cybersecurity dalam format continuous vertical stream. The Productive Doomscroll.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --bg-body: #F8F9FA;
            --card-bg: #FFFFFF;
            --card-border: #E5E7EB;
            --text-title: #0F172A;
            --text-body: #334155;
            --text-muted: #64748B;
            --border-soft: #E2E8F0;
            --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.04), 0 6px 16px rgba(0, 0, 0, 0.02);
            --shadow-hover: 0 12px 28px rgba(15, 23, 42, 0.08), 0 4px 10px rgba(0, 0, 0, 0.03);
            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-full: 9999px;
            --primary: #2563EB;
            --primary-hover: #1D4ED8;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }}

        html {{
            width: 100%;
            min-height: 100%;
            overflow-x: hidden;
            overflow-y: auto;
        }}

        body {{
            width: 100%;
            min-height: 100%;
            font-family: var(--font-main);
            color: var(--text-body);
            background-color: var(--bg-body);
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }}

        body.view-home {{
            background-color: var(--bg-body);
        }}

        body.view-reader {{
            background-color: #0F1117;
        }}

        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 3.5rem 1.5rem 5rem;
        }}

        .hero {{
            text-align: center;
            margin-bottom: 2.25rem;
        }}

        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0.85rem;
            background: #EEF2F6;
            border: 1px solid #E2E8F0;
            border-radius: var(--radius-full);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            color: var(--primary);
            margin-bottom: 1.25rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }}

        .hero-badge-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
        }}

        .hero-title {{
            font-size: clamp(2.2rem, 5vw, 3.2rem);
            font-weight: 800;
            color: var(--text-title);
            letter-spacing: -0.03em;
            margin-bottom: 0.5rem;
        }}

        .hero-desc {{
            font-size: 1rem;
            color: var(--text-muted);
            max-width: 680px;
            margin: 0 auto;
            line-height: 1.5;
        }}

        /* REAL-TIME SEARCH BAR */
        .search-wrapper {{
            position: relative;
            max-width: 680px;
            margin: 1.75rem auto 1.5rem;
            z-index: 100;
        }}

        .search-input-box {{
            position: relative;
            display: flex;
            align-items: center;
            background: #FFFFFF;
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-full);
            padding: 0.55rem 0.75rem 0.55rem 1.35rem;
            box-shadow: var(--shadow-card);
            transition: all 0.2s ease;
        }}

        .search-input-box:focus-within {{
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15), 0 8px 20px rgba(0, 0, 0, 0.06);
        }}

        .search-icon-left {{
            color: var(--text-muted);
            margin-right: 0.75rem;
            display: flex;
            align-items: center;
            font-size: 1.1rem;
        }}

        .search-input {{
            flex: 1;
            border: none;
            outline: none;
            background: transparent;
            font-family: var(--font-main);
            font-size: 0.95rem;
            font-weight: 500;
            color: var(--text-title);
        }}

        .search-input::placeholder {{
            color: #94A3B8;
        }}

        .search-clear-btn {{
            background: #F1F5F9;
            border: none;
            color: var(--text-muted);
            font-size: 0.85rem;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            transition: all 0.15s ease;
        }}

        .search-clear-btn:hover {{
            background: #E2E8F0;
            color: var(--text-title);
        }}

        .search-dropdown {{
            position: absolute;
            top: calc(100% + 8px);
            left: 0;
            right: 0;
            background: #FFFFFF;
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.12);
            overflow: hidden;
            display: none;
            z-index: 1000;
        }}

        .search-dropdown.active {{
            display: block;
        }}

        .dropdown-header {{
            padding: 0.65rem 1rem;
            background: #F8FAFC;
            border-bottom: 1px solid var(--border-soft);
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
        }}

        .search-result-item {{
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #F1F5F9;
            cursor: pointer;
            transition: background 0.15s ease;
        }}

        .search-result-item:hover, .search-result-item.selected {{
            background: #F8FAFC;
        }}

        .result-folder-icon {{
            color: var(--primary);
            margin-right: 0.85rem;
            display: flex;
            align-items: center;
            font-size: 1.25rem;
        }}

        .result-text-block {{
            flex: 1;
            min-width: 0;
        }}

        .result-title-line {{
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-title);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .result-path-line {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.15rem;
        }}

        .result-path-folder {{
            color: var(--primary);
            font-weight: 600;
        }}

        .result-arrow {{
            color: #CBD5E1;
            font-size: 1.1rem;
            margin-left: 0.5rem;
            transition: transform 0.15s ease, color 0.15s ease;
        }}

        .search-result-item:hover .result-arrow {{
            color: var(--primary);
            transform: translateX(3px);
        }}

        .match-mark {{
            background: #DBEAFE;
            color: #1D4ED8;
            padding: 0.1rem 0.25rem;
            border-radius: 4px;
            font-weight: 600;
        }}

        .dropdown-empty {{
            padding: 1.75rem;
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        /* THEME FILTER CHIPS */
        .theme-chips-bar {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            overflow-x: auto;
            padding: 0.5rem 0 1.75rem;
            scrollbar-width: thin;
            justify-content: flex-start;
        }}

        .chip {{
            padding: 0.4rem 0.85rem;
            border-radius: var(--radius-full);
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid var(--border-soft);
            background: #FFFFFF;
            color: var(--text-muted);
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }}

        .chip:hover {{
            border-color: var(--primary);
            color: var(--text-title);
        }}

        .chip.active {{
            background: var(--primary);
            color: #FFFFFF;
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
        }}

        /* FOLDERS GRID */
        .folders-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.35rem;
        }}

        .folder-card {{
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            border: 1px solid var(--card-border);
            box-shadow: var(--shadow-card);
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: visible;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .folder-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--theme-accent, var(--primary));
            border-radius: var(--radius-lg) var(--radius-lg) 0 0;
            opacity: 0.9;
        }}

        .folder-card:hover {{
            transform: translateY(-4px);
            border-color: #CBD5E1;
            box-shadow: var(--shadow-hover);
        }}

        .card-click-area {{
            padding: 1.35rem 1.35rem 0.85rem;
            cursor: pointer;
        }}

        .card-top {{
            display: flex;
            align-items: flex-start;
            gap: 0.85rem;
            margin-bottom: 0.5rem;
        }}

        .folder-icon-box {{
            width: 46px;
            height: 46px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #F8FAFC;
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            font-size: 1.4rem;
            flex-shrink: 0;
            transition: transform 0.2s ease;
        }}

        .folder-card:hover .folder-icon-box {{
            transform: scale(1.06);
            background: #FFFFFF;
        }}

        .folder-info {{
            flex: 1;
            min-width: 0;
        }}

        .number-badge {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            font-family: var(--font-mono);
            color: var(--text-muted);
            background: #F1F5F9;
            padding: 0.1rem 0.45rem;
            border-radius: 4px;
        }}

        .theme-badge {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .folder-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-title);
            line-height: 1.35;
            margin-top: 0.2rem;
        }}

        .card-bottom-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 1.35rem 1.25rem;
            position: relative;
        }}

        .card-dropdown-wrapper {{
            position: relative;
        }}

        .btn-card-list {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: #F8FAFC;
            border: 1px solid var(--border-soft);
            color: var(--text-body);
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.42rem 0.8rem;
            border-radius: var(--radius-full);
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .btn-card-list:hover, .btn-card-list.active {{
            background: #FFFFFF;
            border-color: var(--primary);
            color: var(--primary);
        }}

        .card-dropdown-menu {{
            position: absolute;
            bottom: calc(100% + 8px);
            left: 0;
            width: 320px;
            background: #FFFFFF;
            border: 1px solid var(--border-soft);
            border-radius: var(--radius-md);
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.14);
            overflow: hidden;
            display: none;
            z-index: 1000;
        }}

        .card-dropdown-menu.show {{
            display: block;
        }}

        .card-dropdown-header {{
            padding: 0.65rem 0.95rem;
            background: #F8FAFC;
            border-bottom: 1px solid var(--border-soft);
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--text-title);
            display: flex;
            justify-content: space-between;
        }}

        .card-dropdown-list {{
            max-height: 220px;
            overflow-y: auto;
            padding: 0.25rem 0;
        }}

        .card-dropdown-list::-webkit-scrollbar {{
            width: 5px;
        }}
        .card-dropdown-list::-webkit-scrollbar-thumb {{
            background: #CBD5E1;
            border-radius: 4px;
        }}

        .card-dropdown-item {{
            padding: 0.5rem 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-body);
            font-size: 0.8rem;
            cursor: pointer;
            transition: background 0.15s ease;
        }}

        .card-dropdown-item:hover {{
            background: #F1F5F9;
            color: var(--primary);
        }}

        .btn-read {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: var(--primary);
            color: #FFFFFF;
            border: none;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 0.45rem 1.05rem;
            border-radius: var(--radius-full);
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
            transition: all 0.15s ease;
        }}

        .btn-read:hover {{
            background: var(--primary-hover);
            transform: translateY(-1px);
        }}

        .footer-bar {{
            text-align: center;
            padding: 3.5rem 0 1rem;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        /* ========================================================
           READER VIEW (DOOM-SCROLL 100% WIDTH, 1:3 ASPECT RATIO)
           ======================================================== */
        #readerView {{
            display: none;
            width: 100%;
            min-height: 100vh;
            background-color: #0F1117;
        }}

        .reader-nav {{
            position: fixed;
            top: 14px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 0.55rem;
            background: rgba(15, 17, 23, 0.92);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 0.35rem 0.85rem;
            border-radius: var(--radius-full);
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
            max-width: 95vw;
            opacity: 1;
            visibility: visible;
            transition: opacity 0.35s ease, transform 0.35s ease, visibility 0.35s ease;
        }}

        .reader-nav.nav-hidden {{
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
            transform: translateX(-50%) translateY(-24px) !important;
        }}

        .nav-back-btn, .nav-fullscreen-btn {{
            background: rgba(255, 255, 255, 0.08);
            color: #FFFFFF;
            border: 1px solid rgba(255, 255, 255, 0.12);
            font-size: 0.82rem;
            font-weight: 600;
            padding: 0.35rem 0.75rem;
            border-radius: var(--radius-full);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.15s ease;
        }}

        .nav-back-btn:hover, .nav-fullscreen-btn:hover {{
            background: rgba(255, 255, 255, 0.18);
        }}

        .nav-title-text {{
            font-size: 0.88rem;
            font-weight: 700;
            color: #FFFFFF;
            max-width: 240px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .nav-picker-btn {{
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #FFFFFF;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.35rem 0.75rem;
            border-radius: var(--radius-full);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.15s ease;
        }}

        .nav-picker-btn:hover, .nav-picker-btn.active {{
            background: #FFFFFF;
            color: #0F172A;
        }}

        .nav-picker-dropdown {{
            position: absolute;
            top: calc(100% + 12px);
            left: 50%;
            transform: translateX(-50%);
            width: 320px;
            background: #1E222D;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: var(--radius-md);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8);
            overflow: hidden;
            display: none;
        }}

        .nav-picker-dropdown.show {{
            display: block;
        }}

        .nav-picker-header {{
            padding: 0.55rem 0.85rem;
            background: rgba(255, 255, 255, 0.04);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            font-size: 0.72rem;
            font-weight: 700;
            color: #94A3B8;
            display: flex;
            justify-content: space-between;
        }}

        .picker-total-badge {{
            background: rgba(255, 255, 255, 0.15);
            color: #FFFFFF;
            padding: 0.1rem 0.45rem;
            border-radius: var(--radius-full);
            font-size: 0.68rem;
        }}

        .nav-picker-list {{
            max-height: 240px;
            overflow-y: auto;
            padding: 0.3rem 0;
        }}

        .nav-picker-list::-webkit-scrollbar {{
            width: 5px;
        }}
        .nav-picker-list::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }}

        .nav-picker-item {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.5rem 0.85rem;
            color: #CBD5E1;
            font-size: 0.78rem;
            cursor: pointer;
            transition: all 0.15s ease;
        }}

        .nav-picker-item:hover {{
            background: rgba(255, 255, 255, 0.08);
            color: #FFFFFF;
        }}

        .nav-picker-item.active {{
            background: var(--primary);
            color: #FFFFFF;
            font-weight: 700;
        }}

        .picker-item-num {{
            font-size: 0.7rem;
            font-weight: 700;
            font-family: var(--font-mono);
            color: #94A3B8;
            background: rgba(255, 255, 255, 0.08);
            padding: 0.1rem 0.35rem;
            border-radius: 4px;
        }}

        .nav-picker-item.active .picker-item-num {{
            background: rgba(255, 255, 255, 0.25);
            color: #FFFFFF;
        }}

        .picker-item-title {{
            flex: 1;
            min-width: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .restore-toast {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(30px);
            background: #0F172A;
            color: #FFFFFF;
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 0.55rem 1.25rem;
            border-radius: var(--radius-full);
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            z-index: 10000;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}

        .restore-toast.show {{
            opacity: 1;
            transform: translateX(-50%) translateY(0);
            pointer-events: auto;
        }}

        .doom-feed {{
            width: 100%;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: stretch;
            background-color: #0F1117;
        }}

        .article-frame {{
            width: 100%;
            display: block;
            margin: 0;
            padding: 0;
            border-bottom: 1px solid #0F1117;
            background-color: #151821;
            position: relative;
            line-height: 0;
            aspect-ratio: 1 / 3;
            overflow: hidden;
        }}

        .article-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            margin: 0;
            padding: 0;
            opacity: 0;
            transition: opacity 0.15s ease-out;
        }}

        .article-img.is-loaded {{
            opacity: 1;
        }}
    </style>
</head>
<body class="view-home">

    <!-- ==========================================
         HOME VIEW: LIBRARY GRID & LIVE SEARCH
         ========================================== -->
    <div id="homeView">
        <div class="container">
            <header class="hero">
                <div class="hero-badge">
                    <span class="hero-badge-dot"></span>
                    <span>VIS ENGINE • VERTICAL INFOGRAPHIC STREAM</span>
                </div>
                <h1 class="hero-title">VIS Computer Science &amp; Technology</h1>
                <p class="hero-desc">{total_themes} Tema Utama • {total_topics} Topik • {total_all_images} Konsep Visual 4K • The Productive Doomscroll</p>

                <!-- REAL-TIME SEARCH -->
                <div class="search-wrapper" id="searchWrapper">
                    <div class="search-input-box">
                        <span class="search-icon-left">🔍</span>
                        <input 
                            type="text" 
                            id="globalSearchInput" 
                            class="search-input" 
                            placeholder="Cari judul, topik, atau konsep materi..." 
                            autocomplete="off"
                            spellcheck="false"
                        >
                        <button type="button" id="clearSearchBtn" class="search-clear-btn" title="Hapus">✕</button>
                    </div>

                    <!-- Dropdown Matches -->
                    <div class="search-dropdown" id="searchDropdown">
                        <div class="dropdown-header">
                            <span>Hasil Pencarian:</span>
                            <span id="searchMatchCount">0 cocok</span>
                        </div>
                        <div id="searchResultList"></div>
                    </div>
                </div>

                <!-- THEME FILTER CHIPS -->
                <div class="theme-chips-bar" id="themeChipsBar">
                    {theme_chips_html}
                </div>
            </header>

            <main class="folders-grid" id="foldersGrid">
{all_cards_html}
            </main>

            <footer class="footer-bar">
                <p><strong>VIS Computer Science &amp; Technology</strong> • Institut STTS &amp; Halo ISTTS</p>
                <p style="margin-top: 0.25rem;">Gunakan AI untuk pelajari hal baru bersama Institut STTS!</p>
            </footer>
        </div>
    </div>

    <!-- ==========================================
         READER VIEW: CONTINUOUS VERTICAL STREAM
         ========================================== -->
    <div id="readerView">
        <!-- Floating Navigation Header -->
        <nav class="reader-nav" id="readerNav" onclick="event.stopPropagation();">
            <button type="button" class="nav-back-btn" onclick="closeReader();" title="Kembali ke Beranda">
                <span>← Kembali</span>
            </button>
            <span class="nav-title-text" id="navFolderTitle">Judul Folder</span>

            <!-- Jump Picker Dropdown -->
            <div style="position: relative;">
                <button type="button" class="nav-picker-btn" id="navPickerBtn" onclick="togglePickerDropdown();">
                    <span id="navPickerLabel">#1 Judul Artikel</span>
                    <span>▾</span>
                </button>
                <div class="nav-picker-dropdown" id="navPickerDropdown">
                    <div class="nav-picker-header">
                        <span>PILIH ARTIKEL</span>
                        <span class="picker-total-badge" id="pickerTotalBadge">0 Item</span>
                    </div>
                    <div class="nav-picker-list" id="navPickerList"></div>
                </div>
            </div>

            <button type="button" class="nav-fullscreen-btn" onclick="toggleFullScreen();" title="Layar Penuh">
                <span>⛶</span>
            </button>
        </nav>

        <!-- Restore Scroll Toast -->
        <div class="restore-toast" id="restoreToast">
            <span id="restoreToastText">Melanjutkan membaca...</span>
        </div>

        <!-- Continuous Vertical Infographic Stream -->
        <main class="doom-feed" id="doomFeed"></main>
    </div>

    <!-- Load Embedded Dataset (With Cache Buster) -->
    <script src="data.js?v={int(time.time())}"></script>

    <script>
        const libraryData = (window.libraryData || []);
        const folderMap = {{}};
        libraryData.forEach(f => {{
            folderMap[f.rawName] = f;
        }});

        // DOM References
        const homeView = document.getElementById('homeView');
        const readerView = document.getElementById('readerView');
        const foldersGrid = document.getElementById('foldersGrid');
        const doomFeed = document.getElementById('doomFeed');
        const nav = document.getElementById('readerNav');
        const navFolderTitle = document.getElementById('navFolderTitle');
        const navPickerBtn = document.getElementById('navPickerBtn');
        const navPickerLabel = document.getElementById('navPickerLabel');
        const navPickerDropdown = document.getElementById('navPickerDropdown');
        const navPickerList = document.getElementById('navPickerList');
        const pickerTotalBadge = document.getElementById('pickerTotalBadge');
        const globalSearchInput = document.getElementById('globalSearchInput');
        const clearSearchBtn = document.getElementById('clearSearchBtn');
        const searchDropdown = document.getElementById('searchDropdown');
        const searchResultList = document.getElementById('searchResultList');
        const searchMatchCount = document.getElementById('searchMatchCount');
        const themeChipsBar = document.getElementById('themeChipsBar');
        const restoreToast = document.getElementById('restoreToast');
        const restoreToastText = document.getElementById('restoreToastText');

        // State variables
        let currentActiveFolder = null;
        let currentActiveArtIdx = 1;
        let homeScrollY = 0;
        let imageObserver = null;
        let isScrollTicking = false;
        let isRestoringScroll = false;
        let saveScrollTimeout = null;
        let selectedThemeFilter = '';

        // Visibility Controls (Default: lenyap, toggle via tap/click)
        function showNav() {{ nav.classList.remove('nav-hidden'); }}
        function hideNav() {{ closePickerDropdown(); nav.classList.add('nav-hidden'); }}
        function toggleNav() {{
            if (nav.classList.contains('nav-hidden')) showNav();
            else hideNav();
        }}

        // Independent Position Store per Folder (LocalStorage)
        let folderPositions = {{}};
        function loadAllPositions() {{
            let loaded = {{}};
            try {{
                const raw = localStorage.getItem('vis_tech_positions');
                if (raw) loaded = JSON.parse(raw) || {{}};
            }} catch(e) {{}}
            return loaded;
        }}
        folderPositions = loadAllPositions();

        function saveCurrentPosition() {{
            if (!currentActiveFolder || isRestoringScroll) return;
            const fKey = currentActiveFolder.rawName;
            const artIdx = currentActiveArtIdx || 1;
            const scrollY = Math.round(window.scrollY);

            folderPositions[fKey] = {{
                artIdx: artIdx,
                scrollY: scrollY,
                total: currentActiveFolder.imageCount,
                ts: Date.now()
            }};
            try {{ localStorage.setItem('vis_tech_positions', JSON.stringify(folderPositions)); }} catch(e) {{}}
        }}

        window.addEventListener('beforeunload', () => saveCurrentPosition());
        window.addEventListener('pagehide', () => saveCurrentPosition());

        function escapeHtml(str) {{
            if (!str) return '';
            return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
        }}

        // ================= ROUTING & READER VIEW =================
        function openReader(rawName, targetArt, updateHash) {{
            if (updateHash === undefined) updateHash = true;
            const folder = folderMap[rawName];
            if (!folder) return;
            renderReader(folder, targetArt || 0);
            if (updateHash) {{
                setRoute(rawName, targetArt || 0);
            }}
        }}

        function closeReader(updateHash) {{
            if (updateHash === undefined) updateHash = true;
            if (currentActiveFolder) {{
                saveCurrentPosition();
            }}
            renderHome();
            if (updateHash) {{
                setRoute(null);
            }}
        }}

        function renderHome() {{
            if (currentActiveFolder) {{
                saveCurrentPosition();
            }}
            currentActiveFolder = null;
            closePickerDropdown();
            hideNav();

            document.body.className = 'view-home';
            readerView.style.display = 'none';
            homeView.style.display = 'block';
            document.title = 'VIS Computer Science & Technology • Vertical Infographic Stream';

            if (imageObserver) {{
                imageObserver.disconnect();
                imageObserver = null;
            }}

            window.scrollTo({{ top: homeScrollY, behavior: 'instant' }});
        }}

        // Smart Proactive Image Preloader
        const preloadedUrls = new Set();
        function preloadImageUrl(url) {{
            if (!url || preloadedUrls.has(url)) return;
            preloadedUrls.add(url);
            const temp = new Image();
            temp.decoding = 'async';
            temp.src = url;
        }}

        function loadFrameImage(idx) {{
            if (!currentActiveFolder || !currentActiveFolder.images) return;
            if (idx < 1 || idx > currentActiveFolder.images.length) return;

            const frame = document.getElementById('art-' + idx);
            if (!frame) return;

            const img = frame.querySelector('img.article-img');
            if (!img) return;

            const realSrc = img.getAttribute('data-src');
            if (!realSrc) return;

            if (img.src !== realSrc) {{
                img.src = realSrc;
            }}

            if (img.complete && img.naturalWidth > 0) {{
                img.classList.add('is-loaded');
            }} else {{
                img.onload = () => {{ img.classList.add('is-loaded'); }};
            }}
        }}

        function preloadRunway(currentIdx) {{
            if (!currentActiveFolder || !currentActiveFolder.images) return;
            const total = currentActiveFolder.images.length;
            const start = Math.max(1, currentIdx - 2);
            const end = Math.min(total, currentIdx + 6);

            for (let i = start; i <= end; i++) {{
                loadFrameImage(i);
                const item = currentActiveFolder.images[i - 1];
                if (item && item.url) preloadImageUrl(item.url);
            }}
        }}

        function setupLazyObserver() {{
            const lazyImages = doomFeed.querySelectorAll('.lazy-img');
            if ('IntersectionObserver' in window) {{
                if (imageObserver) imageObserver.disconnect();
                imageObserver = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            const img = entry.target;
                            const idx = parseInt(img.closest('.article-frame')?.getAttribute('data-index'), 10);
                            if (idx) preloadRunway(idx);
                        }}
                    }});
                }}, {{ rootMargin: '600px 0px' }});

                lazyImages.forEach(img => imageObserver.observe(img));
            }} else {{
                for (let i = 1; i <= Math.min(10, currentActiveFolder.images.length); i++) {{
                    loadFrameImage(i);
                }}
            }}
        }}

        function renderReader(folder, targetArticleIndex) {{
            homeScrollY = window.scrollY;
            currentActiveFolder = folder;

            document.body.className = 'view-reader';
            homeView.style.display = 'none';
            readerView.style.display = 'block';

            navFolderTitle.textContent = folder.displayName;
            document.title = `${{folder.displayName}} • VIS Stream`;

            hideNav();

            pickerTotalBadge.textContent = `${{folder.imageCount}} Poster`;
            navPickerList.innerHTML = '';
            folder.images.forEach((img, idx) => {{
                const itemNum = idx + 1;
                const div = document.createElement('div');
                div.className = 'nav-picker-item' + (itemNum === 1 ? ' active' : '');
                div.setAttribute('data-idx', itemNum);
                div.innerHTML = `<span class="picker-item-num">#${{itemNum}}</span><span class="picker-item-title">${{escapeHtml(img.cleanTitle)}}</span>`;
                div.onclick = (e) => {{
                    e.stopPropagation();
                    jumpToArticle(itemNum);
                    closePickerDropdown();
                }};
                navPickerList.appendChild(div);
            }});

            let feedHtml = '';
            folder.images.forEach((img, idx) => {{
                const itemNum = idx + 1;
                feedHtml += `
                    <section class="article-frame" id="art-${{itemNum}}" data-index="${{itemNum}}">
                        <img 
                            class="article-img lazy-img" 
                            data-src="${{img.url}}" 
                            alt="${{escapeHtml(img.cleanTitle)}}" 
                            loading="lazy"
                            decoding="async"
                        >
                    </section>
                `;
            }});
            doomFeed.innerHTML = feedHtml;

            setupLazyObserver();

            let savedPos = folderPositions[folder.rawName];
            let startIdx = targetArticleIndex > 0 ? targetArticleIndex : (savedPos ? savedPos.artIdx : 1);

            preloadRunway(startIdx);

            if (targetArticleIndex > 0) {{
                jumpToArticle(targetArticleIndex, 'instant');
            }} else if (savedPos && savedPos.scrollY > 0) {{
                isRestoringScroll = true;
                setTimeout(() => {{
                    window.scrollTo({{ top: savedPos.scrollY, behavior: 'instant' }});
                    preloadRunway(savedPos.artIdx);
                    updateActiveArticleState(savedPos.artIdx);
                    showToast(`Melanjutkan dari artikel #${{savedPos.artIdx}}`);
                    setTimeout(() => {{ isRestoringScroll = false; }}, 300);
                }}, 50);
            }} else {{
                window.scrollTo({{ top: 0, behavior: 'instant' }});
                updateActiveArticleState(1);
            }}
        }}

        function jumpToArticle(artNum, behavior = 'smooth') {{
            const frame = document.getElementById('art-' + artNum);
            if (frame) {{
                preloadRunway(artNum);
                frame.scrollIntoView({{ behavior: behavior, block: 'start' }});
                updateActiveArticleState(artNum);
                setRoute(currentActiveFolder.rawName, artNum);
            }}
        }}

        function updateActiveArticleState(artNum) {{
            if (!currentActiveFolder || !currentActiveFolder.images) return;
            currentActiveArtIdx = artNum;
            const curItem = currentActiveFolder.images[artNum - 1];
            if (curItem) {{
                navPickerLabel.textContent = `#${{artNum}} ${{curItem.cleanTitle}}`;
            }}

            const items = navPickerList.querySelectorAll('.nav-picker-item');
            items.forEach(it => {{
                if (parseInt(it.getAttribute('data-idx'), 10) === artNum) {{
                    it.classList.add('active');
                    it.scrollIntoView({{ block: 'nearest' }});
                }} else {{
                    it.classList.remove('active');
                }}
            }});
        }}

        function handleReaderScroll() {{
            if (!currentActiveFolder || isRestoringScroll) return;

            if (!nav.classList.contains('nav-hidden')) {{
                hideNav();
            }}

            if (!isScrollTicking) {{
                isScrollTicking = true;
                requestAnimationFrame(() => {{
                    if (!currentActiveFolder || isRestoringScroll) {{
                        isScrollTicking = false;
                        return;
                    }}

                    detectCurrentArticle();
                    isScrollTicking = false;
                }});
            }}

            if (saveScrollTimeout) clearTimeout(saveScrollTimeout);
            saveScrollTimeout = setTimeout(() => {{
                if (!currentActiveFolder || isRestoringScroll) return;
                saveCurrentPosition();
            }}, 100);
        }}
        window.addEventListener('scroll', handleReaderScroll, {{ passive: true }});

        function detectCurrentArticle() {{
            const frames = doomFeed.querySelectorAll('.article-frame');
            if (!frames.length) return;

            const midY = window.innerHeight * 0.35;
            let activeIdx = 1;

            for (let i = 0; i < frames.length; i++) {{
                const rect = frames[i].getBoundingClientRect();
                if (rect.top <= midY && rect.bottom >= midY) {{
                    activeIdx = parseInt(frames[i].getAttribute('data-index'), 10);
                    break;
                }}
            }}

            if (activeIdx !== currentActiveArtIdx) {{
                updateActiveArticleState(activeIdx);
                preloadRunway(activeIdx);
            }}
        }}

        function togglePickerDropdown() {{
            navPickerDropdown.classList.toggle('show');
            navPickerBtn.classList.toggle('active');
        }}

        function closePickerDropdown() {{
            navPickerDropdown.classList.remove('show');
            navPickerBtn.classList.remove('active');
        }}

        function toggleFullScreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen().catch(() => {{}});
            }} else {{
                document.exitFullscreen().catch(() => {{}});
            }}
        }}

        function showToast(msg) {{
            restoreToastText.textContent = msg;
            restoreToast.classList.add('show');
            setTimeout(() => {{ restoreToast.classList.remove('show'); }}, 2500);
        }}

        document.addEventListener('click', (e) => {{
            if (!currentActiveFolder) {{
                document.querySelectorAll('.card-dropdown-menu').forEach(m => m.classList.remove('show'));
                document.querySelectorAll('.btn-card-list').forEach(b => b.classList.remove('active'));
                closePickerDropdown();
                closeSearchDropdown();
                return;
            }}

            if (e.target.closest('#readerNav') || e.target.closest('#restoreToast')) {{
                return;
            }}

            if (e.clientY <= 90) {{
                toggleNav();
            }} else {{
                hideNav();
            }}
        }});

        function toggleCardDropdown(btn) {{
            const menu = btn.nextElementSibling;
            const isOpen = menu.classList.contains('show');
            document.querySelectorAll('.card-dropdown-menu').forEach(m => m.classList.remove('show'));
            document.querySelectorAll('.btn-card-list').forEach(b => b.classList.remove('active'));

            if (!isOpen) {{
                menu.classList.add('show');
                btn.classList.add('active');
            }}
        }}

        document.addEventListener('click', () => {{
            document.querySelectorAll('.card-dropdown-menu').forEach(m => m.classList.remove('show'));
            document.querySelectorAll('.btn-card-list').forEach(b => b.classList.remove('active'));
            closePickerDropdown();
            closeSearchDropdown();
        }});

        themeChipsBar.querySelectorAll('.chip').forEach(chip => {{
            chip.addEventListener('click', () => {{
                themeChipsBar.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                selectedThemeFilter = chip.dataset.theme || '';
                filterFolderCards();
            }});
        }});

        function filterFolderCards() {{
            const cards = foldersGrid.querySelectorAll('.folder-card');
            cards.forEach(c => {{
                if (!selectedThemeFilter || c.dataset.theme === selectedThemeFilter) {{
                    c.style.display = 'flex';
                }} else {{
                    c.style.display = 'none';
                }}
            }});
        }}

        globalSearchInput.addEventListener('input', () => {{
            const query = globalSearchInput.value.trim().toLowerCase();
            clearSearchBtn.style.display = query ? 'flex' : 'none';

            if (!query) {{
                closeSearchDropdown();
                return;
            }}

            const matches = [];
            libraryData.forEach(folder => {{
                folder.images.forEach((img, idx) => {{
                    const artIdx = idx + 1;
                    const title = img.cleanTitle.toLowerCase();
                    const sub = (img.subtitle || '').toLowerCase();
                    if (title.includes(query) || sub.includes(query) || folder.displayName.toLowerCase().includes(query)) {{
                        matches.push({{
                            folder: folder,
                            artIdx: artIdx,
                            img: img
                        }});
                    }}
                }});
            }});

            searchMatchCount.textContent = `${{matches.length}} cocok`;

            if (matches.length === 0) {{
                searchResultList.innerHTML = `<div class="dropdown-empty">Tidak ada materi yang cocok dengan "<strong>${{escapeHtml(query)}}</strong>"</div>`;
            }} else {{
                const limited = matches.slice(0, 10);
                let resHtml = '';
                limited.forEach(m => {{
                    const highlighted = highlightMatch(m.img.cleanTitle, query);
                    resHtml += `
                        <div class="search-result-item" onclick="openReader('${{m.folder.rawName}}', ${{m.artIdx}}); closeSearchDropdown();">
                            <span class="result-folder-icon">${{m.folder.theme.icon}}</span>
                            <div class="result-text-block">
                                <div class="result-title-line">${{highlighted}}</div>
                                <div class="result-path-line"><span class="result-path-folder">${{m.folder.code}} • ${{escapeHtml(m.folder.displayName)}}</span> #${{m.artIdx}}</div>
                            </div>
                            <span class="result-arrow">→</span>
                        </div>
                    `;
                }});
                searchResultList.innerHTML = resHtml;
            }}

            searchDropdown.classList.add('active');
        }});

        function highlightMatch(text, query) {{
            const regex = new RegExp(`(${{query.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&')}})`, 'gi');
            return escapeHtml(text).replace(regex, '<span class="match-mark">$1</span>');
        }}

        clearSearchBtn.addEventListener('click', () => {{
            globalSearchInput.value = '';
            clearSearchBtn.style.display = 'none';
            closeSearchDropdown();
        }});

        function closeSearchDropdown() {{
            searchDropdown.classList.remove('active');
        }}

        function setRoute(rawName, artIdx) {{
            if (!rawName) {{
                history.replaceState(null, '', window.location.pathname + window.location.search);
            }} else {{
                const hash = artIdx && artIdx > 1 ? `#${{rawName}}:${{artIdx}}` : `#${{rawName}}`;
                history.replaceState(null, '', hash);
            }}
        }}

        function handleHashRoute() {{
            const hash = window.location.hash.replace(/^#/, '');
            if (!hash) {{
                if (currentActiveFolder) closeReader(false);
                return;
            }}

            const parts = hash.split(':');
            const folderName = parts[0];
            const artIdx = parts.length > 1 ? parseInt(parts[1], 10) : 0;

            if (folderMap[folderName]) {{
                openReader(folderName, artIdx, false);
            }}
        }}

        window.addEventListener('hashchange', handleHashRoute);
        window.addEventListener('DOMContentLoaded', () => {{
            handleHashRoute();
        }});
    </script>
</body>
</html>
"""
    index_html_path = os.path.join(CWD, "index.html")
    with open(index_html_path, "w", encoding="utf-8") as out:
        out.write(index_html)

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
