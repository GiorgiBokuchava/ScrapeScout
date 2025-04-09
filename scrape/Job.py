class Job:
    def __init__(
        self,
        title,
        company_name,
        job_URL,
        description,
        posted_time,
        salary,
        email,
        favorite,
    ):
        self.title = title
        self.company_name = company_name
        self.job_URL = job_URL
        self.description = description
        self.posted_time = posted_time
        self.salary = salary
        self.email = email
        self.favorite = favorite

    def __str__(self):
        return f"Job Title: {self.title}\nCompany: {self.company_name}\nURL: {self.job_URL}\nDescription: {self.description}\nPosted: {self.posted_time}\nSalary: {self.salary}\nEmail: {self.email}\nFavorite: {self.favorite}"

    def mark_as_favorite(self):
        self.favorite = True

    def update_salary(self, new_salary):
        self.salary = new_salary
