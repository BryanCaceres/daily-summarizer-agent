Info: Work in progres

--------------

# Langchain Daily Job Summarizer

This is a simple lambda function that uses Langchain to summarize daily job information.

Build the Project in a Docker Container

```bash
sam build --use-container
```

Start the Local Server with Endpoints Configured in template.yaml
This allows you to test the endpoints locally.

```bash
sam local start-api --port 3005 --env-vars env.json
```

# Deploy the Project on AWS
Before deploying, it’s recommended to test any changes in your template.yaml locally to avoid syntax errors.

```bash
sam validate --lint
```

Once your template.yaml has been tested locally, you can deploy the project to AWS.

(Recommended for validating configurations during deployment)

```bash
sam deploy --guided
```

or directly:

```bash
sam deploy
```
