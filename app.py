import requests
import streamlit as st
from PIL import Image

from apis import call_video_generation_api

# 设置页面标题
st.set_page_config(
    page_title="Veo2-AI视频生成器",
    layout='wide',
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': '# Veo2-AI视频生成器\n这是一个AI视频生成应用。'

    }
)

# 应用标题
st.title("Veo2-AI视频生成器")
st.markdown("---")

# 创建侧边栏用于选择生成模式
with st.sidebar:
    st.header("生成模式")
    generation_mode = st.radio("选择生成模式", ["文生视频", "图生视频"])

# 主界面
st.header(f"当前模式: {generation_mode}")


# 创建表单
with st.form(key="video_generation_form"):
    # 参数选择部分 - 对两种模式都会显示
    st.subheader("参数设置")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        param1 = st.selectbox(
            "视频比例",
            ["16:9", "9:16"],
            index=1
        )

    with col2:
        param2 = st.selectbox(
            "视频数量",
            [1, 4],
            index=0
        )

    with col3:
        param3 = st.selectbox(
            "视频时长（单位/秒）",
            [5, 6, 7, 8],
            index=3
        )

    with col4:
        param4 = st.selectbox(
            "人物生成",
            ['dont_allow', 'allow_adult'],
            index=1
        )

    # 根据选择的模式显示不同的输入方式
    if generation_mode == "文生视频":
        st.subheader("输入提示文本")
        prompt_text = st.text_area("描述您想要生成的视频内容", height=150)
        input_data = prompt_text
        input_type = "text"
    else:  # 图生视频
        st.subheader("输入提示文本")
        prompt_text = st.text_area("描述您想要生成的视频内容", height=150)
        st.subheader("上传参考图片")
        uploaded_file = st.file_uploader("选择一张图片", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            file_type = uploaded_file.type
            input_data = (prompt_text, uploaded_file, file_type)
            input_type = "image"

        # 提交按钮
    submit_button = st.form_submit_button(label="生成视频")

    # 处理表单提交
if submit_button:
    if input_type == "text" and not input_data:
        st.error("请输入提示文本")
    elif input_type == "image" and input_data is None:
        st.error("请上传图片和输入提示文本")
    else:
        # 显示加载状态
        with st.spinner("正在生成视频，请稍候..."):
            # 准备API调用数据
            api_data = {
                "generation_mode": generation_mode,
                "aspect_ratio": param1,
                "number_of_videos": param2,
                "duration_seconds": param3,
                "person_generation": param4
            }

            if input_type == "text":
                api_data["prompt"] = input_data
            else:
                image = Image.open(input_data[1])
                st.image(image, caption='Uploaded Image', width=100)
                bytes_data = input_data[1].getvalue()
                api_data["prompt"] = input_data[0]
                api_data["image"] = bytes_data
                api_data["file_type"] = input_data[2]

            gcs_url = call_video_generation_api(api_data)
            if gcs_url:
                st.success("视频生成成功!")
                st.subheader("生成结果")

                for gu in gcs_url:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:  # 在中间列显示视频，占总宽度的50%
                        # st.video(gu[0])
                        st.video(gu[0])
                        st.download_button(
                            label="下载视频",
                            data=requests.get(gu[0]).content,
                            file_name=gu[1],
                            mime="video/mp4"
                        )

# 添加一些使用说明
with st.expander("使用说明"):
    st.markdown("""
### 如何使用本应用

1. 在左侧边栏选择生成模式：文生视频或图生视频
2. 文生视频模式：输入详细的文本描述
3. 图生视频模式：上传一张参考图片
4. 调整参数设置
5. 点击"生成视频"按钮
6. 等待视频生成完成后，可以预览和下载

### 注意事项

- 视频生成可能需要一些时间，请耐心等待
- 上传的图片建议格式为PNG，建议像素1280x720或720x1280
- 文本描述越详细，生成的视频效果越好
""")

# 页脚
st.markdown("---")
st.markdown("© 2025 AI视频生成器 | 由WebEye提供支持",)