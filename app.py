import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math

st.title("인형 프로필 콜라주 메이커 🦋")

# 업로드
uploaded_files = st.file_uploader("인형 사진 여러 장 업로드 (jpg/png)", 
                                  type=["jpg", "png"], accept_multiple_files=True)

cols_per_row = st.slider("한 줄에 몇 장?", 1, 6, 3)
bg_color = st.color_picker("배경색 선택", "#000000")
name_text = st.text_input("아래에 넣을 이름/타이틀", "Haemin's Dolls")

if uploaded_files and st.button("콜라주 만들기"):
    images = [Image.open(file) for file in uploaded_files]
    
    # 모든 사진 같은 크기로 리사이즈 (예: 300x300)
    thumb_size = (300, 300)
    thumbs = []
    for im in images:
        im.thumbnail(thumb_size, Image.Resampling.LANCZOS)
        thumbs.append(im)
    
    # 그리드 계산
    n = len(thumbs)
    rows = math.ceil(n / cols_per_row)
    total_width = cols_per_row * thumb_size[0]
    total_height = rows * thumb_size[1] + 100  # 텍스트 공간
    
    # 새 이미지 + 배경색
    collage = Image.new('RGB', (total_width, total_height), color=bg_color)
    
    # 사진 붙이기
    for idx, thumb in enumerate(thumbs):
        x = (idx % cols_per_row) * thumb_size[0]
        y = (idx // cols_per_row) * thumb_size[1]
        collage.paste(thumb, (x, y))
    
    # 텍스트 추가
    draw = ImageDraw.Draw(collage)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 40)  # 일본/한글 지원
    except:
        font = ImageFont.load_default()
    text_width = draw.textlength(name_text, font=font)
    draw.text(((total_width - text_width)/2, total_height - 80), 
              name_text, fill="white", font=font)
    
    # 결과 표시 + 다운로드
    st.image(collage, caption="완성!", use_column_width=True)
    collage.save("collage.jpg")
    with open("collage.jpg", "rb") as f:
        st.download_button("JPG 다운로드", f, "doll_collage.jpg", "image/jpeg")
