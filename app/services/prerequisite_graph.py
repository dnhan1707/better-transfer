from app.db.crud.articulations import db_get_prerequisite_relationships_for_college
from app.db.models.courses import Courses
from sqlalchemy.orm import Session
import math
import re

'''
SORT by Prerequisite

Data Structure: Directed Acyclic Graph
'''

def build_prerequisite_graph(db: Session, college_id: int):
    prerequisite_relationships = db_get_prerequisite_relationships_for_college(db, college_id)
    all_courses = db.query(Courses).filter(Courses.college_id == college_id)
    prerequisite_graph = {}  # course -> prerequisites
    leads_to = {}  # prerequisite -> courses allowed to take after

    for course in all_courses:
        prerequisite_graph[course.code] = []
        leads_to[course.code] = []

    for rel in prerequisite_relationships:
        prerequisite_graph[rel.course_code].append({
            "code": rel.prerequisite_code,
            "type": rel.prerequisite_type
        })

        leads_to[rel.prerequisite_code].append({
            "code": rel.course_code,
            "type": rel.prerequisite_type
        })

    return prerequisite_graph, leads_to

def topological_sort(prerequisite_graph):
    # Make sure the prerequisite courses come first
    visited = set()
    temp_visited = set()
    res = []

    def visit(course):
        if course in temp_visited:
            raise ValueError(f"Cycle detected in prerequisites involving {course}")
        if course not in visited:
            temp_visited.add(course)

            prerequisites = [p["code"] for p in prerequisite_graph.get(course, [])]
            for prere in prerequisites:
                visit(prere)
            
            temp_visited.remove(course)
            visited.add(course)
            res.append(course)

    for course in prerequisite_graph:
        if course not in visited:
            visit(course)
    
    return res

def get_subject(course_code):
    match = re.match(r"^(.*\D)\s*\d", course_code)
    return match.group(1).strip() if match else course_code

def plan_course_sequence(sorted_course, num_of_terms, prerequisite_graph):
    '''
    Group courses into balanced terms
    Somehow ensure prioritize that same type of courses are in different terms

    Draft plan: 
        - max_class_per_term = math.ceil(len(sorted_course) / num_of_terms)
        - create an array with length = number of terms
        - each element is a tuple [(CS 002, MATH 5A), (CS 003A, Math 5B), ...]
        - **Hard**: prioritize not taking the same type of class in the same semester
                    ex: Instead of [(CS 002, CS 003A), (Math 5A, Math 5B), ...], 
                        we want [(CS 002, MATH 5A), (CS 003A, Math 5B), ...]
    
    Goal:   Group courses into balanced terms while respecting prerequisites and diversifying subjects
    '''
    if not sorted_course:
        return [[] for _ in range(num_of_terms)]
        
    max_course_per_term = math.ceil(len(sorted_course) / num_of_terms)
    terms = []
    completed_courses = set()
    
    # Group courses by subject
    subject_courses = {}
    for course in sorted_course:  # Already topologically sorted
        subject = get_subject(course)
        if subject not in subject_courses:
            subject_courses[subject] = []
        subject_courses[subject].append(course)
    
    # Create a queue of courses for each subject (maintaining topological order)
    subject_queues = {subject: courses.copy() for subject, courses in subject_courses.items()}
    
    while any(len(queue) > 0 for queue in subject_queues.values()):
        current_term = []
        term_subjects = set()
        courses_added = False
        
        # First pass: try to add one course from each subject
        for subject, queue in sorted(subject_queues.items()):
            if len(queue) == 0:
                continue
                
            # Find first course whose prerequisites are satisfied
            for i, course in enumerate(queue):
                prerequisites = [p["code"] for p in prerequisite_graph.get(course, [])]
                if all(prereq in completed_courses for prereq in prerequisites):
                    if len(current_term) < max_course_per_term and subject not in term_subjects:
                        current_term.append(course)
                        term_subjects.add(subject)
                        queue.pop(i)
                        courses_added = True
                        break
        
        # Second pass: fill remaining slots with any available courses
        for subject, queue in sorted(subject_queues.items()):
            i = 0
            while i < len(queue) and len(current_term) < max_course_per_term:
                course = queue[i]
                prerequisites = [p["code"] for p in prerequisite_graph.get(course, [])]
                if all(prereq in completed_courses for prereq in prerequisites):
                    current_term.append(course)
                    queue.pop(i)
                    courses_added = True
                else:
                    i += 1
        
        if current_term:
            terms.append(current_term)
            completed_courses.update(current_term)
        
        # If we couldn't add any courses, there may be a prerequisite cycle or other issue
        if not courses_added:
            break
            
    # Improved redistribution logic when we have fewer terms than requested
    if terms and num_of_terms > len(terms):
        # Flatten all courses while preserving order (important for prerequisites)
        all_courses = []
        for term in terms:
            all_courses.extend(term)
        
        # We need a more intelligent distribution while respecting prerequisites
        new_terms = [[] for _ in range(num_of_terms)]
        available_courses = set()  # Courses that have all prerequisites met
        placed_courses = set()  # Courses already placed in new terms
        
        # Initial available courses are those with no prerequisites
        for course in all_courses:
            prereqs = [p["code"] for p in prerequisite_graph.get(course, [])]
            if not prereqs:
                available_courses.add(course)
        
        # Distribute courses across terms
        for term_idx in range(num_of_terms):
            # Try to put roughly equal number of courses in each term
            target_courses = len(all_courses) // num_of_terms
            if term_idx < len(all_courses) % num_of_terms:
                target_courses += 1
                
            # Add courses to this term
            added_to_term = 0
            
            # First, add courses from available_courses (prerequisites satisfied)
            available_list = list(available_courses - placed_courses)
            for course in available_list:
                if added_to_term >= target_courses:
                    break
                    
                new_terms[term_idx].append(course)
                placed_courses.add(course)
                added_to_term += 1
            
            # Update available courses for next term
            for course in all_courses:
                if course not in placed_courses:
                    prereqs = [p["code"] for p in prerequisite_graph.get(course, [])]
                    if all(prereq in placed_courses for prereq in prereqs):
                        available_courses.add(course)
        
        # Any remaining courses go in the last term
        remaining = [c for c in all_courses if c not in placed_courses]
        new_terms[-1].extend(remaining)
        
        terms = new_terms
    
    # Ensure we have exactly num_of_terms terms
    while len(terms) < num_of_terms:
        terms.append([])
    
    return terms[:num_of_terms]  # Ensure we don't return more than requested