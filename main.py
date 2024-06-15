import streamlit as st
from supabase import create_client,Client

# Khởi tạo Supabase client
url = st.secrets["supabase"]["url"]
key = st.secrets["supabase"]["key_public"]

supabase = create_client(url, key)

# Khởi tạo session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("Đăng nhập")
    users_email = st.text_input("Email")
    users_password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập"):
        if not users_email or not users_password:
            st.error("Vui lòng nhập đầy đủ email và mật khẩu.")
        else:
            try:
                session = supabase.auth.sign_in_with_password({"email": users_email, "password": users_password})
                if session:
                    st.success("Đăng nhập thành công!")
                    st.session_state.logged_in = True
                    st.experimental_rerun()
            except Exception as e:
                if '400' in str(e):
                    st.error("Đăng nhập thất bại: Email hoặc mật khẩu không chính xác.")
                else:
                    st.error(f"Đăng nhập thất bại: {str(e)}")

# Kiểm tra trạng thái đăng nhập
def check_logged_in():
    return st.session_state.logged_in

# Trang chính
def main_page():
    st.title("Trang chính")
    st.write("Chào mừng đến với ứng dụng Streamlit!")
    if st.button("Đăng xuất"):
        supabase.auth.sign_out()
        st.session_state.logged_in = False
        st.rerun()





# Kiểm tra trạng thái đăng nhập và hiển thị trang tương ứng
if check_logged_in():
    main_page()
else:
    login_page()