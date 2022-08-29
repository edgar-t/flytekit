@Library("BuildUtils")
import com.curalate.jenkins.*
import com.curalate.jenkins.v3.terraform.*

def utils = new BuildUtils()
def tf = new TerraformFactory()

def flytekitPluginDirectories = ["flytekit-aws-sagemakerprocessing"]

utils.build { BuildMetadata data ->
    setBuildParameters(flytekitPluginDirectories)
    def VERSION = "${getVersion(data)}"
    setBuildName(VERSION)

    dir('plugins') {
        flytekitPluginDirectories.each { plugin ->
            if (hasCodeChangedInDirectory("plugins/" + plugin, utils, data)) {
                dir(plugin) {
                    try {
                        awsCreds("prod") {
                            //  Fetch auth token from AWS
                            def token = sh(returnStdout: true, script:'''
                                aws --region us-east-1 codeartifact get-authorization-token --domain curalate-ml --domain-owner 492572841545 --query authorizationToken --output text
                            ''')
                            withDockerContainer(
                                    image: "492572841545.dkr.ecr.us-east-1.amazonaws.com/python-flyte-build:133-133-fbc2907",
                                    args: "-e TWINE_USERNAME=mlaas-team -e TWINE_REPOSITORY_URL=https://curalate-ml-492572841545.d.codeartifact.us-east-1.amazonaws.com/pypi/machine-learning/ -e TWINE_PASSWORD=$token -e VERSION=$VERSION -u 0"
                            ) {
                                sh 'pipenv install twine'

                                stage("Build $plugin  wheel") {
                                    sh "sed -i 's/0.0.0+develop/$VERSION/' setup.py"
                                    sh 'pipenv run python setup.py sdist bdist_wheel'
                                }

                                stage("Push $plugin wheel to CodeArtifact") {
                                    def FILE=sh(returnStdout: true, script:'''find ./dist/ -name "*whl"''')
                                    sh "pipenv run twine upload --repository codeartifact $FILE"
                                }
                            }
                        }
                    }
                    finally {
                        sh 'sudo chown -R $(whoami):$(whoami) .'
                    }
                }
            }
        }
    }
    setBuildParameters(flytekitPluginDirectories)
}

def getVersion(BuildMetadata data) {
    "${env.BUILD_NUMBER}+git${data.revision}"
}
