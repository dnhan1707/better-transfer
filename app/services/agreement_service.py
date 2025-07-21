from app.db.connection.mongo_connection import MongoDB
from app.services.college_service import CollegeService
from app.services.prerequisite_service import PrerequisiteService
from app.schemas.transferPlanRequest import InputRequest
from app.utils.logging_config import get_logger
from bson.objectid import ObjectId
from typing import List, Dict

logger = get_logger(__name__)

class AgreementService():
    def __init__(self):
        self.mongo = MongoDB("articulation_db")
        self.collection = self.mongo.get_collection("agreements")
        self.college_service = CollegeService()

    async def get_transferplan(self, request: InputRequest):
        """
        Create an optimized transfer plan with courses distributed across terms.
        
        Returns:
            Dict with term-by-term course schedule and metadata
        """
        try:
            number_of_terms = request.number_of_terms
            logger.info(f"Creating transfer plan for {number_of_terms} terms")
            
            # Get all required courses with prerequisites
            all_courses = await self.get_classlist(request)
            
            if not all_courses:
                logger.warning("No courses found for transfer plan")
                return {
                    "terms": [],
                    "total_terms": number_of_terms,
                    "total_courses": 0,
                    "total_units": 0,
                    "metadata": {
                        "avg_units_per_term": 0,
                        "departments_covered": []
                    }
                }
            
            # Get college info for prerequisite service
            college_id = request.targets[0].collegeId
            college_code = await self.college_service.get_college_code(college_id)
            
            if not college_code:
                logger.error(f"Could not find college code for college_id: {college_id}")
                return {"error": "College code not found"}
            
            college_collection_name = str(college_code) + "_course_prerequisites"
            prerequisite_service = PrerequisiteService(college_collection_name)
            
            # Get course sequence organized by prerequisite levels
            class_ids = [course["_id"] for course in all_courses]
            sequence_data = await prerequisite_service.get_course_sequence(class_ids)
            
            # Distribute courses across terms optimally
            terms = self._distribute_courses_across_terms(
                sequence_data["course_sequence"], 
                number_of_terms,
                sequence_data["total_units"]
            )
            
            # Calculate metadata
            total_units = sum(course.get("units", 0) for term in terms for course in term)
            departments = set(course.get("department", "unknown") for term in terms for course in term)
            
            return {
                "terms": terms,
                "total_terms": number_of_terms,
                "total_courses": len(all_courses),
                "total_units": total_units,
                "metadata": {
                    "avg_units_per_term": round(total_units / number_of_terms, 2),
                    "departments_covered": list(departments),
                    "courses_per_term": [len(term) for term in terms],
                    "units_per_term": [sum(course.get("units", 0) for course in term) for term in terms]
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating transfer plan: {e}")
            raise

    def _distribute_courses_across_terms(self, course_levels: List[List[Dict]], target_terms: int, total_units: float) -> List[List[Dict]]:
        """
        Distribute courses across terms optimally considering:
        1. Prerequisite order
        2. Equal unit distribution
        3. Department diversity
        """
        logger.info(f"Distributing {len([c for level in course_levels for c in level])} courses across {target_terms} terms")
        
        # Initialize terms
        terms = [[] for _ in range(target_terms)]
        target_units_per_term = total_units / target_terms
        
        # Track current state
        term_units = [0.0] * target_terms
        term_departments = [set() for _ in range(target_terms)]
        current_term = 0
        
        # Process each prerequisite level
        for level_idx, level_courses in enumerate(course_levels):
            logger.info(f"Processing level {level_idx} with {len(level_courses)} courses")
            
            # Sort courses in this level by optimization criteria
            sorted_courses = sorted(level_courses, key=lambda x: (
                x.get("difficulty", 3),        # Easier courses first
                -x.get("units", 4),           # Higher unit courses first (to balance)
                x.get("department", "z")       # Alphabetical by department
            ))
            
            # Distribute courses in this level across available terms
            for course in sorted_courses:
                best_term = self._find_best_term_for_course(
                    course, terms, term_units, term_departments, 
                    target_units_per_term, current_term, target_terms
                )
                
                # Add course to best term
                terms[best_term].append(course)
                term_units[best_term] += course.get("units", 0)
                term_departments[best_term].add(course.get("department", "unknown"))
                
                logger.info(f"Added {course.get('course_code')} to term {best_term + 1}")
            
            # Move to next term if current level is complete and we have space
            if level_idx < len(course_levels) - 1:
                current_term = min(current_term + 1, target_terms - 1)
        
        return terms

    def _find_best_term_for_course(self, course: Dict, terms: List[List[Dict]], 
                                term_units: List[float], term_departments: List[set],
                                target_units: float, min_term: int, max_terms: int) -> int:
        """
        Find the best term for a course considering unit balance and department diversity.
        """
        course_units = course.get("units", 0)
        course_dept = course.get("department", "unknown")
        
        best_term = min_term
        best_score = float('inf')
        
        # Consider terms from min_term onwards (respects prerequisites)
        for term_idx in range(min_term, max_terms):
            # Calculate score for this term
            
            # Unit balance score (prefer terms closer to target)
            units_after = term_units[term_idx] + course_units
            unit_score = abs(units_after - target_units)
            
            # Department diversity score (prefer terms without this department)
            dept_score = 0 if course_dept not in term_departments[term_idx] else 5
            
            # Term balance score (prefer earlier terms if units are similar)
            term_score = term_idx * 0.1
            
            # Combined score
            total_score = unit_score + dept_score + term_score
            
            if total_score < best_score:
                best_score = total_score
                best_term = term_idx
        
        return best_term

    def _format_term_summary(self, terms: List[List[Dict]]) -> str:
        """Generate a readable summary of the term plan"""
        summary = []
        for i, term in enumerate(terms, 1):
            units = sum(course.get("units", 0) for course in term)
            courses = [course.get("course_code", "Unknown") for course in term]
            departments = set(course.get("department", "unknown") for course in term)
            
            summary.append(f"Term {i}: {len(courses)} courses, {units} units")
            summary.append(f"  Courses: {', '.join(courses)}")
            summary.append(f"  Departments: {', '.join(departments)}")
            summary.append("")
        
        return "\n".join(summary)
    
    async def get_classlist(self, request: InputRequest):
        try:
            agreements = await self.get_agreements(request)
            
            if not agreements:
                logger.warning("No agreements found")
                return []
                
            rules = agreements[0]["rules"]
            classSetIds = set()
            
            for rule in rules:
                source = rule["source"]
                # Extract course IDs from source based on type
                self._extract_course_ids_from_source(source, classSetIds)
            
            # Convert ObjectIds to strings for the prerequisite service
            classSetIds_str = [str(course_id) for course_id in classSetIds]
            
            college_id = request.targets[0].collegeId
            college_code = await self.college_service.get_college_code(college_id)
            
            if not college_code:
                logger.error(f"Could not find college code for college_id: {college_id}")
                return []
                
            college_collection_name = str(college_code) + "_course_prerequisites"
            prerequisite_service = PrerequisiteService(college_collection_name)
            
            return await prerequisite_service.get_classes(classSetIds_str)

        except Exception as e:
            logger.error(f"Error fetching classlist: {e}")
            raise

    def _extract_course_ids_from_source(self, source, classSetIds):
        """Recursively extract course IDs from source structure"""
        
        # Handle different source types
        source_type = source.get("type")
        
        if source_type == "COURSE":
            # Single course - extract ID
            course_id = source.get("id")
            if course_id:
                # Handle both ObjectId and string formats
                if isinstance(course_id, dict) and "$oid" in course_id:
                    classSetIds.add(course_id["$oid"])
                else:
                    classSetIds.add(str(course_id))
                    
        elif source_type == "GROUP":
            # Group of courses - check if it has children
            children = source.get("children", [])
            operator = source.get("operator", "AND")
            
            if operator == "AND":
                # AND: Need all courses
                for child in children:
                    self._extract_course_ids_from_source(child, classSetIds)
            else:  # OR
                # OR: Take first course as representative
                if children:
                    self._extract_course_ids_from_source(children[0], classSetIds)
        
        else:
            logger.warning(f"Unknown source type: {source_type}")

    async def get_agreements(self, request: InputRequest):
        try:
            or_conditions = []
            for target in request.targets:
                or_conditions.append({
                    "collegeId": ObjectId(target.collegeId),
                    "universityId": ObjectId(target.universityId),
                    "majorId": ObjectId(target.majorId)
                })

            if not or_conditions:
                logger.warning("No targets provided in request")
                return []
            
            cursor = self.collection.find({"$or": or_conditions})
            agreements = []
            async for doc in cursor:
                doc.pop('_id', None)
                agreements.append(doc)
            
            return agreements

        except Exception as e:
            logger.error(f"Error fetching agreements: {e}")
            raise

