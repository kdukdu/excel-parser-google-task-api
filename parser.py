import csv


fieldnames = ["Employee", "Manager", "Date", "Checkbox"]
checkbox_status = {
    "TRUE": True,
    "FALSE": False
}


def get_unchecked(filename):
    result = []
    with open(filename, newline='') as my_file:
        reader = csv.DictReader(my_file)
        for line in reader:
            res = {k: line[k] for i, k in enumerate(fieldnames)}
            if not checkbox_status[res['Checkbox']]:
                result.append(line)
    return result
