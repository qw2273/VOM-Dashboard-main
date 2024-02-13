from urllib.error import URLError
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import re
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import numpy as np
nltk.download('stopwords')
import operator
import spacy
from nltk import bigrams, FreqDist, ngrams
import collections
import sys
import os

if st.session_state["authentication_status"]:
    st.set_page_config(page_title="VOM Survey - Membership Support",layout="wide" , page_icon="🙌")
    st.markdown("# Membership Support")

    global data_folder_dir
    dir = os.getcwd()
    data_folder_dir = os.path.join(dir, "data")

    sys.path.append(os.path.join(dir, "code"))
    from utility_function import plot_pie_chart, plot_barplot, plot_yoy_change_chart

    question_list = ['There are policies, benefits, and initiatives in place to ensure my success as a woman at Whirlpool.',
               'The Every Day Performance Excellence process is successful in differentiating talent and supporting advancement for women at Whirlpool.',
               'What Whirlpool policy, benefit, or initiative is most supportive of your career development?',
               'What new Whirlpool policy, benefit, or initiative would be most beneficial to your career development?',
               'What area would you most like to see WWN focus on next year? Please choose TWO:',
               'In the past year, which WWN initiatives have you leveraged? Please select all that apply:',
               'In the past year, which Whirlpool employee resources have you leveraged? Please select all that apply:']

    global section_mapping
    section_mapping = {   's2': 'Membership Support'  }

    global question_mapping
    question_mapping = { "s2": ['There are policies, benefits, and initiatives in place to ensure my success as a woman at Whirlpool.',
               'The Every Day Performance Excellence process is successful in differentiating talent and supporting advancement for women at Whirlpool.',
               'What Whirlpool policy, benefit, or initiative is most supportive of your career development?',
               'What new Whirlpool policy, benefit, or initiative would be most beneficial to your career development?',
               'What area would you most like to see WWN focus on next year? Please choose TWO:',
               'In the past year, which WWN initiatives have you leveraged? Please select all that apply:',
               'In the past year, which Whirlpool employee resources have you leveraged? Please select all that apply:'] }

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
    scale_mapping = {1: 'Strongly Disagree', 2: 'Disagree', 3: 'Neutral', 4: 'Agree', 5: 'Strongly Agree',
                     0: 'No response'}
    scale_cat_list = list(scale_mapping.values())

    s2_q5_default_list = ['Flexibility / Work-Life Balance',
                          'Personal Development',
                          'Exposure to Female Leaders',
                          'Mentorship',
                          'Whirlpool Policies / Benefits',
                          'Networking',
                          'Sponsorship']
    s2_q6_default_list = ['Networking / Social Events',
                          'Speak Up for Diversity',
                          'Career Compass Round Robin',
                          'Personal Branding',
                          'Courageous Conversations',
                          'Culture Catalyst Training',
                          'Policy Education',
                          'Professional Development Competency Series',
                          'None of the Above',]

    s2_q7_default_list = [ 'Whirlpool Health Coach',
                           'Be*Well Pathways / Resources',
                           'LifeWorks',
                           'Whirlpool Human Resources',
                           'Other ERGs',
                           'None of the Above',
                           ]
    def get_data() -> pd.DataFrame:
        df = None
        columns_to_keep = ['Timestamp'] + question_list
        for f in os.listdir(data_folder_dir):
            year_str = f.split("_")[-1].split('.')[0]
            _df = pd.read_excel(os.path.join(data_folder_dir, f))
            _df.rename(columns={f"What area would you most like to see WWN focus on in {int(year_str) + 1}? Please choose TWO:" :
                                'What area would you most like to see WWN focus on next year? Please choose TWO:'
                                }, inplace=True)
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
            st.markdown(f'### **{year_filter} Results Overview ** ')

            df['s2_q1'] =  df['s2_q1'].fillna( 0)
            df['s2_q1_regroup'] = df['s2_q1'].map(scale_mapping )
            fig = plot_barplot(df, 's2_q1', scale_cat_list,
                                 question_rename_col_mapping, use_regroup_value=True)
            st.write(fig)


            df['s2_q2'] =  df['s2_q2'].fillna( 0)
            df['s2_q2_regroup'] = df['s2_q2'].map(scale_mapping )
            fig = plot_barplot(df, 's2_q2', scale_cat_list,
                                 question_rename_col_mapping, use_regroup_value=True)
            st.write(fig)


            # st.markdown(f'#####  What area would you most like to see WWN focus on in {year_filter+1}? Pick Two')
            # counter = collections.Counter(sum([val.strip().split(", ") for val in df['s2_q5'].dropna().values], []))
            # area_to_focus = {tup[0]: tup[1] for tup in counter.most_common() if tup[1] > 0}
            # area_to_focus = pd.DataFrame.from_dict(area_to_focus, orient='index').reset_index().rename( columns={'index': 'Area', 0: 'count'})
            _value= sum([val.strip().split(", ") for val in df['s2_q5'].dropna().values], [])
            tmp = pd.DataFrame(data = { 's2_q5': _value})

            tmp['s2_q5'] = np.where(tmp['s2_q5'] == 'Whirlpool Policies/Benefits',  'Whirlpool Policies / Benefits', tmp['s2_q5'] )
            tmp['s2_q5']  = np.where(tmp['s2_q5'].isin(s2_q5_default_list),   tmp['s2_q5'] , 'Other')
            area_to_focus = tmp.groupby(['s2_q5'], as_index= False).value_counts()
            fig = px.pie(area_to_focus, values='count', names='s2_q5',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            print(f"What area would you most like to see WWN focus on { int(year_filter) +1 }?")
            fig.update_layout(
                title=dict(text=f"What area would you most like to see WWN focus on in { int(year_filter) +1 }?", font=dict(family="Arial", size=15)),
                height=500, width=600,
                font=dict(size=10, color="RebeccaPurple"),
                legend=dict(orientation="h", font=dict(size=10)),
                margin=dict(t=30,  b=10,r=5, l=5))
            fig.update_layout({
            'plot_bgcolor' : 'rgba(0, 0, 0, 0)' ,
            'paper_bgcolor' : 'rgba(0, 0, 0, 0)'
            })
            fig.update_traces(texttemplate='%{percent:.1%}')
            st.write(fig)

            # st.markdown(f'##### In the past year, which Whirlpool employee resources have you leveraged?')
            # counter = collections.Counter(sum([val.strip().split(", ") for val in df['s2_q7'].dropna().values], []))
            # rsc_has_leverage = {tup[0]: tup[1] for tup in counter.most_common() if tup[1] > 1}
            # rsc_has_leverage = pd.DataFrame.from_dict(rsc_has_leverage, orient='index').reset_index().rename(  columns={'index': 'Resource', 0: 'count'})
            _value = sum([val.strip().split(", ") for val in df['s2_q7'].dropna().values], [])
            tmp = pd.DataFrame(data={'s2_q7': _value})
            tmp['s2_q7'] = np.where('LifeWorks' in  tmp['s2_q7'], 'LifeWorks', tmp['s2_q7'])
            tmp['s2_q7'] = np.where(  tmp['s2_q7'] == 'Employee Well-Being & Support Channel / WHR360', 'Be*Well Pathways / Resources',   tmp['s2_q7'])
            tmp['s2_q7_regroup'] = np.where(tmp['s2_q7'].isin(s2_q7_default_list), tmp['s2_q7'], 'Other')
            rsc_has_leverage = tmp.groupby(['s2_q7_regroup'], as_index=False).value_counts()
            fig = px.pie(rsc_has_leverage, values='count', names='s2_q7_regroup',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(
                title=dict(text= "In the past year, which Whirlpool employee resources have you leveraged?", font=dict(family="Arial", size=15)),
                height=500, width=600,
                font=dict(size=10, color="RebeccaPurple"),
                legend=dict(orientation="h", font=dict(size=10)),
                margin=dict(t=30, b=10, r=5, l=5))
            fig.update_layout({
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)'
            })
            fig.update_traces(texttemplate='%{percent:.1%}')
            st.write(fig)

            # st.markdown(f'##### In the past year, which WWN initiatives have you leveraged?')
            # counter = collections.Counter(sum([val.strip().split(", ") for val in df['s2_q6'].dropna().values], []))
            # initiative_has_leverage = {tup[0]: tup[1] for tup in counter.most_common() if tup[1] > 1}
            # initiative_has_leverage = pd.DataFrame.from_dict(initiative_has_leverage, orient='index').reset_index().rename(
            #     columns={'index': 'Initiative', 0: 'count'})

            _value = sum([val.strip().split(", ") for val in df['s2_q6'].dropna().values], [])
            tmp = pd.DataFrame(data={'s2_q6': _value})
            tmp['s2_q6_regroup'] = np.where( tmp['s2_q6'].isin( s2_q6_default_list), tmp['s2_q6'], 'Other')
            initiative_has_leverage = tmp.groupby(['s2_q6_regroup'], as_index=False).value_counts()
            fig = px.pie(initiative_has_leverage, values='count', names='s2_q6_regroup',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(
                title=dict(text= "In the past year, which WWN initiatives have you leveraged?", font=dict(family="Arial", size=15)),
                height=500, width=600,
                font=dict(size=10, color="RebeccaPurple"),
                legend=dict(orientation="h", font=dict(size=10)),
                margin=dict(t=30, b=10, r=5, l=5))
            fig.update_layout({
                'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                'paper_bgcolor': 'rgba(0, 0, 0, 0)'
            })
            fig.update_traces(texttemplate='%{percent:.1%}')
            st.write(fig)

            # word cloud
            st.markdown('##### What Whirlpool policy, benefit, or initiative is most supportive of your career development?')
            def _clean_txt(x):
                if str(x) == 'nan':
                    return x
                else:
                    return re.sub('[^A-Za-z]+', ' ', x).lower()

            def _lemmatize_word(spacy_model,line, STOPWORD_LIST ) :
                """clean the text, lemmatized the word, then excludethe non-noun word
                return: list of lemmatized words
                """
                # # excluded tags
                excluded_tags = { "VERB", "ADJ", "ADV", "ADP", "PROPN"}
                _lemmatize_word = []
                doc = spacy_model(line)
                for token in doc:
                    if  token.pos_ not in excluded_tags and token.text not in STOPWORD_LIST:
                        if len(token.text.strip()) > 0: # keep the token with a character
                            _lemmatize_word += [token.lemma_]
                return _lemmatize_word

            def _plot_word_cloud( ngram_freq_dict, stopwords_list):
                # plot the wordcloud, to show the benefits that wwn members most valued
                wordcloud = WordCloud(stopwords=stopwords_list,  background_color="white").generate_from_frequencies(ngram_freq_dict)
                # Display the generated image:
                fig, ax = plt.subplots(figsize=(4, 3))
                ax.imshow(wordcloud, interpolation='bilinear')
                plt.axis("off")
                st.pyplot(fig)

            def word_cloud_gen_wrapper(col, data, stopwords_list, ngram=2, ngram_freq_thres=3):
                data[col] = data[col].apply(lambda x: _clean_txt(x))

                text = "; ".join(comment.lower() if (str(comment) != 'nan') & (comment != 'none') else "" for comment in data[col])
                nlp = spacy.load('en_core_web_sm')

                lemmatized_word_list = []
                for _line in text.split("; "):
                    lemmatized_word_list += _lemmatize_word(nlp, _line, stopwords_list)
                # bigrams and count the freq
                ngram_freq_dist = FreqDist(ngrams(lemmatized_word_list, ngram))
                # trigram_freq_dist = FreqDist(ngrams(lemmatized_word_list,3 ))

                # combine the bigrams into a single term
                ngram_freq_dict = {}
                for _k, v in sorted(ngram_freq_dist.items(), key=operator.itemgetter(1), reverse=True):
                    k = " ".join(_k)
                    if v >= ngram_freq_thres:
                        ngram_freq_dict[k] = v

                return ngram_freq_dict

            STOPWORD_LIST = list ( stopwords.words('english') )  + ['none']  + ['whirlpool', 'women', 'network']  + ['work']
            ngram_freq_dict = word_cloud_gen_wrapper('s2_q3', df, STOPWORD_LIST, ngram=2, ngram_freq_thres=2)
            _plot_word_cloud( ngram_freq_dict, STOPWORD_LIST)

            st.markdown('#####  What __new__ Whirlpool policy, benefit, or initiative would be most beneficial to your career development?')
            ngram_freq_dict = word_cloud_gen_wrapper('s2_q4', df, STOPWORD_LIST, ngram=2, ngram_freq_thres= 2 )
            _plot_word_cloud( ngram_freq_dict, STOPWORD_LIST)

        else:

            df['s2_q1'] = df['s2_q1'].fillna(0)
            df['s2_q1_regroup'] = df['s2_q1'].map(scale_mapping)
            fig = plot_yoy_change_chart(df, 's2_q1', scale_cat_list, question_rename_col_mapping,  use_regroup_value=True)
            st.write(fig)

            df['s2_q2'] = df['s2_q2'].fillna(0)
            df['s2_q2_regroup'] = df['s2_q2'].map(scale_mapping)
            fig = plot_yoy_change_chart(df, 's2_q2',scale_cat_list, question_rename_col_mapping,   use_regroup_value=True)
            st.write(fig)

            yoy_compare_1 = None
            for year in YEAR_LIST:
                _tmp = df[df['year']==year]
                _value = sum([val.strip().split(", ") for val in _tmp['s2_q5'].dropna().values], [])
                _yoy_compare = pd.DataFrame(data = { 'year': year, 's2_q5':_value })
                _yoy_compare['s2_q5'] = np.where(_yoy_compare['s2_q5'] == 'Whirlpool Policies/Benefits', 'Whirlpool Policies / Benefits', _yoy_compare['s2_q5'] )
                _yoy_compare['s2_q5_regroup'] = np.where(_yoy_compare['s2_q5'].isin(s2_q5_default_list ),_yoy_compare['s2_q5'] , 'Other' )
                yoy_compare_1 = pd.concat([yoy_compare_1, _yoy_compare], axis = 0)
            fig = plot_yoy_change_chart(yoy_compare_1, 's2_q5', s2_q5_default_list , question_rename_col_mapping, True)
            st.write(fig)

            yoy_compare_2 = None
            for year in YEAR_LIST:
                _tmp = df[df['year'] == year]
                _value = sum([val.strip().split(", ") for val in _tmp['s2_q7'].dropna().values], [])
                _yoy_compare = pd.DataFrame(data={'year': year, 's2_q7': _value})
                _yoy_compare['s2_q7'] = np.where( _yoy_compare['s2_q7'].str.contains('Lifeworks' ) , 'LifeWorks', _yoy_compare['s2_q7'])
                _yoy_compare['s2_q7'] = np.where(_yoy_compare['s2_q7'] == 'Employee Well-Being & Support Channel / WHR360',  'Be*Well Pathways / Resources', _yoy_compare['s2_q7'])
                _yoy_compare['s2_q7_regroup'] = np.where(_yoy_compare['s2_q7'].isin(s2_q7_default_list), _yoy_compare['s2_q7'], 'Other')
                yoy_compare_2 = pd.concat([yoy_compare_2, _yoy_compare], axis=0)
            fig = plot_yoy_change_chart(yoy_compare_2, 's2_q7', s2_q7_default_list, question_rename_col_mapping, True)
            st.write(fig)

            yoy_compare_3 = None
            for year in YEAR_LIST:
                _tmp = df[df['year']==year]
                _value = sum([val.strip().split(", ") for val in _tmp['s2_q6'].dropna().values], [])
                _yoy_compare = pd.DataFrame(data = { 'year': year, 's2_q6':_value })
                _yoy_compare['s2_q6_regroup'] = np.where(_yoy_compare['s2_q6'].isin(s2_q6_default_list), _yoy_compare['s2_q6'], 'Other')
                yoy_compare_3 = pd.concat([yoy_compare_3, _yoy_compare], axis = 0)
            fig = plot_yoy_change_chart(yoy_compare_3, 's2_q6', s2_q6_default_list , question_rename_col_mapping, True)
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