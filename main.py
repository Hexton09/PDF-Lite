import flet as ft
import io
import os
import time
from PIL import Image
from pypdf import PdfWriter

def main(page: ft.Page):
    # Standard Page Setup
    page.title = "PDF Lite"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # --- UI Components (Defined early but added later) ---
    def save_to_downloads(data, filename):
        try:
            # Check for permission
            if page.check_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE) != ft.PermissionStatus.GRANTED:
                page.request_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE)

            path = f"/storage/emulated/0/Download/{filename}"
            
            # Conflict check
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(path):
                path = f"/storage/emulated/0/Download/{base}_{counter}{ext}"
                counter += 1

            with open(path, "wb") as f:
                f.write(data)
                
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Success: {os.path.basename(path)}"), bgcolor=ft.Colors.GREEN_700)
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {str(e)}"), bgcolor=ft.Colors.RED_700)
        
        page.snack_bar.open = True
        page.update()

    def process_merge(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                writer = PdfWriter()
                for f in e.files:
                    writer.append(f.path)
                out = io.BytesIO()
                writer.write(out)
                save_to_downloads(out.getvalue(), "merged_pdf.pdf")
            except Exception as ex:
                print(f"Merge error: {ex}")

    def process_jpg(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                images = []
                for f in e.files:
                    img = Image.open(f.path).convert('RGB')
                    images.append(img)
                if images:
                    out = io.BytesIO()
                    images[0].save(out, format="PDF", save_all=True, append_images=images[1:])
                    save_to_downloads(out.getvalue(), "converted_images.pdf")
            except Exception as ex:
                print(f"JPG error: {ex}")

    # Initialize Pickers
    merge_picker = ft.FilePicker(on_result=process_merge)
    jpg_picker = ft.FilePicker(on_result=process_jpg)
    page.overlay.extend([merge_picker, jpg_picker])

    # Build the UI
    page.add(
        ft.AppBar(title=ft.Text("PDF Lite"), bgcolor=ft.Colors.BLUE_700, center_title=True),
        ft.Column([
            ft.Container(height=20),
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.BLUE_700),
                    title=ft.Text("Merge PDF Files"),
                    on_click=lambda _: merge_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["pdf"])
                )
            ),
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.IMAGE, color=ft.Colors.ORANGE_700),
                    title=ft.Text("JPG/PNG to PDF"),
                    on_click=lambda _: jpg_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)
                )
            ),
        ])
    )
    
    # Final page update to ensure everything rendered
    page.update()

# Startup
ft.app(target=main)
