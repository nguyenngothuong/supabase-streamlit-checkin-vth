import requests
import pandas as pd
import re
import unidecode
import streamlit as st
from datetime import timedelta
import json




'''
Tổng quát, hàm sanitize_column_name thực hiện việc loại bỏ dấu, loại bỏ các ký tự đặc biệt, thay thế khoảng trắng bằng dấu gạch dưới và chuyển đổi thành chữ thường để tạo ra một tên cột được chuẩn hóa.
'''
def sanitize_column_name(column_name):
    # Xóa khoảng trống đầu và cuối của tên cột
    column_name = column_name.strip()
    
    # Loại bỏ dấu trong tên cột
    column_name = unidecode.unidecode(column_name)
    
    # Thay thế dấu "/" bằng "_"
    column_name = column_name.replace("/", "_")
    
    #xóa '
    column_name = column_name.replace("'", "")
    
    # Xóa dấu .
    column_name = column_name.replace(".", "")
    
    # Thay thế ký tự "()" bằng "_" và nội dung bên trong
    column_name = re.sub(r'\(.*?\)', lambda x: '' + x.group()[1:-1].lower() + '', column_name)
    
    # Thay thế các khoảng trắng liên tiếp bằng một dấu gạch dưới
    column_name = re.sub(r'\s+', '_', column_name)
    
    # Chuyển đổi tên cột thành chữ thường
    column_name = column_name.lower()
    
    return column_name



def connect_to_larkbase(app_id, app_secret, app_token):
    # Tạo client để kết nối với Larkbase
    client = {
        "app_id": app_id,
        "app_secret": app_secret,
        "app_token": app_token
    }
    return client

@st.cache_resource
def get_list_view(tenant_access_token, app_token, table_id, app_id = None, app_secret = None):
    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/views"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}"
    }
    response = requests.get(url, headers=headers)
    
    data = []
    if response.status_code == 200:
        response_data = response.json()
        data.extend(response_data["data"]["items"])

    elif response.status_code == 400:  # Unauthorized - Token hết hạn
        st.info("tenant_access_token has expired. Obtaining a new one...")
        # get new tenant
        if app_id and app_secret:
            new_token = get_tenant_access_token(app_id, app_secret)
            if new_token:
                tenant_access_token = new_token
                headers["Authorization"] = f"Bearer {tenant_access_token}"
            else:
                st.info("Failed to obtain a new tenant_access_token.")
                return None
        else:
            print("app_id and app_secret are required to obtain a new tenant_access_token.")
            st.info("app_id and app_secret are required to obtain a new tenant_access_token.")
            return None
    elif response.status_code == 403:
        st.error(f"Mã lỗi: {response}")
        st.info("Vui lòng kiểm tra xem bạn đã add bot vào trong file chưa?...")
        return None
    else:
        st.error(f"Error: {response}")
        return None
    
    df = pd.DataFrame(data)
    st.success("Lấy dữ liệu thành công!")
    st.dataframe(df)
    return df

@st.cache_resource
def get_list_table(tenant_access_token, app_token, app_id = None, app_secret = None):
    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{app_token}/tables"
    headers = {
        "Authorization": f"Bearer {tenant_access_token}"
    }
    response = requests.get(url, headers=headers)
    
    data = []
    if response.status_code == 200:
        response_data = response.json()
        data.extend(response_data["data"]["items"])

    elif response.status_code == 400:  # Unauthorized - Token hết hạn
        st.info("tenant_access_token has expired. Obtaining a new one...")
        # get new tenant
        if app_id and app_secret:
            new_token = get_tenant_access_token(app_id, app_secret)
            if new_token:
                tenant_access_token = new_token
                headers["Authorization"] = f"Bearer {tenant_access_token}"
            else:
                st.info("Failed to obtain a new tenant_access_token.")
                return None
        else:
            print("app_id and app_secret are required to obtain a new tenant_access_token.")
            st.info("app_id and app_secret are required to obtain a new tenant_access_token.")
            return None
    elif response.status_code == 403:
        st.error(f"Mã lỗi: {response}")
        st.info("Vui lòng kiểm tra xem bạn đã add bot vào trong file chưa?...")
        return None
    else:
        st.error(f"Error: {response}")
        return None
    
    df = pd.DataFrame(data)
    st.success("Lấy dữ liệu thành công!")
    st.dataframe(df)
    return df



def refresh_token(app_id, app_secret):
    try:
        new_token = get_tenant_access_token(app_id, app_secret)
        if new_token:
            return new_token
        else:
            st.error("Failed to obtain a new tenant_access_token.")
            return None
    except Exception as e:
        st.error(f"Error occurred while refreshing token: {e}")
        return None

def create_a_record(tenant_access_token, app_token, table_id, body, app_id=None, app_secret=None):
    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }
    
    
    st.write(body)
    payload = json.dumps(body, ensure_ascii=False)

    
    try:
        response = requests.post(url, headers=headers, data=payload.encode('utf-8'))
        st.write(response)
        
        if response.status_code == 200:
            response_data = response.json()
            st.info(f"body response: {response_data}")            
            st.info(f"data gửi đi: {payload}")            
            record_id = response_data["data"]["record"]["id"]
            st.info(f"New record created successfully with ID: {record_id}")
            return record_id
        elif response.status_code == 400:  # Unauthorized - Token expired
            st.info("tenant_access_token has expired. Obtaining a new one...")
            
            if app_id and app_secret:
                new_token = refresh_token(app_id, app_secret)
                if new_token:
                    headers["Authorization"] = f"Bearer {new_token}"
                    response = requests.post(url, headers=headers, data=payload)
                    if response.status_code == 200:
                        response_data = response.json()
                        record_id = response_data["data"]["record"]["id"]
                        st.info(f"New record created successfully with ID: {record_id}")
                        return record_id
                    else:
                        st.error(f"Error creating record: {response.status_code}, {response.text}")
                        return None
            else:
                st.error("app_id and app_secret are required to obtain a new tenant_access_token.")
                return None
        elif response.status_code == 403:
            st.error(f"Error code: {response}")
            st.info("Please check if you have added the bot to the file...")
            return None
        else:
            st.error(f"Error creating record: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling API: {e}")
        return None

def create_records(tenant_access_token, app_token, table_id, records, app_id=None, app_secret=None):
    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
    
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }
    
    payload = json.dumps({
        "records": records
    })
    
    try:
        response = requests.post(url, headers=headers, data=payload.encode('utf-8'))

        if response.status_code == 200:
            response_data = response.json()
            st.info(f"Dữ liệu gửi đi: {payload}")
            st.info(f"Dữ liệu trả về: {response_data}")
            record_ids = [record["record_id"] for record in response_data["data"]["records"]]
            st.success(f"Đã tạo thành công {len(record_ids)} bản ghi mới với IDs: {', '.join(record_ids)}")
            return record_ids
        elif response.status_code == 400:  # Unauthorized - Token hết hạn
            st.info("tenant_access_token đã hết hạn, đang lấy mới...")
            
            if app_id and app_secret:
                new_token = get_tenant_access_token(app_id, app_secret)
                if new_token:
                    headers["Authorization"] = f"Bearer {new_token}"
                    response = requests.post(url, headers=headers, data=payload)
                    if response.status_code == 200:
                        response_data = response.json()
                        record_ids = [record["record_id"] for record in response_data["data"]["records"]]
                        st.success(f"Đã tạo thành công {len(record_ids)} bản ghi mới với IDs: {', '.join(record_ids)}")
                        return record_ids
                    else:
                        st.error(f"Lỗi khi tạo bản ghi: {response.status_code}, {response.text}")
                        return None
                else:
                    st.info("Thất bại khi lấy tenant_access_token.")
                    return None
            else:
                st.info("Chưa có app_id, app_secret!")
                st.info("app_id và app_secret là bắt buộc để lấy tenant_access_token mới.")
                return None
        elif response.status_code == 403:
            st.error(f"Mã lỗi: {response}")
            st.info("Vui lòng kiểm tra xem bạn đã add bot vào trong file chưa?...")
            return None
        else:
            st.error(f"Lỗi khi tạo bản ghi: {response.status_code}, {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi khi gọi API: {e}")
        return None


@st.cache_data(ttl=600) #hsd trong vòng 2h nhé.
def get_tenant_access_token(app_id, app_secret):
    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result["code"] == 0:
            tenant_access_token = result["tenant_access_token"]
            expire = result["expire"]
            
            # Tính toán thời gian còn lại
            remaining_time = timedelta(seconds=expire)
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            #hiển thị cho user thấy            
            # st.info(f"Đã lấy mã tenant_access_token mới: {tenant_access_token}")
            # st.info(f"Hạn dùng: {hours} hours, {minutes} minutes")


            return tenant_access_token
        
        else:
            st.info(f"Failed to get tenant_access_token. Error code: {result['code']}, message: {result['msg']}")
            return None

    except requests.exceptions.RequestException as e:
        st.info(f"Error occurred while calling API: {e}")
        return None

def has_specific_keys(value, keys):
    # Kiểm tra xem giá trị có phải là một danh sách hay không
    if isinstance(value, list) and len(value) > 0:
        # Kiểm tra xem phần tử đầu tiên của danh sách có phải là một từ điển hay không
        if isinstance(value[0], dict):
            # Lấy các khóa của từ điển
            dict_keys = value[0].keys()
            # Kiểm tra xem từ điển có chứa tất cả các khóa được chỉ định hay không
            return all(key in dict_keys for key in keys)
    # Nếu không thỏa mãn các điều kiện trên, trả về False
    return False

def flatten_dict(data):
    result = {}
    for key, value in data.items():
        if has_specific_keys(value, ["record_ids", "text", "text_arr"]):
            for i, item in enumerate(value):
                result[f"{key}_text"] = item.get("text", "")
                result[f"{key}_record_ids"] = ", ".join(item.get("record_ids", []))
        elif has_specific_keys(value, ["en_name", "name", "id", "avatar_url"]):
            # Tạo các danh sách để lưu trữ các giá trị tương ứng
            en_names = []
            names = []
            ids = []
            for item in value:
                names.append(item.get("name", ""))
                ids.append(item.get("id", ""))
            # Lưu các giá trị vào các cột riêng biệt trong DataFrame
            result[f"{key}_name"] = ", ".join(names)
            result[f"{key}_id"] = ", ".join(ids)
        else:
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    result[f"{key}_{sub_key}"] = sub_value
            elif isinstance(value, list):
                result[key] = ", ".join(str(item) for item in value)
            else:
                result[key] = value
    return result

def get_larkbase_data_v4(app_token, table_id, view_id=None, payload=None, app_id=None, app_secret=None):
    tenant_access_token = get_tenant_access_token(app_id, app_secret)
    url = f"https://open.larksuite.com/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    
    params = {"page_size": 500}  # Lấy tối đa 500 bản ghi trong một lần gọi API
    if view_id:
        params["view_id"] = view_id
        
    headers = {
        "Authorization": f"Bearer {tenant_access_token}",
        "Content-Type": "application/json"
    }

    items = []
    page_token = None

    while True:
        if page_token:
            params["page_token"] = page_token
        
        try:
            if payload:
                response = requests.post(url + "/search", headers=headers, params=params, json=payload)
            else:
                response = requests.get(url, headers=headers, params=params)

            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            
            response_data = response.json()
            
            if "data" in response_data and "items" in response_data["data"]:
                items.extend(response_data["data"]["items"])
                if response_data["data"].get("has_more"):
                    page_token = response_data["data"].get("page_token")
                else:
                    break
            else:
                st.error(f"Unexpected response structure: {response_data}")
                break

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error: {e.response.status_code}"
            response_data = e.response.json()
            if "code" in response_data and "msg" in response_data:
                error_msg += f" - {response_data['code']}: {response_data['msg']}"
            st.error(error_msg)
            if "error" in response_data and "log_id" in response_data["error"]:
                st.info(f"Log ID: {response_data['error']['log_id']}")
            break
        except requests.exceptions.RequestException as e:
            st.error(f"Error calling API: {e}")
            break
        except json.JSONDecodeError:
            st.error(f"Invalid JSON response: {response.text}")
            break

    return items


# lark_app_id = "cli_a6e8ff5828b89009"
# lark_app_secret = "xxx"
# tenant_access_token = get_tenant_access_token(lark_app_id, lark_app_secret)

# lark_app_token = "A1Dsb8eKQaJRdKszGGQuwnM9sIg" 
# lark_table_id = "tblyzCIrjJNJg9AV"



# payload = {
#     "field_names": ["Tên học viên","Số điện thoại","ID khóa học", "ID MÔN HỌC", "Môn học đăng ký", "Trạng thái"],
#     "filter": {
#         "conjunction": "and",
#         "conditions": [
#             {
#                 "field_name": "Trạng thái",
#                 "operator": "isNot",
#                 "value": ["Đã học"]
#             }
#         ]
#     },
#   "automatic_fields": True
# }

# data = get_larkbase_data_v4(tenant_access_token, lark_app_token, lark_table_id, payload=payload , app_id=lark_app_id, app_secret=lark_app_secret)




# def save_data_to_json(data, filename):
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)


# # Lưu dữ liệu vào tệp JSON
# save_data_to_json(data, 'data.json')



'''
test thêm filter cho version 02
'''
# tenant_access_token = "t-xxx"
# app_token = "zzz"
# table_id = "zxxx"

# filter = {
#     "filter": {
#         "conditions": [
#             {
#                 "field_name": "Tình trạng",
#                 "operator": "is",
#                 "value": [
#                     "Chốt"
#                 ]
#             }
#         ],
#         "conjunction": "and"
#     }
# }

# data = get_larkbase_data_v2(tenant_access_token, app_token, table_id)

# print("số lượng bản ghi: " + str(len(data)))

# if data:
#     # Xử lý dữ liệu trả về
#     for item in data:
#         print(item)
# else:
#     print("Không có dữ liệu hoặc có lỗi xảy ra.")