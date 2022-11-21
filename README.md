# classroom-assigments
Tool to help assign students to classrooms which distributes the children using certain characteristics

# Deploying Cloud Functions
The function needs to be redeployed when changes are made to `assignments_lib.py` or `main.py`:

```
gcloud functions deploy generate-assignments \
  --region=us-east1 --runtime=python310 --trigger-http \
  --entry-point=generate_assignments --allow-unauthenticated \
  --gen2
```
