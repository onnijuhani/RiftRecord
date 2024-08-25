from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

def get_team_profile(team_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT teamname, 
           COUNT(CASE WHEN result = 1 THEN 1 END) * 100.0 / COUNT(*) AS win_percentage,
           league
    FROM joukkuedata
    WHERE teamname = %s
    GROUP BY teamname, league
    ORDER BY COUNT(*) DESC
    LIMIT 1
    """

    cursor.execute(query, (team_name,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return {
            "teamname": result[0],
            "win_percentage": result[1],
            "league": result[2]
        }
    else:
        return None


@app.route('/team/<team_name>', methods=['GET'])
def team_profile(team_name):
    profile = get_team_profile(team_name)
    if profile:
        return jsonify(profile)
    else:
        return jsonify({"error": "Team not found"}), 404


@app.route('/team/<team_name>/tag', methods=['POST'])
def add_tag_to_team(team_name):
    tag = request.json.get('tag', None)
    if not tag:
        return jsonify({'error': 'Tag is required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if the tag already exists
    cur.execute('SELECT COUNT(*) FROM Teams WHERE tag = %s', (tag,))
    tag_exists = cur.fetchone()[0] > 0

    if tag_exists:
        cur.close()
        conn.close()
        return jsonify({'error': 'Tag is already in use'}), 400

    # Update the team with the new tag
    cur.execute('UPDATE Teams SET tag = %s WHERE team_name = %s', (tag, team_name))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'message': 'Tag updated successfully'}), 200


if __name__ == '__main__':
    app.run(port=5000)
