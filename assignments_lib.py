import collections
import csv
import pulp
import sys
from ortools.linear_solver import pywraplp

FEATURE_COLUMNS = {
  'Male': {'Column': 'Sexe', 'Value': 'Masculin'},
  'Francophone': {'Column': 'Francophone', 'Value': 'Oui'},
  'Daycare': {'Column': 'Garderie', 'Value': 'Oui'},
  'SchoolDistrict_5': {'Column': 'École secteur', 'Value': '005', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_6': {'Column': 'École secteur', 'Value': '006', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_7': {'Column': 'École secteur', 'Value': '007', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_8': {'Column': 'École secteur', 'Value': '008'},
  'SchoolDistrict_11': {'Column': 'École secteur', 'Value': '011', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_14': {'Column': 'École secteur', 'Value': '014', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_20': {'Column': 'École secteur', 'Value': '020', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_21': {'Column': 'École secteur', 'Value': '021', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_22': {'Column': 'École secteur', 'Value': '022', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_24': {'Column': 'École secteur', 'Value': '024', 'Constraint': 'NotSingleton'},
  'SchoolDistrict_26': {'Column': 'École secteur', 'Value': '026', 'Constraint': 'NotSingleton'},
  'PossibleDifficulty': {'Column': 'PossibleDifficulty', 'Value': '1'},
  'SoutienExterne': {'Column': 'SoutienExterne', 'Value': '1'},
  'DifficultyFrancias': {'Column': 'DifficultyFrancais', 'Value': '1'},
  'AgeGroup1': {'Column': 'Catégorie d\'âge', 'Value': 'Oct - Jan.'},
  'AgeGroup2': {'Column': 'Catégorie d\'âge', 'Value': 'Fév. - Mai'},
  'AgeGroup3': {'Column': 'Catégorie d\'âge', 'Value': 'Juin - Sept.'},
  'Language_Anglais': {'Column': 'Language', 'Value': 'Anglais', 'Constraint': 'NotSingleton'},
  'Language_Arabe': {'Column': 'Language', 'Value': 'Arabe'},
  'Language_Bengali': {'Column': 'Language', 'Value': 'Bengali', 'Constraint': 'NotSingleton'},
  'Language_Chinois': {'Column': 'Language', 'Value': 'Chinois', 'Constraint': 'NotSingleton'},
  'Language_Creole': {'Column': 'Language', 'Value': 'Créole'},
  'Language_Dari': {'Column': 'Language', 'Value': 'Dari', 'Constraint': 'NotSingleton'},
  'Language_Ewe': {'Column': 'Language', 'Value': 'Ewe', 'Constraint': 'NotSingleton'},
  'Language_Filipino': {'Column': 'Language', 'Value': 'Filipino', 'Constraint': 'NotSingleton'},
  'Language_Lingala': {'Column': 'Language', 'Value': 'Lingala', 'Constraint': 'NotSingleton'},
  'Language_Kinyarwanda': {'Column': 'Language', 'Value': 'Kinyarwanda', 'Constraint': 'NotSingleton'},
  'Language_Malinké': {'Column': 'Language', 'Value': 'Malinké', 'Constraint': 'NotSingleton'},
  'Language_Malayalam': {'Column': 'Language', 'Value': 'Malinké', 'Constraint': 'NotSingleton'},
  'Language_Ourdou': {'Column': 'Language', 'Value': 'Ourdou', 'Constraint': 'NotSingleton'},
  'Language_Tamil/Tamoul': {'Column': 'Language', 'Value': 'Tamil/Tamoul', 'Constraint': 'NotSingleton'},
  'Language_Tamoul': {'Column': 'Language', 'Value': 'Tamoul', 'Constraint': 'NotSingleton'},
  'Language_Yorumba': {'Column': 'Language', 'Value': 'Yorumba', 'Constraint': 'NotSingleton'},
}
SOLVER_TIME_LIMIT_SECONDS = 60


def GetStudents():
  students = {}
  with open('students.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      students[row['id']] = row
  return students



def GetSizeEqualityConstraints(name, solver, assignments, students, num_classes):
  print('name = %s' % name)
  target_size = len(students)/float(num_classes)
  deviations = []
  for j in range(num_classes):
    deviations.append(solver.NumVar(0, solver.infinity(), '%s_equality' % name))
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
      solver.Add(solver.Sum([assignments[sid, cid] for sid in students]) >= 2*x + (1-y))
      terms.append(x)
      terms.append(y)
    return sum(terms)
  # Put all the kids in the same class.
  #solver.Add(solver.Sum([assignments[sid, 0] for sid in students]) == len(students))
  #return sum(terms)


def main():
  students = GetStudents()
  num_classes = 10
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
    solver.Add(solver.Sum([x[sid, cid] for cid in range(num_classes)]) == 1)

  # Handle specific classroom assignments, forcing some students into some classes.
  for sid in students:
    if students[sid]['Classroom'] != '':
      cid = int(students[sid]['Classroom'])
      solver.Add(x[sid, cid] == 1)

  objective_terms = []
  objective_terms.append(GetSizeEqualityConstraints('size', solver, x, students, num_classes))
  for feature in FEATURE_COLUMNS:
    column = FEATURE_COLUMNS[feature]['Column']
    value = FEATURE_COLUMNS[feature]['Value']
    constraint_type = FEATURE_COLUMNS[feature].get('Constraint', 'SizeEquality')
    if constraint_type == 'SizeEquality':
      objective_terms.append(GetSizeEqualityConstraints(
        feature, solver, x, [sid for sid in students if students[sid][column] == value],
        num_classes))
    elif constraint_type == 'NotSingleton':
      # TODO(nav): Was never able to figure this out.
      pass
      #objective_terms.append(AddNotSingletonConstraint(
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
  	print('No solution found.')

  with open('assignments.csv', 'w', newline='') as assignments_csvfile:
    assignments_writer = csv.writer(assignments_csvfile, delimiter=',')
    assignments_writer.writerow(['Classroom', 'StudentNumber', 'Name'] + list(FEATURE_COLUMNS.keys()))

    with open('classrooms.csv', 'w', newline='') as classrooms_csvfile:
      classrooms_writer = csv.writer(classrooms_csvfile, delimiter=',')
      classrooms_writer.writerow(['Classroom', 'Size'] + list(FEATURE_COLUMNS.keys()))
    
      print(classes_to_students)
      for i in range(num_classes):
        print('%d: %d' % (i, len(classes_to_students[i])))
        features = {}
        for feature in FEATURE_COLUMNS:
          features[feature] = 0
        for sid in classes_to_students[i]:
          row = [i, sid, students[sid]['name']]
          for feature in FEATURE_COLUMNS:
            column = FEATURE_COLUMNS[feature]['Column']
            value = FEATURE_COLUMNS[feature]['Value']
            if students[sid][column] == value:
              features[feature] += 1
              row.append(1)
            else:
              row.append(0)
          assignments_writer.writerow(row)
        row = [i, len(classes_to_students[i])]
        for feature in features:
          print('\t%s:%d' % (feature, features[feature]))
          row.append(features[feature])
        classrooms_writer.writerow(row)


if __name__ == '__main__':
  sys.exit(main())
