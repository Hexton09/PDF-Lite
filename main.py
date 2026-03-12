import flet as ft
import io
import os
import traceback

# 1. Wrap imports in a safety net to see if libraries are missing
try:
    from PIL import Image
    from pypdf import PdfWriter
    LOAD_ERROR = None
except Exception:
    LOAD_ERROR = traceback.format_exc()

def main(page: ft.Page):
    page.title = "PDF Lite"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # --- CRASH CATCHER ---
    # If the app fails to import libraries, it shows the error on screen
    if LOAD_ERROR:
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("❌ Startup Error", size=25, color="red", weight="bold"),
                    ft.Text(f"The app couldn't load libraries:\n\n{LOAD_ERROR}", color="black"),
                ], scroll="auto"),
                padding=20, expand=True, bgcolor="#ffebee"
            )
        )
        page.update()
        return

    # --- FEATURE LOGIC ---
    def save_to_downloads(data, filename):
        try:
            # ONLY request permission when the user actually saves a file
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
            
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Saved to Downloads: {os.path.basename(path)}"), bgcolor="green")
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"❌ Storage Error: {str(e)}"), bgcolor="red")
        
        page.snack_bar.open = True
        page.update()

    def process_merge(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                writer = PdfWriter()
                for f in e.files: writer.append(f.path)
                out = io.BytesIO()
                writer.write(out)
                save_to_downloads(out.getvalue(), "merged_pdfs.pdf")
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Merge error: {ex}"))
                page.snack_bar.open = True
                page.update()

    def process_jpg(e: ft.FilePickerResultEvent):
        if e.files:
            try:
                images = [Image.open(f.path).convert('RGB') for f in e.files]
                if images:
                    out = io.BytesIO()
                    images[0].save(out, format="PDF", save_all=True, append_images=images[1:])
                    save_to_downloads(out.getvalue(), "images_to_pdf.pdf")
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"JPG error: {ex}"))
                page.snack_bar.open = True
                page.update()

    # --- UI COMPONENTS ---
    merge_picker = ft.FilePicker(on_result=process_merge)
    jpg_picker = ft.FilePicker(on_result=process_jpg)
    page.overlay.extend([merge_picker, jpg_picker])

    # Initial Welcome Screen
    page.add(
        ft.AppBar(title=ft.Text("PDF Lite", color="white"), bgcolor=ft.Colors.BLUE_700, center_title=True),
        ft.Column([
            ft.Container(height=20),
            ft.Text("Choose a tool:", size=18, weight="bold"),
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
                    title=ft.Text("Convert Images to PDF"),
                    on_click=lambda _: jpg_picker.pick_files(allow_multiple=True, file_type=ft.FilePickerFileType.IMAGE)
                )
            ),
        ])
    )
    
    # Critical: Ensure the page updates at the end of main
    page.update()

ft.app(target=main)
