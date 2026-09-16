

import smtplib
import uuid
import json
import os
from datetime import date
from email.header import Header
from email.mime.text import MIMEText

import streamlit as st

# ==========================================
# 邮箱配置信息（请在此处替换为你自己的配置）
# 建议改为环境变量读取，避免明文泄露应用专用密码
# ==========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL 端口
SENDER_GMAIL = "ytqzytqz@gmail.com"  # 你的 Gmail 账号
SENDER_PASSWORD = "smqk khlq goxb rhdh"
RECEIVER_GMAIL = "ytqzytqz@gmail.com"  # 接收通知的 Gmail 账号


# ==========================================
# 邮件发送
# ==========================================
def _send_email(subject, body):
    """通用邮件发送函数，返回 (success, err_msg)"""
    message = MIMEText(body, "plain", "utf-8")
    message["From"] = Header(f"LinkedIn Video Bot <{SENDER_GMAIL}>", "utf-8")
    message["To"] = Header(RECEIVER_GMAIL, "utf-8")
    message["Subject"] = Header(subject, "utf-8")

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_GMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_GMAIL, [RECEIVER_GMAIL], message.as_string())
        return True, "Success"
    except Exception as e:
        return False, str(e)


def send_email_notification(user_linkedin, user_email, category):
    """用户提交视频生成请求时发送邮件通知"""
    subject = "🚀 New Video Request Submitted"
    body = f"""
    A new user has submitted a request for video generation:

    - Content Category: {category}
    - LinkedIn Profile: {user_linkedin}
    - User Email: {user_email}
    """
    return _send_email(subject, body)


def send_uv_milestone_notification(uv_count, day_str):
    """每日 UV 累计突破阈值时发送邮件通知"""
    subject = f"📈 Daily UV Milestone: {uv_count} Visitors Reached"
    body = f"""
    Daily unique visitor milestone reached!

    - Date: {day_str}
    - Cumulative UV Today: {uv_count}

    Your lawyer short-video marketing page is getting traction. Keep it up!
    """
    return _send_email(subject, body)


# ==========================================
# 每日 UV 统计（文件持久化 + URL 参数识别访客）
# ==========================================
UV_STATS_FILE = "uv_stats.json"
UV_THRESHOLDS = [10, 100, 1000]  # 每突破一次触发一封邮件


def _load_uv_stats():
    if os.path.exists(UV_STATS_FILE):
        try:
            with open(UV_STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"date": "", "count": 0, "visitors": [], "notified": []}


def _save_uv_stats(stats):
    try:
        with open(UV_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False)
    except OSError:
        pass  # 统计失败不影响页面渲染


def track_daily_uv():
    """
    统计当日累计 UV：
    - 通过 URL query param 中的 visitor_id 识别唯一访客
    - 跨天自动清零
    - UV 每突破 10 / 100 / 1000 时各触发一次邮件通知
    返回当日累计 UV 数。
    """
    today = date.today().isoformat()

    # 为每个新访客分配一个持久化的 visitor_id（写在 URL 上，刷新不重复计数）
    if "visitor_id" not in st.query_params:
        st.query_params["visitor_id"] = uuid.uuid4().hex
    visitor_id = st.query_params["visitor_id"]

    stats = _load_uv_stats()

    # 跨天重置
    if stats["date"] != today:
        stats = {"date": today, "count": 0, "visitors": [], "notified": []}

    is_new_visitor = visitor_id not in stats["visitors"]
    if is_new_visitor:
        prev_count = stats["count"]
        stats["visitors"].append(visitor_id)
        stats["count"] += 1
        _save_uv_stats(stats)

        # 检查是否跨过阈值（每档只通知一次）
        for threshold in UV_THRESHOLDS:
            if prev_count < threshold <= stats["count"] and threshold not in stats["notified"]:
                stats["notified"].append(threshold)
                _save_uv_stats(stats)
                send_uv_milestone_notification(stats["count"], today)
    return stats["count"]


# ==========================================
# 三类律师短视频内容定义
# ==========================================
CATEGORIES = [
    {
        "key": "personal_branding",
        "icon": "🤝",
        "title": "Personal Branding & Connection",
        "description": (
            "Build trust before the first consultation. Share your origin story, "
            "values and daily life so potential clients feel they already know you."
        ),
        "videos": [
            ("video_pb_1.mp4", "Attorney Origin Story"),
            ("video_pb_2.mp4", "A Day in the Life of a Lawyer"),
        ],
    },
    {
        "key": "professional_credibility",
        "icon": "⚖️",
        "title": "Professional Credibility",
        "description": (
            "Demonstrate expertise. Break down real cases, debunk legal myths and "
            "explain complex rules in plain language to position yourself as the expert."
        ),
        "videos": [
            ("video_pc_1.mp4", "Landmark Case Breakdown"),
            ("video_pc_2.mp4", "Legal Myth-Busting"),
        ],
    },
    {
        "key": "business_development",
        "icon": "📈",
        "title": "Business Development & Lead Generation",
        "description": (
            "Convert viewers into clients. Showcase practice areas, client "
            "testimonials and clear calls-to-action that drive consultations."
        ),
        "videos": [
            ("video_bd_1.mp4", "Client Success Testimonial"),
            ("video_bd_2.mp4", "Practice Area Spotlight"),
        ],
    },
]

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="LinkedIn Profile to Video Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 2. CSS Styling (LinkedIn Aesthetic)
# ==========================================
st.markdown(
    """
<style>
    /* Global Background and Typography */
    .stApp {
        background-color: #F3F2EF;
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #181818;
    }

    /* Header Styling */
    .main-header {
        background-color: #FFFFFF;
        padding: 2.5rem 2rem 2rem 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E0E0E0;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-title {
        color: #0A66C2;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .main-subtitle {
        color: #5E5E5E;
        font-size: 1.1rem;
    }

    /* Card Styling */
    .css-card {
        background-color: #FFFFFF;
        padding: 1.8rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }

    /* Section Titles */
    .section-title {
        color: #181818;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        border-bottom: 2px solid #F3F2EF;
        padding-bottom: 0.5rem;
    }

    /* Marketing Intro */
    .intro-card {
        background-color: #FFFFFF;
        padding: 1.8rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    .intro-lead {
        font-size: 1rem;
        color: #333333;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    .intro-list {
        margin: 0;
        padding-left: 1.2rem;
        color: #333333;
        line-height: 1.8;
        font-size: 0.95rem;
    }

    /* Category Card */
    .category-card {
        background-color: #FFFFFF;
        padding: 1.5rem 1.8rem 1.2rem 1.8rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        border-left: 5px solid #0A66C2;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .category-card.selected {
        border: 2px solid #0A66C2;
        border-left: 5px solid #0A66C2;
        background-color: #E8F4F9;
        box-shadow: 0 0 0 4px rgba(10, 102, 194, 0.15);
    }
    .category-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #181818;
    }
    .category-desc {
        font-size: 0.9rem;
        color: #5E5E5E;
        margin-top: 0.3rem;
        line-height: 1.5;
    }
    .selected-badge {
        display: inline-block;
        background-color: #0A66C2;
        color: #FFFFFF;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 10px;
        padding: 0.15rem 0.6rem;
        margin-left: 0.5rem;
        vertical-align: middle;
    }

    /* Video Placeholder Box */
    .video-placeholder {
        background-color: #EAEAEA;
        border: 2px dashed #0A66C2;
        border-radius: 8px;
        height: 210px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 1.5rem;
        color: #0A66C2;
    }
    .placeholder-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .placeholder-text {
        font-size: 0.9rem;
        color: #5E5E5E;
    }

    /* Inputs & Buttons */
    div[data-baseweb="input"] {
        border-radius: 4px;
    }

    /* Primary LinkedIn Blue Button */
    .stButton>button {
        background-color: #0A66C2 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        width: 100%;
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
        font-size: 0.9rem;
        color: #004182;
        margin-top: 1rem;
    }

    /* Selected Category Banner above the form */
    .selected-banner {
        background-color: #0A66C2;
        color: #FFFFFF;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #7F7F7F;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-bottom: 1rem;
    }
    .footer-uv {
        display: inline-block;
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 14px;
        padding: 0.25rem 0.9rem;
        margin-bottom: 0.6rem;
        color: #0A66C2;
        font-weight: 600;
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
    <div class="main-subtitle">Turn your LinkedIn profile into a high-quality video showcase with a single click</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 4. Marketing Explanation Section
# ==========================================
st.markdown(
    '<div class="section-title">🎯 Why Lawyers Need Short-Video Marketing</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="intro-card">
    <div class="intro-lead">
        Clients hire lawyers they <b>know, trust, and remember</b>. Effective lawyer
        short-video marketing relies on <b>three types of content</b> working together:
    </div>
    <ul class="intro-list">
        <li><b>🤝 Personal Branding &amp; Connection</b> — let potential clients know who you are:
            your story, your values, and the person behind the title.</li>
        <li><b>⚖️ Professional Credibility</b> — show what you know: case breakdowns, legal
            myth-busting, and plain-language explanations that prove your expertise.</li>
        <li><b>📈 Business Development &amp; Lead Generation</b> — turn viewers into clients:
            practice-area spotlights, client testimonials, and clear calls-to-action.</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">📹 Showcase & Examples</div>',
    unsafe_allow_html=True,
)

# ==========================================
# 5. Category Showcase Sections (2 videos + 1 reserved slot each)
# ==========================================
selected_category = st.session_state.get("selected_category")

for cat in CATEGORIES:
    is_selected = selected_category == cat["title"]
    card_class = "category-card selected" if is_selected else "category-card"
    badge = '<span class="selected-badge">✓ SELECTED</span>' if is_selected else ""

    st.markdown(
        f"""
<div class="{card_class}">
    <div class="category-title">{cat["icon"]} {cat["title"]} {badge}</div>
    <div class="category-desc">{cat["description"]}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    # 本地视频（请替换为你本地实际的视频文件名或绝对路径）
    for i, (video_path, video_title) in enumerate(cat["videos"]):
        with [col1, col2][i]:
            st.markdown(f"**{video_title}**")
            try:
                with open(video_path, "rb") as video_file:
                    st.video(video_file.read())
            except FileNotFoundError:
                st.warning(f"Local video file not found: `{video_path}`")

    # 第三个位置：预留位（点击后选中该类别并引导填写表单）
    with col3:
        st.markdown(f"**Your {cat['title']} Video**")
        st.markdown(
            """
        <div class="video-placeholder">
            <div class="placeholder-title">✨ Your Video Here</div>
            <div class="placeholder-text">
                This slot is reserved for your video.<br>
                Click the button below to generate it for free.
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button(
            f"Generate My {cat['title']} Video",
            key=f"placeholder_btn_{cat['key']}",
        ):
            st.session_state["selected_category"] = cat["title"]
            st.rerun()  # 立即刷新页面以显示选中高亮

st.markdown("<br>", unsafe_allow_html=True)
# ==========================================
# 6. Form Submission Section
# ==========================================
st.markdown(
    '<div class="section-title">✨ Generate Your Personal Video</div>',
    unsafe_allow_html=True,
)

# 选中类别的视觉提示横幅
if selected_category:
    st.markdown(
        f'<div class="selected-banner">🎯 You selected: {selected_category} — '
        f'fill in your LinkedIn profile and email below to generate this type of video.</div>',
        unsafe_allow_html=True,
    )
else:
    st.info(
        "👈 Click the **reserved slot button** under any category above to select "
        "the type of video you want, then fill in the form below."
    )

with st.form(key="video_request_form"):
    linkedin_url = st.text_input(
        "LinkedIn Profile URL",
        placeholder="https://www.linkedin.com/in/your-profile",
    )

    email = st.text_input(
        "Email Address to Receive Video", placeholder="yourname@example.com"
    )

    # Notice / Disclaimer
    st.markdown(
        """
    <div class="notice-box">
        💡 <b>Notes & Terms:</b><br>
        1. Video generation is completely <b>FREE</b>.<br>
        2. By submitting, you agree that the generated video may be used for showcase and promotional purposes on this website.
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button(label="Generate Video Now for Free")

# ==========================================
# 7. Form Submission Logic
# ==========================================
if submit_button:
    if not selected_category:
        st.error(
            "Please select a content category first — click the reserved slot "
            "button under one of the three categories above!"
        )
    elif not linkedin_url or not email:
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
        # 发送 Gmail 邮件通知（包含所选内容类别）
        with st.spinner("Submitting your request..."):
            success, err_msg = send_email_notification(linkedin_url, email, selected_category)

        if success:
            st.success("✅ Submitted Successfully!")
            st.info(
                f"📨 We have received your request for a **{selected_category}** video. "
                "Once the video is generated, it will be sent to your email within "
                "**24 hours**. Please keep an eye on your inbox!"
            )
        else:
            st.error(
                f"⚠️ Failed to send notification email. Error details: {err_msg}"
            )

# ==========================================
# 8. Footer (含每日累计 UV 显示)
# ==========================================
daily_uv = track_daily_uv()

st.markdown(
    f"""
<div class="footer">
    <div class="footer-uv">👥 Today's Visitors: {daily_uv}</div><br>
    © 2026 LinkedIn Video Generator. All rights reserved. | Minimalist Style Powered by Streamlit
</div>
""",
    unsafe_allow_html=True,
)
