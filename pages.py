import streamlit as st
from auth import login, signup, logout
from streamlit_navigation_bar import st_navbar

def login_page():
    st.title("Đăng nhập")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Mật khẩu", type="password", key="login_password")
    
    if st.button("Đăng nhập"):
        if login(email, password):
            st.success("Đăng nhập thành công!")
            st.rerun()

# def signup_page():
#     st.title("Đăng ký")
#     email = st.text_input("Email", key="signup_email")
#     password = st.text_input("Mật khẩu", type="password", key="signup_password")
#     confirm_password = st.text_input("Xác nhận mật khẩu", type="password", key="signup_confirm_password")
    
#     if st.button("Đăng ký"):
#         if password != confirm_password:
#             st.error("Mật khẩu và xác nhận mật khẩu không khớp.")
#         elif len(password) < 8:
#             st.error("Mật khẩu phải có ít nhất 8 ký tự.")
#         elif not any(char.islower() for char in password):
#             st.error("Mật khẩu phải chứa ít nhất một chữ cái thường.")
#         elif not any(char.isupper() for char in password):
#             st.error("Mật khẩu phải chứa ít nhất một chữ cái hoa.")
#         elif not any(char.isdigit() for char in password):
#             st.error("Mật khẩu phải chứa ít nhất một chữ số.")
#         elif not any(char in "!@#$%^&*()_+-=[]{};':\"|\<>?,./" for char in password):
#             st.error("Mật khẩu phải chứa ít nhất một ký tự đặc biệt.")
#         else:
#             try:
#                 if signup(email, password):
#                     st.success("Đăng ký thành công!")
#             except Exception as e:
#                 st.error(f"Đăng ký thất bại: {e}")


def main_page():
    st.title("Trang chính")
    st.write("Chào mừng đến với ứng dụng Streamlit!")
    
    st.text_area("Nhập suy nghĩ của bạn!")
    
    
    with st.popover("Đăng xuất"):
        if st.button("Xác nhận"):
            logout()
            st.success("Đăng xuất thành công!")
            login_page()
            st.rerun()
            
            
def help_page():
    st.title("Hướng dẫn sử dụng")
    st.write("Chào mừng đến với hướng dẫn sử dụng ứng dụng Streamlit!")
    
    st.header("1. Đăng nhập")
    st.write("- Nhập email và mật khẩu của bạn vào các trường tương ứng.")
    st.write("- Nhấn nút 'Đăng nhập' để truy cập vào ứng dụng.")
    st.write("- Nếu bạn chưa có tài khoản, hãy chọn 'Đăng ký' để tạo tài khoản mới.")
    
    st.header("2. Chọn khóa học và môn học")
    st.write("- Sau khi đăng nhập thành công, bạn sẽ thấy trang chính của ứng dụng.")
    st.write("- Chọn khóa học từ danh sách 'Chọn khóa học'.")
    st.write("- Chọn môn học từ danh sách 'Chọn môn học' tương ứng với khóa học đã chọn.")
    
    st.header("3. Điểm danh học viên")
    st.write("- Sau khi chọn khóa học và môn học, danh sách học viên sẽ được hiển thị.")
    st.write("- Mỗi học viên sẽ có thông tin như: STT, Tên học viên, Số điện thoại.")
    st.write("- Đánh dấu vào checkbox 'Điểm danh' để xác nhận sự có mặt của học viên.")
    st.video("https://youtu.be/nTJnCDq3U0Y")
    
    
    st.info("Mới cập nhật 01 07 2024")
    st.header("4. Ghi chú")
    st.write("- Bạn có thể nhập ghi chú vào ô 'Ghi chú' nếu cần thiết.")
    
    st.header("5. Xác nhận và gửi thông tin")
    st.write("- Sau khi hoàn tất việc điểm danh, nhấn nút 'Xác nhận' để gửi thông tin điểm danh đến Larkbase.")
    st.write("- Nếu gửi thành công, bạn sẽ nhận được thông báo 'Điểm danh thành công và đã gửi dữ liệu đến Larkbase!'.")
    
    st.header("6. Đăng xuất")
    st.write("- Để đăng xuất khỏi ứng dụng, nhấn vào nút 'Đăng xuất' ở góc trên cùng bên phải.")
    st.write("- Xác nhận đăng xuất bằng cách nhấn nút 'Xác nhận' trong cửa sổ pop-up.")
    
    
    st.header("Lưu ý quan trọng")
    st.warning("Để đảm bảo ứng dụng hoạt động ổn định và tránh lỗi, vui lòng không tự ý chỉnh sửa tên cột trong Larkbase. Các tên cột sau đây phải được giữ nguyên:")
    st.code("""
        - Tên môn học
        - Tên học viên
        - Số điện thoại
        - ID khóa học
        - ID MÔN HỌC
        - Môn học đăng ký
        - Trạng thái
    """)
    
    st.header("Báo lỗi")
    st.write("Nếu bạn gặp bất kỳ lỗi nào trong quá trình sử dụng ứng dụng, vui lòng gửi email báo lỗi đến địa chỉ:")
    st.code("report@nguyenngothuong.com")
    st.write("Trong email, hãy mô tả chi tiết lỗi bạn gặp phải và cung cấp các thông tin liên quan (ví dụ: ảnh chụp màn hình, thông báo lỗi, ...) để chúng tôi có thể khắc phục vấn đề nhanh chóng.")
    
    st.video("https://youtu.be/YG_utHEWOdg")