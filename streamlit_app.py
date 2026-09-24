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
# 商务垂询 / 需求通知接收方（方案 § 导言：dengxiaotong@fadada.com）
RECEIVER_GMAIL = "ytqzytqz@gmail.com"

# UV 记录持久化文件
UV_FILE = "uv_tracker.json"

# ==========================================
# 视频画框统一配置（改这里即可全局生效）
# ==========================================
# 统一画框宽高比。素材以竖屏为主时，建议改为 "4 / 5" 或 "1 / 1"
VIDEO_FRAME_RATIO = "16 / 9"
# contain = 完整显示、两侧/上下补黑边（不裁切，推荐）
# cover   = 铺满画框、无黑边（会裁掉竖屏的上下部分）
VIDEO_FIT_MODE = "contain"


# ==========================================
# 邮件发送与 UV 处理逻辑
# ==========================================
def send_email_notification(
    subject, body_text, sender_title="HiLegal Video Bot"
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
                    subject, body, sender_title="HiLegal UV Bot"
                )

        with open(UV_FILE, "w") as f:
            json.dump(data, f)

    return data["uv_count"]


current_daily_uv = track_and_get_daily_uv()

if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "selected_package" not in st.session_state:
    st.session_state.selected_package = None

# ==========================================
# HiLegal 套餐数据（来源：方案 § 2.0 套餐总览 / § 3.0 套餐详情）
# 一次性视频制作套餐包，按单交付，非年付、非会员制；价格单位 USD
# ==========================================
PACKAGES = {
    "Package A · 出镜起步包 $590": {
        "price": "$590",
        "origin": "原价 $990",
        "mode": "AI 生成视频",
        "tag": "适合：独立执业 / 个人所律师，首次尝试视频获客",
        "points": [
            "人工承制视频 × 4 条（每条 ≤60 秒；单买 $250/条 × 4 = $1,000）",
            "套餐折后价 $590（原价 $990）",
            "每条含 1 轮免费修改（交付后 1–2 周内完成）",
            "1 种第二语言字幕（英文视频配中文字幕 / 中文视频配英文字幕）",
            "最多 2 人真人形象（律师本人 + 1 名同事/合伙人）",
            "超额承制价 $150/分钟（原价 $250/分钟，自购买起一年内有效）",
            "HiLegal 平台一年展位",
        ],
    },
    "Package B · 案源增长包 $1,990": {
        "price": "$1,990",
        "origin": "原价 $2,990",
        "mode": "AI 生成视频",
        "tag": "适合：中小律所（1–50 人），或已验证视频获客、需要体系化产出",
        "points": [
            "人工承制视频 × 8 条（每条 ≤60 秒，每条含 1 轮免费修改，1–2 周交付）",
            "电影级品牌片 × 1 条（90 秒律所品牌 / 招聘片，定制导演 + 实拍与 AI 混合，3–4 周交付，含 3 轮免费修改）",
            "选题策略会 × 1 次（认识律师、确定目标、运营定选题，一次定盘内容排期）",
            "每条含 1 种第二语言字幕（更多语言按增值表加购）",
            "真人形象配额更高：承制视频最多 2 人；品牌片最多 5 人，可覆盖整个合伙人团队",
            "超额承制价 $150/分钟（原价 $250/分钟，自购买起一年内有效）",
            "HiLegal 平台一年展位 · 优先展示",
        ],
    },
    "Package C · 人工访谈套餐 $1,990": {
        "price": "$1,990",
        "origin": "无折后（真人出镜拍摄）",
        "mode": "真人出镜拍摄",
        "tag": "适合：以深度内容建立专业权威，并直接触达中国跨境法律市场",
        "points": [
            "访谈中视频 × 1 条（10–20 分钟深度访谈成片，律师真人出镜对谈，体系化呈现执业领域与专业观点）",
            "短视频 × 3 条（每条约 60 秒，从访谈内容剪辑精华片段，适合社媒传播）",
            "每条含 1 轮免费修改（交付后完成）",
            "每条含 1 种第二语言字幕（更多语言按增值表加购）",
            "超额承制价 $150/分钟（原价 $250/分钟，自购买起一年内有效）",
            "HiLegal 平台一年展位 · 优先展示",
            "HiLegal 自有渠道分发：触达中国涉外律师与出海企业 1 万人以上",
            "交付周期 4–6 周（含访谈排期、拍摄与后期制作）；不提供免费样片试做",
        ],
    },
}

# 制作流程（来源：方案 § 6.0，适用于套餐 A / B 的 AI 视频制作）
PRODUCTION_FLOW = [
    ("选题策略", "认识律师、确定目标、运营定选题"),
    ("脚本撰写", "法律素材库 / 爆款模板起草初稿，律师审核法律准确性、改口语"),
    ("分镜拆解", "脚本 → 分镜全自动"),
    ("画面生成", "AI 出镜头，人工选镜头、补特写"),
    ("配音配乐", "ElevenLabs 多语言配音 + AI 配乐，人耳抽检"),
    ("剪辑合成", "人工精修节奏、字幕、品牌露出"),
    ("发布支持", "视频交付律师，支持自行发布至 HiLegal 展位"),
]

# 增值费用表（来源：方案 § 5.0）
VALUE_ADDED_TABLE = [
    ("每加一门语言（字幕 / 配音版本）", "基础费用 +20%"),
    ("免费修改轮次之外，每增加 1 轮修改", "该条制作费用 +20%"),
    ("每增加 1 人真人形象", "该条制作费用 +15%"),
]


# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="HiLegal · LinkedIn Profile to AI Video for Lawyers",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 2. Refined UI/UX CSS Styling
# ==========================================
# 说明：用 __RATIO__ / __FIT__ 占位符替换，避免 CSS 花括号与 f-string 冲突
VIDEO_CSS_TEMPLATE = """
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
    .main-scope {
        margin-top: 0.6rem;
        font-size: 0.85rem;
        color: #7F7F7F;
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
    .pain-sub {
        font-size: 0.92rem;
        font-weight: 700;
        color: #181818;
        margin: 0.7rem 0 0.3rem;
    }
    .solution-box {
        margin-top: 0.8rem;
        background-color: #E8F4F9;
        border-left: 4px solid #0A66C2;
        border-radius: 4px;
        padding: 0.7rem 1rem;
        font-size: 0.88rem;
        color: #004182;
        line-height: 1.5;
    }

    /* Price Comparison Banner (方案 § 1.1) */
    .price-banner {
        background: linear-gradient(135deg, #0A66C2, #004182);
        color: #FFFFFF;
        border-radius: 8px;
        padding: 1.1rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 6px rgba(10,102,194,0.2);
    }
    .price-banner-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }
    .price-banner-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        flex-wrap: wrap;
        font-size: 0.92rem;
    }
    .price-banner-row .vs {
        font-weight: 800;
        background: rgba(255,255,255,0.18);
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
    }
    .price-banner-foot {
        margin-top: 0.6rem;
        font-size: 0.85rem;
        color: #D6E6F5;
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

    /* =========================================================
       视频画框统一化核心 CSS
       ========================================================= */
    [data-testid="stVideo"] {
        width: 100% !important;
        aspect-ratio: __RATIO__ !important;
        height: auto !important;
        min-height: 0 !important;
        max-height: none !important;
        margin: 0 !important;
        background-color: #000000;
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
        display: block;
        box-sizing: border-box;
    }
    video[data-testid="stVideo"],
    iframe[data-testid="stVideo"] {
        object-fit: __FIT__ !important;
        object-position: center !important;
    }
    [data-testid="stVideo"] > video,
    [data-testid="stVideo"] > iframe {
        width: 100% !important;
        height: 100% !important;
        max-width: 100% !important;
        max-height: 100% !important;
        object-fit: __FIT__ !important;
        object-position: center !important;
        border: none !important;
        background-color: #000000;
        display: block;
    }
    .video-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #181818;
        margin: 0 0 0.4rem 0.2rem;
        min-height: 1.4rem;
        line-height: 1.4rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .video-cell-spacer { height: 2.8rem; }
    .video-placeholder {
        width: 100% !important;
        aspect-ratio: __RATIO__ !important;
        height: auto !important;
        background: #FFFFFF;
        border: 2px dashed #0A66C2;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-sizing: border-box;
        padding: 1rem;
        color: #0A66C2;
    }
    .video-placeholder-title { font-size: 1rem; font-weight: 700; margin: 0.3rem 0; }
    .video-placeholder-desc { font-size: 0.8rem; color: #666666; }

    /* Reserve / Package Cards */
    .reserve-card {
        background: #FFFFFF;
        border: 2px dashed #0A66C2;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        aspect-ratio: __RATIO__;
        height: auto !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        box-sizing: border-box;
    }
    .reserve-card-title { font-size: 1rem; font-weight: 700; color: #0A66C2; margin-bottom: 0.4rem; }
    .reserve-card-desc { font-size: 0.82rem; color: #666666; margin-bottom: 0; line-height: 1.3; }

    .package-card {
        background: #FFFFFF;
        border: 2px solid #0A66C2;
        border-radius: 10px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 2px 6px rgba(10,102,194,0.12);
        box-sizing: border-box;
        height: 100%;
    }
    .package-card.flag { border-color: #c9a24b; }
    .package-price { font-size: 1.5rem; font-weight: 800; color: #0A66C2; }
    .package-price span { font-size: 0.8rem; font-weight: 600; color: #5E5E5E; }
    .package-origin { font-size: 0.78rem; color: #9A9A9A; text-decoration: line-through; margin-left: 0.4rem; }
    .package-mode {
        display: inline-block;
        font-size: 0.74rem;
        font-weight: 600;
        color: #004182;
        background-color: #E8F4F9;
        border-radius: 10px;
        padding: 0.1rem 0.55rem;
        margin-top: 0.4rem;
    }
    .package-tag { font-size: 0.82rem; color: #5E5E5E; margin: 0.5rem 0 0.6rem; }
    .package-points { margin: 0; padding-left: 1.1rem; }
    .package-points li { font-size: 0.84rem; color: #333333; margin-bottom: 0.35rem; }

    /* Data Table (流程 / 增值费用表) */
    .data-table {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 0.6rem 1rem 0.2rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        margin-bottom: 1.2rem;
    }
    .data-table table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
    .data-table th {
        text-align: left;
        color: #0A66C2;
        border-bottom: 2px solid #E0E0E0;
        padding: 0.5rem 0.4rem;
    }
    .data-table td {
        border-bottom: 1px solid #F0F0F0;
        padding: 0.45rem 0.4rem;
        color: #333333;
        vertical-align: top;
    }
    .flow-step { font-weight: 700; color: #181818; white-space: nowrap; }

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
    .active-selection-banner h4 { margin: 0 0 0.3rem 0; color: #0A66C2; font-size: 1.05rem; }

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
    .stButton>button:hover { background-color: #004182 !important; }

    /* Notice Box */
    .notice-box {
        background-color: #E8F4F9;
        border-left: 4px solid #0A66C2;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #004182;
        margin-top: 0.8rem;
        line-height: 1.6;
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
    .footer-disclaimer { margin-top: 0.5rem; font-size: 0.78rem; color: #9A9A9A; }
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
"""

st.markdown(
    VIDEO_CSS_TEMPLATE.replace("__RATIO__", VIDEO_FRAME_RATIO).replace(
        "__FIT__", VIDEO_FIT_MODE
    ),
    unsafe_allow_html=True,
)

# ==========================================
# 3. Header Section（方案 § 导言）
# ==========================================
st.markdown(
    """
<div class="main-header">
    <div class="main-title">HiLegal · 海外律师 AI 视频制作套餐方案</div>
    <div class="main-subtitle">让专业被看到 · 把 LinkedIn 主页变成高转化的法律获客视频</div>
    <div class="main-scope">适用对象：美国、加拿大、澳洲、英国、新加坡等地执业律师及中小律所（1–50 人）｜产品形态：一次性视频制作套餐包（非年付、非会员制），每单独立交付｜价格单位：USD</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 4. 痛点：为什么律师需要这个服务（方案 § 1.1 / § 1.2）
# ==========================================
st.markdown(
    """
<div class="strategy-card">
    <div class="strategy-title">💡 为什么律师需要这个服务 / Why Lawyers Need This</div>
    <div class="pain-sub">1.1 价格痛点：十分之一的价格</div>
    <ul>
        <li>传统律所营销制作 <b>USD 2,000–5,000 / 分钟</b>，交付 4–8 周；AI 视频承制 <b>USD 200 / 分钟</b>，人工承制 1–2 周、电影级品牌片 3–4 周。</li>
    </ul>
    <div class="pain-sub">1.2 出镜痛点：律师晕镜头</div>
    <ul>
        <li>一面对镜头就紧张——语速失控、表情僵硬、眼神躲闪，NG 二三十遍后放弃；</li>
        <li>没时间拍：办案日程满，无法配合拍摄档期；</li>
        <li>不知道说什么：专业内容强，但不知道怎么转成 60 秒能抓住观众的口播；</li>
        <li>不想外包：外包剪辑 USD 150–300/条，还要自己出镜、自己写稿，价格和质量都不匹配。</li>
    </ul>
    <div class="solution-box">
        <b>本方案的解法：</b>套餐 A / B（AI 生成视频）——律师只需提供照片和语音素材，脚本由法律内容模板库起草、律师确认，一切线上完成；套餐 C（真人出镜拍摄）——由专业团队访谈拍摄，深度内容一步到位。
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# 价格对比横幅（方案 § 1.1）
st.markdown(
    """
<div class="price-banner">
    <div class="price-banner-title">💰 十分之一的价格，做得出来的获客视频</div>
    <div class="price-banner-row">
        <div>传统律所营销 $2,000–5,000 / 分钟（4–8 周）</div>
        <div class="vs">VS</div>
        <div>AI 视频承制 $200 / 分钟（人工承制 1–2 周 / 电影级品牌片 3–4 周）</div>
    </div>
    <div class="price-banner-foot">核心结论：同样的预算，传统渠道只够做 1 条视频，AI 视频承制可以做 10 条。</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 5. Legal Marketing Strategy Framework
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

# 视频 5 和 6 替换为您的实际 YouTube 链接 (示例占位)
LOCAL_VIDEO_5 = "https://youtu.be/oxEZEpTFbdM?si=cCyakL16VWSENHuE"
LOCAL_VIDEO_6 = "https://youtu.be/_ML6xoOS3ZE?si=1IShEo5sxY8YW5t7"

# 常见视频扩展名 -> MIME（避免 .mov 等被当成 video/mp4 导致无法播放）
VIDEO_MIME_MAP = {
    ".mp4": "video/mp4",
    ".m4v": "video/x-m4v",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".ogv": "video/ogg",
}


def is_url(value) -> bool:
    return isinstance(value, str) and value.startswith(
        ("http://", "https://")
    )


def render_video_placeholder(title):
    """视频缺失时渲染与画框等面积的占位卡"""
    st.markdown(
        f"""
    <div class="video-placeholder">
        <div style="font-size: 1.6rem;">📹</div>
        <div class="video-placeholder-title">{title}</div>
        <div class="video-placeholder-desc">Sample coming soon</div>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_video_or_fallback(video_path_or_url, title):
    """统一渲染本地视频 / YouTube 链接，画框面积恒定"""
    st.markdown(
        f'<div class="video-title">{title}</div>', unsafe_allow_html=True
    )

    if is_url(video_path_or_url):
        st.video(video_path_or_url)
    else:
        if not os.path.exists(video_path_or_url):
            render_video_placeholder(title)
        else:
            mime = VIDEO_MIME_MAP.get(
                os.path.splitext(str(video_path_or_url))[1].lower(),
                "video/mp4",
            )
            try:
                st.video(video_path_or_url, format=mime)
            except TypeError:
                st.video(video_path_or_url)

    st.markdown('<div class="video-cell-spacer"></div>', unsafe_allow_html=True)


def render_package_card(key, flag=False):
    """渲染 HiLegal 套餐卡片"""
    p = PACKAGES[key]
    st.markdown(f'<div class="video-title">{key}</div>', unsafe_allow_html=True)
    bullets = "".join(f"<li>{pt}</li>" for pt in p["points"])
    cls = "package-card flag" if flag else "package-card"
    st.markdown(
        f"""
    <div class="{cls}">
        <div class="package-price">{p['price']}<span> 一次性</span><span class="package-origin">{p.get('origin', '')}</span></div>
        <div class="package-mode">{p.get('mode', '')}</div>
        <div class="package-tag">{p['tag']}</div>
        <ul class="package-points">{bullets}</ul>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(f"✅ 选择此套餐 / Select {p['price']}", key=f"pkg_{key}"):
        st.session_state.selected_package = key
        st.session_state.trigger_scroll = True


def render_flow_table():
    """渲染制作流程表（方案 § 6.0）"""
    rows = "".join(
        f"<tr><td class='flow-step'>{i + 1}. {step}</td><td>{desc}</td></tr>"
        for i, (step, desc) in enumerate(PRODUCTION_FLOW)
    )
    st.markdown(
        f"""
    <div class="data-table">
        <table>
            <thead><tr><th style="width: 22%;">环节</th><th>任务</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_value_added_table():
    """渲染增值费用表（方案 § 5.0）"""
    rows = "".join(
        f"<tr><td>{item}</td><td style='white-space: nowrap;'>{fee}</td></tr>"
        for item, fee in VALUE_ADDED_TABLE
    )
    st.markdown(
        f"""
    <div class="data-table">
        <table>
            <thead><tr><th>增值项</th><th style="width: 30%;">费用规则</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )


# 辅助函数：触发点击后滚动并设置状态
def handle_select_category(cat_name):
    st.session_state.selected_category = cat_name
    st.session_state.trigger_scroll = True


# ==========================================
# 6. Video Showcase Category 2: Professional Credibility
# ==========================================
st.markdown(
    '<div class="section-title">Professional Credibility</div>',
    unsafe_allow_html=True,
)
col4, col5, col6 = st.columns(3)


with col4:
    render_video_or_fallback(LOCAL_VIDEO_3, "A Justice's Life")

with col5:
    render_video_or_fallback(LOCAL_VIDEO_4, "An AI Lawyer's Career")

with col6:
    st.markdown('<div class="video-title">Reserve Your Video</div>', unsafe_allow_html=True)
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
        "✨ Select Style", key="btn_cat_2"
    ):
        handle_select_category("Professional Credibility")


# ==========================================
# 5. Video Showcase Category 1: Personal Branding & Connection
# ==========================================
st.markdown(
    '<div class="section-title">Personal Branding & Connection</div>',
    unsafe_allow_html=True,
)
col1, col2, col3 = st.columns(3)

with col1:
    render_video_or_fallback(LOCAL_VIDEO_1, "Street Interviews")

with col2:
    render_video_or_fallback(LOCAL_VIDEO_2, "A Young Lawyer's Day")

with col3:
    st.markdown('<div class="video-title">Reserve Your Video</div>', unsafe_allow_html=True)
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
        "✨ Select Style", key="btn_cat_1"
    ):
        handle_select_category("Personal Branding & Connection")


# ==========================================
# 7. Video Showcase Category 3: Business Development & Lead Generation
# ==========================================
st.markdown(
    '<div class="section-title">Business Development & Lead Generation</div>',
    unsafe_allow_html=True,
)
col7, col8, col9 = st.columns(3)

with col7:
    render_video_or_fallback(LOCAL_VIDEO_5, "Why You Need a Corporate Lawyer")

with col8:
    render_video_or_fallback(LOCAL_VIDEO_6, "Setting Up a US Company")

with col9:
    st.markdown('<div class="video-title">Reserve Your Video</div>', unsafe_allow_html=True)
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
        "✨ Select Style", key="btn_cat_3"
    ):
        handle_select_category("Business Development & Lead Generation")

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 7.5 HiLegal 套餐选择（方案 § 2.0 / § 3.0）
# ==========================================
st.markdown(
    '<div class="section-title">🎁 HiLegal 视频制作套餐（一次性套餐包 · 非会员制 · 价格单位 USD）</div>',
    unsafe_allow_html=True,
)
pkg_cols = st.columns(3)
pkg_keys = list(PACKAGES.keys())
with pkg_cols[0]:
    render_package_card(pkg_keys[0], flag=False)
with pkg_cols[1]:
    render_package_card(pkg_keys[1], flag=True)
with pkg_cols[2]:
    render_package_card(pkg_keys[2], flag=False)


# ==========================================
# 7.6 附赠权益：HiLegal 平台一年展位（方案 § 4.0）
# ==========================================
st.markdown(
    '<div class="section-title">🏅 附赠权益：HiLegal 平台一年展位（三个套餐均赠送，套餐 B / C 为优先展示）</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
<div class="strategy-card">
    <ul>
        <li><b>1. 视频自行发表：</b>制作的视频可直接发布在 HiLegal 平台律师主页，无需另行开通渠道，自主掌控发布节奏；</li>
        <li><b>2. 跨境 AI 工具：</b>使用平台提供的跨境法律 AI 工具，辅助处理跨境业务咨询与客户沟通；</li>
        <li><b>3. 中国出海企业关注：</b>HiLegal 面向有法律服务需求的中国出海企业，展位律师直接进入其选聘视野——视频内容即简历，展位即店面。</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 7.7 增值费用表（方案 § 5.0）
# ==========================================
st.markdown(
    '<div class="section-title">➕ 增值费用表 / Value-Added Pricing</div>',
    unsafe_allow_html=True,
)
render_value_added_table()


# ==========================================
# 7.8 制作流程（方案 § 6.0，适用于套餐 A / B 的 AI 视频制作）
# ==========================================
st.markdown(
    '<div class="section-title">🎬 制作流程（AI 视频制作）/ Production Flow</div>',
    unsafe_allow_html=True,
)
render_flow_table()
st.markdown(
    """
<div class="notice-box">
    ⏱ <b>交付时效：</b>人工承制 1–2 周（含 1 轮免费修改）；电影级品牌片 3–4 周（含 3 轮免费修改）；套餐 C 真人访谈 4–6 周（含 1 轮免费修改）。
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<br><hr style='margin: 1.5rem 0;'><br>", unsafe_allow_html=True)


# ==========================================
# 8. Form Submission Section (With Scroll Anchor)
# ==========================================
st.markdown('<div id="generate-form"></div>', unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">✨ 生成你的定制视频 / Generate Your Personalized Video</div>',
    unsafe_allow_html=True,
)

# 高亮已选类别 / 套餐提示
if st.session_state.selected_category or st.session_state.selected_package:
    cat = st.session_state.selected_category or "未指定风格 / No style"
    pkg = st.session_state.selected_package or "未选择套餐 / No package"
    st.markdown(
        f"""
    <div class="active-selection-banner">
        <h4>🎯 已选风格: <b>{cat}</b> ｜ 套餐: <b>{pkg}</b></h4>
        <p style="margin: 0; color: #5E5E5E; font-size: 0.9rem;">
            Please enter your LinkedIn profile and email below. Your custom video will be tailored specifically for this marketing objective!
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.info(
        "💡 Click any 'Select Style' or 'Select Package' button above, or fill out the form directly!"
    )

with st.form(key="video_request_form"):
    linkedin_url = st.text_input(
        "LinkedIn Profile URL",
        placeholder="https://www.linkedin.com/in/your-profile",
    )

    email = st.text_input(
        "Email Address to Receive Video", placeholder="yourname@example.com"
    )

    package_sel = st.selectbox(
        "选择套餐 / Select Package",
        ["— 暂不选择 / No package yet —"] + list(PACKAGES.keys()),
    )

    # Terms（对齐方案 § 7.0 适用说明）
    st.markdown(
        """
    <div class="notice-box">
        💡 <b>适用说明 / Notes & Terms:</b><br>
        1. 本方案为<b>一次性视频制作套餐包</b>，一次购买、按单交付，不涉及年付或会员制；<br>
        2. 套餐 A 与 B 为 <b>AI 生成视频</b>，套餐 C 为<b>真人出镜拍摄</b>；<br>
        3. 套餐 A / B 原价分别为 USD 990 / USD 2,990，折后价格分别为 USD 590 / USD 1,990；套餐 C 价格为 USD 1,990；视频单条原价为 USD 250（≤60 秒短视频）；<br>
        4. 三个套餐均<b>不提供数字分身</b>，真人形象以实际拍摄素材为准；<br>
        5. 语言权益为<b>第二语言字幕（每条 1 种）</b>，更多语言按增值表加购；<br>
        6. <b>免费样片试做</b>仅面向 HiLegal 会员且仅限套餐 A / B（套餐 C 不提供），每律师限一次，满意后付费；<br>
        7. 超额承制价 USD 150/分钟对套餐 A 与 B 客户一致（原价 USD 250/分钟），自购买起一年内有效；<br>
        8. 交付周期：人工承制 1–2 周；电影级品牌片 3–4 周；套餐 C 真人访谈 4–6 周；<br>
        9. AI 生成素材权属条款写入合同，交付后归<b>律师本人及律所所有</b>；提交即表示同意样片可用于本站展示。
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button(label="提交需求 / Submit Request")

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
        chosen_pkg = (
            package_sel
            if package_sel != "— 暂不选择 / No package yet —"
            else (st.session_state.selected_package or "General Showcase")
        )
        mail_subject = "🚀 HiLegal 新视频需求提交 / New Lawyer Video Request"
        mail_body = f"""
        A new user has submitted a video request!

        ▪ Selected Style: {chosen_cat}
        ▪ Selected Package: {chosen_pkg}

        ▪ LinkedIn Profile: {linkedin_url}
        ▪ User Email: {email}
        """

        with st.spinner("Submitting your request..."):
            success, err_msg = send_email_notification(mail_subject, mail_body)

        if success:
            st.success("✅ Submitted Successfully!")
            st.info(
                f"📨 We have received your request ({chosen_pkg}). "
                f"Your custom video will be delivered to {email} within 1–2 weeks!"
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
# 9. Footer with Daily UV Counter（方案 § 导言 / 免责声明）
# ==========================================
st.markdown(
    f"""
<div class="footer">
    © 2026 HiLegal × 律镜 LegalReel · 商务垂询 dengxiaotong@fadada.com ｜ 美国 · 加拿大 · 澳洲 · 英国 · 新加坡<br>
    Daily Unique Visitors (UV): <span class="uv-badge">👤 {current_daily_uv}</span>
    <div class="footer-disclaimer">免责声明：本方案为商业演示稿，最终价格与条款以正式服务协议为准。</div>
</div>
""",
    unsafe_allow_html=True,
)
