import flet as ft
import io
import os

# Wrap imports in a safety net
try:
    from PIL import Image
    from pypdf import PdfWriter
    IMPORT_ERROR = None
except Exception as e:
    IMPORT_ERROR = str(e)

def main(page: ft.Page):
    page.title = "PDF Lite"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # --- CRASH CATCHER UI ---
    if IMPORT_ERROR:
        page.add(ft.Container(
            content=ft.Text(f"CRITICAL ERROR: {IMPORT_ERROR}\nCheck requirements.txt", color="white"),
            bgcolor="red", padding=20, expand=True
        ))
        return

    # --- SAVE LOGIC ---
    def save_to_downloads(data, filename):
        try:
            # Android 11+ Permission Request
            if page.check_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE) != ft.PermissionStatus.GRANTED:
                page.request_permission(ft.PermissionType.MANAGE_EXTERNAL_STORAGE)

            path = f"/storage/emulated/0/Download/{filename}"
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(path):
                path = f"/storage/emulated/0/Download/{base}_{counter}{ext}"
                counter += 1

            with open(path, "wb") as f:
                f.write(data)
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Saved: {os.path.basename(path)}"), bgcolor="green")
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Permission Error: {str(e)}"), bgcolor="red")
        
        page.snack_bar.open = True
        page.update()

    # --- UI LAYOUT ---
    def on_merge_result(e: ft.FilePickerResultEvent):
        if e.files:
            writer = PdfWriter()
            for f in e.files: writer.append(f.path)
            out = io.BytesIO()
            writer.write(out)
            save_to_downloads(out.getvalue(), "merged.pdf")

    def on_jpg_result(e: ft.FilePickerResultEvent):
        if e.files:
            imgs = [Image.open(f.path).convert("RGB") for f in e.files]
            out = io.BytesIO()
            imgs[0].save(out, format="PDF", save_all=True, append_images=imgs[1:])
            save_to_downloads(out.getvalue(), "images.pdf")

    merge_picker = ft.FilePicker(on_result=on_merge_result)
    jpg_picker = ft.FilePicker(on_result=on_jpg_result)
    page.overlay.extend([merge_picker, jpg_picker])

    page.add(
        ft.AppBar(title=ft.Text("PDF Lite"), bgcolor=ft.Colors.BLUE_700),
        ft.Column([
            ft.Card(content=ft.ListTile(title=ft.Text("Merge PDFs"), on_click=lambda _: merge_picker.pick_files(allow_multiple=True))),
            ft.Card(content=ft.ListTile(title=ft.Text("JPG to PDF"), on_click=lambda _: jpg_picker.pick_files(allow_multiple=True))),
        ])
    )

ft.app(target=main)
