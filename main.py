import flet as ft
import io
import os
import img2pdf
from pypdf import PdfReader, PdfWriter

def main(page: ft.Page):
    page.title = "PDF Lite"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = "auto"

    # --- Feature Logic ---
    def get_size_format(b):
        size = len(b)
        for unit in ['B', 'KB', 'MB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} GB"

    def save_to_downloads(data, filename):
        try:
            # Check for permission first using Flet's native handler
            if page.check_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE) != ft.PermissionStatus.GRANTED:
                page.request_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE)

            # Standard Android Download path
            path = f"/storage/emulated/0/Download/{filename}"
            
            # If file exists, don't overwrite, append a number
            counter = 1
            base_name, extension = os.path.splitext(filename)
            while os.path.exists(path):
                path = f"/storage/emulated/0/Download/{base_name}_{counter}{extension}"
                counter += 1

            with open(path, "wb") as f:
                f.write(data)
                
            page.snack_bar = ft.SnackBar(
                ft.Text(f"✅ Saved to Downloads: {os.path.basename(path)}"), 
                bgcolor=ft.Colors.GREEN_700
            )
        except Exception as e:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"❌ Error: {str(e)}"), 
                bgcolor=ft.Colors.RED_700
            )
        page.snack_bar.open = True
        page.update()

    # --- Pickers ---
    def process_merge(e: ft.FilePickerResultEvent):
        if e.files:
            writer = PdfWriter()
            try:
                for f in e.files:
                    writer.append(f.path)
                out = io.BytesIO()
                writer.write(out)
                save_to_downloads(out.getvalue(), "merged_lite.pdf")
            except Exception as ex:
                print(f"Merge error: {ex}")

    def process_jpg(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                # Get paths of selected images
                image_paths = [f.path for f in e.files]
                pdf_bytes = img2pdf.convert(image_paths)
                save_to_downloads(pdf_bytes, "images_to_pdf.pdf")
            except Exception as ex:
                print(f"JPG conversion error: {ex}")

    merge_picker = ft.FilePicker(on_result=process_merge)
    jpg_picker = ft.FilePicker(on_result=process_jpg)
    page.overlay.extend([merge_picker, jpg_picker])

    # --- UI Layout ---
    page.add(
        ft.AppBar(
            title=ft.Text("PDF Lite", color=ft.Colors.WHITE), 
            bgcolor=ft.Colors.BLUE_700,
            center_title=True
        ),
        ft.Column([
            ft.Container(height=10),
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.MERGE_TYPE, color=ft.Colors.BLUE_700),
                    title=ft.Text("Merge Multiple PDFs"),
                    subtitle=ft.Text("Select 2 or more files"),
                    on_click=lambda _: merge_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["pdf"])
                )
            ),
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.IMAGE_OUTLINED, color=ft.Colors.ORANGE_700),
                    title=ft.Text("JPG to PDF"),
                    subtitle=ft.Text("Convert images to document"),
                    on_click=lambda _: jpg_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)
                )
            ),
        ])
    )

ft.app(target=main)
