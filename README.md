# Python 3 function to assign compact letter display letters

Function to apply compact letter display for pairwise contrasts.
Groups with no significant differences share a letter.

## Parameters:


```python
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
```

## Installation


```python
pip install cld4py
```
