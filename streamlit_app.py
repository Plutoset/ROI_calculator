import streamlit as st
import pandas as pd
import numpy as np


df_input = pd.DataFrame({'ARPU': {1: 0.57,
  2: 0.73,
  3: 0.64,
  4: 0.68,
  5: 0.66,
  6: 0.72,
  7: 0.8,
  8: 0.99,
  9: 0.87,
  10: 0.78,
  11: 0.82,
  12: 0.72,
  13: 1.03,
  14: 1.26,
  15: 1.32,
  16: 0.81,
  17: 1.11,
  18: 1.42,
  19: 1.01,
  20: 1.99,
  21: 2.03,
  22: 1.41,
  23: 1.25,
  24: 1.14,
  25: 0.96,
  26: 1.08,
  27: 1.36,
  28: 1.58,
  29: 1.64,
  30: 1.07},
 '留存': {1: 100,
  2: 44.42,
  3: 28.24,
  4: 21.21,
  5: 16.8,
  6: 14.05,
  7: 12.,
  8: 10.5,
  9: 09.18,
  10: 08.06,
  11: 07.15,
  12: 06.57,
  13: 05.97,
  14: 05.61,
  15: 05.24,
  16: 04.85,
  17: 04.49,
  18: 04.2,
  19: 03.95,
  20: 03.77,
  21: 03.55,
  22: 03.47,
  23: 03.23,
  24: 03.03,
  25: 02.91,
  26: 02.81,
  27: 02.72,
  28: 02.63,
  29: 02.58,
  30: 02.5}})
df_input.index.name = '天数'
default_rows = 30


st.title("ROI计算器")

col1,col2=st.columns(2)
with col1:
    # 显示可编辑表格，带行号
    st.markdown("### 输入ARPU和留存数据")
    edited_df = st.data_editor(
        df_input,
        num_rows="fixed",     # 行数固定为30
        width='stretch',
        hide_index=False,     # 行号可见
        key="arpu_retention_table",
        column_config={
        "留存": st.column_config.NumberColumn(
            "留存", format="%.2f%%", step=0.0001, help="以百分号显示，输入时用0.12代表12%"
        ),
        "ARPU": st.column_config.NumberColumn(
            "ARPU", format="%.2f", step=0.01
        )
    }
    )
with col2:
    st.markdown("### 输入其他参数")
    with st.form("input_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            counter = st.text_input("创号数", value="15000")
            cpi_now = st.text_input("现状CPI", value="10.56")
            rate_now = st.text_input("实收比例", value="0.67")
        with col2:
            rate_guess = st.text_input("预估实收比例", value="0.67")
            arpu_k = st.text_input("ARPU提升量", value="1.4")
            ret30_plus = st.text_input("30留存比上调", value="1.34%")
        with col3:
            cpi_guess = st.text_input("预估CPI", value="11")
            roi_guess = st.text_input("预估首月ROI", value="35.00%")
            ret30_boost = st.text_input("30留上调", value="1.8")
        
        submitted = st.form_submit_button("提交")
        st.markdown("左侧表格可直接在单元格输入或粘贴，支持Excel复制粘贴。")
if submitted:
    dates = range(1, len(edited_df) + 1)
    # 数据类型转换与处理
    counter = float(counter.replace(",", ""))
    cpi_now = float(cpi_now)
    rate_now = float(rate_now)
    rate_guess = float(rate_guess)
    arpu_k = float(arpu_k)
    # ret30_plus 可能带%，去掉
    ret30_plus = float(ret30_plus.replace("%", ""))/100
    cpi_guess = float(cpi_guess)
    roi_guess = float(roi_guess.replace("%", ""))/100
    ret30_boost = float(ret30_boost)
    df_arpu = pd.DataFrame(index=dates, columns=dates)
    df_ret = pd.DataFrame(index=dates, columns=dates)
    df_ltv = pd.DataFrame(index=dates, columns=dates)
    df_ret_guess = pd.DataFrame(index=dates, columns=dates)

    for i, row_date in enumerate(dates):
        for j, col_date in enumerate(dates):
            if j <= i:
                df_arpu.iloc[i,j] = df_input.loc[col_date, 'ARPU']
                df_ret.iloc[i,j] = df_input.loc[col_date, '留存']/100
                df_ret_guess.iloc[i,j] = df_input.loc[col_date, '留存']/100*ret30_boost
                df_ltv.iloc[i,j] = df_input.loc[col_date, 'ARPU'] * df_input.loc[col_date, '留存']/100 * counter
            else:
                df_arpu.iloc[i,j] = np.nan
                df_ret.iloc[i,j] = np.nan
                df_ret_guess.iloc[i,j] = np.nan
                df_ltv.iloc[i,j] = np.nan
    df_cost = pd.DataFrame(index=df_input.index)
    df_cost['创号数'] = counter
    df_cost['COST']=cpi_now*counter
    df_cost['目标COST']=cpi_guess*counter
    df_cost['当前LTV'] = df_ltv.sum(axis=1)


    arpu_now = df_input['ARPU'].mean()
    xiaofei_now = df_cost['COST'].sum()
    liushui_now = df_cost['当前LTV'].sum()
    shishou_now = liushui_now/rate_now
    ltv_now = liushui_now/df_cost['创号数'].sum()
    roi_now = liushui_now/xiaofei_now
    ret7_now = df_ret[7].mean()
    ret14_now = df_ret[14].mean()
    ret30_now = df_ret[30].mean()

    arpu_guess = arpu_now * arpu_k
    xiaofei_guess = df_cost['目标COST'].sum()
    liushui_guess = roi_guess * xiaofei_guess
    shishou_guess = liushui_guess / rate_guess
    ltv_guess = liushui_guess/df_cost['创号数'].sum()
    ret7_guess = df_ret_guess[7].mean()
    ret14_guess = df_ret_guess[14].mean()
    ret30_guess = df_ret_guess[30].mean()
    # 提升幅度
    def percent_diff(a, b):
        if a == 0:
            return "N/A"
        return f"{(b-a)/abs(a)*100:.2f}%"
    
    cols = ["实收比例", "日均ARPU", "CPI", "总消费", "实收", "流水", "首月LTV", "首月ROI", "7留", "14留", "30留"]
    现状 = [f'{rate_now:.2f}', f'{arpu_now:.2f}', f'{cpi_now:.2f}', f'{xiaofei_now:.0f}', f'{shishou_now:.0f}', f'{liushui_now:.0f}', f'{ltv_now:.2f}', f'{roi_now:.2%}', f'{ret7_now:.2%}', f'{ret14_now:.2%}', f'{ret30_now:.2%}']
    预估 = [f'{rate_guess:.2f}', f'{arpu_guess:.2f}', f'{cpi_guess:.2f}', f'{xiaofei_guess:.0f}', f'{shishou_guess:.0f}', f'{liushui_guess:.0f}', f'{ltv_guess:.2f}', f'{roi_guess:.2%}', f'{ret7_guess:.2%}', f'{ret14_guess:.2%}', f'{ret30_guess:.2%}']
    提升 = [
        None,  # 占位
        f'{arpu_guess-arpu_now:.2f}',
        f'{cpi_guess-cpi_now:.2f}',
        f'{xiaofei_guess-xiaofei_now:.0f}',
        f'{shishou_guess-shishou_now:.0f}',
        f'{liushui_guess-liushui_now:.0f}',
        f'{ltv_guess-ltv_now:.2f}',
        percent_diff(roi_now, roi_guess),
        f'{ret7_guess-ret7_now:.2%}',
        f'{ret14_guess-ret14_now:.2%}',
        f'{ret30_guess-ret30_now:.2%}'
    ]

    df = pd.DataFrame(
        [cols,现状, 预估, 提升],
        index=['',"现状", "预估", "提升"],
        
    )

    # 将索引变成一列
    df_with_index = df.reset_index()
    df_with_index.columns = [i+1 for i in range(len(df_with_index.columns))]  # 将第一行设为列名
    df_with_index.index = df_with_index.index+1
    st.markdown("### 计算结果")
    st.write("直接复制下方表格内容到Excel即可：")
    st.dataframe(df_with_index)
