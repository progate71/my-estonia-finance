import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime
import os

# --- КОНФИГУРАЦИЯ ЭСТОНИЯ 2026 ---
TAX_RATE = 0.24  # 24% подоходный налог
FREE_MINIMUM = 700.0  # Необлагаемый минимум

# Настройка API (Ключ нужно будет ввести в интерфейсе)
st.set_page_config(page_title="Estonia Finance AI", layout="wide")
st.title("🇪🇪 Финансовый Агент Эстонии 2026")

# Боковая панель для настроек
with st.sidebar:
    api_key = st.text_input("Введите ваш Gemini API Key:", type="password")
    if api_key:
        genai.configure(api_key=api_key)

# Функция расчета зарплаты
def calculate_neto(bruto):
    # Упрощенный расчет (Пенсия 2% + Безработица 1.6%)
    pension = bruto * 0.02
    unemployment = bruto * 0.016
    taxable = max(0, bruto - pension - unemployment - FREE_MINIMUM)
    income_tax = taxable * TAX_RATE
    return bruto - pension - unemployment - income_tax

# Загрузка данных
if 'costs' not in st.session_state:
    if os.path.exists('my_expenses.csv'):
        st.session_state.costs = pd.read_csv('my_expenses.csv')
    else:
        st.session_state.costs = pd.DataFrame(columns=['Дата', 'Тип', 'Категория', 'Сумма', 'Описание'])

# ИНТЕРФЕЙС
tab1, tab2 = st.tabs(["➕ Добавить запись", "📊 Отчеты и База"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Дата", datetime.now())
        entry_type = st.selectbox("Тип", ["Расход", "Доход (Bruto)"])
        category = st.text_input("Категория (напр. Еда, Аренда, ЗП)")
    with col2:
        amount = st.number_input("Сумма в €", min_value=0.0)
        desc = st.text_input("Описание")
        
    if st.button("Записать в базу"):
        final_amount = amount
        if entry_type == "Доход (Bruto)":
            final_amount = calculate_neto(amount)
            st.success(f"Рассчитано Neto: {final_amount:.2f}€ (Налог 24%)")
            
        new_data = pd.DataFrame([[date, entry_type, category, final_amount, desc]], 
                                columns=st.session_state.costs.columns)
        st.session_state.costs = pd.concat([st.session_state.costs, new_data], ignore_index=True)
        st.session_state.costs.to_csv('my_expenses.csv', index=False)
        st.balloons() 
with tab2:
    st.subheader("Твои транзакции")
    st.dataframe(st.session_state.costs, use_container_width=True)
    
    if not st.session_state.costs.empty:
        total_exp = st.session_state.costs[st.session_state.costs['Тип'] == "Расход"]['Сумма'].sum()
        total_inc = st.session_state.costs[st.session_state.costs['Тип'] == "Доход (Bruto)"]['Сумма'].sum()
        st.metric("Остаток на балансе", f"{total_inc - total_exp:.2f} €")
        
        # Кнопка экспорта
        csv = st.session_state.costs.to_csv(index=False).encode('utf-8')
        st.download_button("Скачать отчет (CSV)", csv, "finances.csv", "text/csv")
