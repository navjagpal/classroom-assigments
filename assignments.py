import argparse
import assignments_lib
import collections
import csv
import json
import sys


def parse_args():
    parser = argparse.ArgumentParser(description='Assign students to classrooms.')
    parser.add_argument('--students_file', type=open, required=True)
    parser.add_argument('--features_file', type=open, required=True)
    parser.add_argument('--num_classes', type=int, required=True)
    parser.add_argument('--assignments_file',
                        type=argparse.FileType('w', encoding='UTF-8'), required=True)
    parser.add_argument('--classrooms_file',
                        type=argparse.FileType('w', encoding='UTF-8'), required=True)
    parser.add_argument('--time_limit_seconds', type=int, default=30)
    parser.add_argument('--columns', type=str)
    return parser.parse_args()


def get_students(students_file):
    students = {}
    reader = csv.DictReader(students_file)
    for row in reader:
        students[row['id']] = row
    return students


def main():
    args = parse_args()
    feature_columns = json.load(args.features_file)
    students = get_students(args.students_file)
    classes_to_students = assignments_lib.generate_assignments(
        students, args.num_classes, feature_columns, args.time_limit_seconds)

    assignments_writer = csv.writer(args.assignments_file, delimiter=',')
    assignments_writer.writerow(
        ['Classroom', 'StudentNumber', 'Name'] + list(feature_columns.keys()))

    classrooms_writer = csv.writer(args.classrooms_file, delimiter=',')
    classrooms_writer.writerow(
        ['Classroom', 'Size'] + list(feature_columns.keys()))

    print(classes_to_students)
    for i in range(args.num_classes):
        print('%d: %d' % (i, len(classes_to_students[i])))
        features = collections.defaultdict(int)
        for sid in classes_to_students[i]:
            row = [i, sid, students[sid]['name']]
            for feature in feature_columns:
                column = feature_columns[feature]['Column']
                value = feature_columns[feature]['Value']
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
