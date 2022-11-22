# classroom-assigments
Tool to help assign students to classrooms which distributes the children using certain characteristics

# Run example request against the live API

```
curl -v -X POST -H "Content-Type: application/json" \
  -d @./example_request.json \
  https://generate-assignments-6ughy77jeq-ue.a.run.app/
```

# Deploying Cloud Functions
The function needs to be redeployed when changes are made to `assignments_lib.py` or `main.py`:

```
gcloud functions deploy generate-assignments \
  --region=us-east1 --runtime=python310 --trigger-http \
  --entry-point=generate_assignments --allow-unauthenticated \
  --gen2
```

# Run the cloud function locally

You can execute the curl request above against `localhost:8080` instead of the live API, if you run the function locally.

```
functions-framework --target=generate_assignments --debug
```
