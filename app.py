import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import math
from datetime import datetime

st.set_page_config(page_title="인형 프로필 콜라주 메이커", layout="wide")
st.title("🦋 인형 프로필 콜라주 메이커")
st.caption("SD/BJD 인형 사진 → 예쁜 콜라주 JPG")

# ==================== 사이드바 옵션 ====================
with st.sidebar:
    st.header("⚙️ 설정")
    
    cols_per_row = st.slider("한 줄에 몇 장?", 1, 10, 3)   # 3000 크기라 3~4 추천
    scale_factor = st.slider("최종 해상도 배율", 1.0, 3.0, 1.8, 0.1)
    
    bg_color = st.color_picker("배경색", "#1E1E1E")
    border_color = st.color_picker("테두리 색상", "#E0E0E0")
    border_width = st.slider("테두리 두께 (px)", 0, 25, 8)
    
    padding = st.slider("사진 사이 여백 (px)", 0, 60, 20)
    
    # 이름 관련 (고정)
    name_font_size = 3000          # 완전 고정
    name_color = st.color_picker("이름 색상", "#FFFFFF")
    name_y_offset = st.slider("이름 위치 (아래로)", 0, 5, 2)
    
    title_text = st.text_input("전체 제목", "Haemin's Doll Collection")
    title_size = st.slider("전체 제목 글자 크기", 30, 200, 80)
    title_color = st.color_picker("제목 색상", "#FFFFFF")

# ==================== 메인 ====================
uploaded_files = st.file_uploader(
    "인형 사진 여러 장 업로드", 
    type=["jpg", "png", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.subheader("📝 각 인형 이름 입력")
    names = []
    cols = st.columns(min(4, len(uploaded_files)))
    
    for idx, file in enumerate(uploaded_files):
        with cols[idx % len(cols)]:
            default_name = file.name.split('.')[0][:25]
            name = st.text_input(f"사진 {idx+1}", value=default_name, key=f"name_{idx}")
            names.append(name)
    
    if st.button("🎨 콜라주 생성하기", type="primary", use_container_width=True):
        with st.spinner("콜라주 만드는 중... (글자가 매우 커서 시간이 좀 걸려요)"):
            images = [Image.open(file).convert("RGB") for file in uploaded_files]
            
            final_thumb = int(150 * scale_factor)   # 사진 기본 크기 150 고정
            thumbs = []
            for img in images:
                img = ImageOps.fit(img, (final_thumb, final_thumb), method=Image.Resampling.LANCZOS)
                if border_width > 0:
                    img = ImageOps.expand(img, border=border_width, fill=border_color)
                thumbs.append(img)
            
            n = len(thumbs)
            rows = math.ceil(n / cols_per_row)
            cell_size = final_thumb + border_width * 2
            
            # 이름 크기가 3000이라 높이 대폭 증가
            total_width = cols_per_row * (cell_size + padding) - padding
            total_height = rows * (cell_size + padding) + 800 + (name_font_size // 2)
            
            collage = Image.new('RGB', (total_width, total_height), color=bg_color)
            draw = ImageDraw.Draw(collage)
            
            try:
                name_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", name_font_size)
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", title_size)
            except:
                name_font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            for idx, (thumb, name) in enumerate(zip(thumbs, names)):
                row = idx // cols_per_row
                col = idx % cols_per_row
                x = col * (cell_size + padding)
                y = row * (cell_size + padding)
                
                collage.paste(thumb, (x, y))
                
                text_width = draw.textlength(name, font=name_font)
                text_x = x + (cell_size - text_width) // 2
                text_y = y + cell_size + name_y_offset
                
                draw.text((text_x, text_y), name, fill=name_color, font=name_font)
            
            # 전체 제목
            title_w = draw.textlength(title_text, font=title_font)
            draw.text(((total_width - title_w)/2, total_height - 180), 
                     title_text, fill=title_color, font=title_font)
            
            st.image(collage, caption="✅ 완성!", use_column_width=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"doll_collage_{timestamp}.jpg"
            collage.save(filename, quality=95, optimize=True)
            
            with open(filename, "rb") as f:
                st.download_button(
                    label="📥 JPG 다운로드",
                    data=f,
                    file_name=filename,
                    mime="image/jpeg"
                )
