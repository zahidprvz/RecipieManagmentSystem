from flask import Flask, request, jsonify, render_template
import pyodbc

app = Flask(__name__)

# ... (other functions remain the same)
# Replace these variables with your MSSQL connection details
server = "DESKTOP-0VNRQF5"
database = "SocialMediaNetworkDB"

# Connect to the database using Windows authentication
def connect_db():
    conn_str = f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    return pyodbc.connect(conn_str)

def create_table():
    with connect_db() as conn:
        cursor = conn.cursor()

        # Check if the 'recipes' table already exists
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'recipes'")
        if cursor.fetchone()[0] == 0:
            # Table does not exist, create it
            cursor.execute('''
                CREATE TABLE recipes (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    name NVARCHAR(255) NOT NULL,
                    category_id INT,
                    ingredients NVARCHAR(MAX) NOT NULL,
                    instructions NVARCHAR(MAX) NOT NULL,
                    cooking_time INT NOT NULL
                )
            ''')
            conn.commit()


def create_categories_table():
    with connect_db() as conn:
        cursor = conn.cursor()

        # Check if the 'categories' table already exists
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'categories'")
        if cursor.fetchone()[0] == 0:
            # Table does not exist, create it
            cursor.execute('''
                CREATE TABLE categories (
                    id INT PRIMARY KEY IDENTITY(1,1),
                    name NVARCHAR(255) NOT NULL
                )
            ''')
            conn.commit()


# Add a recipe to the database
def add_recipe(name, category_id, ingredients, instructions, cooking_time):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO recipes (name, category_id, ingredients, instructions, cooking_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, category_id, ingredients, instructions, cooking_time))
        conn.commit()

# Get all recipes from the database
def get_all_recipes():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM recipes')
        return cursor.fetchall()

# Get recipes matching the keyword from the database
def search_recipes(keyword):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM recipes
            WHERE name LIKE ? OR ingredients LIKE ? OR instructions LIKE ?
        ''', (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
        result = cursor.fetchall()

        # Convert the query result to a list of dictionaries
        recipes = []
        for row in result:
            recipe = {
                "id": row.id,
                "name": row.name,
                "category_id": row.category_id,
                "ingredients": row.ingredients,
                "instructions": row.instructions,
                "cooking_time": row.cooking_time
            }
            recipes.append(recipe)

        return recipes

# Get recipes belonging to a specific category from the database
def categorize_recipes(category_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM recipes WHERE category_id = ?', (category_id,))
        result = cursor.fetchall()

        # Convert the query result to a list of dictionaries
        recipes = []
        for row in result:
            recipe = {
                "id": row.id,
                "name": row.name,
                "category_id": row.category_id,
                "ingredients": row.ingredients,
                "instructions": row.instructions,
                "cooking_time": row.cooking_time
            }
            recipes.append(recipe)

        return recipes

@app.route('/api/add_recipe', methods=['POST'])
def api_add_recipe():
    recipe_data = request.json
    name = recipe_data.get('name')
    category_id = recipe_data.get('category_id')
    ingredients = recipe_data.get('ingredients')
    instructions = recipe_data.get('instructions')
    cooking_time = recipe_data.get('cooking_time')

    if not name or not ingredients or not instructions or not cooking_time:
        return jsonify({'message': 'Please provide all required recipe details.'}), 400

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO recipes (name, category_id, ingredients, instructions, cooking_time) VALUES (?, ?, ?, ?, ?)',
                       (name, category_id, ingredients, instructions, cooking_time))
        conn.commit()

    return jsonify({'message': 'Recipe added successfully.'}), 200


@app.route('/api/search_recipes', methods=['GET'])
def api_search_recipes():
    keyword = request.args.get('keyword')
    recipes = search_recipes(keyword)
    return jsonify(recipes)

@app.route('/api/categorize_recipes', methods=['GET'])
def api_categorize_recipes():
    category_id = request.args.get('category_id')
    recipes = categorize_recipes(category_id)
    return jsonify(recipes)


@app.route('/')
def index():
    return render_template('index.html')

# ... (other routes remain the same)

if __name__ == "__main__":
    create_table()
    create_categories_table()
    app.run(debug=True)
