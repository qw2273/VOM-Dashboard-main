# Created by WUQ2 at 3/24/2023
import pandas as pd
import os

dir = r"C:\Users\wuq2\Documents\wwn-vom"

dataset_path =  os.path.normpath(os.path.join(dir,  "data", "Copy of Voice of the Membership - Work Plan.xlsx")  )


question_list  = ['Location', 'How long have you been at Whirlpool?', 'What new Whirlpool policy, benefit, or initiative would be most beneficial to your career development?', 'I understand WWN’s mission to successfully create an inclusive & equitable environment that enables a natural desire to stay & be committed to Whirlpool.', 'I am actively engaged in WWN activities that help drive an inclusive & equitable environment that enables a natural desire to stay & be committed to Whirlpool.', 'Job Level', 'In the past year, which WWN initiatives have you leveraged? Please select all that apply:', 'If you are not currently actively engaged in WWN, what would inspire you to become more involved?', 'Timestamp', 'In the past year, which Whirlpool employee resources have you leveraged? Please select all that apply:', 'How long have you been a member of WWN?', 'What Whirlpool policy, benefit, or initiative is most supportive of your career development?', 'The Every Day Performance Excellence process is successful in differentiating talent and supporting advancement for women at Whirlpool.', 'Function', 'There are policies, benefits, and initiatives in place to ensure my success as a woman at Whirlpool.', 'How could WWN make the biggest impact for women at Whirlpool in the coming year?', 'Why is supporting WWN important to you (as a female or an ally)?']
columns_to_keep =  question_list +  ["What area would you most like to see WWN focus on in NEXT YEAR}? Please choose TWO:"]
columns_to_keep  += ['Year']
year_list = [2021, 2022]

def get_data(year) -> pd.DataFrame:
    return pd.read_excel(dataset_path, sheet_name=f"Annual Survey Responses_{year}")

yr_2021_df  = get_data(2021)