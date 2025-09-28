pipeline {
    agent any

    parameters {
        string(name: 'DOCKERHUB_USER', defaultValue: 'aragondadinesh', description: 'Docker Hub username')
        choice(name: 'STOP_CONTAINERS', choices: ['no', 'yes'], description: 'Stop and remove running containers?')
        choice(name: 'REMOVE_IMAGES', choices: ['no', 'yes'], description: 'Remove Docker images?')
        string(name: 'GIT_URL', defaultValue: 'https://github.com/Aragondadinesh/Packer-Analyzer-v1.git', description: 'Git repository URL')
        string(name: 'GIT_BRANCH', defaultValue: 'main', description: 'Git branch to checkout')
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
                        echo "⛔ Stopping and removing running Packet Analyzer containers..."
                        for c in ui analyzer-service capture-service parser-service persistor-service postgres; do
                          if [ "$(docker ps -q -f name=$c)" ]; then
                            echo "Stopping container: $c"
                            docker rm -f $c || true
                          else
                            echo "No running container: $c"
                          fi
                        done
                        echo "✅ Containers stopped."
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
                        echo "🗑 Removing Docker images for Packet Analyzer services..."
                        SERVICES=(capture-service parser-service persistor-service analyzer-service ui)
                        for srv in "${SERVICES[@]}"; do
                            IMAGES=$(docker images $DOCKERHUB_USER/$srv -q)
                            if [ -n "$IMAGES" ]; then
                                echo "Removing image: $DOCKERHUB_USER/$srv"
                                docker rmi -f $IMAGES || true
                            fi
                        done
                        POSTGRES_IMG=$(docker images postgres:15 -q)
                        if [ -n "$POSTGRES_IMG" ]; then
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
                    def services = ['capture-service', 'parser-service', 'persistor-service', 'analyzer-service', 'ui']
                    for (srv in services) {
                        sh """
                            echo "📦 Building and pushing image: $DOCKERHUB_USER/${srv}:${IMAGE_TAG}"
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
                    sh '''
                        echo "🚀 Deploying services with Docker Compose..."
                        docker-compose pull || true
                        docker-compose up -d --remove-orphans
                    '''
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
