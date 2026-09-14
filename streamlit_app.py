import streamlit as st

# 1. 页面基本配置
st.set_page_config(
    page_title="LinkedIn Profile to Video Generator",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 注入极简领英风格 CSS 样式
st.markdown("""
<style>
    /* 全局背景色与字体 */
    .stApp {
        background-color: #F3F2EF;
        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #181818;
    }

    /* 顶部标题栏 / Header 样式 */
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

    /* 内容卡片统一样式 */
    .css-card {
        background-color: #FFFFFF;
        padding: 1.8rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }

    /* 模块标题 */
    .section-title {
        color: #181818;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1.2rem;
        border-bottom: 2px solid #F3F2EF;
        padding-bottom: 0.5rem;
    }

    /* 输入框与按钮样式重写 */
    div[data-baseweb="input"] {
        border-radius: 4px;
    }
    
    /* 领英蓝主按钮 */
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

    /* 提示信息样式 */
    .notice-box {
        background-color: #E8F4F9;
        border-left: 4px solid #0A66C2;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #004182;
        margin-top: 1rem;
    }

    /* 页脚 */
    .footer {
        text-align: center;
        color: #7F7F7F;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 头部区域 ---
st.markdown("""
<div class="main-header">
    <div class="main-title">LinkedIn 个人主页转 AI 职场视频</div>
    <div class="main-subtitle">输入你的领英链接，一键生成专属的高品质职场展示视频</div>
</div>
""", unsafe_allow_html=True)

# --- 4. 视频案例展示区 ---
st.markdown('<div class="section-title">📹 案例展示</div>', unsafe_allow_html=True)

# 展示 3 个视频案例列（可以替换为你自己的视频地址或本地视频）
col1, col2, col3 = st.columns(3)

sample_videos = [
    {"title": "高级软件工程师案例", "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    {"title": "资深产品经理案例", "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
    {"title": "市场营销总监案例", "url": "https://www.w3schools.com/html/mov_bbb.mp4"},
]

for col, item in zip([col1, col2, col3], sample_videos):
    with col:
        st.markdown(f"**{item['title']}**")
        st.video(item["url"])

st.markdown("<br>", unsafe_allow_html=True)

# --- 5. 提交表单区 ---
st.markdown('<div class="section-title">✨ 生成你的专属视频</div>', unsafe_allow_html=True)

# 使用表单保证交互体验整洁
with st.form(key="video_request_form"):
    linkedin_url = st.text_input(
        "领英个人主页链接", 
        placeholder="https://www.linkedin.com/in/your-profile"
    )
    
    email = st.text_input(
        "接收视频的 Email 邮箱", 
        placeholder="yourname@example.com"
    )
    
    # 免责/提示说明
    st.markdown("""
    <div class="notice-box">
        💡 <b>提示与声明：</b><br>
        1. 视频生成完全 <b>免费</b>。<br>
        2. 提交即表示您同意生成的视频可能会被用于本网站的案例宣传与演示。
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button(label="立即免费生成视频")

# --- 6. 提交处理逻辑 ---
if submit_button:
    if not linkedin_url or not email:
        st.error("请完整填写领英链接和 Email 邮箱！")
    elif "linkedin.com/in/" not in linkedin_url.lower():
        st.warning("请输入有效的领英个人主页链接（例如：https://www.linkedin.com/in/xxx）")
    elif "@" not in email:
        st.warning("请输入有效的邮箱地址！")
    else:
        # TODO: 这里可以添加将数据写入数据库或发送到 backend API 的逻辑
        st.success("✅ 提交成功！")
        st.info("📨 我们已收到您的请求，视频制作完成后，将在 **24 小时内** 发送至您的 Email 邮箱，请注意查收！")

# --- 7. 页脚 ---
st.markdown("""
<div class="footer">
    © 2026 LinkedIn Video Generator. All rights reserved. | Minimalist Style Powered by Streamlit
</div>
""", unsafe_allow_html=True)
