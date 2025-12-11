# KamSec – Şifre Güvenliği + Brute Force Simülasyonu
import streamlit as st
import string
import math
import time
import itertools

st.set_page_config(page_title="KamSec Password Auditor", layout="centered")
st.title("🔐 KamSec Şifre Güvenliği & Brute Force Simülasyonu")

st.write(
    "Bu araç, girdiğin şifrenin teorik olarak ne kadar sürede kırılabileceğini "
    "hesaplar ve istersen kısa şifreler için bruteforce demo çalıştırır.\n\n"
    "**Not:** Gerçek hesaplarında kullandığın şifreleri yazma, sadece test için kullan."
)

# ---------------------- Analiz Fonksiyonları ---------------------- #

def password_strength(password: str):
    length = len(password)
    pool = 0

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    if has_lower:
        pool += 26
    if has_upper:
        pool += 26
    if has_digit:
        pool += 10
    if has_symbol:
        pool += len(string.punctuation)

    if pool == 0 or length == 0:
        return 0, 0.0, pool, "Geçersiz şifre", "–"

    # Entropi (bit)
    entropy = length * math.log2(pool)

    # 1 milyar tahmin/sn brute force varsayımı
    guesses_per_sec = 1_000_000_000
    seconds = (2 ** (entropy - 1)) / guesses_per_sec
    crack_time_str = format_time(seconds)

    if entropy < 28:
        label = "Çok zayıf"
        score = 10
    elif entropy < 36:
        label = "Zayıf"
        score = 30
    elif entropy < 60:
        label = "Orta"
        score = 55
    elif entropy < 80:
        label = "Güçlü"
        score = 80
    else:
        label = "Çok güçlü"
        score = 95

    return score, entropy, pool, label, crack_time_str


def format_time(seconds: float) -> str:
    minute = 60
    hour = 60 * minute
    day = 24 * hour
    year = 365 * day

    if seconds < minute:
        return f"{seconds:.2f} saniye"
    elif seconds < hour:
        return f"{seconds / minute:.2f} dakika"
    elif seconds < day:
        return f"{seconds / hour:.2f} saat"
    elif seconds < year:
        return f"{seconds / day:.2f} gün"
    else:
        return f"{seconds / year:.2e} yıl"

# ---------------------- Arayüz: Sekmeler ---------------------- #

tab1, tab2 = st.tabs(["🔍 Güvenlik Analizi", "🧨 Brute Force Demo"])

# ---- TAB 1: Güvenlik Analizi ---- #
with tab1:
    password = st.text_input(
        "Test etmek istediğin şifre:",
        type="password",
        help="Gerçek hesabında kullandığın şifreyi yazma, örnek/test şifre gir."
    )

    if st.button("🔎 Şifreyi Analiz Et"):
        if not password:
            st.error("Lütfen analiz için bir şifre gir.")
        else:
            score, entropy, pool, label, crack_time = password_strength(password)

            st.subheader("📊 Şifre Güvenlik Raporu")

            st.metric("Güvenlik Puanı", f"%{score}")
            st.progress(score / 100)

            st.write(f"• Uzunluk: **{len(password)}** karakter")
            st.write(f"• Kullanılan karakter havuzu: **{pool}** farklı karakter")
            st.write(f"• Tahmini entropi: **{entropy:.1f} bit**")
            st.write(f"• Seviye: **{label}**")
            st.write(
                f"• 1 milyar tahmin/sn hızındaki kaba kuvvet saldırısına karşı "
                f"tahmini kırılma süresi: **{crack_time}**"
            )

            st.markdown("### 🔐 Öneriler")
            tips = []
            if len(password) < 12:
                tips.append("Şifrenin uzunluğunu en az 12, mümkünse 16+ karakter yap.")
            if not any(c.islower() for c in password):
                tips.append("Küçük harf kullan.")
            if not any(c.isupper() for c in password):
                tips.append("Büyük harf kullan.")
            if not any(c.isdigit() for c in password):
                tips.append("Rakam ekle.")
            if not any(c in string.punctuation for c in password):
                tips.append("Noktalama/sembol karakterleri ekle (., !, ?, @, # gibi).")

            if tips:
                for t in tips:
                    st.write(f"- {t}")
            else:
                st.write(
                    "- Şifren oldukça iyi görünüyor. Yine de farklı servislerde aynı şifreyi kullanmamaya dikkat et."
                )

# ---- TAB 2: Brute Force Demo ---- #
with tab2:
    st.write(
        "Bu sekme **demo amaçlı** gerçek brute force saldırısını simüle eder.\n"
        "Performans için max **4 karakter**, sadece **harf ve rakam** desteklenir."
    )

    demo_pwd = st.text_input(
        "Simülasyon için test şifresi (max 4 karakter, a–z, A–Z, 0–9):",
        type="password",
        key="demo_pwd"
    )

    max_demo_len = 4
    charset = string.ascii_letters + string.digits

    if st.button("🚀 Brute force ile kırmayı dene"):
        if not demo_pwd:
            st.error("Önce demo için bir şifre gir.")
        elif len(demo_pwd) > max_demo_len:
            st.error(f"Bu demo en fazla {max_demo_len} karaktere kadar destekliyor.")
        elif any(c not in charset for c in demo_pwd):
            st.error("Demo için sadece harf ve rakam kullanabilirsin.")
        else:
            start = time.time()
            found = False
            tries = 0

            with st.spinner("Brute force çalışıyor..."):
                for length in range(1, max_demo_len + 1):
                    for attempt in itertools.product(charset, repeat=length):
                        tries += 1
                        guess = ''.join(attempt)
                        if guess == demo_pwd:
                            found = True
                            break
                    if found:
                        break

            elapsed = time.time() - start

            if found:
                st.success(f"Şifre bulundu: `{demo_pwd}`")
                st.write(f"⏱ Süre: **{elapsed:.4f} sn**")
                st.write(f"🔢 Deneme sayısı: **{tries:,}**")

                if elapsed > 0:
                    speed = tries / elapsed
                    st.write(f"⚙️ Tahmini hız: **{speed:,.0f} deneme/sn**")

                # Analizle bağlayalım
                score, entropy, pool, label, crack_time = password_strength(demo_pwd)
                st.info(
                    f"Teorik entropi: **{entropy:.1f} bit** · "
                    f"Analiz seviyesine göre: **{label} (%{score})**"
                )
            else:
                st.error("Şifre bulunamadı (max uzunluk sınırına takıldı).")
