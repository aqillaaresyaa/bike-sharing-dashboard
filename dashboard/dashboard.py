import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Dashboard Penyewaan Sepeda", layout="wide")
sns.set_theme(style="whitegrid")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Label musim mengikuti kode pada dataset (lihat notebook, bagian Cleaning Data)
SEASONS = ["Musim Semi", "Musim Panas", "Musim Gugur", "Musim Dingin"]
MONTHS = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
          "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
MONTHS_SHORT = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

# Warna konsisten: satu warna hanya mewakili satu makna pada seluruh grafik
COLOR_DAY_TYPE = {"Hari Kerja": "#1f77b4", "Akhir Pekan/Libur": "#ff7f0e"}
COLOR_WEATHER = {"Cerah": "#2a9d8f", "Berkabut": "#8ab9b3", "Hujan/Salju Ringan": "#c5ddd9"}
COLOR_TEMP = ["#d9d9d9", "#a6a6a6", "#737373", "#404040"]
COLOR_SEASON = "#b0bec5"
COLOR_HIGHLIGHT = "#d62728"
COLOR_NEUTRAL = "#b0bec5"


@st.cache_data
def load_data():
    hour = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"), parse_dates=["dteday"])
    day = pd.read_csv(os.path.join(BASE_DIR, "day_data.csv"), parse_dates=["dteday"])
    return hour, day


def show_figure(fig):
    """Tampilkan grafik lalu tutup agar objek gambar tidak menumpuk di memori."""
    st.pyplot(fig)
    plt.close(fig)


hour_df, day_df = load_data()

# Sidebar (filter)
st.sidebar.header("Filter Data")
min_date, max_date = day_df["dteday"].min().date(), day_df["dteday"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
if len(date_range) != 2:
    st.info("Pilih tanggal awal dan akhir pada sidebar.")
    st.stop()
start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

seasons = st.sidebar.multiselect("Musim (label mengikuti kode dataset)", SEASONS, default=SEASONS)
day_f = day_df[(day_df["dteday"].between(start, end)) & (day_df["season"].isin(seasons))]
hour_f = hour_df[(hour_df["dteday"].between(start, end)) & (hour_df["season"].isin(seasons))]

if day_f.empty or hour_f.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# Judul dan indikator utama
st.title("Dashboard Penyewaan Sepeda")
st.caption("Capital Bikeshare, Washington D.C. (2011–2012)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Penyewaan", f"{day_f['cnt'].sum():,}")
c2.metric("Rata-rata per Hari", f"{day_f['cnt'].mean():,.0f}")
c3.metric("Pengguna Registered", f"{day_f['registered'].sum() / day_f['cnt'].sum():.1%}")
c4.metric("Pengguna Casual", f"{day_f['casual'].sum() / day_f['cnt'].sum():.1%}")

tab1, tab2, tab3, tab4 = st.tabs(["Pola Jam", "Cuaca dan Suhu", "Pertumbuhan", "Analisis Lanjutan"])

# Tab 1: Pola jam
with tab1:
    st.subheader("Pada jam berapa penyewaan memuncak pada hari kerja dibandingkan akhir pekan/libur?")
    years = sorted(hour_f["year"].unique())
    year_sel = st.radio("Tahun", ["Semua"] + [str(y) for y in years],
                        index=(len(years) if 2012 in years else 0), horizontal=True)
    h = hour_f if year_sel == "Semua" else hour_f[hour_f["year"] == int(year_sel)]
    hourly = h.pivot_table(index="hour", columns="day_type", values="cnt", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(11, 4.5))
    for t in hourly.columns:
        color = COLOR_DAY_TYPE.get(t, "#555555")
        ax.plot(hourly.index, hourly[t], marker="o", lw=2.5, color=color, label=t)
        top = hourly[t].idxmax()
        ax.annotate(f"{hourly[t].max():.0f}", (top, hourly[t].max()), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontweight="bold", color=color)
    ax.set_xticks(range(24))
    ax.set_xlabel("Jam dalam sehari")
    ax.set_ylabel("Rata-rata penyewaan per jam")
    ax.legend(frameon=False)
    sns.despine()
    show_figure(fig)

    cols = st.columns(len(hourly.columns))
    for col, t in zip(cols, hourly.columns):
        s = hourly[t].dropna()
        col.markdown(f"**{t}**")
        col.write("3 jam tertinggi: " + ", ".join(f"{h_:02d}.00 ({v:.0f})" for h_, v in s.nlargest(3).items()))
        if s.min() > 0:
            col.write(f"Rasio jam puncak terhadap jam terendah: **{s.max() / s.min():.1f} kali**")

    ringkasan = []
    for t in hourly.columns:
        s = hourly[t].dropna()
        ringkasan.append(f"{t.lower()} memuncak pada pukul {int(s.idxmax()):02d}.00 "
                         f"(rata-rata {s.max():.0f} penyewaan per jam)")
    st.info(f"Berdasarkan data yang sedang difilter (tahun: {year_sel.lower()}), " + "; ".join(ringkasan) + ".")

# Tab 2: Cuaca dan suhu
with tab2:
    st.subheader("Seberapa besar cuaca dan musim memengaruhi penyewaan harian?")
    order = [w for w in ["Cerah", "Berkabut", "Hujan/Salju Ringan"] if w in day_f["weathersit"].unique()]
    weather = day_f.groupby("weathersit")["cnt"].agg(jumlah_hari="count", rata_rata="mean").reindex(order)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(weather.index, weather["rata_rata"], color=[COLOR_WEATHER[w] for w in weather.index])
    base = weather["rata_rata"].get("Cerah")
    for b, name in zip(bars, weather.index):
        label = f"{b.get_height():,.0f}"
        if base and name != "Cerah":
            label += f"\n({(b.get_height() / base - 1) * 100:+.0f}%)"
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 60, label, ha="center", fontweight="bold")
    ax.set_ylabel("Rata-rata penyewaan per hari")
    ax.set_ylim(0, weather["rata_rata"].max() * 1.2)
    ax.xaxis.grid(False)
    sns.despine()
    show_figure(fig)

    if base:
        kalimat = []
        for name in weather.index:
            if name == "Cerah":
                continue
            turun = (1 - weather.loc[name, "rata_rata"] / base) * 100
            kalimat.append(f"sekitar {turun:.0f}% saat {name.lower()} ({int(weather.loc[name, 'jumlah_hari'])} hari)")
        if kalimat:
            st.info("Berdasarkan data yang sedang difilter, dibandingkan dengan hari cerah, rata-rata penyewaan harian turun "
                    + " dan ".join(kalimat) + ".")
        else:
            st.info("Pada filter ini hanya terdapat hari dengan cuaca cerah sehingga perbandingan tidak dapat dihitung.")
    else:
        st.info("Pada filter ini tidak ada hari dengan cuaca cerah sehingga persentase penurunan tidak dapat dihitung.")

    st.subheader("Rata-rata penyewaan per musim")
    season_avg = day_f.groupby("season")["cnt"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(season_avg.index, season_avg.values, color=COLOR_SEASON)
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 60, f"{b.get_height():,.0f}",
                ha="center", fontweight="bold")
    ax.set_ylabel("Rata-rata penyewaan per hari")
    ax.set_ylim(0, season_avg.max() * 1.2)
    ax.xaxis.grid(False)
    sns.despine()
    show_figure(fig)
    st.caption("Label musim mengikuti kode pada dataset: Musim Semi (kode 1) mencakup Januari sampai 20 Maret dan "
               "21 sampai 31 Desember, yang secara kalender termasuk musim dingin di Washington D.C.")
    if len(season_avg) > 1:
        st.info(f"Berdasarkan data yang sedang difilter, rata-rata penyewaan tertinggi ada pada {season_avg.index[0]} "
                f"({season_avg.iloc[0]:,.0f} per hari) dan terendah pada {season_avg.index[-1]} ({season_avg.iloc[-1]:,.0f} per hari).")
    else:
        st.info(f"Pada filter ini hanya terdapat {season_avg.index[0]} dengan rata-rata penyewaan "
                f"{season_avg.iloc[0]:,.0f} per hari.")

# Tab 3: Pertumbuhan
with tab3:
    st.subheader("Seberapa besar pertumbuhan penyewaan 2012 dibandingkan dengan 2011, dan pada bulan apa paling lambat?")
    st.caption("Bagian ini selalu memakai seluruh data 2011–2012 (tidak mengikuti filter) agar perbandingan tahunan adil.")
    yearly = day_df.groupby("year")[["casual", "registered", "cnt"]].sum()
    growth = (yearly.loc[2012] / yearly.loc[2011] - 1) * 100
    m1, m2, m3 = st.columns(3)
    m1.metric("Total", f"{growth['cnt']:+.1f}%")
    m2.metric("Registered", f"{growth['registered']:+.1f}%")
    m3.metric("Casual", f"{growth['casual']:+.1f}%")

    monthly = day_df.pivot_table(index="month", columns="year", values="cnt", aggfunc="sum")
    pertumbuhan_bulanan = (monthly[2012] / monthly[2011] - 1) * 100
    low3 = list(pertumbuhan_bulanan.nsmallest(3).index)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.bar(pertumbuhan_bulanan.index, pertumbuhan_bulanan.values,
           color=[COLOR_HIGHLIGHT if m in low3 else COLOR_NEUTRAL for m in pertumbuhan_bulanan.index])
    for m in low3:
        ax.text(m, pertumbuhan_bulanan[m] + 2, f"{pertumbuhan_bulanan[m]:.1f}%", ha="center",
                fontweight="bold", color=COLOR_HIGHLIGHT)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTHS_SHORT)
    ax.set_ylabel("Pertumbuhan 2012 terhadap 2011 (%)")
    ax.set_title("Merah = tiga bulan dengan pertumbuhan terendah", loc="left")
    ax.xaxis.grid(False)
    sns.despine()
    show_figure(fig)

    lebih_cepat, lebih_lambat = ("registered", "casual") if growth["registered"] >= growth["casual"] else ("casual", "registered")
    bulan_lambat = ", ".join(MONTHS[m - 1] for m in sorted(low3))
    st.info(f"Pengguna {lebih_cepat} tumbuh lebih cepat ({growth[lebih_cepat]:.1f}%) dibandingkan pengguna "
            f"{lebih_lambat} ({growth[lebih_lambat]:.1f}%). Pertumbuhan tahunan paling lambat terjadi pada {bulan_lambat}.")

# Tab 4: Analisis lanjutan
with tab4:
    st.subheader("Pengelompokan manual: kategori suhu")
    labels_suhu = ["Dingin (<10°C)", "Sejuk (10–20°C)", "Hangat (20–28°C)", "Panas (>28°C)"]
    temp_cat = pd.cut(day_f["temp_c"], bins=[-1, 10, 20, 28, 50], labels=labels_suhu)
    temp_group = day_f.groupby(temp_cat, observed=True)["cnt"].agg(jumlah_hari="count", rata_rata="mean").round(0)
    st.dataframe(temp_group.rename(columns={"jumlah_hari": "Jumlah hari", "rata_rata": "Rata-rata penyewaan per hari"}))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bar_colors = [COLOR_TEMP[labels_suhu.index(c)] for c in temp_group.index]
    bars = ax.bar(temp_group.index.astype(str), temp_group["rata_rata"], color=bar_colors)
    for b in bars:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 60, f"{b.get_height():,.0f}",
                ha="center", fontweight="bold")
    ax.set_xlabel("Kategori suhu")
    ax.set_ylabel("Rata-rata penyewaan per hari")
    ax.set_ylim(0, temp_group["rata_rata"].max() * 1.15)
    ax.xaxis.grid(False)
    sns.despine()
    show_figure(fig)

    ranking = temp_group["rata_rata"].sort_values(ascending=False)
    teks = (f"Berdasarkan data yang sedang difilter, kategori suhu dengan rata-rata penyewaan tertinggi adalah "
            f"{ranking.index[0]} ({ranking.iloc[0]:,.0f} per hari)")
    if len(ranking) > 1:
        selisih = (ranking.iloc[0] / ranking.iloc[1] - 1) * 100
        teks += f", dengan selisih {selisih:.1f}% terhadap {ranking.index[1]} ({ranking.iloc[1]:,.0f} per hari)"
    st.info(teks + ".")

st.caption("Sumber data: Bike Sharing Dataset (Fanaee-T dan Gama), Capital Bikeshare.")
