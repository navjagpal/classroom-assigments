import argparse
import assignments_lib
import csv
import sys


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


parser = argparse.ArgumentParser(description='Assign students to classrooms.')
args = parser.parse_args()


def main():
  students = GetStudents()
  num_classes = 10
  classes_to_students = assignments_lib.generate_assignments(
    students, num_classes, FEATURE_COLUMNS)

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

