class StudentProgressService:
    """Service for evaluating student progress toward requirements."""
    
    @staticmethod
    def evaluate_node(node, student_completed_courses):
        """Evaluate a single node in the articulation tree against completed courses."""
        if "university_course" in node:
            # This is a leaf node (university course)
            required_courses = node["community_college_courses"]
            relationship = node["cc_course_relationship"]
            
            if relationship == "AND":
                # Must have taken ALL courses
                satisfied = all(course in student_completed_courses for course in required_courses)
            else:
                # Must have taken AT LEAST ONE course (OR relationship)
                satisfied = any(course in student_completed_courses for course in required_courses) if required_courses else True
                
            return {
                "satisfied": satisfied,
                "university_course": node["university_course"],
                "completed_courses": [c for c in required_courses if c in student_completed_courses],
                "missing_courses": [c for c in required_courses if c not in student_completed_courses]
            }
        else:
            # This is an operator node (AND/OR)
            child_results = [StudentProgressService.evaluate_node(child, student_completed_courses) for child in node["groups"]]
            
            if node["operator"] == "AND":
                satisfied = all(result["satisfied"] for result in child_results)
            else:
                satisfied = any(result["satisfied"] for result in child_results) if child_results else True
                
            return {
                "satisfied": satisfied,
                "operator": node["operator"],
                "requirements": child_results
            }
    
    @staticmethod
    def evaluate_student_articulation_progress(student_completed_courses, articulation_tree):
        """Evaluate whether a student has satisfied the articulation requirements."""
        return StudentProgressService.evaluate_node(articulation_tree, student_completed_courses)
    
    @staticmethod
    def consolidate_university_courses(plan):
        """Ensure each university course appears only once in each term while preserving alternatives."""
        for term_data in plan["term_plan"]:
            seen_uni_courses = set()
            filtered_courses = []
            
            for course in term_data["courses"]:
                if "satisfies_university_courses" in course:
                    # Filter out duplicate university courses
                    unique_uni_courses = []
                    for uni_course in course["satisfies_university_courses"]:
                        if uni_course not in seen_uni_courses:
                            unique_uni_courses.append(uni_course)
                            seen_uni_courses.add(uni_course)
                    
                    # Keep the course if it has unique uni courses OR alternatives
                    if unique_uni_courses or ("alternatives" in course and course["alternatives"]):
                        course_copy = course.copy()
                        course_copy["satisfies_university_courses"] = unique_uni_courses
                        filtered_courses.append(course_copy)
                else:
                    filtered_courses.append(course)
            
            term_data["courses"] = filtered_courses
            """Ensure each university course appears only once in each term by removing duplicates."""
            for term_data in plan["term_plan"]:
                seen_uni_courses = set()
                filtered_courses = []
                
                for course in term_data["courses"]:
                    if "satisfies_university_courses" in course:
                        # Filter out duplicate university courses
                        unique_uni_courses = []
                        for uni_course in course["satisfies_university_courses"]:
                            if uni_course not in seen_uni_courses:
                                unique_uni_courses.append(uni_course)
                                seen_uni_courses.add(uni_course)
                        
                        if unique_uni_courses:
                            course_copy = course.copy()
                            course_copy["satisfies_university_courses"] = unique_uni_courses
                            filtered_courses.append(course_copy)
                    else:
                        filtered_courses.append(course)
                
                term_data["courses"] = filtered_courses