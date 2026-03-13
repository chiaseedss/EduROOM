import flet as ft
import threading
import time
from utils.config import ICONS, COLORS
from data.models import UserModel, ActivityLogModel
from views.dashboard_view import show_dashboard
from utils.security import touch_session, get_csrf_token
from utils.email_otp import (
    is_cspc_email,
    send_otp_email,
    verify_otp,
    OTP_EXPIRY_MINUTES,
)


def show_login(page):
    """Display the enhanced login page with database authentication"""
    
    # State for password visibility and loading
    show_password = ft.Ref[ft.TextField]()
    login_button_ref = ft.Ref[ft.ElevatedButton]()
    error_text_ref = ft.Ref[ft.Text]()
    verify_button_ref = ft.Ref[ft.ElevatedButton]()
    send_otp_button_ref = ft.Ref[ft.ElevatedButton]()
    resend_button_ref = ft.Ref[ft.TextButton]()
    
    def on_focus(e, field):
        """Enhanced focus with animation"""
        field.border_color = "#3775a9"
        field.border_width = 2
        page.update()

    def on_blur(e, field):
        """Reset border on blur"""
        field.border_color = "#E5E7EB"
        field.border_width = 1
        page.update()

    # Email field with icon - responsive width
    email_field = ft.TextField(
        label="CSPC Email",
        hint_text="yourname@my.cspc.edu.ph",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        height=65,
        border_radius=12,
        text_size=14,
        border_color="#E5E7EB",
        filled=True,
        bgcolor="#F9FAFB",
        expand=True,
        on_focus=lambda e: on_focus(e, email_field),
        on_blur=lambda e: on_blur(e, email_field)
    )
    
    # ID Number field with icon - responsive width
    id_number_field = ft.TextField(
        label="ID Number",
        hint_text="Enter your CSPC ID Number",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        height=65,
        border_radius=12,
        text_size=14,
        border_color="#E5E7EB",
        filled=True,
        bgcolor="#F9FAFB",
        expand=True,
        on_focus=lambda e: on_focus(e, id_number_field),
        on_blur=lambda e: on_blur(e, id_number_field)
    )
    
    # Password field with show/hide toggle - responsive width
    password_field = ft.TextField(
        ref=show_password,
        label="Password",
        hint_text="Enter your password",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        height=65,
        border_radius=12,
        text_size=14,
        border_color="#E5E7EB",
        filled=True,
        bgcolor="#F9FAFB",
        expand=True,
        on_focus=lambda e: on_focus(e, password_field),
        on_blur=lambda e: on_blur(e, password_field)
    )
    
    # Enhanced error message - responsive width
    error_text = ft.Container(
        ref=error_text_ref,
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color="#EF4444", size=18),
            ft.Text("", color="#EF4444", size=12, weight=ft.FontWeight.W_500, expand=True)
        ], spacing=8),
        padding=12,
        bgcolor="#FEE2E2",
        border_radius=10,
        visible=False,
    )
    
    def show_error(message):
        """Display error message"""
        error_text.content.controls[1].value = message
        error_text.visible = True
        page.update()
    
    def hide_error():
        """Hide error message"""
        error_text.visible = False
        page.update()

    loading_message = ft.Text(
        "Verifying your account...",
        size=14,
        color="#4B5563",
        text_align=ft.TextAlign.CENTER,
    )
    loading_overlay = ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.36, "#0B1220"),
        alignment=ft.alignment.center,
        content=ft.Container(
            width=320,
            padding=ft.padding.symmetric(horizontal=24, vertical=22),
            bgcolor="white",
            border_radius=18,
            border=ft.border.all(1, "#E5E7EB"),
            content=ft.Column(
                [
                    ft.ProgressRing(width=26, height=26, stroke_width=2.5),
                    ft.Text(
                        "Please wait",
                        size=18,
                        weight=ft.FontWeight.W_700,
                        color="#1F2937",
                    ),
                    loading_message,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                tight=True,
            ),
        ),
    )

    def show_loading_overlay(message="Verifying your account..."):
        loading_message.value = message
        loading_overlay.visible = True
        if loading_overlay not in page.overlay:
            page.overlay.append(loading_overlay)
        page.update()

    def hide_loading_overlay():
        loading_overlay.visible = False
        page.update()

    def set_login_loading(is_loading):
        if login_button_ref.current:
            login_button_ref.current.disabled = is_loading
            login_button_ref.current.content.controls[0].visible = is_loading
            login_button_ref.current.content.controls[1].value = (
                "Verifying..." if is_loading else "Login"
            )
            page.update()

    def complete_login(user, activity_message="User logged in"):
        """Set session values and navigate to dashboard."""
        hide_loading_overlay()
        ActivityLogModel.log_activity(user['id'], activity_message)

        page.session.clear()
        page.session.set("user_id", user['id'])
        page.session.set("user_role", user['role'])
        page.session.set("user_name", user['full_name'])
        page.session.set("user_photo", user.get('photo'))

        touch_session(page)
        get_csrf_token(page)
        show_dashboard(page, user['id'], user['role'], user['full_name'])

    # --- Show notice if session expired due to inactivity ---
    login_notice = page.session.get("login_notice")
    if login_notice:
        # Reuse your existing error UI
        show_error(login_notice)
        # Clear it so it doesn't appear again next time
        page.session.set("login_notice", None)


    def login_click(e):
        hide_error()
        
        email = email_field.value.strip()
        id_number = id_number_field.value.strip()
        password = password_field.value
        
        # Validate all fields are filled
        if not email or not id_number or not password:
            show_error("Please fill in all fields")
            return

        # Check if account is deactivated
        is_active, message = UserModel.check_account_status(email, id_number)
        if not is_active:
            show_error(message)
            return

        set_login_loading(True)
        show_loading_overlay("Verifying your credentials...")

        def _login_worker():
            try:
                user, error_message = UserModel.authenticate_with_email(email, id_number, password)
            except Exception as ex:
                hide_loading_overlay()
                set_login_loading(False)
                show_error(f"Login error: {str(ex)}")
                return

            if error_message:
                hide_loading_overlay()
                set_login_loading(False)
                show_error(error_message)
                return

            if user:
                complete_login(user, "User logged in")
                return

            hide_loading_overlay()
            set_login_loading(False)
            show_error("Invalid credentials. Please check your email, ID, and password.")

        threading.Thread(target=_login_worker, daemon=True).start()

    # ==================== OTP STUDENT SIGN-IN FLOW ====================
    otp_step_state = {"value": "send"}
    otp_send_status = ft.Text(value="", size=12, color="#6B7280")
    otp_verify_status = ft.Text(value="", size=12, color="#6B7280")
    otp_timer_text = ft.Text(value="", size=12, color="#F59E0B")
    otp_verify_email_text = ft.Text(value="", size=13, color="#6B7280")
    otp_flow_state = {"email": ""}
    otp_timer_token = {"value": 0}
    resend_cooldown_token = {"value": 0}
    otp_card_bg = "#FFFFFF"
    otp_primary = "#2E6FA3"
    otp_primary_dark = "#255C88"

    otp_email_field = ft.TextField(
        label="CSPC Email",
        hint_text="yourname@my.cspc.edu.ph",
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        width=390,
        height=58,
        border_radius=14,
        filled=True,
        bgcolor="#F7FAFD",
        border_color="#D7E1EB",
        on_focus=lambda e: on_focus(e, otp_email_field),
        on_blur=lambda e: on_blur(e, otp_email_field),
    )

    otp_digit_fields = []

    def handle_otp_digit_change(index):
        def _handler(e):
            raw = (e.control.value or "").strip()
            digits = "".join(ch for ch in raw if ch.isdigit())
            e.control.value = digits[-1] if digits else ""

            if e.control.value and index < len(otp_digit_fields) - 1:
                otp_digit_fields[index + 1].focus()
            page.update()
        return _handler

    for i in range(6):
        otp_digit_fields.append(
            ft.TextField(
                width=48,
                height=54,
                text_align=ft.TextAlign.CENTER,
                max_length=1,
                keyboard_type=ft.KeyboardType.NUMBER,
                text_size=20,
                border_radius=12,
                filled=True,
                bgcolor="#F7FAFD",
                border_color="#D7E1EB",
                content_padding=ft.padding.symmetric(vertical=12),
                on_change=handle_otp_digit_change(i),
            )
        )

    def mask_email(email):
        try:
            local, domain = email.split("@", 1)
            if len(local) <= 2:
                return f"{local[:1]}***@{domain}"
            return f"{local[:2]}***@{domain}"
        except Exception:
            return email

    def start_otp_timer(seconds):
        otp_timer_token["value"] += 1
        token = otp_timer_token["value"]

        def run_countdown():
            remaining = seconds
            while remaining >= 0 and otp_timer_token["value"] == token:
                mins, secs = divmod(remaining, 60)
                otp_timer_text.value = f"OTP expires in {mins:02d}:{secs:02d}"
                otp_timer_text.color = "#F59E0B"
                try:
                    page.update()
                except Exception:
                    return
                time.sleep(1)
                remaining -= 1

            if otp_timer_token["value"] == token:
                otp_timer_text.value = "OTP expired. Please request a new code."
                otp_timer_text.color = "#EF4444"
                try:
                    page.update()
                except Exception:
                    return

        threading.Thread(target=run_countdown, daemon=True).start()

    def set_verify_loading(is_loading):
        if verify_button_ref.current:
            verify_button_ref.current.disabled = is_loading
            verify_button_ref.current.content.controls[0].visible = is_loading
            page.update()

    def set_send_otp_loading(is_loading):
        if send_otp_button_ref.current:
            send_otp_button_ref.current.disabled = is_loading
            send_otp_button_ref.current.content.controls[1].visible = is_loading
            send_otp_button_ref.current.content.controls[0].value = (
                "Sending OTP" if is_loading else "Send OTP"
            )
            page.update()

    def _set_resend_text(text):
        if resend_button_ref.current:
            resend_button_ref.current.content.spans[0].text = text

    def set_resend_loading(is_loading):
        if resend_button_ref.current:
            resend_button_ref.current.disabled = is_loading
            _set_resend_text("Resending..." if is_loading else "Resend code")
            page.update()

    def start_resend_cooldown(seconds=60):
        resend_cooldown_token["value"] += 1
        token = resend_cooldown_token["value"]
        def run_cooldown():
            for remaining in range(seconds, 0, -1):
                if resend_cooldown_token["value"] != token:
                    return
                if resend_button_ref.current:
                    _set_resend_text(f"Resend code ({remaining}s)")
                    resend_button_ref.current.disabled = True
                    page.update()
                time.sleep(1)
            if resend_cooldown_token["value"] == token:
                if resend_button_ref.current:
                    _set_resend_text("Resend code")
                    resend_button_ref.current.disabled = False
                    page.update()
        threading.Thread(target=run_cooldown, daemon=True).start()

    def clear_otp_boxes():
        for field in otp_digit_fields:
            field.value = ""

    def show_send_step():
        otp_step_state["value"] = "send"
        otp_verify_status.value = ""
        otp_timer_text.value = ""
        otp_timer_token["value"] += 1
        resend_cooldown_token["value"] += 1
        set_verify_loading(False)
        set_send_otp_loading(False)
        set_resend_loading(False)
        page.update()

    def show_verify_step(email):
        otp_flow_state["email"] = email
        otp_verify_email_text.value = f"Code sent to {mask_email(email)}"
        otp_step_state["value"] = "verify"
        otp_send_status.value = ""
        otp_verify_status.value = ""
        clear_otp_boxes()
        start_otp_timer(OTP_EXPIRY_MINUTES * 60)
        if otp_digit_fields:
            otp_digit_fields[0].focus()
        page.update()

    send_step = ft.Container(
        visible=True,
        content=ft.Column(
            [
                ft.Text("Sign in with CSPC Email", size=22, weight=ft.FontWeight.W_700, color="#1F2937"),
                ft.Text("Verify your CSPC email to continue", size=13.5, color="#6B7280"),
                ft.Container(height=10),
                otp_email_field,
                otp_send_status,
                ft.ElevatedButton(
                    ref=send_otp_button_ref,
                    content=ft.Row([
                        ft.Text("Send OTP", weight=ft.FontWeight.W_600),
                        ft.ProgressRing(width=16, height=16, stroke_width=2, visible=False),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                    on_click=lambda e: send_otp_click(e),
                    height=50,
                    width=350,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=14),
                        bgcolor=otp_primary,
                        overlay_color=ft.Colors.with_opacity(0.08, "white"),
                        color="white",
                    ),
                ),
                ft.OutlinedButton(
                    "Cancel",
                    on_click=lambda e: close_otp_dialog(),
                    height=46,
                    width=350,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        side=ft.BorderSide(1, "#D1D5DB"),
                        color="#6B7280",
                        bgcolor="#F3F4F6",
                    ),
                ),
            ],
            spacing=11,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
    )

    verify_step = ft.Container(
        visible=False,
        content=ft.Column(
            [
                ft.Text("Verify OTP", size=22, weight=ft.FontWeight.W_700, color="#1F2937"),
                otp_verify_email_text,
                ft.Container(height=8),
                ft.Row(
                    otp_digit_fields,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                otp_timer_text,
                ft.TextButton(
                    ref=resend_button_ref,
                    content=ft.Text(
                        spans=[
                            ft.TextSpan(
                                "Resend code",
                                style=ft.TextStyle(
                                    color="#2E6FA3",
                                    size=13,
                                    decoration=ft.TextDecoration.UNDERLINE,
                                ),
                            )
                        ]
                    ),
                    on_click=lambda e: resend_otp_click(e),
                    style=ft.ButtonStyle(
                        padding=ft.padding.all(0),
                        overlay_color=ft.Colors.TRANSPARENT,
                    ),
                ),
                otp_verify_status,
                ft.ElevatedButton(
                    ref=verify_button_ref,
                    content=ft.Row(
                        [
                            ft.ProgressRing(width=18, height=18, stroke_width=2, visible=False),
                            ft.Text("VERIFY", weight=ft.FontWeight.W_700),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    on_click=lambda e: verify_otp_click(e),
                    height=52,
                    width=350,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=14),
                        bgcolor=otp_primary_dark,
                        overlay_color=ft.Colors.with_opacity(0.08, "white"),
                        color="white",
                    ),
                ),
                ft.OutlinedButton(
                    "Cancel",
                    on_click=lambda e: close_otp_dialog(),
                    height=46,
                    width=350,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        side=ft.BorderSide(1, "#D1D5DB"),
                        color="#6B7280",
                        bgcolor="#F3F4F6",
                    ),
                ),
            ],
            spacing=11,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
    )

    def sync_otp_step_visibility():
        is_send = otp_step_state["value"] == "send"
        send_step.visible = is_send
        verify_step.visible = not is_send

    otp_modal = ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.32, "#0B1220"),
        alignment=ft.alignment.center,
        content=ft.Container(
            width=500,
            padding=ft.padding.symmetric(horizontal=28, vertical=26),
            bgcolor=otp_card_bg,
            border_radius=26,
            border=ft.border.all(1, "#E8EEF5"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=35,
                color=ft.Colors.with_opacity(0.2, "#1F2937"),
                offset=ft.Offset(0, 12),
            ),
            content=ft.Column(
                [
                    send_step,
                    verify_step,
                ],
                spacing=0,
                tight=True,
            ),
        ),
    )

    def close_otp_dialog(e=None):
        otp_timer_token["value"] += 1
        resend_cooldown_token["value"] += 1
        otp_timer_text.value = ""
        otp_modal.visible = False
        set_verify_loading(False)
        set_send_otp_loading(False)
        set_resend_loading(False)
        page.update()

    def send_otp_click(e):
        email = otp_email_field.value.strip().lower()
        if not email:
            otp_send_status.value = "Please enter your CSPC email."
            otp_send_status.color = "#EF4444"
            page.update()
            return

        if not is_cspc_email(email):
            otp_send_status.value = "Only @cspc.edu.ph or @my.cspc.edu.ph emails are allowed."
            otp_send_status.color = "#EF4444"
            page.update()
            return

        existing_user = UserModel.get_user_by_email(email)
        if existing_user and existing_user.get("role") in ("admin", "faculty"):
            otp_send_status.value = "Admin/Faculty accounts must use the normal Login button."
            otp_send_status.color = "#EF4444"
            page.update()
            return

        set_send_otp_loading(True)
        success, message = send_otp_email(email)
        set_send_otp_loading(False)
        otp_send_status.value = message
        otp_send_status.color = "#10B981" if success else "#EF4444"
        page.update()

        if success:
            show_verify_step(email)
            sync_otp_step_visibility()
            page.update()

    def resend_otp_click(e):
        email = otp_flow_state["email"]
        if not email:
            otp_verify_status.value = "Email is missing. Go back and send OTP again."
            otp_verify_status.color = "#EF4444"
            page.update()
            return

        set_resend_loading(True)
        success, message = send_otp_email(email)
        set_resend_loading(False)

        otp_verify_status.value = message
        otp_verify_status.color = "#10B981" if success else "#EF4444"

        if success:
            start_resend_cooldown(60)
            clear_otp_boxes()
            start_otp_timer(OTP_EXPIRY_MINUTES * 60)
            if otp_digit_fields:
                otp_digit_fields[0].focus()

        page.update()

    def verify_otp_click(e):
        email = otp_flow_state["email"]
        otp = "".join((field.value or "").strip() for field in otp_digit_fields)

        if not email or not otp or len(otp) != 6:
            otp_verify_status.value = "Enter the 6-digit OTP code."
            otp_verify_status.color = "#EF4444"
            page.update()
            return

        set_verify_loading(True)
        show_loading_overlay("Verifying OTP and signing you in...")

        def _verify_worker():
            try:
                success, message = verify_otp(email, otp)
            except Exception as ex:
                hide_loading_overlay()
                set_verify_loading(False)
                otp_verify_status.value = f"Verification error: {str(ex)}"
                otp_verify_status.color = "#EF4444"
                page.update()
                return

            if not success:
                hide_loading_overlay()
                set_verify_loading(False)
                otp_verify_status.value = message
                otp_verify_status.color = "#EF4444"
                page.update()
                return

            existing_user = UserModel.get_user_by_email(email)
            if existing_user:
                if existing_user.get("role") in ("admin", "faculty"):
                    hide_loading_overlay()
                    set_verify_loading(False)
                    otp_verify_status.value = "Admin/Faculty accounts must use the normal Login button."
                    otp_verify_status.color = "#EF4444"
                    page.update()
                    return

                if not existing_user.get("is_active", True):
                    hide_loading_overlay()
                    set_verify_loading(False)
                    otp_verify_status.value = "Your account has been deactivated. Please contact an administrator."
                    otp_verify_status.color = "#EF4444"
                    page.update()
                    return

                close_otp_dialog()
                complete_login(existing_user, "Student signed in via CSPC email OTP")
                return

            new_user, create_error = UserModel.create_student_user_from_email(email)
            if create_error:
                hide_loading_overlay()
                set_verify_loading(False)
                otp_verify_status.value = create_error
                otp_verify_status.color = "#EF4444"
                page.update()
                return

            close_otp_dialog()
            complete_login(new_user, "Student account created via CSPC email OTP")

        threading.Thread(target=_verify_worker, daemon=True).start()

    def open_otp_dialog(e):
        hide_error()
        otp_email_field.value = ""
        clear_otp_boxes()
        otp_send_status.value = ""
        otp_verify_status.value = ""
        otp_timer_token["value"] += 1
        otp_timer_text.value = ""
        otp_flow_state["email"] = ""
        otp_step_state["value"] = "send"
        sync_otp_step_visibility()
        otp_modal.visible = True
        if otp_modal not in page.overlay:
            page.overlay.append(otp_modal)
        page.update()

    # Logo section - responsive sizing
    logo = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Image(
                    src="images/cspc-logo.png",
                    width=80,
                    height=80,
                    fit=ft.ImageFit.CONTAIN
                ),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.1, "#3775a9"),
                    offset=ft.Offset(0, 4),
                )
            ),
            ft.Container(height=8),
            ft.Image(
                src="images/EduROOM-logo.png",
                width=220,
                height=65,
                fit=ft.ImageFit.CONTAIN
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0
        )
    )
    
    # login button - responsive width
    login_button = ft.ElevatedButton(
        ref=login_button_ref,
        content=ft.Row([
            ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False),
            ft.Text("Login", size=16, weight=ft.FontWeight.W_600),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        height=55,
        expand=True,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor="#3775a9",
            color="white",
            shadow_color="#3775a9",
            elevation=3,
        ),
        on_click=login_click,
    )

    otp_sign_in_button = ft.OutlinedButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.MARK_EMAIL_READ_OUTLINED, size=18),
                ft.Text("Sign in with CSPC Email", size=14, weight=ft.FontWeight.W_600),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        height=50,
        expand=True,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            side=ft.BorderSide(1, "#3775a9"),
            color="#3775a9",
        ),
        on_click=open_otp_dialog,
    )

    # Main card container with responsive sizing
    login_card = ft.Container(
        content=ft.Column([
            logo,
            ft.Text(
                "Classroom Reservation System",
                size=14,
                color="#6B7280",
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=15),
            
            # Form fields
            email_field,
            ft.Container(height=5),
            id_number_field,
            ft.Container(height=5),
            password_field,
            
            error_text,
            ft.Container(height=8),
            login_button,
            ft.Container(height=6),
            otp_sign_in_button,
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5,
        scroll=ft.ScrollMode.AUTO),
        padding=ft.padding.symmetric(horizontal=30, vertical=35),
        bgcolor="white",
        border_radius=24,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=30,
            color=ft.Colors.with_opacity(0.1, "black"),
            offset=ft.Offset(0, 10),
        ),
        width=450,
    )
    
    # Responsive container wrapper
    responsive_card = ft.Container(
        content=login_card,
        width=450,
        alignment=ft.alignment.center,
    )
    
    # Footer
    footer = ft.Container(
        content=ft.Column([
            ft.Text(
                "© 2025 TechValks",
                size=12,
                color="#9CA3AF",
                text_align=ft.TextAlign.CENTER
            ),
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5),
        padding=ft.padding.only(top=15)
    )

    page.controls.clear()
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    page.add(
        ft.Stack([
            ft.Container(
                image=ft.DecorationImage(
                    src="images/gradient-bg.png",  
                    fit=ft.ImageFit.COVER,
                ),
                blur=10,  
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    responsive_card,
                    footer
                ], 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0),
                alignment=ft.alignment.center,
                expand=True
            )
        ], expand=True)
    )
    page.update()