### Database Schema

#### Tables and Descriptions

---

- **community_colleges**  
  Contains a list of all community colleges.

  | Column        | Type    | Description                     |
  |---------------|---------|---------------------------------|
  | id            | Integer | Primary key                     |
  | college_name  | String  | Name of the community college   |

  **Relationships:**
  - One-to-many with `courses` (a college can have many courses)

---

- **courses**  
  Stores all community college courses.

  | Column      | Type    | Description                                     |
  |-------------|---------|-------------------------------------------------|
  | id          | Integer | Primary key                                     |
  | code        | String  | Course code (e.g., CS 1)                        |
  | name        | String  | Course name                                     |
  | units       | Float   | Number of transferable units                    |
  | difficulty  | Integer | Difficulty level (1-5 scale, optional metric)   |
  | college_id  | Integer | Foreign key to `community_colleges.id`          |

  **Relationships:**
  - Many-to-one with `community_colleges`
  - One-to-many with `articulation_agreements`

---

- **universities**  
  Contains a list of all universities (UCs or CSUs).

  | Column           | Type    | Description                      |
  |------------------|---------|----------------------------------|
  | id               | Integer | Primary key                      |
  | university_name  | String  | Name of the university           |
  | is_uc            | Boolean | Indicates if the school is a UC  |

  **Relationships:**
  - One-to-many with `majors`
  - One-to-many with `articulation_agreements`

---

- **majors**  
  Lists each major offered by a university.

  | Column        | Type    | Description                           |
  |---------------|---------|---------------------------------------|
  | id            | Integer | Primary key                           |
  | major_name    | String  | Name of the major                     |
  | university_id | Integer | Foreign key to `universities.id`      |

  **Relationships:**
  - Many-to-one with `universities`
  - Many-to-many with `university_courses` (via link table)
  - One-to-many with `dashboards`
  - One-to-many with `articulation_agreements`

---

- **university_courses**  
  Stores courses required for each major.

  | Column           | Type    | Description                                |
  |------------------|---------|--------------------------------------------|
  | id               | Integer | Primary key                                |
  | course_code      | String  | Course code at the university              |
  | course_name      | String  | Full name of the course                    |
  | university_id    | Integer | Foreign key to `universities.id`           |

  **Relationships:**
  - Many-to-many with `majors` (via `university_course_major_link`)
  - One-to-many with `articulation_agreements`

---

- **university_course_major_link**  
  Join table for university courses and majors (many-to-many).

  | Column               | Type    | Description                                   |
  |----------------------|---------|-----------------------------------------------|
  | id                   | Integer | Primary key                                   |
  | university_course_id | Integer | Foreign key to `university_courses.id`        |
  | major_id             | Integer | Foreign key to `majors.id`                    |

---

- **articulation_agreements**  
  Maps community college courses to university courses, scoped by university and major.

  | Column                        | Type    | Description                                            |
  |-------------------------------|---------|--------------------------------------------------------|
  | id                            | Integer | Primary key                                            |
  | community_college_course_id   | Integer | FK to `courses.id`                                     |
  | university_course_id          | Integer | FK to `university_courses.id`                          |
  | university_id                 | Integer | FK to `universities.id`                                |
  | major_id                      | Integer | FK to `majors.id`                                      |

---

- **users**  
  Stores student account information.

  | Column      | Type    | Description                      |
  |-------------|---------|----------------------------------|
  | id          | Integer | Primary key                      |
  | name        | String  | User name                        |
  | email       | String  | Unique user email                |
  | password    | String  | Hashed password                  |

  **Relationships:**
  - One-to-many with `dashboards`

---

- **dashboards**  
  Represents user-created transfer plans.

  | Column      | Type    | Description                              |
  |-------------|---------|------------------------------------------|
  | id          | Integer | Primary key                              |
  | user_id     | Integer | Foreign key to `users.id`                |
  | major_id    | Integer | Foreign key to `majors.id`               |
  | title       | String  | Optional name for the dashboard          |

  **Relationships:**
  - One-to-many with `semester_plans`

---

- **semester_plans**  
  Maps a dashboard to courses divided by semester.

  | Column        | Type    | Description                              |
  |---------------|---------|------------------------------------------|
  | id            | Integer | Primary key                              |
  | dashboard_id  | Integer | Foreign key to `dashboards.id`           |
  | course_id     | Integer | Foreign key to `courses.id`              |
  | semester_num  | Integer | Semester number in the plan              |
  | is_completed  | Boolean | Whether the course has been completed    |

