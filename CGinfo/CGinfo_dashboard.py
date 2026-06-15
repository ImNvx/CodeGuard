import flet as ft

def main(page: ft.Page):
    page.title = "CGinfo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    page.add(
        ft.Stack(
            controls=[
                ft.Container(
                    content=ft.Text("CGinfo Dashboard", size=35, weight=ft.FontWeight.BOLD),
                    alignment=ft.Alignment.TOP_LEFT,
                    padding=15,
                ),
                
                ft.Container(
                    content=ft.Image(src="cg_shield.png", width=125),
                    alignment=ft.Alignment.TOP_CENTER,
                    padding=20,
                )
            ],
            expand=True
        )
    )

    #sa fac padding adjustment pe window resize

ft.run(main)