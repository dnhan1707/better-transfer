from app.db.connection.mongo_connection import MongoDB
from app.services.college_service import CollegeService
from app.schemas.transferPlanRequest import InputRequest
from app.utils.logging_config import get_logger
from bson.objectid import ObjectId
from typing import List, Dict, Set, Any

logger = get_logger(__name__)

class PrerequisiteService():
    def __init__(self, collection_name: str):
        self.mongo = MongoDB("course_prerequisite")
        self.collection = self.mongo.get_collection(collection_name.lower()) 
        print(f"Collection name: {collection_name}")
        self.college_service = CollegeService()
    
    async def get_classes(self, class_ids: List[str]) -> List[Dict[str, Any]]:
        '''
        Get all classes including prerequisites, optimized for minimum course load.
        '''
        try:
            # Convert string IDs to ObjectIds
            object_ids = [ObjectId(class_id) for class_id in class_ids]
            logger.info(f"Requested course IDs: {class_ids}")
            
            # Get ONLY the initially requested courses
            required_courses = await self._get_courses_by_ids(object_ids)
            logger.info(f"Found {len(required_courses)} requested courses")
            
            if not required_courses:
                logger.warning("No courses found for provided IDs")
                return []
            
            # Build complete course plan with prerequisites
            all_courses = await self._build_complete_course_plan(required_courses)
            
            # Convert ObjectIds to strings for JSON serialization
            for course in all_courses:
                if '_id' in course:
                    course['_id'] = str(course['_id'])
            
            logger.info(f"Built course plan with {len(all_courses)} total courses")
            return all_courses
            
        except Exception as e:
            logger.error(f"Error in get_classes: {e}")
            raise

    async def _get_courses_by_ids(self, object_ids: List[ObjectId]) -> List[Dict[str, Any]]:
        """Fetch courses by their ObjectIds - ONLY the requested ones"""
        try:
            logger.info(f"Fetching courses with ObjectIds: {object_ids}")
            cursor = self.collection.find({"_id": {"$in": object_ids}})
            courses = []
            async for doc in cursor:
                courses.append(doc)
            
            # Log what we actually found
            found_codes = [course.get("course_code") for course in courses]
            logger.info(f"Found courses: {found_codes}")
            
            return courses
        except Exception as e:
            logger.error(f"Error fetching courses by IDs: {e}")
            raise

    async def _build_complete_course_plan(self, required_courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build complete course plan including all prerequisites"""
        all_courses = {}  # Use dict to avoid duplicates, key = course_code
        visited = set()  # Track processed courses to avoid cycles
        
        logger.info(f"Processing {len(required_courses)} required courses")
        
        # Process each required course
        for course in required_courses:
            course_code = course.get("course_code")
            logger.info(f"Processing required course: {course_code}")
            await self._process_course_prerequisites(course, all_courses, visited)
        
        result_courses = list(all_courses.values())
        result_codes = [c.get("course_code") for c in result_courses]
        logger.info(f"Final course plan: {result_codes}")
        
        return result_courses

    async def _process_prerequisites(self, prerequisites: List[List[str]], all_courses: Dict[str, Dict], visited: Set[str]):
        """
        Process prerequisite groups and choose optimal path.
        Handle both OR and AND relationships properly.
        """
        logger.info(f"Processing prerequisites: {prerequisites}")
        
        # Special case: if all groups have single items, treat as OR (common pattern)
        if all(len(group) == 1 for group in prerequisites if group):
            # Flatten into one OR group
            all_options = [group[0] for group in prerequisites if group]
            logger.info(f"Converting single-item groups to OR: {all_options}")
            
            chosen_prereq = await self._choose_optimal_prerequisite(all_options, visited)
            logger.info(f"Chosen from OR group: {chosen_prereq}")
            
            if chosen_prereq and chosen_prereq not in visited:
                prereq_course = await self._get_course_by_code(chosen_prereq)
                if prereq_course:
                    await self._process_course_prerequisites(prereq_course, all_courses, visited)
        else:
            # Handle as normal AND groups
            for prereq_group in prerequisites:
                if not prereq_group:
                    continue
                    
                chosen_prereq = await self._choose_optimal_prerequisite(prereq_group, visited)
                if chosen_prereq and chosen_prereq not in visited:
                    prereq_course = await self._get_course_by_code(chosen_prereq)
                    if prereq_course:
                        await self._process_course_prerequisites(prereq_course, all_courses, visited)


    async def _process_course_prerequisites(self, course: Dict[str, Any], all_courses: Dict[str, Dict], visited: Set[str]):
        """Recursively process a course and its prerequisites"""
        course_code = course.get("course_code")
        
        if not course_code or course_code in visited:
            return
        
        visited.add(course_code)
        
        # Add current course to the plan
        all_courses[course_code] = course
        
        # Skip prerequisites if assessment is allowed
        if course.get("assessment_allow", False):
            logger.info(f"Course {course_code} allows assessment - skipping prerequisites")
            return
        
        # Process prerequisites
        prerequisites = course.get("prerequisites", [])
        if prerequisites:
            await self._process_prerequisites(prerequisites, all_courses, visited)

    async def _choose_optimal_prerequisite(self, prereq_options: List[str], visited: Set[str]) -> str:
        """
        Choose the optimal prerequisite from a list of options.
        """
        if not prereq_options:
            return None
            
        # If only one option, return it
        if len(prereq_options) == 1:
            return prereq_options[0]
        
        # Check if any prerequisite is already being taken
        for prereq in prereq_options:
            if prereq in visited:
                logger.info(f"Choosing {prereq} - already in course plan")
                return prereq
        
        # Get course details for all options to make optimal choice
        prereq_courses = []
        for prereq_code in prereq_options:
            course = await self._get_course_by_code(prereq_code)
            if course:
                prereq_courses.append(course)
        
        if not prereq_courses:
            return prereq_options[0]  # Fallback to first option
        
        # Choose based on optimization criteria
        optimal_course = min(prereq_courses, key=lambda x: (
            0 if x.get("assessment_allow", False) else 1,  # Assessment-allowed courses first (0 < 1)
            len(x.get("prerequisites", [])),                # Fewest prerequisites first
            x.get("difficulty", 5),                        # Lower difficulty
            x.get("units", 5),                             # Fewer units
        ))
        
        chosen = optimal_course.get("course_code")
        logger.info(f"Optimal choice from {prereq_options}: {chosen} (assessment: {optimal_course.get('assessment_allow')}, prereqs: {len(optimal_course.get('prerequisites', []))})")
        return chosen


    async def _get_course_by_code(self, course_code: str) -> Dict[str, Any]:
        """Get a course by its course code"""
        try:
            course = await self.collection.find_one({"course_code": course_code})
            return course
        except Exception as e:
            logger.error(f"Error fetching course {course_code}: {e}")
            return None

    async def get_course_sequence(self, class_ids: List[str]) -> Dict[str, Any]:
        """
        Get courses organized by prerequisite levels for scheduling.
        Returns courses grouped by the order they should be taken.
        """
        try:
            all_courses = await self.get_classes(class_ids)
            
            # Build dependency graph
            course_graph = self._build_dependency_graph(all_courses)
            
            # Organize into levels (semester order)
            course_levels = self._organize_by_levels(course_graph, all_courses)
            
            return {
                "total_courses": len(all_courses),
                "total_units": sum(course.get("units", 0) for course in all_courses),
                "course_sequence": course_levels,
                "all_courses": all_courses
            }
            
        except Exception as e:
            logger.error(f"Error building course sequence: {e}")
            raise

    def _build_dependency_graph(self, courses: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build a dependency graph showing which courses depend on others"""
        graph = {}
        course_codes = {course.get("course_code") for course in courses}
        
        for course in courses:
            course_code = course.get("course_code")
            if not course_code:
                continue
                
            dependencies = []
            prerequisites = course.get("prerequisites", [])
            
            # Skip prerequisites if this course allows assessment
            if course.get("assessment_allow", False):
                graph[course_code] = []
                continue
            
            # Process each OR group in prerequisites
            for prereq_group in prerequisites:
                # Find ANY prerequisite from this OR group that exists in our course list
                found_prereq = None
                for prereq in prereq_group:
                    if prereq in course_codes:
                        found_prereq = prereq
                        break
                
                # If we found a prerequisite, add it as a dependency
                if found_prereq:
                    dependencies.append(found_prereq)
            
            graph[course_code] = dependencies
        
        return graph

    def _organize_by_levels(self, graph: Dict[str, List[str]], courses: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Organize courses into levels based on prerequisites"""
        levels = []
        remaining_courses = {course.get("course_code"): course for course in courses}
        completed = set()
        
        while remaining_courses:
            current_level = []
            
            # Find courses with no remaining dependencies
            for course_code, course in list(remaining_courses.items()):
                dependencies = graph.get(course_code, [])
                
                # Check if all dependencies are completed or can be bypassed
                can_take = self._can_take_course(course, dependencies, completed, remaining_courses)
                
                if can_take:
                    current_level.append(course)
                    completed.add(course_code)
                    del remaining_courses[course_code]
            
            if not current_level:
                # Handle circular dependencies or missing prerequisites
                logger.warning("Circular dependency or missing prerequisites detected")
                current_level = list(remaining_courses.values())
                break
            
            levels.append(current_level)
        
        return levels

    def _can_take_course(self, course: Dict[str, Any], dependencies: List[str], completed: Set[str], remaining_courses: Dict[str, Dict]) -> bool:
        """
        Determine if a course can be taken based on prerequisites and assessment rules.
        
        Key logic:
        1. If course allows assessment, it can be taken regardless of prerequisites
        2. If prerequisite allows assessment, the dependency is satisfied
        3. Otherwise, check normal prerequisite completion
        """
        course_code = course.get("course_code")
        
        # If this course allows assessment, it can be taken anytime
        if course.get("assessment_allow", False):
            return True
        
        # Check each dependency
        for dep in dependencies:
            # If dependency is already completed, it's satisfied
            if dep in completed:
                continue
                
            # If dependency is in our remaining courses and allows assessment,
            # it can be bypassed
            if dep in remaining_courses:
                dep_course = remaining_courses[dep]
                if dep_course.get("assessment_allow", False):
                    continue
            
            # If we reach here, this dependency is not satisfied
            return False
        
        # All dependencies are satisfied
        return True