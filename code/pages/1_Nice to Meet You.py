from urllib.error import URLError
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

if st.session_state["authentication_status"]:
    st.set_page_config(page_title="VOM Survey - Nice to Meet You",layout="wide" , page_icon="😀")
    st.markdown("# Nice to Meet You")

    global data_folder_dir
    dir = os.getcwd()
    data_folder_dir = os.path.join(dir, "data")

    sys.path.append(os.path.join(dir, "code"))
    from utility_function import plot_pie_chart, plot_barplot, plot_yoy_change_chart

    question_list = ['Job Level',
                     'Function',
                     'Location',
                     'How long have you been at Whirlpool?',
                     'How long have you been a member of WWN?']

    global section_mapping
    section_mapping = {'s1': 'Membership Demographics'}
    global question_mapping
    question_mapping = {
        "s1": ['Job Level', 'Function', 'Location',
               'How long have you been at Whirlpool?',
               'How long have you been a member of WWN?']}

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
            _df = _df[columns_to_keep]
            df = pd.concat([df, _df], axis=0)

        return df

    location_mapping_dict = {'Remote': 'Remote',
                         'Saint Joseph/Benton Harbor': 'St. Joseph / Benton Harbor',
                         'Manufacturing Facility': 'NAR Manufacturing Facility',
                         'Canada': 'Global',
                         'Riverview': 'St. Joseph / Benton Harbor',
                         'Cleveland, TN': 'NAR Manufacturing Facility',
                         'Yate ':'Global',
                         'Benton Harbor BTC': 'St. Joseph / Benton Harbor',
                         'Chicago': 'World of Whirlpool',
                         'Rio Claro': 'Global',
                         'Cleveland CXC': 'NAR Non-Manufacturing Location Outside SJ / BH',
                         'Cleveland, TN (CXC)': 'NAR Non-Manufacturing Location Outside SJ / BH',
                         'Tulsa': 'NAR Manufacturing Facility',
                         'field ': 'field',
                         'NAR Manufacturing Facility': 'NAR Manufacturing Facility',
                         'St. Joseph / Benton Harbor': 'St. Joseph / Benton Harbor',
                         'World of Whirlpool': 'World of Whirlpool',
                         'NAR Non-Manufacturing Location Outside SJ / BH': 'NAR Non-Manufacturing Location Outside SJ / BH',
                         'Global':'Global'}

    job_function_mapping_dict = {'GSS': 'GSS',
     'Sales': 'Sales',
     'DDM': 'DDM',
     'GIS': 'Global IT',
     'Communications': 'Communications',
     'Marketing': 'Marketing',
     'Consumer Services': 'Consumer Services',
     'Legal': 'Legal',
     'Integrated Supply Chain/ISC': 'ISC / Supply Chain',
     'TX': 'Finance',
     'HR': 'HR',
     'Manufacturing': 'Manufacturing',
     'Finance': 'Finance',
     'GPO': 'GPO',
     'Quality': 'Quality',
     'Consumer Services ': 'Consumer Services',
     'service': 'Consumer Services',
     'Field Service Admin': 'Field Service Admin',
     'Trade Support': 'Trade Support',
     'Customer Service   ': 'Consumer Services',
     'GAME': 'GAME',
     'Merchandising': 'Merchandising',
     'Government Relations': 'Government Relations',
     'CSE': 'CSE',
     'KASA': 'KASA',
     'Flight Attendant': 'Flight Attendant',
     'Product Exchange ': 'Product Exchange ',
     'Training': 'Training',
     'Field Services/Customer Service': 'Consumer Services',
     'Call Center': 'Consumer Services',
     'Technician': 'Technician',
     'CCT': 'Consumer Services',
     'Consumer Services - Field Service': 'Consumer Services',
     'Work Force Management': 'Work Force Management',
     '3rd party/resource': '3rd party/resource',
     'ADI': 'ADI',
     'CALL CENTER CUSTOMER SERVICE ': 'Consumer Services',
     'Cooking': 'Cooking',
     'CS Performance Management': 'Consumer Services',
     'Customer Service': 'Consumer Services',
     'Flight Attendant ': 'Flight Attendant ',
     'IT\\MES': 'Global IT',
     'Project Manager': 'Project Manager',
     'Training and Facilitation': 'Training and Facilitation',
     'TX: Consumer Services': 'Consumer Services',
     'CSBD': 'CSBD',
     'Field Service': 'Field Service',
     'FS/AIG': 'FS/AIG',
     'TX OM Multi-Family': 'TX OM Multi-Family',
     'CX Lead': 'Consumer Services',
     'ISC / Supply Chain': 'ISC / Supply Chain',
     'Admin': 'Admin',
     'Tax': 'Finance',
     'Global IT': 'Global IT',
     'EHS': 'EHS',
     'Prefer not to say': 'Prefer not to say',
     'Program Mgmt/Ops': 'Program Mgmt/Ops',
     'Supplier Quality ': 'Supplier Quality ',
     'Chef for the World of Whirlpool/Training': 'Chef for the World of Whirlpool/Training',
     'KitchenAid': 'KitchenAid'}


    # def _group_cx(x):
    #     if str(x) == 'nan':
    #         return x
    #     else:
    #         _x = x.lower()
    #         if 'service' in _x or 'call' in _x or 'cct' in _x or 'call' in _x or 'cx' in _x:
    #             return 'Customer Service'
    #         else:
    #             return x

    try:
        # READ DATA
        df_comb=get_data()
        df_comb['Timestamp']=pd.to_datetime(df_comb['Timestamp'])
        df_comb['year']=df_comb['Timestamp'].dt.year
        YEAR_LIST=df_comb['year'].unique().tolist()
        YEAR_LIST=sorted(YEAR_LIST, reverse=True)
        # clean the data and remap the question name
        df_comb.columns = [column_rename_dict.get(col, col) for col in df_comb.columns]

        # remap function
        df_comb['s1_q2'] = df_comb['s1_q2'].map(job_function_mapping_dict)
        # remap location
        df_comb['s1_q3'] = df_comb['s1_q3'].map(location_mapping_dict)

        # select the year to  view
        # if All is selected - YOY comparison
        year_filter = st.selectbox("Select the Year", YEAR_LIST+['YOY change'])
        if year_filter=='YOY change':
            YOY_COMPARE=True
            df = df_comb.copy()
        else:
            YOY_COMPARE=False
            year_filter=int(year_filter)
            df = df_comb[df_comb['year'] == year_filter]

        if not YOY_COMPARE:
            # Get the distribution in the current year, and compare it with last year to get the difference
            st.markdown(f'### **{year_filter} Results Overview **')
            num_of_response_by_year = df_comb.groupby("year")['s1_q1'].count()
            num_of_response_this_year = int(num_of_response_by_year.loc[year_filter])

            if year_filter == df_comb['year'].min(): # if the selected year is the earliest year in the list,  return nan
                num_of_response_last_year = np.nan
                difference = ""
                st.metric(f"Responses Received: ", str(num_of_response_this_year), difference)
            else:
                num_of_response_last_year = int(num_of_response_by_year.loc[year_filter - 1])
                difference = num_of_response_this_year - num_of_response_last_year
                difference = str(difference)
                st.metric(f"Responses Received: ", str(num_of_response_this_year), difference + ' responses as compared to last year')

            #####################################################################
            st.markdown(f'### {year_filter} Membership Demographics')
            #####################################################################

            #### Location
            s1_q3_default_value = df['s1_q3'].unique().tolist()
            fig = plot_pie_chart(df, 's1_q3', question_rename_col_mapping , use_regroup_value=False)
            st.write(fig)

            #### Job Level
            df['s1_q1'] = np.where(df['s1_q1'].isnull(), 'No response', df['s1_q1'])
            df['s1_q1_regroup'] = np.where(df['s1_q1'] == 'No response', 'No response',
                                           np.where(df['s1_q1'].isin(['Associate', 'Analyst', 'Senior Analyst']), 'IC',
                                           np.where(df['s1_q1'].isin(['Manager', 'Senior Manager']), 'Mgr&SR Mgr', 'Director&Above')))
            fig = plot_pie_chart(df, 's1_q1',  question_rename_col_mapping, use_regroup_value = False)
            st.write(fig)

            ### Job Function
            s1_q2_default_vaue =[ 'Sales',
                                   'Marketing',
                                   'ISC / Supply Chain',
                                   'Manufacturing',
                                   'Consumer Services',
                                   'GSS',
                                   'Global IT',
                                   'Communications',
                                   'HR',
                                   'GPO',
                                   'Finance',
                                   'Legal']
             # customer service & customer services are the same, the error is due to user input
            df['s1_q2_regroup'] = np.where(df['s1_q2'].isin(s1_q2_default_vaue),
                                           df['s1_q2'],
                                           np.where(df['s1_q2'].isnull(), 'No Response', 'Other'))
            fig = plot_pie_chart(df, 's1_q2', question_rename_col_mapping, use_regroup_value = False)
            st.write(fig)

            ### How long have you been at Whirlpool?
            s1_q4_default_vaue =['Less than 1 year', '1-3 years', '4-9 years', '10+ years']
            df['s1_q4_regroup'] = np.where(df['s1_q4'].isin(s1_q4_default_vaue), df['s1_q4'], 'No response')
            # fig = plot_histogram(df, 's1_q4' , s1_q4_default_vaue + ['No response'],  question_rename_col_mapping, use_regroup_value= True)
            fig = plot_pie_chart(df, 's1_q4',  question_rename_col_mapping, use_regroup_value = True)
            st.write(fig)

            ### How long have you been a member of WWN?
            s1_q5_default_vaue = [ 'Less than 1 year', '1-3 years', '4-9 years', '10+ years']
            df['s1_q5_regroup'] = np.where( df['s1_q5'].isin(s1_q5_default_vaue), df['s1_q5'], 'No response' )
            # fig = plot_histogram(df, 's1_q5' , s1_q5_default_vaue + ['No response'],
            #                      question_rename_col_mapping, use_regroup_value= True)
            fig = plot_pie_chart(df, 's1_q5', question_rename_col_mapping,  use_regroup_value = True)

            st.write(fig)


        else:
            # members by job level and by year
            # YOY change in percentage for Location
            fig = plot_yoy_change_chart(df, 's1_q3',df['s1_q3'].unique().tolist(),question_rename_col_mapping,   use_regroup_value = False)
            st.write(fig)

            # YOY change in percentage for Job Level
            fig = plot_yoy_change_chart(df, 's1_q1',df['s1_q1'].unique().tolist(), question_rename_col_mapping,  use_regroup_value = False)
            st.write(fig)

            #  YoY change in members by Job Function
            s1_q2_default_vaue = [ 'Sales',
                                   'Marketing',
                                   'ISC / Supply Chain',
                                   'Manufacturing',
                                   'Consumer Services',
                                   'GSS',
                                   'Global IT',
                                   'Communications',
                                   'HR',
                                   'GPO',
                                   'Finance',
                                   'Legal']
            # customer service & customer services are the same, the error is due to user input
            df['s1_q2_regroup'] = np.where(
                df['s1_q2'].isin(s1_q2_default_vaue),
                df['s1_q2'],
                np.where(df['s1_q2'].isnull(), "No Response", 'Other'))
            fig = plot_yoy_change_chart(df, 's1_q2', df['s1_q2_regroup'].unique().tolist(), question_rename_col_mapping,  use_regroup_value=True)
            st.write(fig)


           # YOY change in percentage for Job Level
            df['s1_q4_regroup'] = df['s1_q4'].fillna("No Response")
            s1_q4_default_value = [  'Less than 1 year', '1-3 years','4-9 years', '10+ years',  "No Response"  ]
            fig = plot_yoy_change_chart(df, 's1_q4',  s1_q4_default_value,question_rename_col_mapping,  use_regroup_value = True)
            st.write(fig)

           # # YOY change in percentage for Job Level
            s1_q5_default_value = ['Less than 1 year',  '1-3 years',  '4-9 years','10+ years',  "I'm not a member."]
            fig = plot_yoy_change_chart(df, 's1_q5',s1_q5_default_value,  question_rename_col_mapping, use_regroup_value = False)
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