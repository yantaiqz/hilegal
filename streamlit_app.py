
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
# 商务垂询 / 需求通知接收方
RECEIVER_GMAIL = "ytqzytqz@gmail.com"

# UV 记录持久化文件
UV_FILE = "uv_tracker.json"

# ==========================================
# 视频画框统一配置
# ==========================================
VIDEO_FRAME_RATIO = "16 / 9"
VIDEO_FIT_MODE = "contain"


# ==========================================
# 邮件发送与 UV 处理逻辑
# ==========================================
def send_email_notification(subject, body_text, sender_title="HiLegal Video Bot"):
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
                subject = f"Milestone Reached: {t} Daily UVs!"
                body = (
                    f"Your app has reached {t} Unique Visitors today ({today_str}).\n\n"
                    f"Current Daily UV Count: {data['uv_count']}"
                )
                send_email_notification(subject, body, sender_title="HiLegal UV Bot")
        with open(UV_FILE, "w") as f:
            json.dump(data, f)
    return data["uv_count"]


current_daily_uv = track_and_get_daily_uv()

# ==========================================
# 多语言（默认英文）
# ==========================================
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "selected_package" not in st.session_state:
    st.session_state.selected_package = None


def L(zh, en):
    """按当前语言返回对应文本（默认英文）"""
    return zh if st.session_state.lang == "zh" else en


# ==========================================
# HiLegal 套餐数据（双语）
# ==========================================
PACKAGES = {
    "A": {
        "price": "$590",
        "origin": L("原价 $990", "was $990"),
        "mode": L("AI 生成视频", "AI-generated video"),
        "flag": False,
        "name": L("套餐 A · 出镜起步包", "Package A · On-Camera Starter"),
        "tag": L(
            "适合：独立执业 / 个人所律师，首次尝试视频获客",
            "Best for solo / small-firm lawyers trying video for the first time",
        ),
        "points": [
            L("人工承制视频 × 4 条（每条 ≤60 秒）", "4 hand-produced videos (each ≤60s)"),
            L("套餐折后价 $590（原价 $990）", "Bundle price $590 (was $990)"),
            L("每条含 1 轮免费修改（交付后 1–2 周内完成）", "1 free revision per video (within 1-2 weeks)"),
            L("1 种第二语言字幕", "1 second-language subtitle per video"),
            L("最多 2 人真人形象", "Up to 2 real-person likenesses"),
            L("超额承制价 $150/分钟（一年内有效）", "Extra footage $150/min (valid 1 year)"),
            L("HiLegal 平台一年展位", "1-year HiLegal platform listing"),
        ],
    },
    "B": {
        "price": "$1,990",
        "origin": L("原价 $2,990", "was $2,990"),
        "mode": L("AI 生成视频", "AI-generated video"),
        "flag": True,
        "name": L("套餐 B · 案源增长包", "Package B · Growth Bundle"),
        "tag": L(
            "适合：中小律所（1–50 人），或需体系化产出",
            "Best for small-mid firms (1-50) scaling content systematically",
        ),
        "points": [
            L("人工承制视频 × 8 条（每条 ≤60 秒，含 1 轮免费修改）", "8 hand-produced videos (each ≤60s, 1 free revision)"),
            L("电影级品牌片 × 1 条（90 秒，定制导演 + 实拍与 AI 混合）", "1 cinematic brand film (90s, custom director, live+AI)"),
            L("选题策略会 × 1 次", "1 strategy & topic workshop"),
            L("每条含 1 种第二语言字幕", "1 second-language subtitle per video"),
            L("真人形象配额更高（品牌片最多 5 人）", "Higher likeness quota (brand film up to 5)"),
            L("超额承制价 $150/分钟（一年内有效）", "Extra footage $150/min (valid 1 year)"),
            L("HiLegal 平台一年展位 · 优先展示", "1-year HiLegal listing · priority placement"),
        ],
    },
    "C": {
        "price": "$1,990",
        "origin": L("无折后（真人出镜拍摄）", "no discount (on-camera shoot)"),
        "mode": L("真人出镜拍摄", "On-camera shoot"),
        "flag": False,
        "name": L("套餐 C · 人工访谈套餐", "Package C · Interview Bundle"),
        "tag": L(
            "适合：以深度内容建立专业权威，直接触达中国跨境法律市场",
            "Best for building authority via in-depth content for the China cross-border market",
        ),
        "points": [
            L("访谈中视频 × 1 条（10–20 分钟深度访谈成片）", "1 mid-length interview film (10-20 min, on-camera)"),
            L("短视频 × 3 条（每条约 60 秒，剪辑精华片段）", "3 short clips (~60s each, cut from the interview)"),
            L("每条含 1 轮免费修改", "1 free revision per video"),
            L("每条含 1 种第二语言字幕", "1 second-language subtitle per video"),
            L("超额承制价 $150/分钟（一年内有效）", "Extra footage $150/min (valid 1 year)"),
            L("HiLegal 平台一年展位 · 优先展示", "1-year HiLegal listing · priority placement"),
            L("HiLegal 自有渠道分发：触达 1 万人以上", "Distribution via HiLegal channels (10,000+ audience)"),
            L("交付周期 4–6 周；不提供免费样片试做", "Delivery 4-6 weeks; no free sample"),
        ],
    },
}

PKG_KEYS = ["A", "B", "C"]

VALUE_ADDED_TABLE = [
    (L("每加一门语言（字幕 / 配音版本）", "Each extra language (sub / dub)"), L("基础费用 +20%", "+20% base fee")),
    (L("免费修改轮次之外每加 1 轮修改", "Each extra revision beyond free rounds"), L("该条制作费用 +20%", "+20% for that video")),
    (L("每增加 1 人真人形象", "Each additional real-person likeness"), L("该条制作费用 +15%", "+15% for that video")),
]

# ==========================================
# 视频素材
# ==========================================
LOCAL_VIDEO_1 = "01.mp4"
LOCAL_VIDEO_2 = "02.mov"
LOCAL_VIDEO_3 = "03.mp4"
LOCAL_VIDEO_4 = "04.mp4"
LOCAL_VIDEO_5 = "https://youtu.be/oxEZEpTFbdM?si=cCyakL16VWSENHuE"
LOCAL_VIDEO_6 = "https://youtu.be/_ML6xoOS3ZE?si=1IShEo5sxY8YW5t7"

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
    return isinstance(value, str) and value.startswith(("http://", "https://"))


# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(
    page_title="HiLegal · AI Video Production for Lawyers",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 2. 律所专业风 CSS（深海军蓝 + 低调金 + 衬线标题 + 留白 + 细边框）
# ==========================================
CSS_TEMPLATE = """
<style>
    .stApp {
        background-color: #F5F4F0;
        font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #1C2B3A;
    }
    
    /* === 2. 彻底去除顶部留白 === */
    [data-testid="stHeader"] {
        display: none !important;
    }
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    .block-container { padding-top: 1.4rem !important; padding-bottom: 3rem !important; max-width: 1120px; }

    /* 语言切换工具条 */
    .stButton > button {
        background: #FFFFFF !important; color: #0B2545 !important; font-weight: 600 !important;
        border: 1px solid #C9CFD6 !important; border-radius: 6px !important;
        padding: .25rem .9rem !important; width: auto !important; min-width: 62px !important;
        font-size: .84rem !important; letter-spacing: .04em;
    }
    .stButton > button:hover { border-color: #0B2545 !important; }

    /* 顶部品牌条 */
    .main-header {
        background: #FFFFFF; padding: 2rem 2.2rem; border-radius: 6px;
        border: 1px solid #E3E1DB; border-top: 3px solid #B08D57; margin-bottom: 1.4rem;
    }
    .brand-line { display:flex; align-items:baseline; gap:.6rem; }
    .brand-mark {
        font-family: Georgia, "Times New Roman", serif; font-size: 2rem; font-weight: 700;
        color: #0B2545; letter-spacing: .02em;
    }
    .brand-mark .accent { color: #B08D57; }
    .main-subtitle {
        color: #4A5568; font-size: 1.02rem; margin-top: .5rem;
        font-family: Georgia, "Times New Roman", serif; font-style: italic;
    }
    .main-scope { margin-top: .9rem; font-size: .82rem; color: #7C8698; line-height: 1.5; }

    /* 小节标题（金色眉标 + 衬线） */
    .eyebrow {
        font-size: .74rem; letter-spacing: .18em; text-transform: uppercase;
        color: #B08D57; font-weight: 700; margin-top: 1.6rem; margin-bottom: .1rem;
    }
    .section-title {
        font-family: Georgia, "Times New Roman", serif; color: #0B2545;
        font-size: 1.5rem; font-weight: 700; margin: 0 0 .9rem 0;
    }
    .section-title::after {
        content: ""; display: block; width: 46px; height: 3px; background: #B08D57; margin-top: .5rem;
    }

    /* 价格对比条 */
    .price-banner { background: #0B2545; color: #FFFFFF; border-radius: 6px; padding: 1.3rem 1.6rem; margin-bottom: 1.6rem; }
    .price-banner-title { font-family: Georgia, serif; font-size: 1.1rem; font-weight: 700; margin-bottom: .7rem; color:#F5F4F0; }
    .price-banner-row { display: flex; align-items: center; justify-content: center; gap: 1rem; flex-wrap: wrap; font-size: .92rem; }
    .price-banner-row .vs { font-weight: 800; background: rgba(176,141,87,.35); color:#fff; padding: .2rem .7rem; border-radius: 4px; }
    .price-banner-foot { margin-top: .7rem; font-size: .85rem; color: #C9CFD6; }

    /* 通用卡片 */
    .card { background: #FFFFFF; padding: 1.3rem 1.6rem; border-radius: 6px; border: 1px solid #E3E1DB; margin-bottom: 1.2rem; }
    .card ul { margin: .3rem 0 0; padding-left: 1.2rem; }
    .card li { font-size: .9rem; color: #34404F; margin-bottom: .35rem; line-height: 1.5; }
    .pain-sub { font-size: .95rem; font-weight: 700; color: #0B2545; margin: .8rem 0 .3rem; }
    .solution-box { margin-top: .9rem; background: #F1EEE8; border-left: 3px solid #B08D57; border-radius: 3px; padding: .7rem 1rem; font-size: .88rem; color: #34404F; line-height: 1.55; }

    /* 视频画框 */
    [data-testid="stVideo"] {
        width: 100% !important; aspect-ratio: __RATIO__ !important; height: auto !important;
        min-height: 0 !important; max-height: none !important; margin: 0 !important;
        background-color: #000 !important; border: none !important; border-radius: 5px; overflow: hidden; display: block; box-sizing: border-box;
    }
    [data-testid="stVideo"] > video, [data-testid="stVideo"] > iframe {
        width: 100% !important; height: 100% !important; object-fit: __FIT__ !important;
        object-position: center !important; border: none !important; background-color: #000; display: block;
    }
    .video-title { font-size: .88rem; font-weight: 600; color: #0B2545; margin: 0 0 .45rem .1rem; min-height: 1.3rem; line-height: 1.3rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .video-cell-spacer { height: 1.6rem; }
    .video-placeholder {
        width: 100% !important; aspect-ratio: __RATIO__ !important; height: auto !important;
        background: #FFFFFF; border: 1px dashed #B08D57; border-radius: 5px;
        display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;
        box-sizing: border-box; padding: 1rem; color: #B08D57;
    }
    .video-placeholder-title { font-size: .95rem; font-weight: 700; margin: .3rem 0; }
    .video-placeholder-desc { font-size: .78rem; color: #7C8698; }

    .reserve-card {
        background: #FFFFFF; border: 1px dashed #B08D57; border-radius: 5px; padding: 1rem; text-align: center;
        aspect-ratio: __RATIO__; height: auto !important; display: flex; flex-direction: column; justify-content: center; align-items: center; box-sizing: border-box;
    }
    .reserve-card-title { font-family: Georgia, serif; font-size: 1rem; font-weight: 700; color: #0B2545; margin-bottom: .4rem; }
    .reserve-card-desc { font-size: .8rem; color: #7C8698; margin-bottom: 0; line-height: 1.35; }

    /* 套餐卡片 */
    .package-card { background: #FFFFFF; border: 1px solid #E3E1DB; border-top: 3px solid #0B2545; border-radius: 6px; padding: 1.2rem 1.3rem; box-sizing: border-box; height: 100%; }
    .package-card.flag { border-top-color: #B08D57; }
    .package-name { font-family: Georgia, serif; font-size: 1.08rem; font-weight: 700; color: #0B2545; margin-bottom: .4rem; }
    .package-price { font-size: 1.55rem; font-weight: 800; color: #0B2545; }
    .package-price span { font-size: .78rem; font-weight: 600; color: #7C8698; }
    .package-origin { font-size: .76rem; color: #9AA3B0; text-decoration: line-through; margin-left: .4rem; }
    .package-mode { display: inline-block; font-size: .72rem; font-weight: 600; color: #0B2545; background-color: #F1EEE8; border-radius: 3px; padding: .12rem .55rem; margin-top: .4rem; }
    .package-tag { font-size: .82rem; color: #4A5568; margin: .55rem 0 .65rem; line-height: 1.45; }
    .package-points { margin: 0; padding-left: 1.1rem; }
    .package-points li { font-size: .84rem; color: #34404F; margin-bottom: .38rem; line-height: 1.45; }

    /* 表格 */
    .data-table { background: #FFFFFF; border: 1px solid #E3E1DB; border-radius: 6px; padding: .6rem 1rem .2rem; margin-bottom: 1.2rem; }
    .data-table table { width: 100%; border-collapse: collapse; font-size: .86rem; }
    .data-table th { text-align: left; color: #0B2545; border-bottom: 2px solid #E3E1DB; padding: .55rem .4rem; }
    .data-table td { border-bottom: 1px solid #F1EFEA; padding: .5rem .4rem; color: #34404F; vertical-align: top; }
    .flow-step { font-weight: 700; color: #0B2545; white-space: nowrap; }

    .active-selection-banner { background: #F1EEE8; border: 1px solid #B08D57; border-radius: 6px; padding: 1rem 1.2rem; text-align: center; margin-bottom: 1.2rem; }
    .active-selection-banner h4 { margin: 0 0 .3rem 0; color: #0B2545; font-size: 1.05rem; }

    .notice-box { background: #F1EEE8; border-left: 3px solid #B08D57; padding: .85rem 1rem; border-radius: 3px; font-size: .84rem; color: #34404F; margin-top: .8rem; line-height: 1.7; }

    .footer { text-align: center; color: #7C8698; font-size: .82rem; margin-top: 2.6rem; padding: 1.1rem 0 1rem; border-top: 1px solid #E3E1DB; }
    .footer-disclaimer { margin-top: .5rem; font-size: .76rem; color: #9AA3B0; }
    .uv-badge { display: inline-block; background: #EDEAE3; color: #0B2545; font-weight: 600; padding: .12rem .5rem; border-radius: 3px; margin-left: .4rem; font-size: .8rem; }
</style>
"""

st.markdown(
    CSS_TEMPLATE.replace("__RATIO__", VIDEO_FRAME_RATIO).replace("__FIT__", VIDEO_FIT_MODE),
    unsafe_allow_html=True,
)


# ==========================================
# 语言切换工具条（右上，默认英文）
# ==========================================
tb = st.columns([7, 1.2, 1.2])
with tb[1]:
    if st.button("EN", key="lang_en"):
        st.session_state.lang = "en"
        st.rerun()
with tb[2]:
    if st.button("中文", key="lang_zh"):
        st.session_state.lang = "zh"
        st.rerun()

# ==========================================
# 3. 顶部品牌条
# ==========================================
st.markdown(
    f"""
<div class="main-header">
    <div class="brand-line">
        <span class="brand-mark">HiLegal <span class="accent">× 律镜 LegalReel</span></span>
    </div>
    <div class="main-subtitle">{L('让专业被看到 · 把 LinkedIn 主页变成高转化的法律获客视频', 'Make expertise visible — turn your LinkedIn profile into high-converting legal videos')}</div>
    <div class="main-scope">{L('适用对象：美国、加拿大、澳洲、英国、新加坡等地执业律师及中小律所（1–50 人）｜产品形态：一次性视频制作套餐包（非年付、非会员制），每单独立交付｜价格单位：USD', 'For lawyers & small-mid firms (1-50) in the US, Canada, Australia, UK, Singapore · One-time production packages (no subscription), delivered per order · Prices in USD')}</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 4. 价格对比条
# ==========================================
st.markdown(
    f"""
<div class="price-banner">
    <div class="price-banner-title">{L('十分之一的价格，做得出来的获客视频', 'Acquisition videos at one-tenth the price')}</div>
    <div class="price-banner-row">
        <div>{L('传统律所营销 $2,000–5,000 / 分钟（4–8 周）', 'Traditional agency $2,000-5,000 / min (4-8 weeks)')}</div>
        <div class="vs">VS</div>
        <div>{L('AI 视频承制 $200 / 分钟（人工承制 1–2 周 / 品牌片 3–4 周）', 'AI production $200 / min (1-2 weeks / brand film 3-4 weeks)')}</div>
    </div>
    <div class="price-banner-foot">{L('核心结论：同样的预算，传统渠道只够做 1 条视频，AI 视频承制可以做 10 条。', 'Same budget: one video the old way, ten with AI production.')}</div>
</div>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 5. 视频展示（首页：3 行 × 每行 3 个）
# ==========================================
def render_video_or_fallback(video_path_or_url, title):
    st.markdown(f'<div class="video-title">{title}</div>', unsafe_allow_html=True)
    if is_url(video_path_or_url):
        st.video(video_path_or_url)
    else:
        if not os.path.exists(video_path_or_url):
            st.markdown(
                '<div class="video-placeholder">'
                '<div style="font-size: 1.5rem;">&#127909;</div>'
                f'<div class="video-placeholder-title">{title}</div>'
                f'<div class="video-placeholder-desc">{L("样片即将上线", "Sample coming soon")}</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            mime = VIDEO_MIME_MAP.get(os.path.splitext(str(video_path_or_url))[1].lower(), "video/mp4")
            try:
                st.video(video_path_or_url, format=mime)
            except TypeError:
                st.video(video_path_or_url)
    st.markdown('<div class="video-cell-spacer"></div>', unsafe_allow_html=True)


def render_reserve_card(cat_name, title, card_title, card_desc):
    st.markdown(f'<div class="video-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="reserve-card">'
        f'<div class="reserve-card-title">{card_title}</div>'
        f'<div class="reserve-card-desc">{card_desc}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if st.button(L("✨ 选择此风格", "✨ Select style"), key=f"btn_{cat_name}"):
        st.session_state.selected_category = cat_name
        st.session_state.trigger_scroll = True


def section_header(eyebrow, title):
    st.markdown(
        f'<div class="eyebrow">{eyebrow}</div><div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )


# --- 第一行：电影品质视频 ---
section_header(L('作品集 · 01', 'Showreel · 01'), L('电影品质视频', 'Cinematic-Quality Videos'))
r1 = st.columns(3)
with r1[0]:
    render_video_or_fallback(LOCAL_VIDEO_3, L("大法官的人生", "A Justice Life"))
with r1[1]:
    render_video_or_fallback(LOCAL_VIDEO_4, L("AI 律师的职业路", "An AI Lawyer Career"))
with r1[2]:
    render_reserve_card(
        "cinematic", L("你的品牌大片", "Your Brand Film"),
        L("电影级品牌片", "Cinematic Brand Film"),
        L("定制导演 + 实拍与 AI 混合，90 秒呈现律所品牌与招聘形象。", "Custom director, live + AI blend, a 90s brand & recruiting film."),
    )

# --- 第二行：承接制作视频 ---
section_header(L('作品集 · 02', 'Showreel · 02'), L('承接制作视频', 'Hand-Produced Videos'))
r2 = st.columns(3)
with r2[0]:
    render_video_or_fallback(LOCAL_VIDEO_1, L("街头访谈实录", "Street Interviews"))
with r2[1]:
    render_video_or_fallback(LOCAL_VIDEO_2, L("年轻律师的一天", "A Young Lawyer Day"))
with r2[2]:
    render_reserve_card(
        "produced", L("你的执业介绍", "Your Practice Intro"),
        L("人工承制短视频", "Hand-Produced Short"),
        L("律师仅需照片与语音素材，脚本由模板库起草、律师确认，全流程线上完成。", "Just photos & voice; scripts drafted then lawyer-approved, fully online."),
    )

# --- 第三行：访谈视频 ---
section_header(L('作品集 · 03', 'Showreel · 03'), L('访谈视频', 'Interview Videos'))
r3 = st.columns(3)
with r3[0]:
    render_video_or_fallback(LOCAL_VIDEO_5, L("为什么你需要公司法律师", "Why You Need a Corporate Lawyer"))
with r3[1]:
    render_video_or_fallback(LOCAL_VIDEO_6, L("在美国注册公司全流程", "Setting Up a US Company"))
with r3[2]:
    render_reserve_card(
        "interview", L("你的深度访谈", "Your Deep-Dive Interview"),
        L("真人出镜访谈", "On-Camera Interview"),
        L("10–20 分钟深度对谈，体系化呈现执业领域与专业观点。", "A 10-20 min on-camera dialogue systematizing your practice & views."),
    )

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. 为什么律师需要这个服务
# ==========================================
section_header(L('为什么选择我们', 'Why This Service'), L('为什么律师需要这个服务', 'Why Lawyers Need This'))
st.markdown(
    f"""
<div class="card">
    <div class="pain-sub">{L('1.1 价格痛点：十分之一的价格', '1.1 Price: one-tenth the cost')}</div>
    <ul><li>{L('传统律所营销制作 USD 2,000–5,000 / 分钟，交付 4–8 周；AI 视频承制 USD 200 / 分钟，人工承制 1–2 周、电影级品牌片 3–4 周。', 'Traditional production runs USD 2,000-5,000 / min in 4-8 weeks; AI production USD 200 / min — 1-2 weeks hand-produced, 3-4 weeks cinematic.')}</li></ul>
    <div class="pain-sub">{L('1.2 出镜痛点：律师晕镜头', '1.2 On-camera: nerves & no time')}</div>
    <ul>
        <li>{L('一面对镜头就紧张——语速失控、表情僵硬、眼神躲闪；', 'Nervous on camera — pace, expression and eye contact break down;')}</li>
        <li>{L('没时间拍：办案日程满，无法配合拍摄档期；', 'No time — a packed caseload leaves no room to fit a shoot;')}</li>
        <li>{L('不知道说什么：专业内容强，但不知如何转成 60 秒口播；', 'Unclear scripting — strong expertise, hard to compress into 60s;')}</li>
        <li>{L('不想外包：外包剪辑 USD 150–300/条，仍要自己出镜写稿。', 'Outsourcing costs USD 150-300/clip and still needs you on camera.')}</li>
    </ul>
    <div class="solution-box"><b>{L('本方案的解法：', 'Our solution: ')}</b>{L('套餐 A / B（AI 生成视频）——律师只需提供照片和语音素材，脚本由法律内容模板库起草、律师确认，一切线上完成；套餐 C（真人出镜拍摄）——由专业团队访谈拍摄，深度内容一步到位。', 'Packages A/B (AI-generated) — you only provide photos & voice; scripts drafted from a legal template library then lawyer-approved, all online. Package C (on-camera) — a professional team shoots the interview for in-depth content.')}</div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 7. HiLegal 套餐选择
# ==========================================
def render_package_card(key):
    p = PACKAGES[key]
    bullets = "".join(f"<li>{pt}</li>" for pt in p["points"])
    cls = "package-card flag" if p["flag"] else "package-card"
    st.markdown(
        f"""
    <div class="{cls}">
        <div class="package-name">{p['name']}</div>
        <div class="package-price">{p['price']}<span> {L(' 一次性', ' one-time')}</span><span class="package-origin">{p['origin']}</span></div>
        <div class="package-mode">{p['mode']}</div>
        <div class="package-tag">{p['tag']}</div>
        <ul class="package-points">{bullets}</ul>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button(L("✅ 选择此套餐", "✅ Select package"), key=f"pkg_{key}"):
        st.session_state.selected_package = f"{p['name']} {p['price']}"
        st.session_state.trigger_scroll = True


section_header(L('价格与权益', 'Packages & Pricing'), L('HiLegal 视频制作套餐', 'HiLegal Video Packages'))
pkg_cols = st.columns(3)
for i, k in enumerate(PKG_KEYS):
    with pkg_cols[i]:
        render_package_card(k)

# ==========================================
# 8. 附赠权益
# ==========================================
section_header(L('附赠权益', 'Included Perks'), L('附赠：HiLegal 平台一年展位', 'Included: 1-Year HiLegal Listing'))
st.markdown(
    f"""
<div class="card">
    <ul>
        <li><b>{L('1. 视频自行发表：', '1. Self-publish: ')}</b>{L('制作的视频可直接发布在 HiLegal 平台律师主页，自主掌控发布节奏。', 'Publish videos directly on your HiLegal lawyer page at your own cadence.')}</li>
        <li><b>{L('2. 跨境 AI 工具：', '2. Cross-border AI tools: ')}</b>{L('使用平台提供的跨境法律 AI 工具，辅助跨境业务咨询与客户沟通。', 'Use platform cross-border legal AI for consultations and client communication.')}</li>
        <li><b>{L('3. 中国出海企业关注：', '3. China outbound visibility: ')}</b>{L('展位律师直接进入中国出海企业的选聘视野——视频内容即简历，展位即店面。', 'Listed lawyers enter the selection view of Chinese outbound firms — your video is your resume, the listing is your storefront.')}</li>
    </ul>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 9. 增值费用表 + 制作流程
# ==========================================
def render_value_added_table():
    rows = "".join(
        f"<tr><td>{item}</td><td style='white-space: nowrap;'>{fee}</td></tr>" for item, fee in VALUE_ADDED_TABLE
    )
    st.markdown(
        f"""
    <div class="data-table">
        <table>
            <thead><tr><th>{L('增值项', 'Add-on')}</th><th style="width: 34%;">{L('费用规则', 'Pricing Rule')}</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )


def render_flow_table():
    steps = [
        (L("选题策略", "Topic Strategy"), L("认识律师、确定目标、运营定选题", "Know the lawyer, set goals, pick topics")),
        (L("脚本撰写", "Script Writing"), L("法律素材库 / 爆款模板起草初稿，律师审核", "Drafted from a legal template library, lawyer-reviewed")),
        (L("分镜拆解", "Storyboard"), L("脚本 → 分镜全自动", "Script to storyboard, fully automated")),
        (L("画面生成", "Visual Generation"), L("AI 出镜头，人工选镜头、补特写", "AI shots, human-selected with extra close-ups")),
        (L("配音配乐", "Voice & Music"), L("多语言配音 + AI 配乐，人耳抽检", "Multilingual voiceover + AI music, human QC")),
        (L("剪辑合成", "Editing"), L("人工精修节奏、字幕、品牌露出", "Human polish of pacing, subtitles, branding")),
        (L("发布支持", "Publishing"), L("视频交付律师，支持发布至 HiLegal 展位", "Delivered to the lawyer, publishable to the HiLegal listing")),
    ]
    rows = "".join(
        f"<tr><td class='flow-step'>{i + 1}. {s}</td><td>{d}</td></tr>" for i, (s, d) in enumerate(steps)
    )
    st.markdown(
        f"""
    <div class="data-table">
        <table>
            <thead><tr><th style="width: 26%;">{L('环节', 'Step')}</th><th>{L('任务', 'Task')}</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )


section_header(L('加购选项', 'Add-ons'), L('增值费用表', 'Value-Added Pricing'))
render_value_added_table()

section_header(L('如何交付', 'How It Works'), L('制作流程（AI 视频制作）', 'Production Flow'))
render_flow_table()
st.markdown(
    f"""
<div class="notice-box">
    {L('交付时效：人工承制 1–2 周（含 1 轮免费修改）；电影级品牌片 3–4 周（含 3 轮免费修改）；套餐 C 真人访谈 4–6 周（含 1 轮免费修改）。',
       'Delivery: hand-produced 1-2 weeks (1 free revision); cinematic brand film 3-4 weeks (3 free revisions); Package C interview 4-6 weeks (1 free revision).')}
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("<br><hr style='margin: 1.5rem 0;'><br>", unsafe_allow_html=True)

# ==========================================
# 10. 表单
# ==========================================
st.markdown('<div id="generate-form"></div>', unsafe_allow_html=True)
section_header(L('立即开始', 'Get Started'), L('生成你的定制视频', 'Generate Your Personalized Video'))

if st.session_state.selected_category or st.session_state.selected_package:
    cat = st.session_state.selected_category or L("未指定风格", "No style")
    pkg = st.session_state.selected_package or L("未选择套餐", "No package")
    st.markdown(
        f"""
    <div class="active-selection-banner">
        <h4>{L('已选风格', 'Selected style')}: <b>{cat}</b> ｜ {L('套餐', 'Package')}: <b>{pkg}</b></h4>
        <p style="margin: 0; color: #4A5568; font-size: .9rem;">
            {L('请在下方填写你的 LinkedIn 主页与邮箱，我们会按此营销目标为你定制视频！',
               'Enter your LinkedIn profile and email below — your video will be tailored to this objective!')}
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.info(L("💡 点击上方任一「选择风格」或「选择套餐」按钮，或直接填写表单！",
              "💡 Click any Select style / Select package button above, or fill out the form directly!"))

pkg_options = [L("— 暂不选择 —", "— No package yet —")] + [f"{PACKAGES[k]['name']} {PACKAGES[k]['price']}" for k in PKG_KEYS]

with st.form(key="video_request_form"):
    linkedin_url = st.text_input("LinkedIn Profile URL", placeholder="https://www.linkedin.com/in/your-profile")
    email = st.text_input(L("接收视频的邮箱", "Email address to receive video"), placeholder="yourname@example.com")
    package_sel = st.selectbox(L("选择套餐", "Select package"), pkg_options)
    st.markdown(
        f"""
    <div class="notice-box">
        <b>{L('适用说明 / Notes & Terms:', 'Notes & Terms:')}</b><br>
        {L('1. 本方案为一次性视频制作套餐包，一次购买、按单交付，不涉及年付或会员制；<br>',
           '1. One-time production packages, delivered per order — no subscription;<br>')}
        {L('2. 套餐 A 与 B 为 AI 生成视频，套餐 C 为真人出镜拍摄；<br>',
           '2. Packages A/B are AI-generated; Package C is an on-camera shoot;<br>')}
        {L('3. 套餐 A / B 原价 USD 990 / 2,990，折后 USD 590 / 1,990；套餐 C 为 USD 1,990；单条原价 USD 250（≤60 秒）；<br>',
           '3. A/B were USD 990 / 2,990, now USD 590 / 1,990; C is USD 1,990; a single clip is USD 250 (≤60s);<br>')}
        {L('4. 三个套餐均不提供数字分身，真人形象以实际拍摄素材为准；<br>',
           '4. No digital clones; likenesses reflect actual footage;<br>')}
        {L('5. 语言权益为第二语言字幕（每条 1 种），更多语言按增值表加购；<br>',
           '5. Each video includes 1 second-language subtitle; extra languages per the add-on table;<br>')}
        {L('6. 免费样片试做仅面向 HiLegal 会员且仅限套餐 A / B，每律师限一次；<br>',
           '6. Free sample trial is HiLegal-members only and limited to A/B, once per lawyer;<br>')}
        {L('7. 超额承制价 USD 150/分钟对 A、B 一致（原价 USD 250/分钟），一年内有效；<br>',
           '7. Extra footage USD 150/min applies equally to A/B (was USD 250), valid one year;<br>')}
        {L('8. 交付周期：人工承制 1–2 周；品牌片 3–4 周；套餐 C 访谈 4–6 周；<br>',
           '8. Delivery: 1-2 weeks hand-produced; 3-4 weeks brand film; 4-6 weeks Package C;<br>')}
        {L('9. AI 生成素材权属写入合同，交付后归律师本人及律所所有；提交即同意样片用于本站展示。',
           '9. AI asset ownership is in the contract and vests in the lawyer/firm; submitting consents to on-site sample display.')}
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    submit_button = st.form_submit_button(label=L("提交需求 / Submit Request", "Submit Request"))

if submit_button:
    if not linkedin_url or not email:
        st.error(L("请完整填写 LinkedIn 链接与邮箱！", "Please complete both the LinkedIn URL and Email fields!"))
    elif "linkedin.com/in/" not in linkedin_url.lower():
        st.warning(L("请输入有效的 LinkedIn 主页链接（如 https://www.linkedin.com/in/xxx）",
                     "Please enter a valid LinkedIn profile link (e.g. https://www.linkedin.com/in/xxx)"))
    elif "@" not in email:
        st.warning(L("请输入有效的邮箱地址！", "Please enter a valid email address!"))
    else:
        chosen_cat = st.session_state.selected_category or "General Showcase"
        chosen_pkg = package_sel if package_sel != pkg_options[0] else (st.session_state.selected_package or "General Showcase")
        mail_subject = "HiLegal 新视频需求提交 / New Lawyer Video Request"
        mail_body = (
            "A new user has submitted a video request!\n\n"
            f"Selected Style: {chosen_cat}\n"
            f"Selected Package: {chosen_pkg}\n\n"
            f"LinkedIn Profile: {linkedin_url}\n"
            f"User Email: {email}\n"
        )
        with st.spinner(L("正在提交你的需求...", "Submitting your request...")):
            success, err_msg = send_email_notification(mail_subject, mail_body)
        if success:
            st.success(L("✅ 提交成功！", "✅ Submitted Successfully!"))
            st.info(
                f"{L('我们已收到你的需求', 'We received your request')} ({chosen_pkg}). "
                f"{L('定制视频将在 1–2 周内发送至', 'Your custom video will be delivered to')} {email}."
            )
        else:
            st.error(f"{L('⚠️ 通知发送失败：', '⚠️ Failed to send notification: ')}{err_msg}")

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
# 11. Footer
# ==========================================
st.markdown(
    f"""
<div class="footer">
    © 2026 HiLegal × 律镜 LegalReel · {L('商务垂询', 'Business enquiries')} dengxiaotong@fadada.com ｜ {L('美国 · 加拿大 · 澳洲 · 英国 · 新加坡', 'US · Canada · Australia · UK · Singapore')}<br>
    Daily Unique Visitors (UV): <span class="uv-badge">{current_daily_uv}</span>
    <div class="footer-disclaimer">{L('免责声明：本方案为商业演示稿，最终价格与条款以正式服务协议为准。',
                                       'Disclaimer: This is a business demo; final pricing and terms are governed by the formal service agreement.')}</div>
</div>
""",
    unsafe_allow_html=True,
)
