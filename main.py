import flet as ft
import io
import os
from PIL import Image  # Replacing img2pdf
from pypdf import PdfWriter

def main(page: ft.Page):
    page.title = "PDF Lite"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = "auto"

    def save_to_downloads(data, filename):
        try:
            # Request permission specifically for Android 11+
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
                
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Saved to Downloads: {os.path.basename(path)}"), bgcolor=ft.Colors.GREEN_700)
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Storage Error: {str(e)}"), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()

    def process_merge(e: ft.FilePickerResultEvent):
        if e.files:
            writer = PdfWriter()
            try:
                for f in e.files:
                    writer.append(f.path)
                out = io.BytesIO()
                writer.write(out)
                save_to_downloads(out.getvalue(), "merged_pdfs.pdf")
            except Exception as ex:
                print(f"Merge error: {ex}")

    def process_jpg(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                images = []
                for f in e.files:
                    img = Image.open(f.path)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                
                if images:
                    out = io.BytesIO()
                    # Native Pillow PDF conversion (Android compatible)
                    images[0].save(out, format="PDF", save_all=True, append_images=images[1:])
                    save_to_downloads(out.getvalue(), "images_to_pdf.pdf")
            except Exception as ex:
                print(f"JPG conversion error: {ex}")

    merge_picker = ft.FilePicker(on_result=process_merge)
    jpg_picker = ft.FilePicker(on_result=process_jpg)
    page.overlay.extend([merge_picker, jpg_picker])

    page.add(
        ft.AppBar(title=ft.Text("PDF Lite"), bgcolor=ft.Colors.BLUE_700, center_title=True),
        ft.Column([
            ft.Container(height=10),
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.MERGE_TYPE, color=ft.Colors.BLUE_700),
                    title=ft.Text("Merge PDFs"),
                    on_click=lambda _: merge_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["pdf"])
                )
            ),
            ft.Card(
                content=ft.ListTile(
                    leading=ft.Icon(ft.Icons.IMAGE, color=ft.Colors.ORANGE_700),
                    title=ft.Text("JPG to PDF"),
                    on_click=lambda _: jpg_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)
                )
            ),
        ])
    )

ft.app(target=main)
