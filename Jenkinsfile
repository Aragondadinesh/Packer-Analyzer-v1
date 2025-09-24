pipeline {
    agent any

    parameters {
        string(name: 'DOCKERHUB_USER', defaultValue: 'aragondadinesh', description: 'Docker Hub username')
        choice(name: 'STOP_CONTAINERS', choices: ['no', 'yes'], description: 'Stop and remove running containers?')
        choice(name: 'REMOVE_IMAGES', choices: ['no', 'yes'], description: 'Remove Docker images?')
        string(name: 'GIT_URL', defaultValue: 'https://github.com/Aragondadinesh/Packer-Analyzer-v1.git', description: 'Git repository URL')
        string(name: 'GIT_BRANCH', defaultValue: 'Docker-features-Suhanson', description: 'Git branch to checkout')
    }

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-cred')
        DOCKERHUB_PASS = "${DOCKERHUB_CREDENTIALS_PSW}"
        IMAGE_TAG = "latest"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${params.GIT_BRANCH}", url: "${params.GIT_URL}"
            }
        }

        stage('Docker Login') {
            steps {
                sh "echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin"
            }
        }

        stage('Stop Containers') {
            when {
                expression { return params.STOP_CONTAINERS == 'yes' }
            }
            steps {
                script {
                    sh '''
                        echo "⛔ Stopping and removing containers for services, pgadmin, and db..."
                        for c in ui-service analyzer-service capture-service parser-service persistor-service pgadmin db; do
                          if [ "$(docker ps -q -f name=$c)" ]; then
                            echo "Stopping container: $c"
                            docker rm -f $c || true
                          else
                            echo "No running container: $c"
                          fi
                        done
                        echo "✅ Container stop complete."
                    '''
                }
            }
        }

        stage('Remove Images') {
            when {
                expression { return params.REMOVE_IMAGES == 'yes' }
            }
            steps {
                script {
                    sh '''
                        echo "🗑 Removing images for $DOCKERHUB_USER/*, pgadmin, and postgres:15..."
                        IMAGES=$(docker images "${DOCKERHUB_USER}/*" -q)
                        if [ -n "$IMAGES" ]; then
                          echo "Removing images for namespace: $DOCKERHUB_USER"
                          docker rmi -f $IMAGES || true
                        else
                          echo "No images found for $DOCKERHUB_USER"
                        fi

                        PGADMIN_IMG=$(docker images dpage/pgadmin4 -q)
                        if [ -n "$PGADMIN_IMG" ]; then
                          echo "Removing pgadmin image"
                          docker rmi -f $PGADMIN_IMG || true
                        fi

                        POSTGRES_IMG=$(docker images postgres:15 -q)
                        if [ -n "$POSTGRES_IMG" ]; then
                          echo "Removing postgres:15 image"
                          docker rmi -f $POSTGRES_IMG || true
                        fi
                        echo "✅ Image removal complete."
                    '''
                }
            }
        }

        stage('Build & Push Images') {
            steps {
                script {
                    def services = [
                        'capture-service',
                        'analyzer-service',
                        'parser-service',
                        'persistor-service',
                        'ui-service'
                    ]
                    for (srv in services) {
                        sh """
                            echo "📦 Building and pushing image for $srv..."
                            docker build -t $DOCKERHUB_USER/${srv}:${IMAGE_TAG} -f ${srv}/Dockerfile .
                            docker push $DOCKERHUB_USER/${srv}:${IMAGE_TAG}
                        """
                    }
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                script {
                    sh """
                        echo "🚀 Deploying services with Docker Compose..."
                        export DOCKERHUB_USER=$DOCKERHUB_USER
                        docker-compose pull
                        docker-compose up -d --remove-orphans
                    """
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
    }
}
