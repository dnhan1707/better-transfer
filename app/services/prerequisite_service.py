from app.db.queries.prerequisite_queries import db_get_prerequisite_relationships_for_college
from app.db.models.courses import Courses
from sqlalchemy.orm import Session
import re

class PrerequisiteService:
    """Service for handling course prerequisites and dependency graphs."""
    
    @staticmethod
    def build_prerequisite_graph(db: Session, college_id: int):
        """Build a graph representing course prerequisites."""
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
    
    @staticmethod
    def topological_sort(prerequisite_graph):
        """Sort courses so that prerequisites come before their dependent courses."""
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
    
    @staticmethod
    def get_subject(course_code):
        """Extract the subject from a course code."""
        match = re.match(r"^(.*\D)\s*\d", course_code)
        return match.group(1).strip() if match else course_code
    
    @staticmethod
    def has_prerequisites_satisfied(course, completed_courses, prerequisite_graph):
        """Check if all prerequisites for a course have been completed."""
        prerequisites = [p["code"] for p in prerequisite_graph.get(course, [])]
        return all(prereq in completed_courses for prereq in prerequisites)
    
    @staticmethod
    def group_courses_by_subject(sorted_courses):
        """Group courses by their subject area."""
        subject_courses = {}
        for course in sorted_courses:
            subject = PrerequisiteService.get_subject(course)
            if subject not in subject_courses:
                subject_courses[subject] = []
            subject_courses[subject].append(course)
        return subject_courses