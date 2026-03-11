import streamlit as st
import io
import fitz  # PyMuPDF
import img2pdf
from pypdf import PdfReader, PdfWriter
import docx2txt

st.set_page_config(page_title="Pro PDF Tool", layout="wide")
st.title("🛠️ Functional PDF Suite")

# Helper function for human-readable file sizes
def get_file_size(file_bytes):
    size = len(file_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"

tabs = st.tabs(["Merge", "JPG ↔ PDF", "Compress", "Word to PDF"])

# --- 1. PDF MERGE ---
with tabs[0]:
    st.header("Merge PDFs")
    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True, key="m")
    if files and st.button("Merge Files"):
        writer = PdfWriter()
        for f in files:
            writer.append(f)
        
        out = io.BytesIO()
        writer.write(out)
        final_bytes = out.getvalue()

        # Preview Section
        st.success(f"Successfully merged {len(files)} files!")
        st.metric("New File Size", get_file_size(final_bytes))
        st.download_button("Download Merged PDF", final_bytes, "merged.pdf")

# --- 2. JPG ↔ PDF ---
with tabs[1]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("JPG to PDF")
        imgs = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        if imgs and st.button("Convert Images"):
            pdf_bytes = img2pdf.convert([i.getvalue() for i in imgs])
            
            st.metric("Generated PDF Size", get_file_size(pdf_bytes))
            st.download_button("Download PDF", pdf_bytes, "images_to.pdf")
            
    with col2:
        st.subheader("PDF to JPG")
        pdf_img = st.file_uploader("Upload PDF", type="pdf", key="p2j")
        if pdf_img and st.button("Process Extraction"):
            pdf_data = pdf_img.read()
            doc = fitz.open(stream=pdf_data, filetype="pdf")
            st.write(f"Found {len(doc)} pages. Download them individually below:")
            
            for i, page in enumerate(doc):
                pix = page.get_pixmap()
                img_data = pix.tobytes("jpg")
                st.download_button(f"Download Page {i+1} ({get_file_size(img_data)})", img_data, f"page_{i+1}.jpg")

# --- 3. COMPRESSOR ---
with tabs[2]:
    st.header("PDF Compressor")
    to_comp = st.file_uploader("Upload heavy PDF", type="pdf")
    if to_comp:
        orig_bytes = to_comp.getvalue()
        orig_size_val = len(orig_bytes)
        
        if st.button("Optimize Size"):
            reader = PdfReader(io.BytesIO(orig_bytes))
            writer = PdfWriter()
            for page in reader.pages:
                page.compress_content_streams()
                writer.add_page(page)
            
            out = io.BytesIO()
            writer.write(out)
            new_bytes = out.getvalue()
            new_size_val = len(new_bytes)

            # Preview Section with Delta
            st.markdown("---")
            col_a, col_b = st.columns(2)
            col_a.metric("Original Size", get_file_size(orig_bytes))
            
            # Calculate reduction percentage
            reduction = ((orig_size_val - new_size_val) / orig_size_val) * 100
            col_b.metric("Compressed Size", get_file_size(new_bytes), delta=f"-{reduction:.1f}%")
            
            st.download_button("Download Compressed PDF", new_bytes, "compressed.pdf")

# --- 4. WORD TO PDF ---
with tabs[3]:
    st.header("Word to PDF")
    st.info("Simple conversion: Extracts text and converts to PDF.")
    doc_file = st.file_uploader("Upload .docx", type="docx")
    if doc_file and st.button("Convert to PDF"):
        text = docx2txt.process(doc_file)
        new_pdf = fitz.open()
        page = new_pdf.new_page()
        page.insert_text((50, 72), text)
        
        out = io.BytesIO()
        new_pdf.save(out)
        final_pdf = out.getvalue()
        
        st.metric("Final PDF Size", get_file_size(final_pdf))
        st.download_button("Download PDF", final_pdf, "word_converted.pdf")