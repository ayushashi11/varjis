from typing import Callable
import flet as ft
from parsing import parse, Output
from utils import clean_text, speak_ssml


class CustomTile(ft.Column):
    def __init__(self, content: str, on_send: Callable[..., None], **kwargs):
        super().__init__(controls=[], **kwargs)
        self.content = content
        self.speech = ""
        self.spoken = False
        self.send = on_send
    
    def did_mount(self):
        self.add("")
        return super().did_mount()

    def add(self, text: str):
        self.content += text
        print(self.content)
        click = None
        partial = True
        try:
            out, partial = parse(self.content)
        except Exception as e:
            if not partial:
                self.speech = "an error occurred"
                out = Output()
                out.message = f"an error occurred {e}"
                partial = False
            else:
                return
        print("adding")
        render, self.speech = clean_text(out.message)
        controls: list[ft.Control] = [
            ft.Markdown(
                render,
                selectable=True,
                extension_set="gitHubWeb",  # type: ignore
                code_theme="atom-one-dark",
                code_style=ft.TextStyle(font_family="Fira Mono"),
                # on_tap_link=lambda e: page.launch_url(e.data),
            )
        ]
        if not partial and out.is_only_tool:
            self.send(out.tool_name,out.parameters)
            out = Output()
            out.message = f"*Running **{out.tool_name}***"
        if out.images:
            row = ft.Row(
                [ft.Image(i, height=100) for i in out.images],
                scroll=ft.ScrollMode.ALWAYS,
            )
            controls.insert(0, row)
        if out.tool_name == "command":
            #TODO
            command = out.parameters.get("command", list())
            if out.parameters.get("sudo_flag", False):
                command.insert(0, "sudo")
            if not partial:
                click = lambda *_args: self.send(out.tool_name,out.parameters)
            controls.append(
                ft.Stack(
                    [
                        ft.Markdown(
                            f"```zsh\n\n {' '.join(command)}\n```",
                            selectable=True,
                            extension_set="gitHubWeb",  # type: ignore
                            code_theme="atom-one-dark",
                            code_style=ft.TextStyle(font_family="Fira Code")
                        ),
                        ft.IconButton(ft.icons.TERMINAL, on_click=click, tooltip="Run command"),
                    ],
                )
            )
        self.controls = controls
        if not partial and not self.spoken:
            self.spoken = True
            speak_ssml(f"<speak>{self.speech}</speak>")
        print(partial)
        return self.update()
    
def test(page: ft.Page):
    import time
    cont = CustomTile("", lambda name,params: print(name, params))
    page.add(cont)
    cont.add("""{
"message":"hello""")
    page.update()
    time.sleep(1)
    cont.add(""" *world*",\n""")
    page.update()
    #time.sleep(1)
    cont.add(""" "images":["https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png", """)
    page.update()
    #time.sleep(1)
    cont.add(""" "https://picsum.photos/200"],""")
    page.update()
    #time.sleep(1)
    cont.add(""" "tool_name":"command",
"parameters": {
    "command": ["cd", "-l"],
    "sudo_flag": false,
    "stdin": ""
}}""")
    page.update()
    con2 = CustomTile("""{
        "is_only_tool": true,
        "tool_name": "command",
        "parameters": {
            "command": ["cd", "-l"],
            "sudo_flag": false,
            "stdin": ""
        }
}""", lambda name,params: print(name, params))
    page.add(con2)
    page.update()
if __name__ == "__main__":
    ft.app(test)
