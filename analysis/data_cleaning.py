from data_mgmt.data_frame_analysis import extract_column_data

def clear_duplicate_uids(df):
    """
    Given a DataFrame with UIDs in the headers, return a new DataFrame with repeated UIDs removed.

    Args:
    df (Pandas DataFrame): The DataFrame to deduplicate
    """
    uids = set()

    def is_not_duplicate(col_name):
        nonlocal uids
        col_data = extract_column_data(col_name)
        uid = col_data['uid']
        if(uid in uids):
            return False
        else:
            uids.add(uid)
            return True

    df_included_columns = [col_name for col_name in df.columns[1:] if is_not_duplicate(col_name)]
    return df[df_included_columns]

def clear_blacklisted_uids(df, blacklist):
    """
    Given a DataFrame with UIDs in the headers, return a new DataFrame with blacklisted UIDs
      removed.

    Args:
    df (Pandas DataFrame): The DataFrame to deduplicate
    blacklist (list): The list of uids to not include in the output DataFrame.
    """
    df_included_columns = [col_name for col_name in df.columns[1:] if extract_column_data(col_name)['uid'] not in blacklist]
    return df[df_included_columns]