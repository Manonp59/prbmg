import pandas as pd 
import os 
from openai import AzureOpenAI


naming_api_type = os.getenv('NAMING_OPENAI_API_TYPE') 
naming_openai_api_version = os.getenv('NAMING_OPENAI_API_VERSION')
naming_openai_api_base = os.getenv('NAMING_OPENAI_API_BASE')
naming_openai_api_key = os.getenv('NAMING_OPENAI_API_KEY') 

client = AzureOpenAI(api_key=naming_openai_api_key,azure_endpoint=naming_openai_api_base,api_version=naming_openai_api_version)

def make_naming(df):
    data =[]

    for c in (df.clusters.unique()):
        cluster = df.query(f"clusters == {c}")
        docs_str = "\n".join(cluster[cluster['clusters'] == c]['docs'])
        docs_str = docs_str[:130000]
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
            {"role": "system", "content": "You're an IT Service Suppport Manager. You're helping me name each IT incident into problem."},
            {"role": "user", "content": f"Using the following incident descriptions, write a problem title that summarizes all of them.\n\nIncidents:{docs_str}\n\nPROBLEM TITLE:"}
        ]
        )
        problem_title = completion.choices[0].message.content
        print(problem_title)
        df.loc[df.clusters == c, "problem_title"] = problem_title
        
        data.append({'cluster': c, 'problem_title': problem_title})

    
    df_title = pd.DataFrame(data)
    

    return df, df_title


