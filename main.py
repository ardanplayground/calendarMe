import streamlit as st
import requests
import calendar
from datetime import datetime, date
import pandas as pd

# Konfigurasi halaman
st.set_page_config(
    page_title="Kalender Indonesia",
    page_icon="📅",
    layout="wide"
)

# CSS untuk styling mirip tanggalan.com
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .calendar-container {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .month-header {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 20px;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
    }
    .day-header {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        margin-bottom: 10px;
        font-weight: bold;
        color: #34495e;
    }
    .day-name {
        text-align: center;
        padding: 10px;
        background-color: #ecf0f1;
        border-radius: 5px;
    }
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
    }
    .day-cell {
        aspect-ratio: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        background-color: white;
        transition: all 0.3s;
        min-height: 80px;
    }
    .day-cell:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .day-number {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .today {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: bold;
    }
    .holiday {
        background-color: #ff6b6b;
        color: white !important;
    }
    .weekend {
        background-color: #ffeaa7;
    }
    .empty-day {
        border: none;
        background-color: transparent;
    }
    .holiday-name {
        font-size: 10px;
        text-align: center;
        margin-top: 5px;
        line-height: 1.2;
    }
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .holiday-list-item {
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_holidays(year):
    """Mengambil data hari libur dari API"""
    try:
        url = f"https://api-harilibur.vercel.app/api?year={year}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            holidays = {}
            for holiday in data:
                holiday_date = datetime.strptime(holiday['holiday_date'], '%Y-%m-%d').date()
                holidays[holiday_date] = holiday['holiday_name']
            return holidays
        else:
            return {}
    except Exception as e:
        st.error(f"Error mengambil data libur: {e}")
        return {}

def generate_calendar_html(year, month, holidays, today):
    """Generate HTML untuk kalender bulanan"""
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    html = f'<div class="calendar-container">'
    html += f'<div class="month-header">{month_name} {year}</div>'
    
    # Header hari
    html += '<div class="day-header">'
    day_names = ['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab']
    for day in day_names:
        html += f'<div class="day-name">{day}</div>'
    html += '</div>'
    
    # Grid kalender
    html += '<div class="calendar-grid">'
    for week in cal:
        for day_idx, day in enumerate(week):
            if day == 0:
                html += '<div class="day-cell empty-day"></div>'
            else:
                current_date = date(year, month, day)
                classes = ['day-cell']
                
                # Cek hari ini
                if current_date == today:
                    classes.append('today')
                # Cek hari libur
                elif current_date in holidays:
                    classes.append('holiday')
                # Cek weekend
                elif day_idx in [0, 6]:
                    classes.append('weekend')
                
                class_str = ' '.join(classes)
                html += f'<div class="{class_str}">'
                html += f'<div class="day-number">{day}</div>'
                
                # Tampilkan nama libur jika ada
                if current_date in holidays:
                    holiday_name = holidays[current_date]
                    # Perpendek nama jika terlalu panjang
                    if len(holiday_name) > 20:
                        holiday_name = holiday_name[:17] + '...'
                    html += f'<div class="holiday-name">{holiday_name}</div>'
                
                html += '</div>'
    
    html += '</div></div>'
    return html

# Judul aplikasi
st.title("📅 Kalender Indonesia")
st.markdown("*Dengan Hari Libur Nasional*")

# Sidebar untuk navigasi
with st.sidebar:
    st.header("⚙️ Pengaturan")
    
    # Pilih tahun
    current_year = datetime.now().year
    selected_year = st.selectbox(
        "Pilih Tahun",
        range(current_year - 2, current_year + 5),
        index=2
    )
    
    # Pilih bulan
    current_month = datetime.now().month
    month_names_id = [
        'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    
    view_option = st.radio(
        "Tampilan",
        ["Bulan Ini", "Bulan Tertentu", "Seluruh Tahun"]
    )
    
    if view_option == "Bulan Tertentu":
        selected_month_name = st.selectbox("Pilih Bulan", month_names_id, index=current_month-1)
        selected_month = month_names_id.index(selected_month_name) + 1
    elif view_option == "Bulan Ini":
        selected_month = current_month
    
    st.markdown("---")
    st.markdown("### 📌 Keterangan")
    st.markdown("🟣 **Ungu**: Hari ini")
    st.markdown("🔴 **Merah**: Hari libur nasional")
    st.markdown("🟡 **Kuning**: Akhir pekan")

# Ambil data hari libur
holidays = get_holidays(selected_year)
today = date.today()

# Tampilkan kalender
if view_option == "Seluruh Tahun":
    st.subheader(f"Kalender Tahun {selected_year}")
    
    # Buat 3 kolom untuk menampilkan 3 bulan per baris
    for row in range(4):
        cols = st.columns(3)
        for col_idx in range(3):
            month = row * 3 + col_idx + 1
            with cols[col_idx]:
                calendar_html = generate_calendar_html(selected_year, month, holidays, today)
                st.markdown(calendar_html, unsafe_allow_html=True)
else:
    # Tampilkan bulan tunggal dengan ukuran lebih besar
    calendar_html = generate_calendar_html(selected_year, selected_month, holidays, today)
    st.markdown(calendar_html, unsafe_allow_html=True)

# Daftar hari libur
st.markdown("---")
st.subheader(f"📋 Daftar Hari Libur Nasional {selected_year}")

if holidays:
    # Filter berdasarkan tampilan
    if view_option != "Seluruh Tahun":
        filtered_holidays = {k: v for k, v in holidays.items() if k.month == selected_month}
    else:
        filtered_holidays = holidays
    
    if filtered_holidays:
        # Urutkan berdasarkan tanggal
        sorted_holidays = sorted(filtered_holidays.items())
        
        for holiday_date, holiday_name in sorted_holidays:
            day_name = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'][holiday_date.weekday()]
            date_str = holiday_date.strftime('%d %B %Y')
            
            st.markdown(f"""
            <div class="holiday-list-item">
                <strong>{holiday_name}</strong><br>
                {day_name}, {date_str}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"Tidak ada hari libur nasional di bulan ini.")
else:
    st.warning("Tidak dapat memuat data hari libur. Silakan coba lagi nanti.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p>Data hari libur nasional Indonesia dari <a href='https://api-harilibur.vercel.app/' target='_blank'>API Hari Libur</a></p>
    <p>Dibuat dengan ❤️ menggunakan Streamlit</p>
</div>
""", unsafe_allow_html=True)
