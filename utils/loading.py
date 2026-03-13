import threading
import time
import flet as ft


def _build_overlay(message_text):
    return ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.36, "#0B1220"),
        alignment=ft.alignment.center,
        content=ft.Container(
            width=330,
            padding=ft.padding.symmetric(horizontal=24, vertical=22),
            bgcolor="white",
            border_radius=18,
            border=ft.border.all(1, "#E5E7EB"),
            content=ft.Column(
                [
                    ft.ProgressRing(width=28, height=28, stroke_width=2.5),
                    ft.Text(
                        "Please wait",
                        size=18,
                        weight=ft.FontWeight.W_700,
                        color="#1F2937",
                    ),
                    message_text,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                tight=True,
            ),
        ),
    )


def _get_loader_state(page):
    state = getattr(page, "_global_loader_state", None)
    if state is None:
        message_text = ft.Text(
            "Loading...",
            size=14,
            color="#4B5563",
            text_align=ft.TextAlign.CENTER,
        )
        overlay = _build_overlay(message_text)
        state = {
            "lock": threading.Lock(),
            "next_token": 0,
            "active_tokens": set(),
            "messages": {},
            "visible": False,
            "overlay": overlay,
            "message_text": message_text,
        }
        setattr(page, "_global_loader_state", state)

    if state["overlay"] not in page.overlay:
        page.overlay.append(state["overlay"])

    return state


def start_loading(page, message="Loading...", delay_seconds=1.0):
    state = _get_loader_state(page)

    with state["lock"]:
        state["next_token"] += 1
        token = state["next_token"]
        state["active_tokens"].add(token)
        state["messages"][token] = message

    def _show_if_still_loading():
        time.sleep(max(0.0, delay_seconds))
        should_show = False
        overlay_message = message

        with state["lock"]:
            if token in state["active_tokens"]:
                should_show = True
                state["visible"] = True
                overlay_message = state["messages"].get(token, message)

        if should_show:
            state["message_text"].value = overlay_message
            state["overlay"].visible = True
            try:
                page.update()
            except Exception:
                return

    threading.Thread(target=_show_if_still_loading, daemon=True).start()
    return token


def stop_loading(page, token):
    state = _get_loader_state(page)

    hide_overlay = False
    with state["lock"]:
        state["active_tokens"].discard(token)
        state["messages"].pop(token, None)

        if not state["active_tokens"] and state["visible"]:
            state["visible"] = False
            hide_overlay = True

    if hide_overlay:
        state["overlay"].visible = False
        try:
            page.update()
        except Exception:
            return


def run_with_loading(page, task, message="Loading...", delay_seconds=1.0, run_in_thread=True):
    token = start_loading(page, message=message, delay_seconds=delay_seconds)

    def _runner():
        try:
            task()
        finally:
            stop_loading(page, token)

    if run_in_thread:
        page.run_thread(_runner)
    else:
        _runner()
