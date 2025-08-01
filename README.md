# PDF Reader + Translator

This is a Python application for reading and translating PDF files with optional OCR (Optical Character Recognition) support. It allows you to display the original PDF pages as images and view the translated text upon request.

## Features

- Display original PDF pages as high-resolution images.
- Translate page text using Microsoft Azure Translator API.
- Automatically switch to OCR if no readable text is detected on a page.
- Toggle between "Original" (PDF image) and "Translated" (text) view.
- Navigate through pages using keyboard or buttons.
- Accelerated navigation when holding arrow keys.

## Requirements

- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (must be installed separately and added to PATH)

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

### Example requirements.txt

```
pytesseract
Pillow
PyMuPDF
requests
customtkinter
langdetect
```

## Azure Translator Configuration

Set your Azure credentials in the script:

```python
AZURE_KEY = "your-key-here"
AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
AZURE_REGION = "your-region"  # e.g., "eastus"
```

Get your credentials from the [Azure Portal](https://portal.azure.com).

## How It Works

1. When opening a PDF, each page is checked:
   - If extractable text exists → used directly.
   - If not → page is converted to image and sent to Tesseract (OCR).
2. Translations are triggered only by clicking the **Translate** button.
3. Navigation:
   - Use `↑` / `↓` keys or the on-screen buttons.
   - Holding a key accelerates scrolling speed.

## Usage

Run the main application:

```bash
python your_script_name.py
```

## Notes

- Translations are only performed on-demand.
- OCR can be slower for scanned or low-quality documents.
- Translation target is Russian by default (`to_lang='ru'`), but can be changed.

## License
MIT

This project is intended for educational or personal use. You are free to modify or extend it.
