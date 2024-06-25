import random

def gale_shapley_with_capacities(students, projects, capacities, willing_to_accept_unlisted):
    """Gale-Shapley algorithm to find stable matching with capacities and partial preference lists."""
    n = len(students)
    free_students = list(range(n))
    next_proposal = [0] * n
    current_matches = {i: [] for i in range(len(projects))}

    while free_students:
        student = free_students.pop(0)
        while next_proposal[student] < len(students[student]):
            project = students[student][next_proposal[student]]
            next_proposal[student] += 1

            if student not in projects[project]:
                if willing_to_accept_unlisted[project]:
                    current_matches[project].append(student)
                    break
                else:
                    continue
            
            if len(current_matches[project]) < capacities[project]:
                current_matches[project].append(student)
                break
            else:
                worst_student = max(current_matches[project], key=lambda s: projects[project].index(s) if s in projects[project] else len(projects[project]))
                if worst_student not in projects[project]:
                    worst_student_rank = len(projects[project])
                else:
                    worst_student_rank = projects[project].index(worst_student)
                
                if projects[project].index(student) < worst_student_rank:
                    current_matches[project].remove(worst_student)
                    current_matches[project].append(student)
                    free_students.append(worst_student)
                    break
                else:
                    free_students.append(student)
                    break
    
    matches = [-1] * n
    for project, matched_students in current_matches.items():
        for student in matched_students:
            matches[student] = project

    return matches

def calculate_egalitarian_cost(matches, students, projects, willing_to_accept_unlisted):
    """Calculate the egalitarian cost of a matching."""
    total_cost = 0
    for student, project in enumerate(matches):
        if project == -1:
            continue
        student_rank = students[student].index(project)
        if student in projects[project]:
            project_rank = projects[project].index(student)
        else:
            project_rank = len(projects[project]) if willing_to_accept_unlisted[project] else float('inf')
        total_cost += student_rank + project_rank
    return total_cost

def find_all_stable_matchings(students, projects, capacities, willing_to_accept_unlisted):
    """Find all stable matchings considering capacities and partial preference lists."""
    n = len(students)
    all_matches = []

    def generate_permutations(array, start, end):
        if start == end:
            match = gale_shapley_with_capacities(students, projects, capacities, willing_to_accept_unlisted)
            all_matches.append(match)
        else:
            for i in range(start, end + 1):
                array[start], array[i] = array[i], array[start]
                generate_permutations(array, start + 1, end)
                array[start], array[i] = array[i], array[start]

    generate_permutations(list(range(n)), 0, n - 1)
    return all_matches

def is_stable_with_capacities(matches, students, projects, capacities, willing_to_accept_unlisted):
    """Check if a matching is stable considering capacities and partial preference lists."""
    current_matches = {i: [] for i in range(len(projects))}
    for student, project in enumerate(matches):
        if project != -1:
            current_matches[project].append(student)
    
    for project, matched_students in current_matches.items():
        if len(matched_students) > capacities[project]:
            return False
        for student in matched_students:
            for preferred_project in students[student]:
                if preferred_project == project:
                    break
                if len(current_matches[preferred_project]) < capacities[preferred_project]:
                    return False
                worst_student = max(current_matches[preferred_project], key=lambda s: projects[preferred_project].index(s) if s in projects[preferred_project] else len(projects[preferred_project]))
                if student not in projects[preferred_project]:
                    student_rank = len(projects[preferred_project])
                else:
                    student_rank = projects[preferred_project].index(student)
                if student_rank < projects[preferred_project].index(worst_student) if worst_student in projects[preferred_project] else len(projects[preferred_project]):
                    return False
    return True

def assign_remaining_students(matches, capacities):
    """Assign remaining students randomly to projects with available capacity."""
    n = len(matches)
    remaining_students = [i for i in range(n) if matches[i] == -1]
    project_vacancies = {i: capacities[i] - matches.count(i) for i in range(len(capacities))}

    for student in remaining_students:
        available_projects = [project for project, vacancies in project_vacancies.items() if vacancies > 0]
        if available_projects:
            chosen_project = random.choice(available_projects)
            matches[student] = chosen_project
            project_vacancies[chosen_project] -= 1

    return matches

# Example usage:
students = [
    [0, 1, 2],
    [2, 0, 1],
    [1, 0, 2]
]

projects = [
    [0, 1],  # Project 0 prefers student 0 and 1
    [2, 0],  # Project 1 prefers student 2 and 0
    [1, 0]   # Project 2 prefers student 1 and 0
]

capacities = [1, 1, 1]
willing_to_accept_unlisted = [True, False, True]  # Project 1 will not accept unlisted students

all_matches = find_all_stable_matchings(students, projects, capacities, willing_to_accept_unlisted)

min_cost = float('inf')
optimal_matching = None

for match in all_matches:
    if is_stable_with_capacities(match, students, projects, capacities, willing_to_accept_unlisted):
        cost = calculate_egalitarian_cost(match, students, projects, willing_to_accept_unlisted)
        if cost < min_cost:
            min_cost = cost
            optimal_matching = match

if optimal_matching is not None:
    optimal_matching = assign_remaining_students(optimal_matching, capacities)
    print("Optimal Stable Matching:", optimal_matching)
    print("Egalitarian Cost:", min_cost)
else:
    print("No stable matching found.")