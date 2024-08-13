from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.http import Http404
from prbmg import settings
from .forms import LoginForm,UpdateUserForm, SignUpForm, UploadFileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
import io 
import os 
import requests
import re
import json 
from datetime import datetime
from prbmg.opentelemetry_setup import logger




def home(request):
    """Vue pour la page d'accueil du site. Affiche des statistiques sur les rendez-vous
    à venir et les créneaux horaires libres si le coach est connecté. Sinon il affiche la présentation du coach et ses prestations.

    Args:
        request : requête HTTP reçue par la vue

    Returns:
        - réponse HTTP avec un template rendu contenant les statistiques suivantes pour le coach :
            - le nombre de rendez-vous à venir 
            - le nombre de créneaux horaires libres
            - la date courante au format 'YYYY-MM-DD'
            - l'heure courante au format 'HH:MM'
    """
    return render(request, 'home.html')


def login_page(request):
    """
    Vue pour la page de connexion du site. Permet à un utilisateur de se connecter avec son nom d'utilisateur
    et son mot de passe, puis redirige l'utilisateur vers la page d'accueil si les informations de connexion
    sont valides.

    Parameters:
    - request: requête HTTP reçue par la vue

    Returns:
    - réponse HTTP avec un template rendu contenant un formulaire de connexion et un message d'erreur (si applicable)
      - si le formulaire est soumis et valide, l'utilisateur est authentifié et redirigé vers la page d'accueil
      - sinon, le formulaire est réaffiché avec un message d'erreur indiquant que les identifiants sont invalides
    """
    form = LoginForm()
    message = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                logger.info(f'User {user.username} successfully logged in.')
                return redirect('home')
            else:
                message = 'Invalid password or username'
                logger.warning(f'Failed login attempt for username: {form.cleaned_data["username"]}')
    return render(
        request, 'login.html', context={'form': form, 'message': message})


@login_required(login_url='login')
def logout_user(request):
    """
    Vue pour la déconnexion de l'utilisateur connecté. Déconnecte l'utilisateur actuel et le redirige vers la
    page d'accueil.

    Parameters:
    - request: requête HTTP reçue par la vue

    Returns:
    - réponse HTTP avec une redirection vers la page d'accueil
    """
    user = request.user
    logout(request)
    logger.info(f'User {user.username} logged out.')
    return redirect('home')


def signup_page(request):
    """
    Vue pour la page d'inscription du site. Affiche un formulaire d'inscription permettant à un nouvel utilisateur
    de créer un compte. Si le formulaire est soumis et valide, le nouvel utilisateur est enregistré et connecté automatiquement, puis redirigé vers la
    page d'accueil.

    Parameters:
    - request: requête HTTP reçue par la vue

    Returns:
    - réponse HTTP avec un template rendu contenant un formulaire d'inscription
      - si le formulaire est soumis et valide, un nouvel utilisateur est créé et connecté, puis l'utilisateur est
        redirigé vers la page d'accueil
      - sinon, le formulaire est réaffiché avec les erreurs de validation appropriées
    """
    form = SignUpForm()
    message = ''
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'New user signed up and logged in: {user.username}')
            return redirect('home')
    return render(request, 'signup.html', {'form':form})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        
        if form.is_valid():
            user = form.save()
            login(request, user)  
            logger.info(f'User profile updated for {user.username}')
            messages.success(request, 'Vos modifications ont bien été prises en compte ✅')
            return redirect('update_user')
        else:
            # Afficher les erreurs du formulaire dans les messages
            for field, errors in form.errors.items():
                for error in errors:
                    logger.error(f"Error in field {field} for user {user.username}: {error}")
                    messages.error(request, f"Erreur dans le champ {field}: {error}")
    else:
        form = UpdateUserForm(instance=user)
    
    return render(request, 'update_user.html', {'form': form})

def handle_uploaded_file(f):
    df = pd.read_csv(io.StringIO(f.read().decode('utf-8')), index_col=False)
    logger.info(f'File uploaded with {len(df)} rows.')
    print(df.columns)
    mask_origin_request = df["Origin of Request"] == "Monitoring"
    mask_requesting_person = df["Requesting Person"] == "REST API - ZABBIX"
    df = df[mask_origin_request & mask_requesting_person]
    clean_names = {}
    for col in df.columns:
        # Remplacer les espaces par des _
        new_name = col.strip().lower().replace(' ', '_')
        # Retirer tous les caractères spéciaux
        new_name = re.sub('[^a-zA-Z0-9_]', '', new_name)
        clean_names[col] = new_name

    # Renommer les colonnes avec les nouveaux noms nettoyés
    df = df.rename(columns=clean_names)
    df = df.drop_duplicates(subset='incident_number')
    df = df.dropna(subset='incident_number')

    
    return df

API_URL = "http://prbmg-api-ia.francecentral.azurecontainer.io:8001/predict"
API_KEY = os.getenv('API_IA_SECRET_KEY')

def process_clustering(df):
    API_URL = "http://prbmg-api-ia.francecentral.azurecontainer.io:8001/predict"
    API_KEY = os.getenv('API_IA_SECRET_KEY')
    headers = {"X-API-Key": API_KEY}
    df['cluster_number'] = None
    df['problem_title'] = None
    for index, row in df.iterrows():
        data = {
            "incident_number": row['incident_numbers'],
            "creation_date": row['creation_date'],
            "description": row['description'],
            "category_full": row["category_full"],
            "ci_name": row["ci_name"],
            "location_full": row['location_full']
        }


        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            df.at[index, 'cluster_number'] = result.get('cluster_number')
            df.at[index, 'problem_title'] = result.get('problem_title')
        else:
            logger.error(f'API request error for incident {row["incident_number"]}')
            df.at[index, 'cluster_number'] = 'Error'
            df.at[index, 'problem_title'] = f"Error for incident {row['incident_number']}"

    return df

def get_location(df):
    API_URL = "http://prbmg-api-database.francecentral.azurecontainer.io:8000/ci_location"
    API_KEY = os.getenv('API_DATABASE_SECRET_KEY')
    print(API_KEY)
    headers = {"X-API-Key": API_KEY}
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        ci_location_data = response.json()
        logger.info(f'CI Location data fetched and merged into dataframe.')
    else:
        logger.error(f'API request error while fetching CI Location data')
        raise Exception(f"Failed to fetch CI Location data: {response.status_code} {response.text}")
        

    # Création d'un dictionnaire pour un accès rapide
    ci_location_dict = {item['ci_name']: item['location_full'] for item in ci_location_data}
    for index, row in df.iterrows():
        df['location_full'] = df['ci_name'].apply(lambda x: ci_location_dict.get(x, None))
    
    return df


@login_required(login_url='login')
def upload_file(request):
    message = ''
    df = None
    download_link = None
    file_name = None
    has_data = False

    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                df = handle_uploaded_file(request.FILES['file'])
                df = get_location(df)
                df['location_full'] = df['location_full'].fillna(value="")
                df = process_clustering(df)
                
                has_data = not df.empty
                
                file_name = "clustered_data.csv"
                file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                df.to_csv(file_path, index=False)
                df = df[['incident_number','cluster_number','problem_title']]
                download_link = settings.MEDIA_URL + "clustered_data.csv"
                message = 'File uploaded successfully!'
                logger.info(f'File uploaded and processed successfully: {file_name}')
            except Exception as e:
                logger.error(f'Error during file upload or processing: {e}')
                message = f'An error occurred: {e}'
        else:
            message = 'Form is not valid'
            logger.warning('File upload form is not valid.')
    else:
        form = UploadFileForm()

    
    if df is not None:
        df_list = df.values.tolist()
        df_columns = df.columns.tolist()
    else:
        df_list = []
        df_columns = []
    # Préparez le contexte pour le template
    context = {
        'form': form,
        'message': message,
        'download_link': download_link,
        'file_path': file_name,
        'df': {
            'columns': df_columns,
            'values': df_list
        },
        'has_data':has_data
    }

    return render(request, 'upload.html', context)



@login_required(login_url='login')
def download_file(request, file_path):
    file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    print(file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            logger.info(f'File downloaded: {file_path}')
            return response
    raise Http404


@login_required(login_url='login')
def dashboard_predictions(request):
    API_URL = "http://prbmg-api-database.francecentral.azurecontainer.io:8000/predictions"
    API_KEY = os.getenv('API_DATABASE_SECRET_KEY')
    headers = {"X-API-Key": API_KEY}
    response = requests.get(API_URL, headers=headers)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        predictions_data = response.json()
        logger.info('Predictions data fetched successfully.')
    else:
        logger.error(f'API request error while fetching predictions data')
        raise Exception(f"Failed to fetch predictions data: {response.status_code} {response.text}")
    # Convertir les dates de chaînes de caractères en objets datetime.date
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = None

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = None

    # Filtrer les prédictions en fonction des dates si elles sont fournies
    if start_date and end_date:
        filtered_predictions = [
            prediction for prediction in predictions_data
            if datetime.strptime(prediction['creation_date'], '%d/%m/%Y %H:%M').date() >= start_date
            and datetime.strptime(prediction['creation_date'], '%d/%m/%Y %H:%M').date() <= end_date
        ]
    elif start_date:
        filtered_predictions = [
            prediction for prediction in predictions_data
            if datetime.strptime(prediction['creation_date'], '%d/%m/%Y %H:%M').date() >= start_date
        ]
    elif end_date:
        filtered_predictions = [
            prediction for prediction in predictions_data
            if datetime.strptime(prediction['creation_date'], '%d/%m/%Y %H:%M').date() <= end_date
        ]
    else:
        filtered_predictions = predictions_data

    filtered_predictions = sorted(filtered_predictions, key=lambda x: x.get('cluster_number', 0), reverse=False)
    df = pd.DataFrame(filtered_predictions)
    df = df.sort_values(by="cluster_number", ascending=False)
    file_name = f"clustered_data_{start_date}_to_{end_date}.csv"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    df.to_csv(file_path, index=False)

    pie_data = df['problem_title'].value_counts().reset_index()
    pie_data.columns = ['label', 'y'] 
    pie_data = pie_data.to_dict(orient="records")
    
    print(pie_data)
    return render(request, 'dashboard_predictions.html', {'predictions': filtered_predictions, 'download_link': settings.MEDIA_URL + f"clustered_data_{start_date}_to_{end_date}.csv","file_path":file_name, "data_points":pie_data})

   


    