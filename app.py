import streamlit as st 
import pandas as pd

# ==========================
# Load Data
# ==========================
@st.cache_data
def load_data():
    df = pd.read_excel("TransJakarta_FP.xlsx", sheet_name="TransJakarta")  
    df['payUserID'] = df['payUserID'].astype(str)
    users_df = df[['payUserID', 'typeCard', 'userName', 'userSex', 'userBirthYear']].drop_duplicates()
    return df, users_df

df, users_df = load_data()

# ==========================
# Session states
# ==========================
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'users' not in st.session_state:
    st.session_state.users = users_df.copy()
if 'df' not in st.session_state:
    st.session_state.df = df.copy()

# ==========================
# Navigasi
# ==========================
def go_to(page):
    st.session_state.page = page

# LOGIN PAGE
def login_page():
    st.title("🔐 Login Pengguna")

    pay_id = st.text_input("Masukkan PayUserID:")
    login = st.button("Login")
    register = st.button("Register")

    if login:
        if pay_id in st.session_state.users['payUserID'].values:
            st.session_state.user_id = pay_id
            go_to('main_menu')
        else:
            st.error("PayUserID tidak ditemukan. Silakan registrasi.")

    if register:
        go_to('register')

# REGISTER PAGE
def register_page():
    st.title("📝 Register Pengguna Baru")

    payUserID = st.text_input("PayUserID")
    typeCard = st.text_input("Jenis Kartu")
    userName = st.text_input("Nama")
    userSex = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    userBirthYear = st.number_input("Tahun Lahir", min_value=1900, max_value=2025, value=2000)

    if st.button("Daftar"):
        if not payUserID.isdigit() or len(payUserID) != 12:
            st.error("PayUserID harus terdiri dari 12 digit angka.")
        elif payUserID in st.session_state.users['payUserID'].values:
            st.error("PayUserID sudah terdaftar.")
        else:
            new_user = pd.DataFrame([{
                "payUserID": payUserID,
                "typeCard": typeCard,
                "userName": userName,
                "userSex": userSex,
                "userBirthYear": userBirthYear
            }])
            st.session_state.users = pd.concat([st.session_state.users, new_user], ignore_index=True)
            st.success("Registrasi berhasil!")
            go_to('login')

    if st.button("Kembali"):
        go_to('login')

# MAIN MENU
def main_menu(df):
    user_id = st.session_state.user_id
    user = st.session_state.users[st.session_state.users['payUserID'] == user_id].iloc[0]
    st.title(f"👋 Selamat datang, {user['userName']}!")

    if st.button("Cari Koridor"):
        go_to('corridor')
    if st.button("Cek Riwayat"):
        go_to('history')
    if st.button("Logout"):
        st.session_state.user_id = None
        go_to('login')

# CORRIDOR PAGE
def corridor_page(df):
    st.title("🛣️ Cari Koridor")

    route_list = df['routeName'].dropna().unique().tolist()
    selected_route = st.selectbox("Pilih atau ketik nama rute:", sorted(route_list), placeholder="Contoh: Rute 1")

    if selected_route and st.button("Cari"):
        matched = df[df['routeName'] == selected_route]
        if not matched.empty:
            st.success(f"Corridor Name: {matched.iloc[0]['corridorName']}")
        else:
            st.error("Koridor tidak ditemukan.")

    if st.button("Kembali"):
        go_to('main_menu')

# HISTORY PAGE
def history_page(df):
    st.title("📜 Riwayat Perjalanan")

    user_id = st.session_state.user_id
    user_data = st.session_state.users[st.session_state.users['payUserID'] == user_id]

    if user_data.empty:
        st.error("User tidak ditemukan.")
        return

    user = user_data.iloc[0]
    st.write(f"**Nama**: {user['userName']}")
    st.write(f"**Tipe Kartu**: {user['typeCard']}")
    st.write(f"**Jenis Kelamin**: {user['userSex']}")
    st.write(f"**Tahun Lahir**: {user['userBirthYear']}")

    # tampilkan hanya kolom-kolom yang tersedia
    history = df[df['payUserID'] == user_id][['transID', 'routeID', 'transDate', 'duration', 'direction']]
    if history.empty:
        st.warning("Tidak ada riwayat perjalanan.")
    else:
        st.dataframe(history.reset_index(drop=True))

    if st.button("Kembali"):
        go_to('main_menu')

# ==========================
# ROUTING
# ==========================
if st.session_state.page == 'login':
    login_page()
elif st.session_state.page == 'register':
    register_page()
elif st.session_state.page == 'main_menu':
    main_menu(st.session_state.df)
elif st.session_state.page == 'corridor':
    corridor_page(st.session_state.df)
elif st.session_state.page == 'history':
    history_page(st.session_state.df)
