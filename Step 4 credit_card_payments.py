


import pandas as pd
import numpy as np
bereau_df = pd.read_csv('bureau.csv')



def generate_credit_card_dataset(input_df):
    """
    Generate a credit card statement dataset based on an input DataFrame.
    
    Parameters:
    input_df (pd.DataFrame): Input DataFrame containing SK_ID_CURR and other relevant data.
    
    Returns:
    pd.DataFrame: Generated credit card dataset with the required columns.
    """
    num_records = len(input_df)
    
    output_df = pd.DataFrame()
    
    # Generating synthetic values for each column
    output_df['SK_ID_PREV'] = np.random.randint(1000000, 9999999, num_records)
    output_df['sk_id_curr'] = input_df['sk_id_curr']
    output_df['MONTHS_BALANCE'] = np.random.randint(-60, 0, num_records)
    
    # Assign AMT_CREDIT_LIMIT_ACTUAL from amt_credit_sum_limit for corresponding SK_ID_CURR
    output_df = output_df.merge(input_df[['sk_id_curr', 'amt_credit_sum_limit']], on='sk_id_curr', how='left')
    num_records = len(output_df) 
    output_df.rename(columns={'amt_credit_sum_limit': 'AMT_CREDIT_LIMIT_ACTUAL'}, inplace=True)
    
    # Interlinked amount columns
    credit_limit = output_df['AMT_CREDIT_LIMIT_ACTUAL'].fillna(0).astype(float)
    output_df['AMT_BALANCE'] = np.random.uniform(0, credit_limit * 0.9).round(2)
    output_df['AMT_DRAWINGS_ATM_CURRENT'] = np.random.uniform(0, credit_limit * 0.2).round(2)
    output_df['AMT_DRAWINGS_OTHER_CURRENT'] = np.random.uniform(0, credit_limit * 0.1).round(2)
    output_df['AMT_DRAWINGS_POS_CURRENT'] = np.random.uniform(0, credit_limit * 0.3).round(2)
    output_df['AMT_DRAWINGS_CURRENT'] = (
        output_df['AMT_DRAWINGS_ATM_CURRENT'] + 
        output_df['AMT_DRAWINGS_OTHER_CURRENT'] + 
        output_df['AMT_DRAWINGS_POS_CURRENT']
    ).round(2)
    output_df['AMT_INST_MIN_REGULARITY'] = np.random.uniform(100, credit_limit * 0.05).round(2)
    output_df['AMT_PAYMENT_CURRENT'] = np.random.uniform(0, output_df['AMT_BALANCE'] * 0.8).round(2)
    output_df['AMT_PAYMENT_TOTAL_CURRENT'] = (output_df['AMT_PAYMENT_CURRENT'] + np.random.uniform(0, output_df['AMT_INST_MIN_REGULARITY'])).round(2)
    output_df['AMT_RECEIVABLE_PRINCIPAL'] = np.random.uniform(0, output_df['AMT_BALANCE']).round(2)
    output_df['AMT_RECIVABLE'] = (output_df['AMT_RECEIVABLE_PRINCIPAL'] + np.random.uniform(0, output_df['AMT_INST_MIN_REGULARITY'])).round(2)
    output_df['AMT_TOTAL_RECEIVABLE'] = (output_df['AMT_RECIVABLE'] + np.random.uniform(0, output_df['AMT_INST_MIN_REGULARITY'])).round(2)
    
    # Count-based columns with mostly 0 values (90%)
    mask = np.random.rand(num_records) < 0.9
    output_df['CNT_DRAWINGS_ATM_CURRENT'] = np.where(mask, 0, np.random.randint(1, 10, num_records))
    output_df['CNT_DRAWINGS_OTHER_CURRENT'] = np.where(mask, 0, np.random.randint(1, 5, num_records))
    output_df['CNT_DRAWINGS_POS_CURRENT'] = np.where(mask, 0, np.random.randint(1, 10, num_records))
    output_df['CNT_DRAWINGS_CURRENT'] = (
        output_df['CNT_DRAWINGS_ATM_CURRENT'] + 
        output_df['CNT_DRAWINGS_OTHER_CURRENT'] + 
        output_df['CNT_DRAWINGS_POS_CURRENT']
    )
    output_df['CNT_INSTALMENT_MATURE_CUM'] = np.where(mask, 0, np.random.randint(1, 20, num_records))
    
    output_df['NAME_CONTRACT_STATUS'] = np.random.choice(['Active', 'Completed', 'Signed', 'Canceled'], num_records)
    output_df['SK_DPD'] = np.random.randint(0, 60, num_records)
    output_df['SK_DPD_DEF'] = output_df['SK_DPD'] - np.random.randint(0, 5, num_records)
    output_df['SK_DPD_DEF'] = output_df['SK_DPD_DEF'].clip(lower=0)  # Ensuring non-negative values
    
    return output_df

# Example usage
if __name__ == "__main__":
    # Creating a sample input DataFrame with SK_ID_CURR
    input_data = bereau_df.loc[bereau_df['credit_type'] == "Credit Card Loan", ['sk_id_curr', 'amt_credit_sum_limit']]
    generated_df = generate_credit_card_dataset(input_data)
    generated_df.to_csv("creditcard.csv", index=False)





