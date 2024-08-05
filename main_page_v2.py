import streamlit as st
import json
import requests
from requests.auth import HTTPBasicAuth
from lark_connector import get_larkbase_data_v4, get_tenant_access_token
from auth import login, signup, logout, check_logged_in 
from pages import login_page, signup_page, help_page

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ''

def format_phone_number(phone_number):
    return f"{phone_number[:3]}***{phone_number[-3:]}"

def save_data_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def send_data_to_webhook(json_data, webhook_url, user, password):
    info_placeholder = st.empty()
    info_placeholder.info("Đang lưu dữ liệu, vui lòng chờ xíu nhen 😉")
    auth = HTTPBasicAuth(user, password)
    response = requests.post(webhook_url, json=json_data, auth=auth)
    if response.status_code == 200:
        info_placeholder.empty()
        st.success("Dữ liệu đã được gửi thành công đến webhook.")
    else:
        info_placeholder.empty()
        st.error(f"Gửi dữ liệu đến webhook thất bại. Mã trạng thái: {response.status_code}")
        st.error(f"Nội dung phản hồi: {response.text}")

st.cache_data
def get_lark_data(base_token, table_id, app_id, app_secret):
    payload = {
        "field_names": ["Tên môn học", "Tên học viên", "Số điện thoại", "ID_KHOA_HOC_TEXT", "ma_mon_hoc_text", "Môn học đăng ký", "Trạng thái"],
        "filter": {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": "Trạng thái",
                    "operator": "isNot",
                    "value": ["Đã học"]
                }
            ]
        },
        "automatic_fields": True
    }
    return get_larkbase_data_v4(base_token, table_id, payload=payload , app_id=app_id, app_secret=app_secret)

def extract_number(khoa_hoc):
    return int(khoa_hoc.split(' ')[0][1:])

def get_sorted_khoa_hoc_list(records):
    khoa_hoc_list = list(set(hv['fields'].get('ID_KHOA_HOC_TEXT', {}).get('value', [{}])[0].get('text', '') for hv in records))
    return sorted(khoa_hoc_list, key=extract_number, reverse=True)

def get_sorted_mon_hoc_list(records, selected_khoa_hoc):
    mon_hoc_list = list(set(hv['fields'].get('Tên môn học', {}).get('value', [{}])[0].get('text', '') 
                        for hv in records if hv['fields'].get('ID_KHOA_HOC_TEXT', {}).get('value', [{}])[0].get('text', '') == selected_khoa_hoc))
    return sorted(list(filter(None, mon_hoc_list)), reverse=False)

def filter_hoc_vien(records, selected_khoa_hoc, selected_mon_hoc):
    return [hv for hv in records if hv['fields'].get('ID_KHOA_HOC_TEXT', {}).get('value', [{}])[0].get('text', '') == selected_khoa_hoc 
            and hv['fields'].get('Tên môn học', {}).get('value', [{}])[0].get('text', '') == selected_mon_hoc]


# @st.cache_data(experimental_allow_widgets=True)  # 👈 Set the parameter
def display_hoc_vien(filtered_hoc_vien, selected_khoa_hoc, selected_mon_hoc):
    for i, hv in enumerate(filtered_hoc_vien, start=1):
        st.write(f"STT: {i}")
        st.write(f"Tên học viên: {hv['fields'].get('Tên học viên', {}).get('value', [{}])[0].get('text', '')}")
        st.write(f"Số điện thoại: {format_phone_number(hv['fields'].get('Số điện thoại', {}).get('value', [''])[0])}")
        hv['trang_thai'] = st.checkbox("Có mặt", key=f"{selected_khoa_hoc}_{selected_mon_hoc}_{i}")
        st.write("---")

def prepare_diem_danh_data_ban_cu(filtered_hoc_vien, note, user):
    diem_danh_data = {
        "note": note,
        "records": []
    }
    for hv in filtered_hoc_vien:
        diem_danh_data["records"].append({
            "record_id": hv['record_id'],
            "fields": {
                "Trạng thái": "Có mặt" if hv.get('trang_thai', False) else "Vắng mặt",
                "Người điểm danh": user
            }
        })
    return diem_danh_data


def prepare_diem_danh_data(filtered_hoc_vien, note, user):
    diem_danh_data = {
        "note": note,
        "records": []
    }
    for hv in filtered_hoc_vien:
        diem_danh_data["records"].append({
            "record_id": hv['record_id'],
            "fields": {
                "Trạng thái": "Có mặt" if hv.get('trang_thai', False) else "Vắng mặt",
                "Người điểm danh": user,
                "Tên học viên": hv['fields'].get('Tên học viên', {}).get('value', [{}])[0].get('text', ''),
                "Mã khóa học": hv['fields'].get('ID_KHOA_HOC_TEXT', {}).get('value', [{}])[0].get('text', ''),
                "Mã môn học": hv['fields'].get('ma_mon_hoc_text', {}).get('value', [{}])[0].get('text', ''),
                "Tên môn học": hv['fields'].get('Tên môn học', {}).get('value', [{}])[0].get('text', ''),
                "Số điện thoại": hv['fields'].get('Số điện thoại', {}).get('value', [''])[0],
                "Ghi chú": note,
                "Thông tin liên quan": [hv['record_id']]  # Đặt record_id trong một danh sách
            }
        })
    return diem_danh_data

def main_page():
    if not st.session_state.logged_in:
        st.write("Vui lòng đăng nhập để tiếp tục")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Đăng nhập", type="login_primary"):
            if login(email, password):
                st.success("Đăng nhập thành công!")
            else:
                st.error("Sai tài khoản hoặc mật khẩu")
    else:
        st.write(f"Xin chào {st.session_state.user}!")
        
        lark_app_id = st.secrets["larkapp"]["lark_app_id"]
        lark_app_secret = st.secrets["larkapp"]["lark_app_secret"]
        
        larkbase_token = st.secrets["larkbase"]["larkbase_token"]
        larkbase_table_id = st.secrets["larkbase"]["larkbase_table_id"]
        
        http_basic_auth_user = st.secrets["webhook"]["http_basic_auth_user"]
        http_basic_auth_password = st.secrets["webhook"]["http_basic_auth_password"]
        webhook_url = st.secrets["webhook"]["webhook_url"]

        records = get_lark_data(larkbase_token, larkbase_table_id, lark_app_id, lark_app_secret)
        
        st.title("Điểm danh học viên")

        st.session_state.khoa_hoc_list = get_sorted_khoa_hoc_list(records)
        st.session_state.selected_khoa_hoc = st.selectbox("Chọn khóa học", st.session_state.khoa_hoc_list)

        st.session_state.mon_hoc_list = get_sorted_mon_hoc_list(records, st.session_state.selected_khoa_hoc)
        selected_mon_hoc = st.selectbox("Chọn môn học", st.session_state.mon_hoc_list)

        st.session_state.filtered_hoc_vien = filter_hoc_vien(records, st.session_state.selected_khoa_hoc, selected_mon_hoc)

        st.write("---")
        display_hoc_vien(st.session_state.filtered_hoc_vien, st.session_state.selected_khoa_hoc, selected_mon_hoc)
        
        note = st.text_area("Ghi chú", placeholder="Nhập ghi chú...")

        if st.button("Xác nhận điểm danh", key="gui_thong_tin_di"):
            diem_danh_data = prepare_diem_danh_data(st.session_state.filtered_hoc_vien, note, st.session_state.user)
            send_data_to_webhook(diem_danh_data, webhook_url, http_basic_auth_user, http_basic_auth_password)

        st.write("")
        with st.popover("Đăng xuất"):
            if st.button("Xác nhận", key="xác nhận logout"):
                logout()
                st.success("Đăng xuất thành công!")
                login_page()
                st.rerun()

if __name__ == "__main__":
    main_page()