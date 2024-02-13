# Created by WUQ2 at 10/3/2023
import plotly.express as px  # interactive charts

def plot_pie_chart(df, question_no, mapping_dict,  use_regroup_value=False):
    if use_regroup_value:
        val_col = question_no + '_regroup'
    else:
        val_col = question_no
    cnt_ser = df.groupby('year', as_index=False)[val_col].value_counts(). \
        rename(columns={val_col: mapping_dict[question_no]})
    fig = px.pie(cnt_ser,
                 values='count',
                 names=mapping_dict[question_no],
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(
        title=dict(text=mapping_dict[question_no], font=dict(family="Arial", size=15)),
        height=500, width=800,
        font=dict(size=13, color="RebeccaPurple"),
        legend=dict(orientation="h", font=dict(size=14)),
        margin=dict(t=40, b=10, r=5,  l=5))
    fig.update_layout({
    'plot_bgcolor' : 'rgba(0, 0, 0, 0)' ,
    'paper_bgcolor' : 'rgba(0, 0, 0, 0)'
    })
    fig.update_traces(texttemplate='%{percent:.1%}')
    return fig


def plot_barplot(df, question_no, default_value_list, mapping_dict , use_regroup_value=True):
    if use_regroup_value:
        val_col = question_no + '_regroup'
    else:
        val_col = question_no
    count_ser = df.groupby('year', as_index=False)[val_col].value_counts(dropna=False). \
        rename(columns={val_col: mapping_dict[question_no]})
    pct_ser =  df.groupby('year', as_index=False)[val_col].value_counts(dropna=False,normalize = True ). \
        rename(columns={val_col:mapping_dict[question_no] })
    comb_ser = count_ser.merge(pct_ser, on=['year'] + [mapping_dict[question_no]])
    fig = px.bar(data_frame=comb_ser, x=mapping_dict[question_no], y='count',
                 text=comb_ser.apply(lambda x: f"{round(x['count'])} ({round(x['proportion'] *100, 1)}%)" , axis =1  ))
    fig.update_layout(
        title=dict(
            text=mapping_dict[question_no], # add rule to auto break line
            font=dict(family="Arial", size=15),
        ),
        height=400,
        width=1000,
        xaxis_title=None,
        yaxis_title="Number of Responses",
        font=dict(size=10, color="RebeccaPurple"),
        margin=dict(t=40, b=10, r=5,  l=5))
    fig.update_layout({
            'plot_bgcolor' : 'rgba(0, 0, 0, 0)' ,
            'paper_bgcolor' : 'rgba(0, 0, 0, 0)'
            })
    fig.update_xaxes(categoryarray=default_value_list)
    return fig

def plot_yoy_change_chart(df, question_no, default_value_list , mapping_dict,  use_regroup_value = True):
    if use_regroup_value:
        val_col = question_no + '_regroup'
    else:
        val_col = question_no

    tmp = df.groupby('year', as_index=False)[val_col].value_counts(normalize=True).groupby([val_col, 'year'], as_index=False)[
        'proportion'].max()
    tmp['proportion'] = tmp['proportion']
    tmp['change in distribution'] = tmp.groupby([val_col])['proportion'].diff()
    # drop the first year since they're all NAs
    tmp = tmp.dropna(subset=['change in distribution'])
    tmp = tmp.drop(columns=['proportion'])
    tmp = tmp.sort_values(by=[val_col, 'year'])
    tmp['year'] = tmp['year'].astype(str)
    fig = px.bar(tmp,
                 x=val_col,
                 y='change in distribution',
                 color='year',
                 barmode='group',
                 text_auto='.1%',
                 )
    fig.update_layout(
        title=dict(text=mapping_dict[question_no],
                   font=dict(family="Arial", size=15),
                   ),
        xaxis_title="",
        height=500, width=1000,
        legend=dict(orientation="v", font=dict(size=8)),
        font=dict(size=10, color="RebeccaPurple"),
        margin=dict(t=20, b=10, l=5, r=5))
    fig.update_xaxes(categoryarray=default_value_list)
    return fig
