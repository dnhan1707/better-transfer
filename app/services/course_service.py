from app.services.prerequisite_service import PrerequisiteService
from app.db.models.courses import Courses
from sqlalchemy.orm import Session

import math

class CourseSchedulingService:
    """Service for scheduling courses across terms while respecting prerequisites."""
    def __init__(self):
        self.prerequisite_service = PrerequisiteService()

    def create_initial_term_distribution(self, subject_queues, max_course_per_term, prerequisite_graph, completed_courses):
        """Create an initial distribution of courses across terms."""
        current_term = []
        term_subjects = set()
        courses_added = False
        
        # First pass: try to add one course from each subject
        for subject, queue in sorted(subject_queues.items()):
            if len(queue) == 0:
                continue
                
            # Find first course whose prerequisites are satisfied
            for i, course in enumerate(queue):
                if self.prerequisite_service.has_prerequisites_satisfied(course, completed_courses, prerequisite_graph):
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
                if self.prerequisite_service.has_prerequisites_satisfied(course, completed_courses, prerequisite_graph):
                    current_term.append(course)
                    queue.pop(i)
                    courses_added = True
                else:
                    i += 1
        
        return current_term, completed_courses.union(current_term), courses_added
    
    def update_available_courses(self, all_courses, placed_courses, available_courses, prerequisite_graph):
        """Update the set of available courses based on which prerequisites have been satisfied."""
        for course in all_courses:
            if course not in placed_courses:
                prereqs = [p["code"] for p in prerequisite_graph.get(course, [])]
                if all(prereq in placed_courses for prereq in prereqs):
                    available_courses.add(course)
    
    def redistribute_courses(self, all_courses, num_of_terms, prerequisite_graph):
        """Redistribute courses across terms while respecting prerequisites."""
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
            # Calculate target number of courses for this term
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
            self.update_available_courses(all_courses, placed_courses, available_courses, prerequisite_graph)
        
        # Any remaining courses go in the last term
        remaining = [c for c in all_courses if c not in placed_courses]
        new_terms[-1].extend(remaining)
        
        return new_terms
    
    def plan_course_sequence(self, sorted_courses, num_of_terms, prerequisite_graph):
        """Group courses into balanced terms while respecting prerequisites and diversifying subjects."""
        if not sorted_courses:
            return [[] for _ in range(num_of_terms)]
            
        max_course_per_term = math.ceil(len(sorted_courses) / num_of_terms)
        terms = []
        completed_courses = set()
        
        # Group courses by subject
        subject_courses = self.prerequisite_service.group_courses_by_subject(sorted_courses)
        
        # Create a queue of courses for each subject (maintaining topological order)
        subject_queues = {subject: courses.copy() for subject, courses in subject_courses.items()}
        
        # Distribute courses across terms
        while any(len(queue) > 0 for queue in subject_queues.values()):
            current_term, completed_courses, courses_added = self.create_initial_term_distribution(
                subject_queues, max_course_per_term, prerequisite_graph, completed_courses
            )
            
            if current_term:
                terms.append(current_term)
            
            # If we couldn't add any courses, there may be a prerequisite cycle or other issue
            if not courses_added:
                break
                
        # Handle redistribution when we have fewer terms than requested
        if terms and num_of_terms > len(terms):
            # Flatten all courses while preserving order (important for prerequisites)
            all_courses = []
            for term in terms:
                all_courses.extend(term)
            
            # Redistribute courses across the requested number of terms
            terms = self.redistribute_courses(all_courses, num_of_terms, prerequisite_graph)
        
        # Ensure we have exactly num_of_terms terms
        while len(terms) < num_of_terms:
            terms.append([])
        
        return terms[:num_of_terms]  # Ensure we don't return more than requested
    
    def extract_course_details(self, courses):
        """Extract details like units and name from course objects."""
        course_details = {}
        for course in courses:
            course_details[course.code] = {
                "units": course.units,
                "name": course.name
            } 
        return course_details
    
    def get_course_alternatives(self, cc_course, satisfies_uni_courses, uni_course_alternatives):
        """Find alternative courses for a given CC course."""
        alternatives = set()
        for uni_course in satisfies_uni_courses:
            alt_cc_courses = uni_course_alternatives.get(uni_course, [])
            course_alternatives = [alt for alt in alt_cc_courses if alt != cc_course]
            alternatives.update(course_alternatives)
        return alternatives

    def prepare_course_sequence(self, db: Session, college_id: int, cc_courses_to_take):
        """Build prerequisite graph and sort courses."""
        prerequisite_graph, _ = self.prerequisite_service.build_prerequisite_graph(db, college_id)
        sorted_courses = self.prerequisite_service.topological_sort(prerequisite_graph)
        sorted_courses = [c for c in sorted_courses if c in cc_courses_to_take]
        return prerequisite_graph, sorted_courses
