import fitz, requests, uuid, json
import os, io, time
import tkinter as tk
import pytesseract
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import customtkinter as ctk

# === Конфигурация Azure ===
AZURE_KEY = ""
AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
AZURE_REGION = "eastus" 

def azure_translate(text, to_lang='ru', from_lang=None):
    path = '/translate'
    url = AZURE_ENDPOINT + path
    params = {'api-version': '3.0', 'to': [to_lang]}
    if from_lang and from_lang != 'auto':
        params['from'] = from_lang
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_REGION,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{'text': text}]
    response = requests.post(url, params=params, headers=headers, json=body)
    response.raise_for_status()
    return response.json()[0]['translations'][0]['text']

def extract_text_or_ocr(page):
    text = page.get_text()
    if text and len(text.strip()) > 20:
        return ("text", text)
    else:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        ocr_text = pytesseract.image_to_string(img)
        return ("ocr", ocr_text)

class PDFReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Reader + Translate")
        self.root.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.text_area = ctk.CTkTextbox(root, wrap='word', font=("Consolas", 14))
        self.text_area.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(root, bg='white', height=400)
        self.canvas.pack(fill='both', expand=True)

        self.view_mode = tk.StringVar(value="original")
        toggle_frame = ctk.CTkFrame(root)
        toggle_frame.pack(pady=5)
        ctk.CTkRadioButton(toggle_frame, text="Оригинал", variable=self.view_mode, value="original", command=self.update_view).pack(side='left', padx=10)
        ctk.CTkRadioButton(toggle_frame, text="Перевод", variable=self.view_mode, value="translated", command=self.update_view).pack(side='left', padx=10)

        nav_frame = ctk.CTkFrame(root)
        nav_frame.pack()
        ctk.CTkButton(nav_frame, text="▲", width=5, command=lambda: self.change_page(-1)).pack(side='left', padx=10)
        ctk.CTkButton(nav_frame, text="▼", width=5, command=lambda: self.change_page(1)).pack(side='left', padx=10)
        ctk.CTkButton(nav_frame, text="Перевести PDF", command=self.translate_all).pack(side='left', padx=10)

        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Открыть PDF", command=self.open_pdf)
        menubar.add_cascade(label="Файл", menu=filemenu)
        root.config(menu=menubar)

        self.doc = None
        self.page_index = 0
        self.original_images = []
        self.page_texts = []
        self.page_translations = []
        self.tk_images = []
        self.last_press_time = 0
        self.acceleration_factor = 1

        root.bind('<Up>', lambda e: self.key_change_page(-1))
        root.bind('<Down>', lambda e: self.key_change_page(1))

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return
        self.doc = fitz.open(path)
        self.page_index = 0
        self.original_images.clear()
        self.page_texts.clear()
        self.page_translations.clear()
        self.tk_images.clear()

        for page in self.doc:
            kind, content = extract_text_or_ocr(page)
            self.page_texts.append(content)
            pix = page.get_pixmap(dpi=150)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            self.original_images.append(img)
            self.tk_images.append(ImageTk.PhotoImage(img))
            self.page_translations.append(None)

        self.show_page()

    def translate_all(self):
        for i, text in enumerate(self.page_texts):
            try:
                translated = azure_translate(text[:4500])
            except Exception as e:
                translated = f"[Ошибка перевода: {e}]"
            self.page_translations[i] = translated
        self.update_view()

    def show_page(self):
        self.text_area.delete("1.0", tk.END)
        self.canvas.delete("all")

        if self.view_mode.get() == "original":
            self.canvas.create_image(0, 0, anchor='nw', image=self.tk_images[self.page_index])
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
        else:
            translated = self.page_translations[self.page_index]
            self.text_area.insert(tk.END, translated or "[Нажмите 'Перевести PDF']")

        self.root.title(f"PDF Reader - Страница {self.page_index + 1} / {len(self.page_texts)}")

    def update_view(self):
        self.show_page()

    def change_page(self, delta):
        new_index = self.page_index + delta
        if 0 <= new_index < len(self.page_texts):
            self.page_index = new_index
            self.show_page()

    def key_change_page(self, delta):
        now = time.time()
        if now - self.last_press_time < 0.3:
            self.acceleration_factor = min(self.acceleration_factor + 1, 5)
        else:
            self.acceleration_factor = 1
        self.last_press_time = now
        for _ in range(self.acceleration_factor):
            self.change_page(delta)

if __name__ == "__main__":
    root = ctk.CTk()
    app = PDFReaderApp(root)
    root.mainloop()
