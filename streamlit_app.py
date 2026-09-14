import smtplib
from email.header import Header
from email.mime.text import MIMEText
import streamlit as st

# ==========================================
# 邮箱配置信息（请在此处替换为你自己的配置）
# ==========================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # SSL 端口
SENDER_GMAIL = "ytqzytqz@gmail.com"  # 你的 Gmail 账号
SENDER_PASSWORD = "smqk khlq goxb rhdh"  # 你的 Gmail 应用专用密码 (App Password)
RECEIVER_GMAIL = "ytqzytqz@gmail.com"  # 接收通知的 Gmail 账号




def send_email_notification(user_linkedin, user_email):
    """发送邮件通知函数"""
    subject = "🚀 New Video Request Submitted"
    body = f"""
    A new user has submitted a request for video generation:

    - LinkedIn Profile: {user_linkedin}
    - User Email: {user_email}
    """

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


# 1. Page Configuration
st.set_page_config(
    page_title="LinkedIn Profile to Video Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. CSS Styling (LinkedIn Aesthetic)
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

    /* Footer */
    .footer {
        text-align: center;
        color: #7F7F7F;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- 3. Header Section ---
st.markdown(
    """
<div class="main-header">
    <div class="main-title">LinkedIn Profile to AI Professional Video</div>
    <div class="main-subtitle">Turn your LinkedIn profile into a high-quality video showcase with a single click</div>
</div>
""",
    unsafe_allow_html=True,
)

# --- 4. Video Showcase Section ---
st.markdown(
    '<div class="section-title">📹 Showcase & Examples</div>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

# 本地视频路径定义（请替换为你本地实际的视频文件文件名或绝对路径）
LOCAL_VIDEO_1 = "video_1.mp4"
LOCAL_VIDEO_2 = "video_2.mp4"

# 1. 本地视频 1
with col1:
    st.markdown("**Senior Software Engineer Case**")
    try:
        # 读取本地视频文件
        with open(LOCAL_VIDEO_1, "rb") as video_file:
            st.video(video_file.read())
    except FileNotFoundError:
        st.warning(f"Local video file not found: `{LOCAL_VIDEO_1}`")

# 2. 本地视频 2
with col2:
    st.markdown("**Senior Product Manager Case**")
    try:
        # 读取本地视频文件
        with open(LOCAL_VIDEO_2, "rb") as video_file:
            st.video(video_file.read())
    except FileNotFoundError:
        st.warning(f"Local video file not found: `{LOCAL_VIDEO_2}`")

# 3. 空白占位符（提示用户这里将是生成的视频）
with col3:
    st.markdown("**Your Personalized Showcase**")
    st.markdown(
        """
    <div class="video-placeholder">
        <div class="placeholder-title">✨ Your Video Here</div>
        <div class="placeholder-text">
            Submit your profile below! <br>
            AI will generate your personalized career showcase video right here.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. Form Submission Section ---
st.markdown(
    '<div class="section-title">✨ Generate Your Personal Video</div>',
    unsafe_allow_html=True,
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

# --- 6. Form Submission Logic ---
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
        # 发送 Gmail 邮件通知
        with st.spinner("Submitting your request..."):
            success, err_msg = send_email_notification(linkedin_url, email)

        if success:
            st.success("✅ Submitted Successfully!")
            st.info(
                "📨 We have received your request. Once the video is generated, it will be sent to your email within **24 hours**. Please keep an eye on your inbox!"
            )
        else:
            st.error(
                f"⚠️ Failed to send notification email. Error details: {err_msg}"
            )

# --- 7. Footer ---
st.markdown(
    """
<div class="footer">
    © 2026 LinkedIn Video Generator. All rights reserved. | Minimalist Style Powered by Streamlit
</div>
""",
    unsafe_allow_html=True,
)
