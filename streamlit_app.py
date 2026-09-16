from datetime import date
from email.header import Header
from email.mime.text import MIMEText
import json
import os
import smtplib
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 邮箱配置信息
# ==========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL 端口
SENDER_GMAIL = "ytqzytqz@gmail.com"
SENDER_PASSWORD = "smqk khlq goxb rhdh"
RECEIVER_GMAIL = "ytqzytqz@gmail.com"

# UV 记录持久化文件
UV_FILE = "uv_tracker.json"


# ==========================================
# 邮件发送与 UV 处理逻辑
# ==========================================
def send_email_notification(
    subject, body_text, sender_title="LinkedIn Video Bot"
):
    """通用发送 Gmail 通知函数"""
    message = MIMEText(body_text, "plain", "utf-8")
    message["From"] = Header(f"{sender_title} <{SENDER_GMAIL}>", "utf-8")
    message["To"] = Header(RECEIVER_GMAIL, "utf-8")
    message["Subject"] = Header(subject, "utf-8")

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_GMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_GMAIL, [RECEIVER_GMAIL], message.as_string())
        return True, "Success"
    except Exception as e:
        return False, str(e)


def track_and_get_daily_uv():
    """管理每日 Unique Visitor (UV) 并检查里程碑阈值"""
    today_str = str(date.today())

    data = {"date": today_str, "uv_count": 0, "notified_thresholds": []}
    if os.path.exists(UV_FILE):
        try:
            with open(UV_FILE, "r") as f:
                loaded_data = json.load(f)
                if loaded_data.get("date") == today_str:
                    data = loaded_data
        except Exception:
            pass

    if "uv_tracked" not in st.session_state:
        st.session_state.uv_tracked = True
        data["uv_count"] += 1

        thresholds = [10, 100, 1000]
        for t in thresholds:
            if data["uv_count"] >= t and t not in data["notified_thresholds"]:
                data["notified_thresholds"].append(t)
                subject = f"🎉 Milestone Reached: {t} Daily UVs!"
                body = f"Congratulations! Your app has reached {t} Unique Visitors (UV) today ({today_str}).\n\nCurrent Daily UV Count: {data['uv_count']}"
                send_email_notification(
                    subject, body, sender_title="UV Analytics Bot"
                )

        with open(UV_FILE, "w") as f:
            json.dump(data, f)

    return data["uv_count"]


current_daily_uv = track_and_get_daily_uv()

if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="LinkedIn Profile to Video Generator for Lawyers",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 2. Refined UI/UX CSS Styling
# ==========================================
st.markdown(
    """
<style>
    /* Global Styling */
    .stApp {
        background-color: #F3F2EF;
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #181818;
    }

    /* Main Container Padding Compactness */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1100px;
    }

    /* Compact Header */
    .main-header {
        background-color: #FFFFFF;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
        border: 1px solid #E0E0E0;
        margin-bottom: 1.2rem;
        text-align: center;
    }
    .main-title {
        color: #0A66C2;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .main-subtitle {
        color: #5E5E5E;
        font-size: 0.98rem;
    }

    /* Strategy Card UI Optimization */
    .strategy-card {
        background-color: #FFFFFF;
        padding: 1.2rem 1.5rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
    }
    .strategy-title {
        color: #0A66C2;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .strategy-card ul {
        margin-top: 0.3rem;
        margin-bottom: 0;
        padding-left: 1.2rem;
    }
    .strategy-card li {
        font-size: 0.9rem;
        color: #333333;
        margin-bottom: 0.3rem;
    }
    
    /* Section Header */
    .section-title {
        color: #181818;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        border-left: 4px solid #0A66C2;
        padding-left: 0.6rem;
    }

    /* Reserve Card / Placeholder Box */
    .reserve-card {
        background: #FFFFFF;
        border: 2px dashed #0A66C2;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .reserve-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0A66C2;
        margin-bottom: 0.4rem;
    }
    .reserve-card-desc {
        font-size: 0.82rem;
        color: #666666;
        margin-bottom: 0.8rem;
        line-height: 1.3;
    }

    /* Form & Banner Highlight */
    .active-selection-banner {
        background-color: #E8F4F9;
        border: 2px solid #0A66C2;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        text-align: center;
        margin-bottom: 1.2rem;
        animation: fadeIn 0.4s ease-in-out;
    }
    .active-selection-banner h4 {
        margin: 0 0 0.3rem 0;
        color: #0A66C2;
        font-size: 1.05rem;
    }

    /* Streamlit Button Overrides */
    .stButton>button {
        background-color: #0A66C2 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.4rem 1.2rem !important;
        width: 100%;
        font-size: 0.88rem !important;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #004182 !important;
    }

    /* Notice Box */
    .notice-box {
        background-color: #E8F4F9;
        border-left: 4px solid #0A66C2;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #004182;
        margin-top: 0.8rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #7F7F7F;
        font-size: 0.82rem;
        margin-top: 2.5rem;
        padding-bottom: 1rem;
        border-top: 1px solid #E0E0E0;
        padding-top: 1rem;
    }
    .uv-badge {
        display: inline-block;
        background-color: #E0E0E0;
        color: #333333;
        font-weight: 600;
        padding: 0.15rem 0.5rem;
        border-radius: 10px;
        margin-left: 0.4rem;
        font-size: 0.8rem;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. Header Section
# ==========================================
st.markdown(
    """
<div class="main-header">
    <div class="main-title">LinkedIn Profile to AI Professional Video</div>
    <div class="main-subtitle">Turn your LinkedIn profile into high-converting video content tailored for legal marketing</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 4. Legal Marketing Strategy Framework
# ==========================================
st.markdown(
    """
<div class="strategy-card">
    <div class="strategy-title">💡 Strategic Content Pillars for Legal Marketing</div>
    <ul>
        <li><b>1. Personal Branding & Connection:</b> Humanize your practice and build authentic trust with prospective clients.</li>
        <li><b>2. Professional Credibility:</b> Showcase case wins, legal expertise, and industry thought leadership.</li>
        <li><b>3. Business Development & Lead Generation:</b> Address client pain points, provide actionable legal solutions, and drive inbound leads.</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)

LOCAL_VIDEO_1 = "01.mp4"
LOCAL_VIDEO_2 = "02.mov"
LOCAL_VIDEO_3 = "03.mp4"
LOCAL_VIDEO_4 = "04.mp4"


def render_video_or_fallback(video_path, title):
    st.markdown(f"**{title}**")
    try:
        with open(video_path, "rb") as video_file:
            st.video(video_file.read())
    except FileNotFoundError:
        st.info(f"📹 Case Sample: `{title}`")


# 辅助函数：触发点击后滚动并设置状态
def handle_select_category(cat_name):
    st.session_state.selected_category = cat_name
    st.session_state.trigger_scroll = True


# ==========================================
# 5. Video Showcase Category 1: Personal Branding & Connection
# ==========================================
st.markdown(
    '<div class="section-title">1️⃣ Personal Branding & Connection</div>',
    unsafe_allow_html=True,
)
col1, col2, col3 = st.columns(3)

with col1:
    render_video_or_fallback(LOCAL_VIDEO_1, "Street Interviews")

with col2:
    render_video_or_fallback(LOCAL_VIDEO_2, "A Young Lawyer's Day")

with col3:
    st.markdown("**Reserve Your Video**")
    st.markdown(
        """
    <div class="reserve-card">
        <div class="reserve-card-title">✨ Personal Brand Showcase</div>
        <div class="reserve-card-desc">Generate an authentic video introducing your background & law practice values.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(
        "✨ Select & Generate This Style", key="btn_cat_1"
    ):
        handle_select_category("Personal Branding & Connection")


# ==========================================
# 6. Video Showcase Category 2: Professional Credibility
# ==========================================
st.markdown(
    '<div class="section-title">2️⃣ Professional Credibility</div>',
    unsafe_allow_html=True,
)
col4, col5, col6 = st.columns(3)


with col4:
    render_video_or_fallback(LOCAL_VIDEO_3, "A Justice's Life")

with col5:
    render_video_or_fallback(LOCAL_VIDEO_4, "An AI Lawyer's Career")

with col6:
    st.markdown("**Reserve Your Video**")
    st.markdown(
        """
    <div class="reserve-card">
        <div class="reserve-card-title">✨ Authority Showcase</div>
        <div class="reserve-card-desc">Highlight landmark cases, legal insights, and your authority in practice areas.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(
        "✨ Select & Generate This Style", key="btn_cat_2"
    ):
        handle_select_category("Professional Credibility")


# ==========================================
# 7. Video Showcase Category 3: Business Development & Lead Generation
# ==========================================
st.markdown(
    '<div class="section-title">3️⃣ Business Development & Lead Generation</div>',
    unsafe_allow_html=True,
)
col7, col8, col9 = st.columns(3)

with col7:
    render_video_or_fallback(LOCAL_VIDEO_1, "Why You Need a Corporate Lawyer")

with col8:
    render_video_or_fallback(LOCAL_VIDEO_2, "Setting Up a US Company")

with col9:
    st.markdown("**Reserve Your Video**")
    st.markdown(
        """
    <div class="reserve-card">
        <div class="reserve-card-title">✨ Lead Gen Showcase</div>
        <div class="reserve-card-desc">Address client legal challenges directly and turn viewers into consultations.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(
        "✨ Select & Generate This Style", key="btn_cat_3"
    ):
        handle_select_category("Business Development & Lead Generation")

st.markdown("<br><hr style='margin: 1.5rem 0;'><br>", unsafe_allow_html=True)


# ==========================================
# 8. Form Submission Section (With Scroll Anchor)
# ==========================================
# 设置 HTML 锚点便于自动滚动到达
st.markdown('<div id="generate-form"></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">✨ Generate Your Personalized Video</div>',
    unsafe_allow_html=True,
)

# 高亮已选类别提示
if st.session_state.selected_category:
    st.markdown(
        f"""
    <div class="active-selection-banner">
        <h4>🎯 Selected Style: <b>{st.session_state.selected_category}</b></h4>
        <p style="margin: 0; color: #5E5E5E; font-size: 0.9rem;">
            Please enter your LinkedIn profile and email below. Your custom video will be tailored specifically for this marketing objective!
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.info(
        "💡 Click any of the **'Select & Generate This Style'** buttons above to choose a content style, or fill out the form directly!"
    )

with st.form(key="video_request_form"):
    linkedin_url = st.text_input(
        "LinkedIn Profile URL",
        placeholder="https://www.linkedin.com/in/your-profile",
    )

    email = st.text_input(
        "Email Address to Receive Video", placeholder="yourname@example.com"
    )

    # Terms
    st.markdown(
        """
    <div class="notice-box">
        💡 <b>Notes & Terms:</b><br>
        1. Video generation is completely <b>FREE</b>.<br>
        2. By submitting, you agree that the generated video may be featured on our site for showcase and demonstration purposes.
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button(label="Generate Video Now for Free")

# 提交处理
if submit_button:
    if not linkedin_url or not email:
        st.error(
            "Please complete both the LinkedIn URL and Email address fields!"
        )
    elif "linkedin.com/in/" not in linkedin_url.lower():
        st.warning(
            "Please enter a valid LinkedIn profile link (e.g., https://www.linkedin.com/in/xxx)"
        )
    elif "@" not in email:
        st.warning("Please enter a valid email address!")
    else:
        chosen_cat = (
            st.session_state.selected_category
            if st.session_state.selected_category
            else "General Showcase"
        )
        mail_subject = "🚀 New Lawyer Video Request Submitted"
        mail_body = f"""
        A new user has submitted a video request!

        - Selected Category: {chosen_cat}
        - LinkedIn Profile: {linkedin_url}
        - User Email: {email}
        """

        with st.spinner("Submitting your request..."):
            success, err_msg = send_email_notification(mail_subject, mail_body)

        if success:
            st.success("✅ Submitted Successfully!")
            st.info(
                f"📨 We have received your request for **{chosen_cat}**. Your custom video will be delivered to **{email}** within **24 hours**!"
            )
        else:
            st.error(f"⚠️ Failed to send notification: {err_msg}")

# 执行平滑向下滚动至表单区域
if st.session_state.get("trigger_scroll", False):
    st.session_state.trigger_scroll = False
    components.html(
        """
        <script>
            window.parent.document.getElementById('generate-form').scrollIntoView({behavior: 'smooth'});
        </script>
        """,
        height=0,
    )

# ==========================================
# 9. Footer with Daily UV Counter
# ==========================================
st.markdown(
    f"""
<div class="footer">
    © 2026 LinkedIn Video Generator for Lawyers. All rights reserved. | 
    Daily Unique Visitors (UV): <span class="uv-badge">👤 {current_daily_uv}</span>
</div>
""",
    unsafe_allow_html=True,
)
