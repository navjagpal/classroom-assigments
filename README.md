# classroom-assigments
Tool to help assign students to classrooms which distributes the children using certain characteristics.

The code was heavily inspired by the paper [An optimization-based DSS for student-to-teacher assignment: Classroom heterogeneity and teacher performance measures](https://www.researchgate.net/publication/331538110_An_optimization-based_DSS_for_student-to-teacher_assignment_Classroom_heterogeneity_and_teacher_performance_measures), and this [spreadsheet](https://github.com/MattDBailey/PrincipalDSS) from the paper. The author of the paper, [@MattDBailey](https://github.com/MattDBailey), was responsive over email to help answer some questions about the paper and the spreadsheet. We thank him for his help, and for publishing his work. This approach has saved a local Montreal elementary school countless hours of work every year. 

# Run example request against the live API
This is the simplest way to interact with the logic without having to install any dependencies.

```
curl -v -X POST -H "Content-Type: application/json" \
  -d @./example_request.json \
  https://generate-assignments-6ughy77jeq-ue.a.run.app/
```

# Install dependencies
If you want to run the scripts locally, you need to install some additional libraries.

```
pip3 install -r requirements.txt
```

# Running the command line tool

Example usage
```
python3 assignments.py \
  --students_file=students.csv \
  --assignments_file=assignments.csv \
  --classrooms_file=classrooms.csv \
  --num_classes=10 \
  --time_limit_seconds=30 \
  --features_file=features.json
```

# Run the cloud function locally

You can execute the curl request above against `localhost:8080` instead of the live API, if you run the function locally.

```
functions-framework --target=generate_assignments --debug
```

# Deploying Cloud Functions
The function needs to be redeployed when changes are made to `assignments_lib.py` or `main.py`. These are primarily instructions for myself, but they might be useful to you too if you want to deploy the function inside of your own project.

```
gcloud functions deploy generate-assignments \
  --region=us-east1 --runtime=python310 --trigger-http \
  --entry-point=generate_assignments --allow-unauthenticated \
  --gen2
```
