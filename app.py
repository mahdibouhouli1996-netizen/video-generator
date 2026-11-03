import asyncio
import os
import streamlit as st
import edge_tts
import subprocess

st.set_page_config(page_title="مولد الفيديوهات الإعلانية DZ", page_icon="📢", layout="centered")

st.title("📢 مولد الفيديوهات الإعلانية - DZ")
st.write("ارفع صورة منتجك، اكتب النص الإعلاني، وأحصل على فيديو واحد لريلز والتيكتوك.")

# رفع صورة المنتج
uploaded_file = st.file_uploader("📂 اختر صورة المنتج (JPG/PNG)", type=["jpg", "jpeg", "png"])

# النص الإعلاني
ad_text = st.text_area("✍️ النص الإعلاني (بالدارجة أو العربية)", "Produit de qualité supérieure, livraison disponible sur 58 wilayas et paiement à la livraison.")

# اختيار صوت التعليق
voice_option = st.selectbox(
    "🎙️ اختر صوت التعليق",
    ("ar-DZ-IsmaelNeural (صوت جزائري)", "ar-FR-HenriNeural", "fr-FR-DeniseNeural")
)

# استخراج كود الصوت الفعلي
if "Ismael" in voice_option:
    selected_voice = "ar-DZ-IsmaelNeural"
elif "FR-Henri" in voice_option:
    selected_voice = "ar-FR-HenriNeural"
else:
    selected_voice = "fr-FR-DeniseNeural"

if st.button("🚀 توليد الفيديو الآن"):
    if uploaded_file is not None:
        # حفظ الصورة المرفوعة مؤقتاً
        image_path = "temp_image.png"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.info("⏳ جاري توليد الصوت الذكي...")
        
        # دالة توليد الصوت مع إعادة المحاولة لتفادي أخطاء السيرفر
        async def generate_voice_with_retry(text, voice, retries=3, delay=2):
            for attempt in range(retries):
                try:
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save("temp_voice.mp3")
                    return True
                except Exception as e:
                    if attempt == retries - 1:
                        raise e
                    await asyncio.sleep(delay)

        try:
            # تشغيل دالة الصوت
            asyncio.run(generate_voice_with_retry(ad_text, selected_voice))
            
            st.info("🎬 جاري دمج الصورة والصوت عبر FFmpeg...")
            
            # أمر FFmpeg لإنتاج فيديو مربّع ريلز/تيكتوك
            output_video = "output_ad.mp4"
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", image_path,
                "-i", "temp_voice.mp3",
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                output_video
            ]
            
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                st.success("🎉 تم توليد الفيديو الإعلاني بنجاح!")
                st.video(output_video)
                
                with open(output_video, "rb") as file:
                    st.download_button(
                        label="📥 تحميل الفيديو الإعلاني",
                        data=file,
                        file_name="mhd_ad_video.mp4",
                        mime="video/mp4"
                    )
            else:
                st.error(f"❌ حدث خطأ أثناء معالجة الفيديو: {result.stderr.decode('utf-8')}")
                
        except Exception as e:
            st.error(f"⚠️ فشل الاتصال بخدمة توليد الصوت (قد يكون بسبب ضغط السيرفر المؤقت): {str(e)}")
            st.info("💡 نصيحة: اعرِض الصفحة وعاود المحاولة بعد لحظات قليلة.")
    else:
        st.warning("⚠️ يرجى رفع صورة المنتج أولاً قبل الضغط على التوليد.")