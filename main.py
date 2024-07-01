import os
import subprocess
import logging
import shutil
from flask import Flask, send_file, request, jsonify

# Настройки
REPOSITORY_URL = 'https://github.com/MaxSuvorov/build_server'
PROJECT_DIR = '/Users/raiden/Desktop/build_serv'
ARTIFACT_DIR = '/Users/raiden/Desktop/build_artifacts'
BUILD_SERVER_URL = 'http://127.0.0.1:4444'

# Настройка логирования
logging.basicConfig(filename='build.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Инициализация Flask-приложения
app = Flask(__name__)

def clone_project():
    """
    Функция для клонирования проекта из Git-репозитория.
    """
    try:
        if os.path.exists(PROJECT_DIR):
            shutil.rmtree(PROJECT_DIR)
        os.makedirs(PROJECT_DIR)
        subprocess.check_call(['git', 'clone', REPOSITORY_URL, PROJECT_DIR])
        logging.info('Проект успешно клонирован.')
    except subprocess.CalledProcessError as e:
        logging.error(f'Ошибка клонирования проекта: {e}')
        return False
    return True

def build_project():
    """
    Функция для сборки проекта.
    """
    try:
        os.chdir(PROJECT_DIR)
        subprocess.check_call(['make', 'build'])
        logging.info('Проект успешно собран.')
    except subprocess.CalledProcessError as e:
        logging.error(f'Ошибка при сборке проекта: {e}')
        return False
    return True

def create_artifact():
    """
    Функция для создания архива с артефактами сборки.
    """
    try:
        if not os.path.exists(ARTIFACT_DIR):
            os.makedirs(ARTIFACT_DIR)
        artifact_path = os.path.join(ARTIFACT_DIR, 'build_artifacts.zip')
        shutil.make_archive(artifact_path[:-4], 'zip', PROJECT_DIR, 'build')
        logging.info('Артефакты сборки успешно созданы.')
    except Exception as e:
        logging.error(f'Ошибка создания артефактов: {e}')
        return False
    return True

@app.route('/build', methods=['POST'])
def build_handler():
    """
    Эндпоинт для запуска сборки проекта.
    """
    if clone_project() and build_project() and create_artifact():
        return 'Сборка успешна', 200
    else:
        return 'Ошибка сборки', 500

@app.route('/errors', methods=['GET'])
def get_build_errors():
    """
    Эндпоинт для получения информации об ошибках сборки.
    """
    try:
        with open('build.log', 'r') as f:
            errors = f.read()
        return jsonify({'errors': errors}), 200
    except Exception as e:
        logging.error(f'Ошибка при получении информации об ошибках: {e}')
        return 'Не удалось получить информацию об ошибках', 500

@app.route('/artifacts', methods=['GET'])
def download_artifacts():
    """
    Эндпоинт для скачивания артефактов сборки.
    """
    try:
        artifact_path = os.path.join(ARTIFACT_DIR, 'build_artifacts.zip')
        return send_file(artifact_path, as_attachment=True)
    except Exception as e:
        logging.error(f'Ошибка при скачивании артефактов: {e}')
        return 'Не удалось скачать артефакты', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4444, debug=True)