import os
import json
import re
from html import unescape
from tkinter import Tk, filedialog

root = Tk()
root.withdraw()
selected_folder = filedialog.askdirectory()

original_files = {}

en_json = {}

pattern = re.compile(r'(?<=\>)([^<]+)(?=\<)')

def add_language_toggle(content):
    footer_end_pattern = re.compile(r'(</footer>)(.*)', re.DOTALL)
    toggle_html = '''
				    <!-- Dil Toggle Button -->
					<input type="checkbox" id="language-toggle">
                    <label id="button" for="language-toggle">
	                    <div id="knob"></div>
	                    <div id="language-text">Türkçe</div>
                    </label>
                    <div style="opacity:20%;color:#f0f1f2;">Developer by <img style="max-height:20px;max-width:20px;border-radius:50px;" src="https://mebularts.com.tr/public/images/media/1663876743MBLogoBeyaz.jpg" class="icon-favicon" alt="mebularts logo" /> <a style="font-family:Righteous,sans-serif;font-weight:400;color:#fff;text-transform: lowercase;" href="https://mebularts.com.tr/" target="_blank">mebularts</a>.</div>
                    <script src="assets/language.js"></script>
                    <link rel="stylesheet" href="assets/language.css">
    '''
    return footer_end_pattern.sub(r'\1' + toggle_html + r'\2', content)

def process_files(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.php') or file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                    original_files[file_path] = original_content

                    processed_content = original_content
                    matches = re.findall(pattern, original_content)
                    file_name = os.path.splitext(file)[0]

                    for idx, text in enumerate(matches):
                        clean_text = text.strip()
                        if clean_text and not clean_text.isspace():
                            clean_text = unescape(clean_text)

                            key = f"{file_name}_{idx + 1}".lower()

                            if 'id="language-text"' in processed_content:
                                continue

                            if f'data-text="{key}"' not in processed_content:
                                if key not in en_json:
                                    en_json[key] = clean_text

                                processed_content = re.sub(
                                    rf'(<[^>]*)(>)(\s*{re.escape(text)}\s*)(</[^>]+>)',
                                    rf'\1 data-text="{key}"\2\3\4',
                                    processed_content,
                                    count=1
                                )

                    processed_content = add_language_toggle(processed_content)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(processed_content)

    with open(os.path.join(folder_path, 'assets/en.json'), 'w', encoding='utf-8') as f:
        json.dump(en_json, f, ensure_ascii=False, indent=4)

    create_language_js(folder_path)

    create_language_css(folder_path)

def create_language_js(folder_path):
    language_js_content = """
document.addEventListener("DOMContentLoaded", function () {
    const languageToggle = document.getElementById('language-toggle');
    const languageText = document.getElementById('language-text');

    languageToggle.addEventListener('change', () => {
        const language = languageToggle.checked ? 'en' : 'tr';
        localStorage.setItem('preferredLanguage', language);
        languageText.textContent = language === 'en' ? 'English' : 'Türkçe';
        loadLanguage(language);
    });

    function loadLanguage(language) {
        fetch(`assets/lang/${language}.json`)
            .then(response => response.json())
            .then(data => {
                document.querySelectorAll('[data-text]').forEach(element => {
                    const key = element.getAttribute('data-text');
                    if (data[key]) {
                        element.textContent = data[key];
                    }
                });
            })
            .catch(error => console.error("Dil dosyası yüklenemedi:", error));
    }

    const preferredLanguage = localStorage.getItem('preferredLanguage') || 'en';
    languageToggle.checked = (preferredLanguage === 'en'); // Toggle butonunu ayarla
    languageText.textContent = preferredLanguage === 'en' ? 'English' : 'Türkçe';
    loadLanguage(preferredLanguage);
});
    """
    language_js_path = os.path.join(folder_path, 'assets', 'language.js')
    os.makedirs(os.path.dirname(language_js_path), exist_ok=True)
    with open(language_js_path, 'w', encoding='utf-8') as f:
        f.write(language_js_content)

def create_language_css(folder_path):
    language_css_content = """
@import url('https://fonts.googleapis.com/css2?family=SUSE:wght@100..800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200..1000;1,200..1000&family=SUSE:wght@100..800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Righteous&display=swap');

input[type="checkbox"] {
  display: none;
}

#button {
  position: relative;
  display: block;
  width: 150px;
  height: 60px;
  background-color: #b80404;
  border-radius: 30px;
  cursor: pointer;
  margin: 20px auto;
  transition: background-color 0.3s ease;
}

#knob {
  width: 50px;
  height: 50px;
  background-color: #fff;
  position: absolute;
  top: 5px;
  left: 5px;
  border-radius: 50%;
  transition: 0.4s ease left, 0.4s ease background-color;
  background-image: url(https://i.hizliresim.com/ltsw1d9.jpg);
  background-size: cover;
  background-position: center;;
}

#language-text {
  position: absolute;
  top: 50%;
  left: 70px;
  transform: translateY(-50%);
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  transition: color 0.4s ease, left 0.4s ease;;
}

#language-toggle:checked + #button {
  background-color: #0d1366;
}

#language-toggle:checked + #button #knob {
  left: 95px;
  background-color: #ffffff;
  background-image: url(https://m.media-amazon.com/images/I/61dHFpZmRSL._AC_UF1000,1000_QL80_.jpg);
}

#language-toggle:checked + #button #language-text {
  color: #ffffff;
  left: 20px;
  transition: left 0.4s ease;
}

/* Follow Me instagram.com/mebularts :) */
    """
    language_css_path = os.path.join(folder_path, 'assets', 'language.css')
    os.makedirs(os.path.dirname(language_css_path), exist_ok=True)
    with open(language_css_path, 'w', encoding='utf-8') as f:
        f.write(language_css_content)
        
def undo_changes():
    for file_path, content in original_files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

process_files(selected_folder)

# undo_changes()
