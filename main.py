import flet as ft
import io
import os
import time
from PIL import Image
from pypdf import PdfWriter

def main(page: ft.Page):
    # Give the Android bridge a second to initialize
    time.sleep(0.5)
    
    page.title = "PDF Lite"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # --- Feature Logic ---
    def save_to_downloads(data, filename):
        try:
            # Request permission ONLY when saving
            if page.check_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE) != ft.PermissionStatus.GRANTED:
                page.request_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE)

            path = f"/storage/emulated/0/Download/{filename}"
            with open(path, "wb") as f:
                f.write(data)
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Saved to Downloads"), bgcolor="green")
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {str(e)}"), bgcolor="red")
        page.snack_bar.open = True
        page.update()

    def process_merge(e: ft.FilePickerResultEvent):
        if e.files:
            writer = PdfWriter()
            for f in e.files: writer.append(f.path)
            out = io.BytesIO()
            writer.write(out)
            save_to_downloads(out.getvalue(), "merged.pdf")

    def process_jpg(e: ft.FilePickerResultEvent):
        if e.files:
            images = [Image.open(f.path).convert('RGB') for f in e.files]
            out = io.BytesIO()
            images[0].save(out, format="PDF", save_all=True, append_images=images[1:])
            save_to_downloads(out.getvalue(), "images.pdf")

    # --- UI Elements ---
    merge_picker = ft.FilePicker(on_result=process_merge)
    jpg_picker = ft.FilePicker(on_result=process_jpg)
    page.overlay.extend([merge_picker, jpg_picker])

    page.add(
        ft.AppBar(title=ft.Text("PDF Lite"), bgcolor=ft.Colors.BLUE_700),
        ft.Column([
            ft.Container(height=20),
            ft.Card(content=ft.ListTile(
                leading=ft.Icon(ft.Icons.PICTURE_AS_PDF),
                title=ft.Text("Merge PDFs"), 
                on_click=lambda _: merge_picker.pick_files(allow_multiple=True)
            )),
            ft.Card(content=ft.ListTile(
                leading=ft.Icon(ft.Icons.IMAGE),
                title=ft.Text("JPG to PDF"), 
                on_click=lambda _: jpg_picker.pick_files(allow_multiple=True)
            )),
        ])
    )
    
    # Force the UI to draw
    page.update()

ft.app(target=main)
