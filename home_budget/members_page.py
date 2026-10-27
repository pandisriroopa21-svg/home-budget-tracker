from flask import Flask, request, render_template_string
import mysql.connector

app = Flask(__name__)


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",
        database="home_budget"
    )


@app.route("/members")
def members():
    page = request.args.get("page", 1, type=int)
    page = max(1, page)

    per_page = 20
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM members")
    total = cursor.fetchone()["total"]

    cursor.execute(
        """
        SELECT member_id, member_name, email, city
        FROM members
        ORDER BY member_id
        LIMIT %s OFFSET %s
        """,
        (per_page, offset)
    )

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Home Budget - Members</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f4f7fb;
                    padding: 30px;
                }

                h1 {
                    color: #174ea6;
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                }

                th, td {
                    padding: 12px;
                    border: 1px solid #ddd;
                    text-align: left;
                }

                th {
                    background: #174ea6;
                    color: white;
                }

                a {
                    display: inline-block;
                    margin: 15px 10px 0 0;
                    padding: 10px 15px;
                    background: #174ea6;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }
            </style>
        </head>

        <body>
            <h1>Home Budget - Members</h1>

            <h3>Total Members: {{ total }}</h3>

            <table>
                <tr>
                    <th>ID</th>
                    <th>Member Name</th>
                    <th>Email</th>
                    <th>City</th>
                </tr>

                {% for member in data %}
                <tr>
                    <td>{{ member.member_id }}</td>
                    <td>{{ member.member_name }}</td>
                    <td>{{ member.email }}</td>
                    <td>{{ member.city }}</td>
                </tr>
                {% endfor %}
            </table>

            <p>Page {{ page }} of {{ total_pages }}</p>

            {% if page > 1 %}
                <a href="/members?page={{ page - 1 }}">
                    Previous
                </a>
            {% endif %}

            {% if page < total_pages %}
                <a href="/members?page={{ page + 1 }}">
                    Next
                </a>
            {% endif %}
        </body>
        </html>
        """,
        data=data,
        total=total,
        page=page,
        total_pages=total_pages
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
