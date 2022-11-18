import argparse
import assignments_lib
import collections
import csv
import sys


FEATURE_COLUMNS = {
    'Male': {'Column': 'Sexe', 'Value': 'Masculin'},
    'Francophone': {'Column': 'Francophone', 'Value': 'Oui'},
    'Daycare': {'Column': 'Garderie', 'Value': 'Oui'},
    'SchoolDistrict_5': {'Column': 'École secteur', 'Value': '005', 'Constraint': 'Ignore'},
    'SchoolDistrict_6': {'Column': 'École secteur', 'Value': '006', 'Constraint': 'Ignore'},
    'SchoolDistrict_7': {'Column': 'École secteur', 'Value': '007', 'Constraint': 'Ignore'},
    'SchoolDistrict_8': {'Column': 'École secteur', 'Value': '008'},
    'SchoolDistrict_11': {'Column': 'École secteur', 'Value': '011', 'Constraint': 'Ignore'},
    'SchoolDistrict_14': {'Column': 'École secteur', 'Value': '014', 'Constraint': 'Ignore'},
    'SchoolDistrict_20': {'Column': 'École secteur', 'Value': '020', 'Constraint': 'Ignore'},
    'SchoolDistrict_21': {'Column': 'École secteur', 'Value': '021', 'Constraint': 'Ignore'},
    'SchoolDistrict_22': {'Column': 'École secteur', 'Value': '022', 'Constraint': 'Ignore'},
    'SchoolDistrict_24': {'Column': 'École secteur', 'Value': '024', 'Constraint': 'Ignore'},
    'SchoolDistrict_26': {'Column': 'École secteur', 'Value': '026', 'Constraint': 'Ignore'},
    'PossibleDifficulty': {'Column': 'PossibleDifficulty', 'Value': '1'},
    'SoutienExterne': {'Column': 'SoutienExterne', 'Value': '1'},
    'DifficultyFrancias': {'Column': 'DifficultyFrancais', 'Value': '1'},
    'AgeGroup1': {'Column': 'Catégorie d\'âge', 'Value': 'Oct - Jan.'},
    'AgeGroup2': {'Column': 'Catégorie d\'âge', 'Value': 'Fév. - Mai'},
    'AgeGroup3': {'Column': 'Catégorie d\'âge', 'Value': 'Juin - Sept.'},
    'Language_Anglais': {'Column': 'Language', 'Value': 'Anglais', 'Constraint': 'Ignore'},
    'Language_Arabe': {'Column': 'Language', 'Value': 'Arabe'},
    'Language_Bengali': {'Column': 'Language', 'Value': 'Bengali', 'Constraint': 'Ignore'},
    'Language_Chinois': {'Column': 'Language', 'Value': 'Chinois', 'Constraint': 'Ignore'},
    'Language_Creole': {'Column': 'Language', 'Value': 'Créole'},
    'Language_Dari': {'Column': 'Language', 'Value': 'Dari', 'Constraint': 'Ignore'},
    'Language_Ewe': {'Column': 'Language', 'Value': 'Ewe', 'Constraint': 'Ignore'},
    'Language_Filipino': {'Column': 'Language', 'Value': 'Filipino', 'Constraint': 'Ignore'},
    'Language_Lingala': {'Column': 'Language', 'Value': 'Lingala', 'Constraint': 'Ignore'},
    'Language_Kinyarwanda': {'Column': 'Language', 'Value': 'Kinyarwanda', 'Constraint': 'Ignore'},
    'Language_Malinké': {'Column': 'Language', 'Value': 'Malinké', 'Constraint': 'Ignore'},
    'Language_Malayalam': {'Column': 'Language', 'Value': 'Malinké', 'Constraint': 'Ignore'},
    'Language_Ourdou': {'Column': 'Language', 'Value': 'Ourdou', 'Constraint': 'Ignore'},
    'Language_Tamil/Tamoul': {'Column': 'Language', 'Value': 'Tamil/Tamoul', 'Constraint': 'Ignore'},
    'Language_Tamoul': {'Column': 'Language', 'Value': 'Tamoul', 'Constraint': 'Ignore'},
    'Language_Yorumba': {'Column': 'Language', 'Value': 'Yorumba', 'Constraint': 'Ignore'},
}
SOLVER_TIME_LIMIT_SECONDS = 60


def GetStudents(students_file):
    students = {}
    reader = csv.DictReader(students_file)
    for row in reader:
        students[row['id']] = row
    return students


parser = argparse.ArgumentParser(description='Assign students to classrooms.')
parser.add_argument('--students_file', type=open, required=True)
parser.add_argument('--num_classes', type=int, required=True)
parser.add_argument('--assignments_file',
                    type=argparse.FileType('w', encoding='UTF-8'), required=True)
parser.add_argument('--classrooms_file',
                    type=argparse.FileType('w', encoding='UTF-8'), required=True)
parser.add_argument('--time_limit_seconds', type=int, default=30)
args = parser.parse_args()


def main():
    students = GetStudents(args.students_file)
    classes_to_students = assignments_lib.generate_assignments(
        students, args.num_classes, FEATURE_COLUMNS, args.time_limit_seconds)

    assignments_writer = csv.writer(args.assignments_file, delimiter=',')
    assignments_writer.writerow(
        ['Classroom', 'StudentNumber', 'Name'] + list(FEATURE_COLUMNS.keys()))

    classrooms_writer = csv.writer(args.classrooms_file, delimiter=',')
    classrooms_writer.writerow(
        ['Classroom', 'Size'] + list(FEATURE_COLUMNS.keys()))

    print(classes_to_students)
    for i in range(args.num_classes):
        print('%d: %d' % (i, len(classes_to_students[i])))
        features = collections.defaultdict(int)
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
