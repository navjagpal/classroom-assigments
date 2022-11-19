import collections
from ortools.linear_solver import pywraplp


def get_size_equality_constraints(name, solver, assignments, students, num_classes):
    target_size = len(students)/float(num_classes)
    deviations = []
    for j in range(num_classes):
        deviations.append(solver.NumVar(
            0, solver.infinity(), '%s_equality' % name))
    for j in range(num_classes):
        student_sum = solver.Sum([assignments[sid, j] for sid in students])
        solver.Add((student_sum - target_size)/target_size <= deviations[j])
        solver.Add((target_size - student_sum)/target_size <= deviations[j])
    return sum(deviations)


def generate_assignments(students, num_classes, feature_columns, time_limit_seconds):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    # x[i, j] is an array of 0-1 variables (binary), which will be 1
    # if student i is assigned to classroom j.
    x = {}
    for row in students.values():
        for i in range(num_classes):
            x[row['id'], i] = solver.IntVar(0, 1, '')

    # Each student is assigned to exactly one class.
    for sid in students:
        solver.Add(solver.Sum([x[sid, cid]
                   for cid in range(num_classes)]) == 1)

    # Handle specific classroom assignments, forcing some students into some classes.
    for sid in students:
        if students[sid].get('Classroom', '') != '':
            cid = int(students[sid]['Classroom'])
            solver.Add(x[sid, cid] == 1)

    objective_terms = []
    # We're assuming that a desired characteristic is evently sized classes.
    objective_terms.append(get_size_equality_constraints(
        'size', solver, x, students, num_classes))
    # Build a set of constraints based on the feature columns. For each feature,
    # select the subset of students which match the feature (based on column values)
    # and add a constaint that attempts to evenly distribute those students across
    # all classes.
    for feature in feature_columns:
        column = feature_columns[feature]['Column']
        value = feature_columns[feature]['Value']
        constraint_type = feature_columns[feature].get(
            'Constraint', 'SizeEquality')
        if constraint_type == 'SizeEquality':
            objective_terms.append(get_size_equality_constraints(
                feature, solver, x, [
                    sid for sid in students if students[sid][column] == value],
                num_classes))
        elif constraint_type == 'Ignore':
            pass
        else:
            raise RuntimeError('Unknown constraint type: %s' % constraint_type)

    solver.SetTimeLimit(time_limit_seconds * 1000)
    solver.Minimize(solver.Sum(objective_terms))
    status = solver.Solve()
    classes_to_students = collections.defaultdict(list)
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        for sid in students:
            for j in range(num_classes):
                # Test if x[i,j] is 1 (with tolerance for floating point arithmetic).
                # This is how we decide of a student was assigned to a classroom.
                if x[sid, j].solution_value() > 0.5:
                    classes_to_students[j].append(sid)
    else:
        raise RuntimeError('No solution found.')
    return classes_to_students
