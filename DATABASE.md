### Database Schema

#### Tables and Descriptions

- **community_colleges**  
    Contains a list of all community colleges.

- **courses**  
    Stores all community college courses.  
    **Foreign Key:** References `community_colleges`.

- **universities**  
    Contains a list of all universities (UCs or CSUs).

- **majors**  
    Lists each major offered by a university.  
    **Foreign Key:** References `universities`.

- **university_courses**  
    Stores courses required for each major.  
    **Foreign Key:** References `majors`.

- **articulation_agreements**  
    Maps community college courses to university courses, scoped by university and major.

- **users**  
    Stores student account information.

- **dashboards**  
    Represents user-created plans.  
    **Foreign Keys:** References `users` and `majors`.

- **semester_plans**  
    Maps a semester to a list of courses.  
    **Foreign Key:** References `dashboards`.