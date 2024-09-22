from turtle import color
import flet as ft
import time, json, subprocess as sb, wikipedia, io
import ai, sys
import duckduckgo_search as ddg
from utils import record_and_recognise
from widgets import CustomTile
ddgs = ddg.DDGS()

def ai_run_command(page: ft.Page, command, sudo_flag, stdin=""):
    print(type(command), command, sudo_flag, stdin)
    if sudo_flag:
        prompt = ft.Markdown(f"Bot wants to run \n```sh\n{' '.join(command)}\n```\n with sudo. do you want to allow?",extension_set="gitHubWeb",
            code_theme="atom-one-dark",
            code_style=ft.TextStyle(font_family="Roboto Mono"))
        pass_inp = ft.TextField(password=True, label="Password")
        dl_open = True
        close_pressed = False
        def on_close(*args):
            nonlocal close_pressed, dialog, dl_open
            dl_open = False
            close_pressed = True
            page.close(dialog)
        def on_submit(*args):
            nonlocal dialog, dl_open
            dl_open = False
            page.close(dialog)
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Sudo Permission"),
            content=ft.Column([prompt, pass_inp]),
            actions=[ft.TextButton("Close", on_click=on_close), ft.TextButton("Allow", on_click=on_submit)]
        )
        page.open(dialog)
        if close_pressed: return "User denied sudo permission"
        while dl_open:
            time.sleep(0.1)
        command = ["sshpass", "-p", pass_inp.value or "", "sudo", "-k"]+command
    if "apt" in command or "apt-get" in command or "dpkg" in command or "snap" in command or "snapd" in command or "flatpak" in command or "rpm" in command or "yum" in command or "dnf" in command or "zypper" in command or "pacman" in command:
        command = ["gnome-terminal", "--"] +command
    process = sb.Popen(command, stdin=sb.PIPE, stdout=sb.PIPE, stderr=sb.PIPE)
    output, error = process.communicate(stdin.encode("utf-8"))
    return json.dumps({"stdout": output.decode("utf-8"),"stderr":error.decode("utf-8")})
def ai_math(formulas, units):
    data = {}
    for key, value in formulas.items():
        import math, sympy
        local = locals()
        local.update(math.__dict__)
        local.update(sympy.__dict__)
        try:
            data[key] = f"{eval(value, {}, local)} {units.get(key,'')}"
        except Exception as e:
            data[key] = f"Error: {e}"
    return json.dumps(data)
def ai_news(keywords, max_results=3):
    if type(max_results) == str: max_results = int(max_results)
    return ddgs.text(keywords, max_results=max_results)
def ai_search_ddgs(keywords, max_results=3):
    if type(max_results) == str: max_results = int(max_results)
    return ddgs.text(keywords, max_results=max_results)
def ai_edit_settings(key, value):
    keys = key.split(".")
    if len(keys) == 1:
        ai.settings[key] = value
        return f"Settings updated successfully, settings[{key}] = {value}"
    settings = ai.settings
    for k in keys[:-1]:
        if k not in settings:
            settings[k] = {}
        settings = settings[k]
    settings[keys[-1]] = value
    with open("settings.json", "w") as f:
        json.dump(ai.settings, f)
    return f"Settings updated successfully, settings[{key}] = {value}"
def ai_remove_settings(key):
    keys = key.split(".")
    if len(keys) == 1:
        ai.settings.pop(key, None)
        return f"Settings {key} removed successfully"
    settings = ai.settings
    for k in keys[:-1]:
        if k not in settings:
            return f"Settings {key} not found, problem at part {k}, nothing removed"
        settings = settings[k]
    else:
        settings.pop(keys[-1], None)
    with open("settings.json", "w") as f:
        json.dump(ai.settings, f)
    return f"Settings {key} removed successfully"
# fns = {"command": ai_run_command, "math": ai_math}
def main(page: ft.Page):
    global init
    init = False
    widgets = []
    input = ft.TextField(
            label="Message",
            #border=ft.InputBorder.NONE,
            filled=True,
            border_radius=ft.border_radius.all(10),
            expand = True,
            multiline=True,
            shift_enter=True
    )
    btn = ft.IconButton(
        icon = ft.icons.SEND_ROUNDED,
        icon_color = "orange",
    )
    def on_send(msg:str, role="user"):
        global init
        btn.disabled = True
        if not init: init = True
        else: widgets.append(ft.Divider())
        for_run = False
        data = ""
        tile = ft.ListTile(title=ft.Container(content=ft.Markdown("# "+msg, selectable=True), padding=ft.Padding(0, 0, 0, 10)), subtitle=CustomTile(data, lambda name,params: print(name, params)))
        widgets.append(
            ft.Container(
                content = tile,
                alignment = ft.alignment.center_left,
                #border_radius = ft.border_radius.all(10),
                #bgcolor = ft.colors.SECONDARY_CONTAINER,
            )
        )
        page.update()
        ai.messages.append(
            {
                "role": "user",
                "content": msg
            }
        )
        response = ai.together.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            messages=ai.messages,
            max_tokens=1024,
            stream = True
        )
        # data += next(response).choices[0].delta.content or ""
        # print(data)
        # tile.subtitle.add()
        for chunk in response:
            if not for_run:
                for_run = True
            chnk = chunk.choices[0].delta.content or ""
            data += chnk
            tile.subtitle.add(chnk)
            tile.update()
        if not for_run:
            tile.subtitle.add(data)
            tile.update()
        # print("speaking", speech)
        # speak_ssml(page, f"<speak>{speech}</speak>")#speech.replace("|||", ""))
        ai.messages.append({
            "role": "assistant",
            "content": data #+ (f"|||{speech}" if speech else "")
        })
        btn.disabled = False
        page.update()
    input.on_submit = lambda _e: (k:=input.value, input.__setattr__("value", ""), on_send(k or ""))[2]
    btn.on_click = lambda _e: (k:=input.value, input.__setattr__("value", ""), on_send(k or ""))[2]
    page.title = "MyApp"
    page.window.width = 500
    page.window.height = 500
    page.window.always_on_top = True
    page.theme = ft.Theme(color_scheme_seed='#202222')
    page.add(
        ft.Container(
            content=ft.Column(widgets, auto_scroll=True, scroll=ft.ScrollMode.ALWAYS,),
            expand=True,
            padding=10,
        )
    )
    mic = ft.IconButton(icon=ft.icons.MIC_ROUNDED, icon_color="orange")
    mic.on_click = lambda *args, **kwargs: record_and_recognise(page, mic, input, ai.auto_send and btn)
    page.add(
        ft.Row(
            [
                mic,
                input,
                btn
            ]
        )
    )

ft.app(main, assets_dir=".")
print(ai.messages)

# print(fn, inp)
#             incorrect_fn = False
#             try:
#                 inp = json.loads(inp)
#                 fn = fn.lstrip("{\"").rstrip("\"}")
#                 print("running", fn)
#                 if fn == "command":
#                     data = ai_run_command(page, **inp)
#                 elif fn == "math":
#                     data = ai_math(**inp)
#                 elif fn == "wikipedia":
#                     pg = wikipedia.page(inp["topic"])
#                     tile = ft.ListTile()
#                     tile.expand = True
#                     widgets[-1].content = ft.Column([ft.ListTile(title=ft.Container(content=ft.Markdown(f"# {pg.title}", selectable=True), padding=ft.Padding(0, 0, 0, 10))), ft.Row([ft.Image(src=img, height=100) for img in pg.images[:3]], scroll=ft.ScrollMode.ALWAYS), tile], scroll=ft.ScrollMode.ALWAYS, height=500)
#                     data = pg.content
#                     widgets[-1].update()
#                 elif fn == "news":
#                     data = ai_news(**inp)
#                 elif fn == "search":
#                     data = ai_search_ddgs(**inp)
#                 elif fn == "editApplicationSettings":
#                     data = ai_edit_settings(**inp)
#                 elif fn == "removeApplicationSettings":
#                     data = ai_remove_settings(**inp)
#                 else:
#                     incorrect_fn = True
#                     data = " unknown function dumdum"
#             except Exception as e:
#                 data = f"Error: {e}"
#                 incorrect_fn = True
#             ai.messages.append({
#                 "role": "tool",
#                 "content": f"{'The system ran the function successfully, please respond to the user that the output is :' if not incorrect_fn else ''}{data}"
#             })
#             data = ""
#             response = ai.together.chat.completions.create(
#                 model="mistralai/Mixtral-8x22B-Instruct-v0.1",#"meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
#                 messages=ai.messages,
#                 max_tokens=1024,
#                 stream = True
#             )
#             data += next(response).choices[0].delta.content or ""
#             print(data)