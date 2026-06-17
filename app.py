pythonimport streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import math
import os
from datetime import datetime

def load_font(size):
    candidates = [
        "fonts/NotoSansKR-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    st.warning("CJK 폰트를 못 찾았어요. 글자가 작게 나옵니다.")
    return ImageFont.load_default()

st.set_page_config(page_title="인형 프로필 콜라주 메이커", layout="wide")
st.title("🦋 인형 프로필 콜라주 메이커")
st.caption("SD/BJD 인형 사진 → 예쁜 콜라주 JPG")

# ==================== 사이드바 옵션 ====================
with st.sidebar:
    st.header("⚙️ 설정")
   
    cols_per_row = st.slider("한 줄에 몇 장?", 1, 10, 3)
    scale_factor = st.slider("사진 & 전체 해상도 배율", 1.0, 4.0, 2.0, 0.1)
   
    bg_color = st.color_picker("배경색", "#1E1E1E")
    border_color = st.color_picker("테두리 색상", "#E0E0E0")
    border_width = st.slider("테두리 두께 (px)", 0, 30, 10)
   
    padding = st.slider("사진 사이 여백 (px)", 0, 80, 30)
   
    # 이름 설정 (독립적으로 크게)
    name_font_size_base = st.slider("이름 글자 크기", 80, 800, 320, 10)
    name_color = st.color_picker("이름 색상", "#FFFFFF")
    name_y_offset = st.slider("이름 위치 (아래로)", 0, 150, 45)
   
    title_text = st.text_input("전체 제목", "Haemin's Doll Collection")
    title_size = st.slider("전체 제목 글자 크기", 40, 250, 100)
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
            default_name = file.name.split('.')[0][:30]
            name = st.text_input(f"사진 {idx+1}", value=default_name, key=f"name_{idx}")
            names.append(name)
   
    if st.button("🎨 콜라주 생성하기", type="primary", use_container_width=True):
        with st.spinner("콜라주 만드는 중... 조금만 기다려~"):
            images = [Image.open(file).convert("RGB") for file in uploaded_files]
           
            # 사진 크기 (scale_factor로만 조절)
            final_thumb = int(220 * scale_factor)   # 기본 사진 크기 좀 더 크게 조정
            thumbs = []
            for img in images:
                img = ImageOps.fit(img, (final_thumb, final_thumb), method=Image.Resampling.LANCZOS)
                if border_width > 0:
                    img = ImageOps.expand(img, border=border_width, fill=border_color)
                thumbs.append(img)
           
            n = len(thumbs)
            rows = math.ceil(n / cols_per_row)
            cell_size = final_thumb + border_width * 2   # 사진+테두리 크기
            
            # 이름 폰트 크기 (scale_factor 반영)
            name_font_size = int(name_font_size_base * scale_factor * 0.95)
           
            # === 높이 계산 개선 ===
            name_area_height = name_font_size + name_y_offset + 80
            cell_height = cell_size + name_area_height
            total_width = cols_per_row * (cell_size + padding) - padding
            total_height = rows * (cell_height + padding) - padding + title_size + 220
           
            collage = Image.new('RGB', (total_width, total_height), color=bg_color)
            draw = ImageDraw.Draw(collage)
           
            name_font = load_font(name_font_size)
            title_font = load_font(title_size)
           
            for idx, (thumb, name) in enumerate(zip(thumbs, names)):
                row = idx // cols_per_row
                col = idx % cols_per_row
                
                x = col * (cell_size + padding)
                y = row * (cell_height + padding)
               
                # 사진 붙이기
                collage.paste(thumb, (x, y))
               
                # 이름 텍스트 (정확한 중앙 정렬)
                text_bbox = draw.textbbox((0, 0), name, font=name_font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x + (cell_size - text_width) // 2
                text_y = y + cell_size + name_y_offset
                
                draw.text((text_x, text_y), name, fill=name_color, font=name_font)
           
            # 전체 제목
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_w = title_bbox[2] - title_bbox[0]
            title_x = (total_width - title_w) // 2
            title_y = total_height - title_size - 100
            draw.text((title_x, title_y), title_text, fill=title_color, font=title_font)
           
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
