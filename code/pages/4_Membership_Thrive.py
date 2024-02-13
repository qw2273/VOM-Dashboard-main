# Created by WUQ2 at 10/6/2023
import streamlit as st
import pandas as pd
from urllib.error import URLError
import sys
import os

if st.session_state["authentication_status"]:
    st.set_page_config(page_title="VOM Survey - Membership Thrive",layout="wide" , page_icon="🚀")
    st.markdown("# Membership Thrive")

    global data_folder_dir
    dir = os.getcwd()
    data_folder_dir = os.path.join(dir, "data")
    sys.path.append(os.path.join(dir, "code"))
    from utility_function import plot_pie_chart, plot_barplot, plot_yoy_change_chart

    question_list =  ['Today, I am thriving at Whirlpool. ']
    global section_mapping
    section_mapping = {'s4': 'Membership Thrive'}
    global question_mapping
    question_mapping = { "s4" : ['Today, I am thriving at Whirlpool. ']}


    question_column_remap = []
    for s_num, qst_list in question_mapping.items():
        for q_num, qst in enumerate(qst_list):
            question_column_remap.append([s_num, "q" + str(q_num + 1), section_mapping.get(s_num), qst])
    question_column_remap = pd.DataFrame(data=question_column_remap,
                                         columns=['section_num', 'question_num', 'section', 'question'])
    question_column_remap['section_question_num'] = question_column_remap['section_num'] + '_' + question_column_remap[ 'question_num']
    column_rename_dict = question_column_remap.groupby(['question'])['section_question_num'].max().to_dict()
    global question_rename_col_mapping
    question_rename_col_mapping = question_column_remap[['section_question_num', 'question']].\
        set_index('section_question_num').to_dict()['question']

    def get_data() -> pd.DataFrame:
        df = None
        columns_to_keep =  [ 'Timestamp'] +  question_list
        for f in os.listdir(data_folder_dir):
            _df = pd.read_excel(os.path.join(data_folder_dir, f))
            if set(question_list) & set(_df.columns) != set():
                _df = _df.loc[:, columns_to_keep]
                df = pd.concat([df, _df], axis=0)
            else:
                pass
        return df



    try:
        # READ DATA
        df_comb=get_data()
        df_comb['Timestamp']=pd.to_datetime(df_comb['Timestamp'])
        df_comb['year']=df_comb['Timestamp'].dt.year
        YEAR_LIST=df_comb['year'].unique().tolist()
        YEAR_LIST=sorted(YEAR_LIST, reverse=True)

        # clean the data and remap the question name
        df_comb.columns = [column_rename_dict.get(col, col) for col in df_comb.columns]

        #  select the year to  view
        year_filter = st.selectbox("Select the Year", YEAR_LIST)
        year_filter = int(year_filter)
        df = df_comb[df_comb['year'] == year_filter]

        st.markdown(f'### **{year_filter} Results Overview **')

        s4_q1_default_value = {1: 'Strongly Disagree', 2: 'Disagree',3:'Neutral',  4 :'Agree', 5: 'Strongly Agree',0:'No response'}
        df['s4_q1'] = df['s4_q1'].fillna(0 )
        df['s4_q1_regroup'] = df['s4_q1'].map(s4_q1_default_value )
        fig = plot_pie_chart(df, 's4_q1', question_rename_col_mapping, use_regroup_value = True)
        st.write(fig)

    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )

else:
    st.write("# Please Login first to continue 😅")