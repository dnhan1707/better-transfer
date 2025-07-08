from sqlalchemy.orm import Session
from app.db.queries.institution_queries import db_get_basic_info
from app.schemas.transferPlanRequest import FullRequest, ReOrderRequestModel
from RAG.db.vector_store import VectorStore
from RAG.services.synthesizer import Synthesizer
from app.utils.logging_config import get_logger
import json
import traceback
from RAG.db.prereqisite_graph import prerequisite_graph

logger = get_logger(__name__)

class TransferPlanService:
    """Service for generating transfer plans."""
    def __init__(self):
        self.vector_store = VectorStore()
        self.synthesizer = Synthesizer()


    async def create_RAG_transfer_plan_v2(self, app_db: Session, vector_db: Session, full_request: FullRequest):
        try:
            # Validate input
            if not full_request.request:
                return {"error": "No transfer plan requests provided"}
        
            # Get information for all requested university-major combinations
            target_combinations = []
            college = None
            
            for request in full_request.request:
                basic_info = db_get_basic_info(app_db, request)
                if not basic_info:
                    logger.error(f"Could not find information for request: {request}")
                    continue
                    
                # All requests have the same college
                if not college:
                    college = basic_info["college"]
                    
                target_combinations.append({
                    "college": basic_info["college"],
                    "university": basic_info["university"],
                    "major": basic_info["major"]
                })
            
            if not target_combinations:
                return {"error": "No valid university-major combinations found"}
                
            # Build the multi-target query
            query_parts = ["Create an optimized transfer plan from " + college + " that satisfies requirements for:"]
            for idx, target in enumerate(target_combinations):
                query_parts.append(f"{idx+1}. {target['university']} - {target['major']}")
            query_parts.append(f"Duration: {full_request.number_of_terms} terms.")
            query_parts.append("Find courses that satisfy requirements for multiple universities when possible.")
            query = "\n".join(query_parts)
            
            # Get context for all targets at once
            vector_res = await self.vector_store.vector_search_v2(vector_db, query, target_combinations)
            
            # Generate the optimized plan
            result = await self.synthesizer.generate_response(question=query, number_of_terms=full_request.number_of_terms, vector_res=vector_res)
            
            return result
                
        except Exception as e:
            logger.error(f"Error RAG creating transfer plan: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}
        

    async def re_order_transfer_plan_v1(self, app_db: Session, vector_db: Session, request: ReOrderRequestModel):
        try:
            if not request.taken_classes or len(request.taken_classes) == 0:
                logger.error("No taken classes provided in request")
                return {"error": "Please specify at least one taken course"}
            
            original_plan = request.original_plan.model_dump()
            taken_classes = request.taken_classes
            source_college = request.original_plan.source_college
            courses_data = await self.vector_store.get_courses_data(vector_db, source_college)

            user_prompt = f"""
                # Original Transfer Plan Structure (to maintain)
                {json.dumps(original_plan, indent=2)}

                # Courses Already Taken (remove these)
                {json.dumps(taken_classes, indent=2)}

                # Instructions
                Please reorganize the transfer plan while:
                1. Preserving the EXACT same JSON structure shown above
                2. Removing all courses in the "taken_classes" list
                3. Redistributing remaining courses across the same number of terms
                4. Maintaining prerequisite ordering
            """

            return await self.synthesizer.generate_reorder_plan_response(user_prompt, courses_data)
            

        except Exception as e:
            logger.error(f"Error RAG re-order transfer plan: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}
        

    async def re_order_transfer_plan_v2(self, request: ReOrderRequestModel):
        """Algorithmically reorder a transfer plan after removing taken courses."""
        try:
            if not request.taken_classes or len(request.taken_classes) == 0:
                logger.error("No taken classes provided in request")
                return {"error": "Please specify at least one taken course"}
            
            original_plan = request.original_plan.model_dump()
            source_college = original_plan["source_college"]  # Use dict access, not attribute
            
            # Get prerequisite map
            prerequisite_data = prerequisite_graph.get(source_college, {})
            if not prerequisite_data:
                logger.warning(f"No prerequisite data found for {source_college}")
                return {"error": f"Prerequisite data not available for {source_college}"}
            
            taken_courses = request.taken_classes
            all_courses = await self.extract_all_courses(original_plan)
            
            # Filter out taken courses and their prerequisites
            remaining_courses = await self.filter_taken_course(taken_courses, all_courses, prerequisite_data)
            
            # Create a new plan structure
            new_plan = self._create_plan_structure(original_plan)
            
            # Build course dependency graph
            course_graph = await self._build_course_graph(remaining_courses, prerequisite_data)
            
            # Distribute courses across terms
            await self._distribute_courses(new_plan, course_graph)
            
            logger.info(f"Successfully reordered plan, removed {len(all_courses) - len(remaining_courses)} courses")
            return new_plan
            
        except Exception as e:
            logger.error(f"Error in re_order_transfer_plan_v2: {str(e)}")
            traceback.print_exc()
            return {"error": str(e)}
        


# =================================== Helper Functions ===============================================

    async def extract_all_courses(self, plan):
        """Extract all courses from the original plan."""
        all_courses = []
        for term in plan["term_plan"]:
            for course in term["courses"]:
                all_courses.append(course)
        return all_courses
    
    async def filter_taken_course(self, taken_courses, all_courses, prerequisite_data):
        """
        Filter courses based on taken courses, including prerequisite implications.
        Recursively finds all prerequisites of taken courses.
        """
        # Start with explicitly taken courses
        all_taken = set(taken_courses)
        
        # Find all implicit prerequisites recursively
        new_taken = set(taken_courses)
        while new_taken:
            next_level = set()
            for course_code in new_taken:
                if course_code in prerequisite_data:
                    # Process each prerequisite group (OR relationship)
                    for prereq_group in prerequisite_data[course_code]["prerequisites"]:
                        # Each element in the group has an AND relationship
                        for prereq in prereq_group:
                            if prereq not in all_taken:
                                next_level.add(prereq)
                
            # Add the new prerequisites and prepare for next iteration
            all_taken.update(next_level)
            new_taken = next_level
        
        # Filter out all taken courses from the plan
        filtered_courses = []
        for course in all_courses:
            if course["code"] not in all_taken:  # Fixed: use dict access, not attribute
                filtered_courses.append(course)
        
        logger.debug(f"Removed {len(all_taken)} courses ({len(taken_courses)} explicit + {len(all_taken) - len(taken_courses)} implicit)")
        return filtered_courses
                    
    def _create_plan_structure(self, original_plan):
        """Create empty plan with same structure as original."""
        new_plan = {
            "targets": original_plan["targets"],
            "source_college": original_plan["source_college"],
            "term_plan": []
        }
        
        # Create same number of empty terms
        for term in original_plan["term_plan"]:
            new_plan["term_plan"].append({
                "term": term["term"],
                "courses": []
            })
        
        # Add unscheduled courses if present in original
        if "unscheduled_courses" in original_plan:
            new_plan["unscheduled_courses"] = []
            
        return new_plan

    async def _build_course_graph(self, courses, prerequisite_data):
        """Build a graph of courses with dependencies for scheduling."""
        course_graph = {}
        
        # Initialize the graph
        for course in courses:
            code = course["code"]
            course_graph[code] = {
                "data": course,
                "prerequisites": [],
                "difficulty": course.get("difficulty", 3),
                "department": self._get_department(code),
                "earliest_term": 1
            }
            
            # Add prerequisite information
            if code in prerequisite_data:
                # Flatten the prerequisite groups
                prereqs = []
                for group in prerequisite_data[code]["prerequisites"]:
                    for prereq in group:
                        # Only add prerequisites that are still in our course list
                        if any(c["code"] == prereq for c in courses):
                            prereqs.append(prereq)
                course_graph[code]["prerequisites"] = prereqs
        
        # Calculate earliest possible term for each course
        for code in course_graph:
            self._calculate_earliest_term(code, course_graph, set())
            
        return course_graph
        
    def _calculate_earliest_term(self, code, graph, visited):
        """Recursively determine the earliest term a course can be placed in."""
        if code in visited:
            return  # Prevent cycles
            
        visited.add(code)
        
        if not graph[code]["prerequisites"]:
            graph[code]["earliest_term"] = 1
            return
            
        max_term = 0
        for prereq in graph[code]["prerequisites"]:
            if prereq in graph:
                self._calculate_earliest_term(prereq, graph, visited)
                max_term = max(max_term, graph[prereq]["earliest_term"])
                
        graph[code]["earliest_term"] = max_term + 1

    def _get_department(self, course_code):
        """Extract department code from course code."""
        return course_code.split(" ")[0]

    async def _distribute_courses(self, plan, course_graph):
        """Distribute courses across terms respecting prerequisites and balancing."""
        # Sort courses by earliest possible term, then by prerequisite chain length
        sorted_courses = sorted(
            course_graph.keys(),
            key=lambda x: (course_graph[x]["earliest_term"], -len(self._get_dependents(x, course_graph)))
        )
        
        # Initialize term stats
        num_terms = len(plan["term_plan"])
        term_difficulties = [0] * num_terms
        term_departments = [{} for _ in range(num_terms)]
        
        # Place each course in the best term
        for code in sorted_courses:
            course = course_graph[code]
            earliest = min(course["earliest_term"] - 1, num_terms - 1)  # Convert to 0-indexed
            
            # Find the best term based on balancing criteria
            best_term = earliest
            best_score = float('inf')
            
            for term_idx in range(earliest, num_terms):
                # Calculate balance score (lower is better)
                difficulty_score = term_difficulties[term_idx]
                
                # Diversity penalty - discourage too many courses from same department
                dept = course["department"]
                dept_count = term_departments[term_idx].get(dept, 0)
                diversity_penalty = dept_count * 2
                
                # Total score
                score = difficulty_score + diversity_penalty
                
                # Prefer earlier terms when scores are equal
                if score < best_score:
                    best_score = score
                    best_term = term_idx
            
            # Add course to chosen term
            plan["term_plan"][best_term]["courses"].append(course_graph[code]["data"])
            
            # Update term stats
            term_difficulties[best_term] += course["difficulty"]
            if course["department"] not in term_departments[best_term]:
                term_departments[best_term][course["department"]] = 0
            term_departments[best_term][course["department"]] += 1

    def _get_dependents(self, code, graph):
        """Get all courses that depend on this one."""
        dependents = []
        for other_code, other_course in graph.items():
            if code in other_course["prerequisites"]:
                dependents.append(other_code)
        return dependents