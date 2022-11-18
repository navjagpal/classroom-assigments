import collections
import csv
from ortools.linear_solver import pywraplp


def GetSizeEqualityConstraints(name, solver, assignments, students, num_classes):
    print('name = %s' % name)
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


def AddNotSingletonConstraint(name, solver, assignments, students, num_classes):
    if len(students) < 2:
        return
    terms = []
    if True:
        for cid in range(num_classes):
            x = solver.NumVar(0, solver.infinity(), '%s_x' % name)
            y = solver.BoolVar('%s_binary' % name)
            #solver.Add(solver.Sum([assignments[sid, cid] for sid in students]) == 2*x + (1-y))
            solver.Add(solver.Sum([assignments[sid, cid]
                       for sid in students]) >= 2*x + (1-y))
            terms.append(x)
            terms.append(y)
        return sum(terms)
    # Put all the kids in the same class.
    #solver.Add(solver.Sum([assignments[sid, 0] for sid in students]) == len(students))
    # return sum(terms)


def generate_assignments(students, num_classes, feature_columns):
    target_size = len(students)/float(num_classes)

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
        if students[sid]['Classroom'] != '':
            cid = int(students[sid]['Classroom'])
            solver.Add(x[sid, cid] == 1)

    objective_terms = []
    objective_terms.append(GetSizeEqualityConstraints(
        'size', solver, x, students, num_classes))
    for feature in feature_columns:
        column = feature_columns[feature]['Column']
        value = feature_columns[feature]['Value']
        constraint_type = feature_columns[feature].get(
            'Constraint', 'SizeEquality')
        if constraint_type == 'SizeEquality':
            objective_terms.append(GetSizeEqualityConstraints(
                feature, solver, x, [
                    sid for sid in students if students[sid][column] == value],
                num_classes))
        elif constraint_type == 'NotSingleton':
            # TODO(nav): Was never able to figure this out.
            pass
            # objective_terms.append(AddNotSingletonConstraint(
            #  feature, solver, x, [sid for sid in students if students[sid][column] == value],
            #  num_classes))
        else:
            raise RuntimeError('Unknown constraint type: %s' % constraint_type)

    #solver.parameters.max_time_in_seconds = SOLVER_TIME_LIMIT_SECONDS
    solver.Minimize(solver.Sum(objective_terms))
    status = solver.Solve()
    classes_to_students = {}
    for i in range(num_classes):
        classes_to_students[i] = []
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        print(f'Total cost = {solver.Objective().Value()}\n')
        for sid in students:
            for j in range(num_classes):
                # Test if x[i,j] is 1 (with tolerance for floating point arithmetic).
                if x[sid, j].solution_value() > 0.5:
                    classes_to_students[j].append(sid)
    else:
        raise RuntimeError('No solution found.')
    return classes_to_students
