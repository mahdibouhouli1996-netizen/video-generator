import streamlit as st
import asyncio
import edge_tts
import os
import subprocess

st.set_page_config(page_title="مولد إعلانات التجارة الإلكترونية", page_icon="🎬", layout="centered")

st.title("🚀 مولد الفيديوهات الإعلانية - DZ")
st.write("ارفع صورة المنتج، اكتب النص الإعلاني، واحصل على فيديو واجد للريلز والتيكتوك!")

# مدخلات المستخدم
uploaded_image = st.file_uploader("📸 اختر صورة المنتج (JPG/PNG)", type=["jpg", "jpeg", "png"])
ad_text = st.text_area("✍️ النص الإعلاني (بالدارجة أو الفرنسية)", "Produit de qualite superieure, livraison disponible sur 58 wilayas et paiement a la livraison.")
voice_option = st.selectbox("🎙️ اختر صوت المعلق", ["fr-FR-HenriNeural", "ar-SA-ZariyahNeural", "ar-DZ-IsmailNeural"])

# زر التشغيل
if st.button("🎬 توليد الفيديو الآن"):
    if uploaded_image is None:
        st.error("❌ يرجى رفع صورة المنتج أولاً!")
    else:
        with st.spinner("⏳ جاري إنشاء الصوت والفيديو..."):
            # 1. حفظ صورة المنتج
            image_path = "temp_product.jpg"
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

            # 2. توليد الصوت بـ edge-tts
            async def generate_voice():
                communicate = edge_tts.Communicate(ad_text, voice_option)
                await communicate.save("temp_voice.mp3")

            asyncio.run(generate_voice())

            # 3. دمج الصوت والصورة باستخدام FFMPEG مباشرة (سريع وبدون أخطاء MoviePy)
            output_video = "final_ad.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", image_path,
                "-i", "temp_voice.mp3",
                "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p", "-shortest", output_video
            ]
            
            try:
                subprocess.run(cmd, check=True)
                st.success("✅ تم إنشاء الفيديو بنجاح!")
                
                # عرض الفيديو وتحميله
                st.video(output_video)
                with open(output_video, "rb") as file:
                    st.download_button(
                        label="📥 تحميل الفيديو (MP4)",
                        data=file,
                        file_name="ecommerce_ad.mp4",
                        mime="video/mp4"
                    )
            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة الفيديو: {e}")