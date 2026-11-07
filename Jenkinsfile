// Конвейер Jenkins для лабораторной работы 10 — CI/CD.
//
// Этапы: получение кода → установка зависимостей → автотесты →
// публикация на GitHub Pages (только из ветки main и только при успешных тестах).

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    environment {
        BROWSER = 'chrome'
        HEADLESS = '1'
        GIT_TOKEN = credentials('github-token')
    }

    stages {
        stage('Получение исходного кода') {
            steps {
                checkout scm
                script {
                    env.BRANCH = sh(
                        script: 'git rev-parse --abbrev-ref HEAD',
                        returnStdout: true).trim()
                    echo "Собрана ветка: ${env.BRANCH}"
                }
            }
        }

        stage('Подготовка окружения') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --upgrade pip
                    .venv/bin/pip install -r tests/requirements.txt
                '''
            }
        }

        stage('Автотесты пользовательского интерфейса') {
            steps {
                sh '.venv/bin/python -m pytest tests -v --junitxml=reports/junit.xml'
                junit testResults: 'reports/junit.xml', allowEmptyResults: false
            }
        }

        stage('Публикация на GitHub Pages') {
            // Публикация выполняется только из ветки main.
            when {
                expression { env.BRANCH == 'main' }
            }
            steps {
                sh '''
                    rm -rf .publish
                    mkdir -p .publish
                    cp -r app/* .publish/
                    cd .publish
                    git init -q
                    git add -A
                    git -c user.name="Andrey" -c user.email="Andreymay009@gmail.com" \
                        commit -q -m "deploy: публикация приложения на GitHub Pages"
                    git push -f "https://x-access-token:${GIT_TOKEN}@github.com/ATOM556/lab10-cicd.git" \
                        HEAD:gh-pages
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        failure {
            echo 'Сборка завершилась неуспешно: публикация не выполнялась.'
        }
    }
}
