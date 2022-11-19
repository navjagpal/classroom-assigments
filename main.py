import functions_framework

from assignments import assignments_lib


@functions_framework.http
def generate_assignments(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    feature_values = request.json["feature_values"]
    students = {}
    for student in request.json["students"]:
        students[student["id"]] = student
    num_classes = request.json["num_classes"]
    classes_to_students = assignments_lib.generate_assignments(
        students, num_classes, feature_values, 30)
    return classes_to_students
