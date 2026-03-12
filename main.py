import flet as ft
import io
import os
from PIL import Image
from pypdf import PdfWriter

def main(page: ft.Page):
    page.title = "PDF Lite"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # --- Helper to handle Android Downloads ---
    def save_to_downloads(data, filename):
        try:
            # Trigger permission request
            if page.check_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE) != ft.PermissionStatus.GRANTED:
                page.request_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE)

            path = f"/storage/emulated/0/Download/{filename}"
            
            # Simple conflict resolver
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(path):
                path = f"/storage/emulated/0/Download/{base}_{counter}{ext}"
                counter += 1

            with open(path, "wb") as f:
                f.write(data)
                
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Saved to Downloads: {os.path.basename(path)}"), bgcolor="green")
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {str(e)}"), bgcolor="red")
        
        page.snack_bar.open = True
        page.update()

    # --- Feature Logic ---
    def process_merge(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                writer = PdfWriter()
                for f in e.files:
                    writer.append(f.path)
                out = io.BytesIO()
                writer.write(out)
                save_to_downloads(out.getvalue(), "merged_result.pdf")
            except Exception as ex:
                print(f"Merge error: {ex}")

    def process_jpg(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                images = [Image.open(f.path).convert('RGB') for f in e.files]
                if images:
                    out = io.BytesIO()
                    images[0].save(out, format="PDF", save_all=True, append_images=images[1:])
                    save_to_downloads(out.getvalue(), "images_to_pdf.pdf")
            except Exception as ex:
                print(f"JPG error: {ex}")

    # --- Pickers ---
    merge_picker = ft.FilePicker(on_result=process_merge)
    jpg_picker = ft.FilePicker(on_result=process_jpg)
    page.overlay.extend([merge_picker, jpg_picker])

    # --- UI Layout ---
    page.add(
        ft.AppBar(title=ft.Text("PDF Lite", color="white"), bgcolor=ft.Colors.BLUE_700, center_title=True),
        ft.Column([
            ft.Container(height=20),
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.BLUE_700),
                    title=ft.Text("Merge PDFs"),
                    on_click=lambda _: merge_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["pdf"])
                )
            ),
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.IMAGE, color=ft.Colors.ORANGE_700),
                    title=ft.Text("Images to PDF"),
                    on_click=lambda _: jpg_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)
                )
            ),
        ])
    )
    page.update()

ft.app(target=main)
