import string
import pandas as pd


def assign_letters(df, G1, G2, P, alpha=.05,
           order=None, data=None, vals=None, group=None):
    """
    Function to apply compact letter display for pairwise contrasts.
    Groups with no significant differences share a letter.
    
    Parameters:
    
      Required:
        df    - dataframe with contrasts (pairwise comparisons).
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
    df[P] = df[P].apply(pd.to_numeric)
    
    #define order
    if order == None:
        order = sorted(set(df[G1].tolist() + df[G2].tolist()))
    if order in ['ascending', 'descending']:
        asc = order=='ascending'
        data[vals] = data[vals].apply(pd.to_numeric)
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


def plot_letters(cld, data, vals, group, figax, 
                axis='x', plot='boxplot', pos='upper',
                pad=1, c='black', fs=None, lim=0):
    """
    Function to plot CLD letters for sns boxplot, violinplot, barplot or swarmplot.
    Groups with no significant differences share a letter.
    
    Parameters:
    
      Required:
        cld    - dataframe or dictionary with groups and letters. If df then groups 
                 should be in the index and letters in the "Letters" column.
        data   - dataframe with values that were plotted.
        vals   - column in data with compared values.
        group  - column in data with group information.
        figax  - matplotlib or sns figure or ax with plot.
        
      Optional:
        axis   - axis with plotted groups: "x" or "y" (default "x").
        plot   - plot type: "boxplot", "violinplot", "barplot" or "swarmplot"
                 (default "boxplot").
        pos    - letters position: "upper", "lower", "top" or "bottom" 
                 (default: "upper"). If axis = "y", "upper" and "top" will be 
                 plotted on the right side, "lower" and "bottom" - on the left.
        pad    - distance (% of data range) to the plotted group object (default 1).     
        c      - color of letters.
        fs     - fontsize of letters.
        lim    - increase axes limits, expressed in "pad" (see above) values (default 0)
    """
    
    #import
    import seaborn as sns
    import matplotlib.pyplot as plt
    from matplotlib.cbook import boxplot_stats

    types = ['boxplot', 'violinplot', 'barplot', 'swarmplot']
    labels = figax.get_xticklabels() if axis=="x" else figax.get_yticklabels()
    
    #check parameters
    if axis not in "xy":
        raise ValueError('axis should by either "x" or "y"')
    if plot not in types:
        raise ValueError(f'"{plot}" is not in the list of supported types')
    if pos not in ["upper", "lower", "top", "bottom"]:
        raise ValueError('pos should by either "upper", "lower", "top" or "bottom"')
    if not any([isinstance(cld, pd.DataFrame), isinstance(cld, dict)]):
        raise ValueError('cld should by either dataframe or dictionary')
    if fs ==  None:
        fs = labels[0].get_fontsize()
        
    #set limits
    step = (data[vals].max()-data[vals].min())/100*(pad+1)
    if axis=="y":
        va = 'center'
        lims = figax.get_xlim()
        if pos in ['upper', 'top']:
            figax.set_xlim(min(lims), max(lims)+lim*step)
        else:
            figax.set_xlim(min(lims)-lim*step, max(lims))
    if axis=="x":
        lims = figax.get_ylim()
        if pos in ['upper', 'top']:
            figax.set_ylim(min(lims), max(lims)+lim*step)
        else:
            figax.set_xlim(min(lims)-lim*step, max(lims))

    #plot letters
    pos_dict = {
        'top': max(figax.get_ylim())-step if axis=='x' else max(figax.get_xlim())-step,
        'bottom': min(figax.get_ylim())+step if axis=='x' else min(figax.get_xlim())+step}
    
    if axis=='x':
        ha = 'center'
        va = 'bottom' if pos in ['upper', 'bottom'] else 'top'
    if axis=='y':
        va = 'center'
        ha = 'left' if pos in ['upper', 'bottom'] else 'right'
    if not isinstance(cld, dict):
        cld = {i: cld.loc[i, 'Letters'] for i in cld.index}
        
    for i, label in enumerate(labels):
        df = data.loc[data[group]==label.get_text()]
        x, y = label.get_position()

        #boxplot
        if plot == 'boxplot':
            pos_dict.update({'upper': boxplot_stats(df[vals])[0]['whishi'] + step})
            pos_dict.update({'lower': boxplot_stats(df[vals])[0]['whislo'] - step})
            
        #violinplot
        if plot == 'violinplot':
            pos_dict.update({'upper': df[vals].max() + step*2})
            pos_dict.update({'lower': df[vals].min() - step*2})
            
        #barplot
        if plot == 'barplot':
            line = figax.lines[i]
            gain = line.get_ydata() if axis=="x" else line.get_xdata()
            pos_dict.update({'upper': step + abs(max(gain))})
            pos_dict.update({'lower': -step + abs(min(gain))})
        
        #swarmplot
        if plot == 'swarmplot':
            pos_dict.update({'upper': df[vals].max() + step})
            pos_dict.update({'lower': df[vals].min() - step})
            
        xpos = x if axis=="x" else pos_dict[pos]
        ypos = y if axis=="y" else pos_dict[pos]   
        if plot == 'barplot':
            mn, mx = 0, max(lims)+lim*step
            [figax.set_ylim(mn, mx) if axis=='x' else figax.set_xlim(mn, mx)]
                        
        figax.text(xpos, ypos, cld[label.get_text()], size=fs, color=c, ha=ha, va=va,)