import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import math
from datetime import datetime

st.set_page_config(page_title="인형 프로필 콜라주 메이커", layout="wide")
st.title("🦋 인형 프로필 콜라주 메이커")
st.caption("SD/BJD 인형 사진 여러 장 → 예쁜 콜라주 JPG")

# ==================== 사이드바 옵션 ====================
with st.sidebar:
    st.header("설정")
    cols_per_row = st.slider("한 줄에 몇 장?", 1, 6, 3)
    thumb_size = st.slider("사진 기본 크기 (px)", 200, 500, 300)
    scale_factor = st.slider("최종 해상도 배율", 1.0, 3.0, 1.5, 0.1)
    
    bg_color = st.color_picker("배경색", "#1E1E1E")
    border_color = st.color_picker("테두리 색상", "#FFFFFF")
    border_width = st.slider("테두리 두께 (px)", 0, 20, 8)
    
    padding = st.slider("사진 사이 여백 (px)", 0, 50, 15)
    
    title_text = st.text_input("전체 제목 (아래쪽)", "Haemin's Doll Collection")
    title_size = st.slider("제목 글자 크기", 20, 80, 45)
    title_color = st.color_picker("제목 색상", "#FFFFFF")

# ==================== 메인 ====================
uploaded_files = st.file_uploader(
    "인형 사진 여러 장 업로드 (jpg, png)", 
    type=["jpg", "png", "jpeg"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 각 사진별 이름 입력
    st.subheader("📝 각 인형 이름 입력")
    names = []
    cols = st.columns(min(3, len(uploaded_files)))
    
    for idx, file in enumerate(uploaded_files):
        with cols[idx % len(cols)]:
            default_name = file.name.split('.')[0][:20]  # 파일명에서 자동 추출
            name = st.text_input(f"사진 {idx+1}", value=default_name, key=f"name_{idx}")
            names.append(name)
    
    if st.button("🎨 콜라주 생성하기", type="primary"):
        with st.spinner("콜라주 만드는 중..."):
            images = []
            for file in uploaded_files:
                img = Image.open(file).convert("RGB")
                images.append(img)
            
            # 리사이즈 & 정사각형 크롭
            final_thumb = int(thumb_size * scale_factor)
            thumbs = []
            for img in images:
                # 정사각형 크롭
                img = ImageOps.fit(img, (final_thumb, final_thumb), method=Image.Resampling.LANCZOS)
                
                # 테두리 추가
                if border_width > 0:
                    img = ImageOps.expand(img, border=border_width, fill=border_color)
                
                thumbs.append(img)
            
            # 그리드 계산
            n = len(thumbs)
            rows = math.ceil(n / cols_per_row)
            cell_size = final_thumb + border_width * 2
            total_width = cols_per_row * (cell_size + padding) - padding
            total_height = rows * (cell_size + padding) + 150  # 제목 공간
            
            # 새 이미지 생성
            collage = Image.new('RGB', (total_width, total_height), color=bg_color)
            draw = ImageDraw.Draw(collage)
            
            # 폰트 (한글/일본어 지원)
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 28)
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", title_size)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            # 사진 + 이름 배치
            for idx, (thumb, name) in enumerate(zip(thumbs, names)):
                row = idx // cols_per_row
                col = idx % cols_per_row
                
                x = col * (cell_size + padding)
                y = row * (cell_size + padding)
                
                collage.paste(thumb, (x, y))
                
                # 이름 텍스트
                text_x = x + (cell_size - draw.textlength(name, font=font)) // 2
                text_y = y + cell_size + 5
                draw.text((text_x, text_y), name, fill=title_color, font=font)
            
            # 전체 제목
            title_w = draw.textlength(title_text, font=title_font)
            draw.text(((total_width - title_w)/2, total_height - 90), 
                     title_text, fill=title_color, font=title_font)
            
            # 결과 표시
            st.image(collage, caption="완성된 콜라주", use_column_width=True)
            
            # 다운로드
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"doll_collage_{timestamp}.jpg"
            collage.save(filename, quality=95)
            
            with open(filename, "rb") as f:
                st.download_button(
                    label="📥 JPG 다운로드",
                    data=f,
                    file_name=filename,
                    mime="image/jpeg"
                )
