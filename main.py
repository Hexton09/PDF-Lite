import flet as ft
import flet_permission_handler as fph
import io
import os
import img2pdf
from pypdf import PdfReader, PdfWriter

def main(page: ft.Page):
    page.title = "PDF Lite"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = "auto"

    # Initialize Permission Handler
    ph = fph.PermissionHandler()
    page.overlay.append(ph)

    # --- Startup Logic ---
    def check_permissions():
        # Request storage permission on startup
        status = ph.request_permission(fph.PermissionType.STORAGE)
        if status != fph.PermissionStatus.GRANTED:
            # If denied, show a permanent alert until they allow it
            page.dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Permission Required"),
                content=ft.Text("This app needs storage access to merge and save your PDFs. Please allow it to continue."),
                actions=[
                    ft.TextButton("Open Settings", on_click=lambda _: ph.open_app_settings()),
                    ft.TextButton("Try Again", on_click=lambda _: check_permissions()),
                ],
            )
            page.dialog.open = True
            page.update()
        else:
            if page.dialog:
                page.dialog.open = False
            page.update()

    # --- Feature Logic ---
    def get_size_format(b):
        size = len(b)
        for unit in ['B', 'KB', 'MB']:
            if size < 1024: return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} GB"

    def save_to_downloads(data, filename):
        try:
            path = f"/storage/emulated/0/Download/{filename}"
            with open(path, "wb") as f:
                f.write(data)
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ Saved: {filename} ({get_size_format(data)})"), bgcolor=ft.Colors.GREEN_700)
        except Exception:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Error: Permission denied. Check app settings."), bgcolor=ft.Colors.RED_700)
        page.snack_bar.open = True
        page.update()

    # --- UI Elements ---
    merge_picker = ft.FilePicker(on_result=lambda e: process_merge(e))
    jpg_picker = ft.FilePicker(on_result=lambda e: process_jpg(e))
    page.overlay.extend([merge_picker, jpg_picker])

    def process_merge(e):
        if e.files:
            writer = PdfWriter()
            for f in e.files: writer.append(f.path)
            out = io.BytesIO()
            writer.write(out)
            save_to_downloads(out.getvalue(), "merged.pdf")

    def process_jpg(e):
        if e.files:
            pdf_bytes = img2pdf.convert([f.path for f in e.files])
            save_to_downloads(pdf_bytes, "images.pdf")

    # --- App Build ---
    page.add(
        ft.AppBar(title=ft.Text("PDF Lite"), bgcolor=ft.Colors.BLUE_700),
        ft.Column([
            ft.Card(content=ft.ListTile(title=ft.Text("Merge PDFs"), on_click=lambda _: merge_picker.pick_files(allow_multiple=True))),
            ft.Card(content=ft.ListTile(title=ft.Text("JPG to PDF"), on_click=lambda _: jpg_picker.pick_files(allow_multiple=True))),
        ])
    )

    # Trigger the permission check immediately
    check_permissions()

ft.app(target=main)