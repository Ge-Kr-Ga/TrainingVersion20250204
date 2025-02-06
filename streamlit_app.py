import streamlit as st
import pandas as pd
import os
from io import BytesIO

# 定义文件路径
CSV_FILE = "finance_records.csv"
PASSWORD_FILE = "password.txt"

# 初始化 CSV 文件（如果文件不存在）
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=['姓名', '缴费项目', '缴费金额']).to_csv(CSV_FILE, index=False)

# 初始化密码文件（如果文件不存在）
if not os.path.exists(PASSWORD_FILE):
    with open(PASSWORD_FILE, "w") as f:
        f.write("123456")  # 默认密码

# 从 CSV 文件中加载数据
def load_data():
    return pd.read_csv(CSV_FILE)

# 将数据保存到 CSV 文件
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# 导出数据为 Excel 文件
def export_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="缴费记录")
    output.seek(0)
    return output

# 获取当前密码
def get_password():
    with open(PASSWORD_FILE, "r") as f:
        return f.read().strip()

# 设置新密码
def set_password(new_password):
    with open(PASSWORD_FILE, "w") as f:
        f.write(new_password)

# 页面1: 输入界面
def input_page():
    st.title("客户缴费输入界面")
    
    with st.form("input_form"):
        name = st.text_input("客户姓名")
        item = st.text_input("缴费项目")
        amount = st.number_input("缴费金额", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("提交")
        
        if submitted:
            new_record = pd.DataFrame([[name, item, amount]], columns=['姓名', '缴费项目', '缴费金额'])
            df = load_data()
            df = pd.concat([df, new_record], ignore_index=True)
            save_data(df)
            st.success("缴费记录已添加！")

# 页面2: 缴费明细页面（需要密码）
def details_page():
    st.title("缴费明细页面")
    
    password = st.text_input("请输入密码", type="password")
    if st.button("验证密码"):
        if password == get_password():
            st.session_state["authenticated"] = True
            st.success("密码正确！")
        else:
            st.error("密码错误，无法访问！")
    
    if st.session_state.get("authenticated", False):
        df = load_data()
        st.write("所有客户的缴费明细：")
        st.dataframe(df)

        # 添加导出按钮
        if st.button("导出为 Excel 文件"):
            excel_file = export_to_excel(df)
            st.download_button(
                label="下载 Excel 文件",
                data=excel_file,
                file_name="finance_records.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# 页面3: 查询页面
def query_page():
    st.title("客户缴费查询页面")
    
    name_to_query = st.text_input("请输入客户姓名")
    if st.button("查询"):
        df = load_data()
        result = df[df['姓名'] == name_to_query]
        if not result.empty:
            st.write(f"{name_to_query} 的缴费记录：")
            st.dataframe(result)
        else:
            st.warning("未找到该客户的缴费记录。")

# 页面4: 密码设置页面
def password_page():
    st.title("密码设置页面")
    
    current_password = st.text_input("请输入当前密码", type="password")
    new_password = st.text_input("请输入新密码", type="password")
    confirm_password = st.text_input("请确认新密码", type="password")
    
    if st.button("设置新密码"):
        if current_password != get_password():
            st.error("当前密码错误！")
        elif new_password != confirm_password:
            st.error("新密码与确认密码不一致！")
        else:
            set_password(new_password)
            st.success("密码已更新！")

# 主页面导航
st.sidebar.title("导航")
page = st.sidebar.radio("选择页面", ["输入界面", "缴费明细页面", "查询页面", "密码设置页面"])

if page == "输入界面":
    input_page()
elif page == "缴费明细页面":
    details_page()
elif page == "查询页面":
    query_page()
elif page == "密码设置页面":
    password_page()