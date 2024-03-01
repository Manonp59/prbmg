import pandas as pd 

def test_no_duplicates_in_dataframe():
    # Charger le fichier CSV dans un dataframe
    df = pd.read_csv('/home/utilisateur/DevIA/prbmg/df_clean.csv')

    # Vérifier que les incident_number sont uniques
    assert len(df['incident_number']) == len(df['incident_number'].unique())

def test_no_na():
    # Charger le fichier CSV dans un dataframe
    df = pd.read_csv('/home/utilisateur/DevIA/prbmg/df_clean.csv')

    # Vérifier que les incident_number sont uniques
    assert df['incident_number'].isna().sum() == 0
    assert df['description'].isna().sum() == 0
    assert df['category_full'].isna().sum() == 0
    assert df['ci_name'].isna().sum() == 0


def test_data_type():
    df = pd.read_csv('/home/utilisateur/DevIA/prbmg/df_clean.csv')
    assert df['incident_number'].dtype == "object"
    assert df['description'].dtype == "object"
    assert df['category_full'].dtype == "object"
    assert df['ci_name'].dtype == "object"

