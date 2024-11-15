from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Route to serve the frontend
@app.route("/")
def index():
    return render_template("index.html")

# Function to scrape a single URL and extract course data
def scrape_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Locate all course-related tables
        program_tables = soup.find_all("div", class_="TableRichTextElement-items")
        if not program_tables:
            return f"No program requirements found for {url}"

        courses = []
        for table in program_tables:
            for row in table.find_all("tr")[1:]:  # Skip header row
                cols = row.find_all("td")
                if len(cols) >= 5:  # Ensure there are enough columns
                    course_number = cols[0].get_text(strip=True)
                    title = cols[1].get_text(strip=True)
                    semesters_offered = cols[2].get_text(strip=True)
                    credit_hours = cols[3].get_text(strip=True)
                    prerequisites = cols[4].get_text(strip=True)

                    courses.append({
                        "courseNumber": course_number,
                        "title": title,
                        "semestersOffered": semesters_offered,
                        "creditHours": credit_hours,
                        "prerequisites": prerequisites,
                    })

        return courses
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

# API route to scrape data from multiple URLs
@app.route("/api/scrape", methods=["POST"])
def scrape_pages():
    data = request.json
    major_url = data.get("majorUrl")
    minor1_url = data.get("minor1Url")
    minor2_url = data.get("minor2Url")

    if not major_url or not minor1_url or not minor2_url:
        return jsonify({"error": "All three URLs are required."}), 400

    major_data = scrape_url(major_url)
    minor1_data = scrape_url(minor1_url)
    minor2_data = scrape_url(minor2_url)

    return jsonify({
        "majorCourses": major_data,
        "minor1Courses": minor1_data,
        "minor2Courses": minor2_data
    })

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

