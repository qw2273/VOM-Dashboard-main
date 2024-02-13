from urllib.error import URLError
import streamlit as st
import pandas as pd
import sys
import os

if st.session_state["authentication_status"]:

    st.set_page_config(page_title="VOM Survey - Membership Commitment",layout="wide" , page_icon="🤝")
    st.markdown("# Membership Commitment")

    global data_folder_dir
    dir = os.getcwd()
    data_folder_dir = os.path.join(dir, "data")
    sys.path.append(os.path.join(dir, "code"))
    from utility_function import plot_pie_chart, plot_barplot, plot_yoy_change_chart

    question_list = [
            'I understand WWN’s mission to successfully create an inclusive & equitable environment that enables a natural desire to stay & be committed to Whirlpool.',
            'I am actively engaged in WWN activities that help drive an inclusive & equitable environment that enables a natural desire to stay & be committed to Whirlpool.',
            'If you are not currently actively engaged in WWN, what would inspire you to become more involved?',
            'Why is supporting WWN important to you (as a female or an ally)?',
            'How could WWN make the biggest impact for women at Whirlpool in the coming year?']

    global section_mapping
    section_mapping = {  's3': 'Membership Commitment'}
    global question_mapping
    question_mapping = {
        "s3": [  'I understand WWN’s mission to successfully create an inclusive & equitable environment that enables a natural desire to stay & be committed to Whirlpool.',
            'I am actively engaged in WWN activities that help drive an inclusive & equitable environment that enables a natural desire to stay & be committed to Whirlpool.',
            'If you are not currently actively engaged in WWN, what would inspire you to become more involved?',
            'Why is supporting WWN important to you (as a female or an ally)?',
            'How could WWN make the biggest impact for women at Whirlpool in the coming year?'] }

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
        columns_to_keep = ['Timestamp'] + question_list
        for f in os.listdir(data_folder_dir):
            year_str = f.split("_")[-1].split('.')[0]
            _df = pd.read_excel(os.path.join(data_folder_dir, f))
            # _df.rename(columns={f"What area would you most like to see WWN focus on in {int(year_str) + 1}? Please choose TWO:":
            #            "What area would you most like to see WWN focus on in next year? Please choose TWO:"}, inplace=True)
            _df = _df[columns_to_keep]
            df = pd.concat([df, _df], axis=0)
        return df

    def data_clean(df):

        question_column_remap = []
        for s_num, qst_list in question_mapping.items():
            for q_num, qst in enumerate(qst_list):
                question_column_remap.append([ s_num, "q" + str(q_num +1 ),  section_mapping.get(s_num), qst] )

        question_column_remap = pd.DataFrame(data=question_column_remap,
                                             columns=['section_num', 'question_num', 'section', 'question'])

        question_column_remap['section_question_num'] = question_column_remap['section_num'] + '_' + question_column_remap[
            'question_num']

        column_rename_dict = question_column_remap.groupby(['question'])['section_question_num'].max().to_dict()

        df.columns = [column_rename_dict.get(col, col) for col in df.columns]
        return df


    try:
        # READ DATA
        df_comb = get_data()
        df_comb['Timestamp'] = pd.to_datetime(df_comb['Timestamp'])
        df_comb['year'] = df_comb['Timestamp'].dt.year
        YEAR_LIST = df_comb['year'].unique().tolist()
        YEAR_LIST = sorted(YEAR_LIST, reverse=True)
        # clean the data and remap the question name
        df_comb = data_clean(df_comb)

        #  select the year to  view
        # select the year to  view
        # if All is selected - YOY comparison
        year_filter = st.selectbox("Select the Year", YEAR_LIST + ['YOY change'])
        if year_filter == 'YOY change':
            YOY_COMPARE = True
            df = df_comb.copy()
        else:
            YOY_COMPARE = False
            year_filter = int(year_filter)
            df = df_comb[df_comb['year'] == year_filter]

        if not YOY_COMPARE:

            st.markdown(f'### **{year_filter} Results Overview **')

            #   'I understand WWN’s mission to successfully create an inclusive & equitable environment that enables a natural desire to stay & be committed to Whirlpool.'
            df['s3_q1'] = df['s3_q1'].fillna(0)
            s3_q1_default_value = {1: 'Strongly Disagree', 2: 'Disagree', 3: 'Neutral', 4: 'Agree', 5: 'Strongly Agree',
                                   0: 'No response'}
            df['s3_q1_regroup'] = df['s3_q1'].map(s3_q1_default_value)
            fig = plot_barplot(df, 's3_q1', list(s3_q1_default_value.values()),
                                 question_rename_col_mapping, use_regroup_value=True)
            st.write(fig)

            #  'I am actively engaged in WWN activities that help drive an inclusive & equitable environment that enables a natural desire to stay & be committed to Whirlpool.',
            df['s3_q2'] = df['s3_q2'].fillna(0)
            s3_q2_default_value = {1: 'Strongly Disagree', 2: 'Disagree', 3: 'Neutral', 4: 'Agree', 5: 'Strongly Agree',
                                   0: 'No response'}
            df['s3_q2_regroup'] = df['s3_q2'].map(s3_q2_default_value)
            fig = plot_barplot(df, 's3_q2', list(s3_q2_default_value.values()),
                                 question_rename_col_mapping, use_regroup_value=True)
            st.write(fig)

        else:
            scale_mapping =  {1: 'Strongly Disagree', 2: 'Disagree', 3: 'Neutral', 4: 'Agree', 5: 'Strongly Agree',
                            0: 'No response'}
            scale_cat_list  =list (scale_mapping.values())

            df['s3_q1'] = df['s3_q1'].fillna(0)
            df['s3_q1_regroup'] = df['s3_q1'].map(scale_mapping)
            fig = plot_yoy_change_chart(df, 's3_q1', scale_cat_list , question_rename_col_mapping,
                                        use_regroup_value=True)
            st.write(fig)

            df['s3_q2'] = df['s3_q2'].fillna(0)
            df['s3_q2_regroup'] = df['s3_q2'].map(scale_mapping)
            fig = plot_yoy_change_chart(df, 's3_q2', scale_cat_list, question_rename_col_mapping,
                                        use_regroup_value=True)
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