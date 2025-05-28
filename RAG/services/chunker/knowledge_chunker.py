from sqlalchemy.orm import Session
from app.db.models import (
    Courses, 
    Colleges, 
    ArticulationAgreements,
    Universities,
    UniversityCourses,
    Majors,
    Prerequisites
)
from typing import List, Dict, Any
from RAG.services.embedding_services import EmbeddingService

class KnowledgeChunker:

    @staticmethod
    async def generate_course_chunker(db: Session) -> List[Dict[str, Any]]:
        chunks = []

        courses = db.query(
            Courses, Colleges
        ).join(
            Colleges,
            Courses.college_id == Colleges.id
        ).all()

        for course, college in courses:
            content = (
                f"Course Information: {course.code} ({course.name}) at {college.college_name} is worth {course.units} "
                f"units. Its difficulty level is rated as {course.difficulty}/10. "
            )

            chunks.append({
                "content": content,
                "college_id": college.id,
                "college_name": college.college_name,
                "chunk_type": "course_description",
                "metadata": {
                    "course_code": course.code,
                    "units": course.units,
                }
            })

        return chunks
        
    @staticmethod
    async def generate_articulation_chunker(db: Session) -> List[Dict[str, Any]]:
        chunks = []

        articulations = db.query(
            ArticulationAgreements,
            Courses,
            UniversityCourses,
            Universities,
            Majors,
            Colleges
        ).join(
            Courses,
            ArticulationAgreements.community_college_course_id == Courses.id
        ).join(
            UniversityCourses,
            ArticulationAgreements.university_course_id == UniversityCourses.id
        ).join(
            Universities, ArticulationAgreements.university_id == Universities.id
        ).join(
            Majors, ArticulationAgreements.major_id == Majors.id
        ).join(
            Colleges, Courses.college_id == Colleges.id
        ).all()
        
        for agreement, cc_course, uni_course, university, major, college in articulations:
            relationship = "satifies" if agreement.relationship_type == "OR" else "must be taken with other courses to satisfy"

            content = (
                f"Course {cc_course.code} ({cc_course.name}) at {college.college_name} {relationship} "
                f"course {uni_course.course_code} ({uni_course.course_name}) at {university.university_name} "
                f"for the {major.major_name} major."
            )

            chunks.append({
                "content": content,
                "college_id": college.id,
                "college_name": college.college_name,
                "university_id": university.id,
                "university_name": university.university_name,
                "major_id": major.id,
                "major_name": major.major_name,
                "chunk_type": "articulation"
            })
        
        return chunks
    
    @staticmethod
    async def generate_prerequisite_chunk(db: Session) -> List[Dict[str, Any]]:
        chunks = []

        prerequisites = db.query(
            Prerequisites,
            Courses.code.label("course_code"),
            Courses.name.label("course_name"),
            Colleges.college_name,
            Colleges.label.id("college_id")
        ).join(
            Courses,
            Prerequisites.course_id == Courses.id
        ).join(
            Colleges,
            Courses.college_id == Colleges.id
        ).join(
            Courses,
            Prerequisites.prerequisite_course_id == Courses.id,
            aliased=True
        ).all()

        for prereq, course_code, course_name, college_name, college_id, prereq_code, prereq_name in prerequisites:
            # Build prerequisite description
            prereq_type = "required" if prereq.prerequisite_type == "REQUIRED" else "recommended"
            
            content = (
                f"Course {course_code} ({course_name}) at {college_name} has {prereq_code} ({prereq_name}) "
                f"as a {prereq_type} prerequisite."
            )
            
            chunks.append({
                "content": content,
                "college_id": college_id,
                "college_name": college_name,
                "chunk_type": "prerequisite"
            })
        
        return chunks
    
    @staticmethod
    async def store_chunks(db: Session, chunks: List[Dict[str, Any]], instruction: str) -> None:
        texts = [chunk["content"] for chunk in chunks]
        embedding_service = EmbeddingService(instruction) 

        embeddings = embedding_service.batch_create_embedding(texts)

        # Insert into database
        for i, chunk in enumerate(chunks):
            embedding = embeddings[i]

            db.execute(
                """
                INSERT INTO rag-database
                (content, embedding, college_id, university_id, major_id, chunk_type) 
                VALUES (:content, :embedding, :college_id, :college_name, :university_id, :university_name, :major_id, :major_name, :chunk_type)
                """,
                {
                    "content": chunk["content"],
                    "embedding": embedding,
                    "college_id": chunk.get("college_id"),
                    "college_name": chunk.get("college_name"),
                    "university_id": chunk.get("university_id"),
                    "university_name": chunk.get("university_name"),
                    "major_id": chunk.get("major_id"), 
                    "major_name": chunk.get("major_name"), 
                    "chunk_type": chunk["chunk_type"]
                }
            )

        db.commit()
        

