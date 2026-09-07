import streamlit as st
import pandas as pd
#from pyvis.network import Network
import io
from datetime import datetime
import streamlit.components.v1 as components
import os  # 新增：导入os模块用于路径处理


# -------------------------- 右上角功能区 --------------------------

st.markdown("""
<style>

    /* 隐藏右上角的 Streamlit 主菜单（包含部署、源码、设置等） */
    #MainMenu {visibility: hidden;}
    /* 隐藏页脚（包含 "Made with Streamlit" 文字） */
    footer {visibility: hidden;}
    /* 隐藏顶部的 header（包含部署按钮） */
    header[data-testid="stHeader"] {display: none;}
    
    /* 2. HTML 链接按钮 (Get New Apps) */
    .neal-btn {
        font-family: 'Inter', sans-serif;
        background: #fff;
        border: 1px solid #e5e7eb;
        color: #111;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        text-decoration: none !important;
        width: 100%;
        height: 38px; /* 强制与 st.button 高度对齐 */
    }
    .neal-btn:hover {
        background: #f9fafb;
        border-color: #111;
        transform: translateY(-1px);
    }
    .neal-btn-link { text-decoration: none; width: 100%; display: block; }
</style>
""", unsafe_allow_html=True)


# 创建右上角布局（占满整行，右侧显示按钮/链接）
col_empty, col_more = st.columns([0.7, 0.1])

with col_more:
    # 修复：改用 HTML 链接按钮（替代 webbrowser 方式，兼容 Streamlit 云环境）
    st.markdown(
        f"""
        <a href="https://haowan.streamlit.app/" target="_blank" class="neal-btn-link">
            <button class="neal-btn">✨ 更多好玩应用</button>
        </a>
        """, 
        unsafe_allow_html=True
    )

# ==============================================================================
# 0. 全局配置 & 颜色定义
# ==============================================================================

st.set_page_config(layout="wide", page_title="国资持股企业拓扑图", page_icon="📊")

# 行业颜色映射表
FIELD_COLORS = {
    '新能源/汽车': '#1E88E5',        # 亮蓝色
    '电子信息产业': '#9C27B0',      # 深紫色
    '科技硬件/制造': '#FF9800',      # 橙色
    '医药/生物': '#E91E63',          # 玫红色
    '大消费/零售': '#4CAF50',        # 绿色
    'TMT/金融': '#00BCD4',           # 青色
    '化工新材料': '#795548',         # 棕色
    '其他': '#9E9E9E'               # 灰色
}

# 国资股东专用颜色
SHAREHOLDER_COLOR = '#D32F2F'    # 红色背景
SHAREHOLDER_BORDER = '#FFEB3B'   # 黄色边框

# 定义默认文件路径（新增核心配置）
default_file_path = os.path.expanduser("国资.xlsx")  # ~代表当前用户家目录

# ==============================================================================
# 1. 核心功能函数
# ==============================================================================

def load_data_from_file(uploaded_file=None):
    """加载并清洗数据：优先上传文件，无则读取默认路径文件"""
    try:
        # 优先使用用户上传的文件
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            #st.success(f"✅ 成功加载上传文件：{uploaded_file.name}")
        # 无上传文件时，尝试读取默认路径文件
        elif os.path.exists(default_file_path):
            df = pd.read_excel(default_file_path)
            #st.success(f"✅ 成功加载默认文件：{default_file_path}")
        # 两者都无则返回None
        else:
            st.warning(f"⚠️ 未检测到上传文件，且默认路径文件不存在：{default_file_path}")
            return None
        
        # 列名映射
        column_mapping = {
            '企业名称': '公司名称', 
            '市值(亿)': '市值 (亿元)', 
            '核心领域': '核心领域',
            '一级领域': '核心领域',
            '国资股东': '国资股东名称 (单列)', 
            '持股比(%)': '单一持股比', 
            '持股比例(%)': '单一持股比',
            '持股价值(亿)': '单一持股价值 (亿元)'
        }
        
        available_cols = set(df.columns)
        rename_dict = {k: v for k, v in column_mapping.items() if k in available_cols}
        df = df.rename(columns=rename_dict)
        
        # 检查必要列
        required_target_cols = ['公司名称', '市值 (亿元)', '核心领域', '国资股东名称 (单列)', '单一持股价值 (亿元)']
        missing_cols = [col for col in required_target_cols if col not in df.columns]
        if missing_cols:
            st.error(f"❌ 数据缺少必要列，需要包含：{required_target_cols}")
            st.info(f"🔍 当前缺失列：{missing_cols}")
            return None

        # 数据清洗
        df = df.fillna('')
        df['市值 (亿元)'] = pd.to_numeric(df['市值 (亿元)'], errors='coerce').fillna(0)
        df['单一持股价值 (亿元)'] = pd.to_numeric(df['单一持股价值 (亿元)'], errors='coerce').fillna(0)
        
        def clean_ratio(x):
            if isinstance(x, str) and '%' in x:
                return float(x.strip('%')) / 100
            return float(x) if isinstance(x, (int, float)) else 0
            
        if '单一持股比' in df.columns:
            df['单一持股比'] = df['单一持股比'].apply(clean_ratio)
        else:
            df['单一持股比'] = 0.0

        return df
    
    except Exception as e:
        st.error(f"❌ 数据加载失败: {str(e)}")
        st.exception(e)  # 打印详细异常信息
        return None

@st.cache_resource
def create_graph(data_frame, max_mc, max_shareholder_value):
    """生成 Pyvis 网络图"""
    net = Network(
        height='800px', 
        width='100%', 
        bgcolor='#000000', 
        font_color='#FFFFFF',
        directed=True
    )
    
    # 物理引擎配置
    options = '''
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -80,
          "centralGravity": 0.01,
          "springLength": 250,
          "springConstant": 0.05,
          "avoidOverlap": 1
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      },
      "nodes": {
        "font": { "size": 16, "color": "#FFFFFF", "strokeWidth": 2, "strokeColor": "#000000", "vadjust": -30 },
        "shadow": true
      },
      "edges": {
        "smooth": { "type": "continuous", "roundness": 0.5 }
      }
    }
    '''
    net.set_options(options)
    
    # 1. 企业节点
    companies = data_frame.drop_duplicates('公司名称')
    for _, row in companies.iterrows():
        company = row['公司名称']
        market_cap = row['市值 (亿元)']
        field = row['核心领域']
        color = FIELD_COLORS.get(field, FIELD_COLORS['其他'])
        
        size = 30
        if max_mc > 0:
            size += (market_cap / max_mc) ** 0.5 * 80
            
        tooltip = f"🏢 企业：{company}<br>🏷 领域：{field}<br>💰 市值：{market_cap:,.0f} 亿"
        
        net.add_node(
            company, label=company, title=tooltip, group=field, color=color,
            size=int(size), shape='dot', borderWidth=1, borderColor='#FFFFFF'
        )
        
    # 2. 股东节点
    shareholder_stats = data_frame.groupby('国资股东名称 (单列)')['单一持股价值 (亿元)'].sum()
    for shareholder, total_value in shareholder_stats.items():
        if not shareholder: continue
        size = 30
        if max_shareholder_value > 0:
            size += (total_value / max_shareholder_value) ** 0.5 * 80
            
        tooltip = f"🏛 股东：{shareholder}<br>💎 持股总额：{total_value:,.1f} 亿"
        label_name = shareholder[:6] + '..' if len(shareholder) > 8 else shareholder
        
        net.add_node(
            shareholder, label=label_name, title=tooltip, group='国资股东',
            color={'background': SHAREHOLDER_COLOR, 'border': SHAREHOLDER_BORDER},
            size=int(size), shape='dot', borderWidth=3
        )
        
    # 3. 连线
    for _, row in data_frame.iterrows():
        src = row['国资股东名称 (单列)']
        dst = row['公司名称']
        val = row['单一持股价值 (亿元)']
        if src and val > 0:
            width = 1 + (val / 10) ** 0.5
            net.add_edge(
                src, dst, title=f"持股价值：{val:,.1f} 亿", width=width,
                color='#FFC107', opacity=0.6
            )
            
    net.save_graph('network.html')
    with open('network.html', 'r', encoding='utf-8') as f:
        return f.read()

def export_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export = df.copy()
        df_export['单一持股比'] = df_export['单一持股比'].apply(lambda x: f"{x:.2%}")
        df_export.to_excel(writer, sheet_name='持股明细', index=False)
        
        field_summ = df.groupby('核心领域').agg({
            '公司名称': 'nunique', 
            '市值 (亿元)': lambda x: x.drop_duplicates().sum(),
            '单一持股价值 (亿元)': 'sum'
        }).reset_index()
        field_summ.columns = ['核心领域', '企业数量', '总市值估算', '国资持股总额']
        field_summ.to_excel(writer, sheet_name='领域汇总', index=False)
    output.seek(0)
    return output

# ==============================================================================
# 2. 界面 UI 布局
# ==============================================================================

# CSS 深度美化 (调整了 legend-box 样式为横向排列)
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #FFFFFF; }
    
    /* 图例容器：改为横向排列，适合放在图表下方 */
    .legend-box {
        background-color: #1a1a1a; 
        padding: 15px 25px; 
        border-radius: 8px; 
        border: 1px solid #333;
        margin-top: 10px;
        margin-bottom: 20px;
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        align-items: center;
    }
    
    /* 图例项 */
    .legend-item { display: flex; align-items: center; font-size: 14px; }
    .legend-dot { 
        width: 12px; height: 12px; border-radius: 50%; 
        margin-right: 8px; border: 1px solid rgba(255,255,255,0.5); 
    }
    
    div[data-testid="stMetric"] {
        background-color: #111; border: 1px solid #333; 
        padding: 10px; border-radius: 5px;
    }
    div[data-testid="stMetric"] label { color: #aaa; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] { color: #fff; }
    .stFileUploader label { color: #fff !important; }
</style>
""", unsafe_allow_html=True)

st.title("🖍️染红：A股民营企业国资持股渗透拓扑图")
st.caption("可视化展示：节点大小代表资金/市值规模 | 连线代表持股关系")
# 新增：显示默认文件路径提示
#st.info(f"📂 默认数据文件路径：{default_file_path}")

# --- 侧边栏 ---
with st.sidebar:
    st.header("📂 数据接入")
    uploaded_file = st.file_uploader("上传Excel数据文件", type=["xlsx", "xls"])
    
    # 优化提示：显示默认文件路径
    if not uploaded_file:
        st.info(f"👋 可直接上传文件，或将数据文件放在：{default_file_path}")

# --- 主逻辑 ---
df = load_data_from_file(uploaded_file)

if df is not None:
    MAX_MC = df['市值 (亿元)'].max()
    MAX_SHARE_VAL = df.groupby('国资股东名称 (单列)')['单一持股价值 (亿元)'].sum().max()

    # 侧边栏仅保留筛选器
    with st.sidebar:
        st.markdown("---")
        st.header("🔍 视图过滤")
        existing_fields = sorted(df['核心领域'].unique())
        selected_fields = st.multiselect("选择显示行业", options=existing_fields, default=existing_fields)
        min_val = st.slider("过滤小额持股 (亿元)", 0, 100, 0)

    # 数据过滤
    filtered_df = df[(df['核心领域'].isin(selected_fields)) & (df['单一持股价值 (亿元)'] >= min_val)]

    # 核心指标
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏢 关联企业", f"{filtered_df['公司名称'].nunique()} 家")
    c2.metric("🏛 国资机构", f"{filtered_df['国资股东名称 (单列)'].nunique()} 家")
    c3.metric("💰 涉及持股总值", f"{filtered_df['单一持股价值 (亿元)'].sum():,.0f} 亿")
    c4.metric("📊 当前节点数", len(filtered_df))

    # 图表渲染
    if not filtered_df.empty:
        try:
            html_source = create_graph(filtered_df, MAX_MC, MAX_SHARE_VAL)
            # 渲染图表
            components.html(html_source, height=800, scrolling=False)
            
            # === 新增位置：在图表下方渲染横向图例 ===
            legend_html = '<div class="legend-box">'
            # 1. 特殊图例：国资股东
            legend_html += f"""
            <div class="legend-item" style="border-right: 1px solid #444; padding-right: 20px; margin-right: 10px;">
                <span style="color: #ffcccc; font-weight: bold;">🔴 国资股东 (红色)</span>
                <span style="font-size: 12px; color: #888; margin-left: 5px;">(大小=持股总额)</span>
            </div>
            """
            # 2. 行业颜色图例
            for field in existing_fields:
                color = FIELD_COLORS.get(field, FIELD_COLORS['其他'])
                legend_html += f"""
<div class="legend-item">
    <div class="legend-dot" style="background-color: {color};"></div>
    <span style="color: #ddd;">{field}</span>
</div>
                """
            legend_html += '</div>'
            st.markdown(legend_html, unsafe_allow_html=True)
            # ========================================

        except Exception as e:
            st.error(f"图表生成错误: {e}")
            st.exception(e)
    else:
        st.warning("⚠️ 当前筛选条件下无数据，请调整筛选器。")

    # 数据导出区
    st.markdown("---")
    col_dl, col_view = st.columns([1, 4])
    with col_dl:
        excel_data = export_to_excel(filtered_df)
        st.download_button(
            label="📥 导出筛选结果 (Excel)",
            data=excel_data,
            file_name=f"国资持股分析_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with col_view:
        with st.expander("查看原始数据明细"):
            st.dataframe(filtered_df, use_container_width=True)

else:
    st.markdown(f"""
    <div style="text-align: center; padding: 50px; color: #666;">
        <h3>👈 请在左侧上传数据文件，或将数据文件放在以下路径：</h3>
        <p style="font-size: 16px; margin-top: 20px;">{default_file_path}</p>
    </div>
    """, unsafe_allow_html=True)
