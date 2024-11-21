import string
import pandas as pd

def cld4py(df, G1, G2, P, alpha=.05,
           order=None, data=None, vals=None, group=None):
    """
    Function to apply compact letter display for pairwise contrasts.
    Groups with no significant differences share a letter.
    
    Parameters:
      Required:
        df     - dataframe with contrasts (pairwise comparisons).
        G1, G2 - columns in contrasts df with compared groups.
        P      - column in contrasts df with p-value (adjusted, right?).
      Optional:
        alpha  - sigificance level (default 0.05).
        order  - None (default), list or ['ascending', 'descending'].
                 This parameter will define the order of assigned letters.
                 None - alphabetical order will be applied.
                 List - order of groups will be defined by that list.
                 String 'ascending' or 'descending' requires parameters
                 'data', 'values' and 'group' to order groups by the mean.
        data   - dataframe with values that were compared to get contrasts.
        vals   - column in data with compared values.
        group  - column in data with group information.
    """
    
    #helper function to check p
    def is_sign(lv1, lv2, df=df, alpha=alpha):
        return df.loc[(df[G1]==lv1)&(df[G2]==lv2)|(df[G1]==lv2)&(df[G2]==lv1),P].iloc[0] < alpha
          
    letters = string.ascii_lowercase
    df[P] = df[P].apply(pd.to_numeric, errors='ignore')
    
    #define order
    if order == None:
        order = sorted(set(df[G1].tolist() + df[G2].tolist()))
    if order in ['ascending', 'descending']:
        asc = order=='ascending'
        data[vals] = data[vals].apply(pd.to_numeric, errors='ignore')
        order = pd.DataFrame(data.groupby(group)[vals].mean()).sort_values(vals, ascending=asc).index.tolist()

    #assign letters
    draft, sets = {}, []
    for i, l1 in enumerate(order):
        draft.update({i: {l1}})
        for l2 in order: 
            if l1 != l2 and not any([is_sign(l1,l2)]+[is_sign(l,l2) for l in draft[i]]):
                    draft[i].add(l2)
    [sets.append(v) for v in draft.values() if v not in sets]
    cld = pd.DataFrame(columns=['Group', 'Letters'])
    for i,l in enumerate(order):
        cld.loc[i, ['Group', 'Letters']] = l, ''.join([letters[j] for j,s in enumerate(sets) if l in s])
    return cld.set_index('Group')