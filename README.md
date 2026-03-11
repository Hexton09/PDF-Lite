# 🛠️ PDF Lite

**PDF Lite** is a no-nonsense, high-performance web utility designed to handle common PDF tasks without the bloat. Built with Python and Streamlit, it processes files entirely in memory, ensuring your data never touches a permanent storage disk.

## ✨ Features

- **Merge PDFs**: Concatenate multiple documents into one in seconds.
- **JPG ↔ PDF**: Two-way conversion between images and PDF documents.
- **PDF Compressor**: Lossless compression to reduce file size for email and web uploads.
- **Word to PDF**: Extract and convert `.docx` content into portable PDF format.
- **Size Preview**: Real-time "Before & After" file size metrics for every operation.
- **Privacy First**: Files are processed in RAM and never saved to the server.

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- [Streamlit](https://streamlit.io/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/pdf-lite.git](https://github.com/yourusername/pdf-lite.git)
   cd pdf-lite
   ```
2. Install Dependencies
  ```
  pip install -r requirements.txt
  ```
3. Run the application
   ```
   streamlit run app.py
   ```

## 📦 Tech Stack
* Frontend/UI: Streamlit

* PDF Logic: pypdf, PyMuPDF (fitz)

* Image Conversion: img2pdf

* Document Parsing: docx2txt
