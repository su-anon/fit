import sqlite3
import schema
import newadmin

exercises = [
    ("Morning Jog", 1, 1, 200),
    ("HIIT Workout", 1, 1, 300),
    ("Push-ups & Sit-ups", 1, 1, 180),
    ("Cycling", 1, 1, 250),
    ("Yoga Flow", 1, 1, 180),
    ("Jump Rope", 1, 1, 120),
    ("Plank Variations", 1, 1, 150),
    ("Dumbbell Squats", 1, 1, 220),
    ("Lunges & Step-ups", 1, 1, 200),
    ("Box Breathing + Stretch", 1, 1, 80),
    ("Pull-ups + Rows", 1, 1, 250),
    ("Mountain Climbers", 1, 1, 160),
    ("Burpees + Jump Squats", 1, 1, 280),
    ("Stair Sprints", 1, 1, 220),
    ("Dance Cardio", 1, 1, 300),
    ("Shadow Boxing", 1, 1, 260),
    ("Pilates Core Routine", 1, 1, 200),
    ("Wall Sits + Calf Raises", 1, 1, 180),
    ("Resistance Band Training", 1, 1, 230),
    ("Walking with Incline", 1, 1, 220),
    ("Kettlebell Swings", 1, 1, 230),
    ("Burpees", 1, 1, 270),
    ("High Knees", 1, 1, 210),
    ("Box Jumps", 1, 1, 250),
    ("Lateral Raises", 1, 1, 150),
    ("Treadmill Sprint", 1, 1, 350),
    ("Sled Pushes", 1, 1, 320),
    ("Rowing Machine", 1, 1, 220),
    ("Bicep Curls", 1, 1, 140),
    ("Tricep Dips", 1, 1, 160),
    ("Leg Press", 1, 1, 240)
]
foods = [
    ("Oatmeal with Bananas", "1 bowl", 300),
    ("Greek Yogurt & Berries", "1 cup", 280),
    ("Grilled Chicken Breast", "200g", 350),
    ("Tofu & Veggie Stir Fry", "1 serving", 400),
    ("Avocado Toast on Multigrain", "1 slice", 330),
    ("Boiled Eggs & Spinach", "2 eggs + 1 cup spinach", 320),
    ("Quinoa Bowl with Chickpeas", "1 bowl", 390),
    ("Smoothie with Chia & Mango", "1 cup", 310),
    ("Cottage Cheese & Pineapple", "1 cup", 260),
    ("Lentil Soup & Wholegrain Bread", "1 bowl + 1 slice", 400),
    ("Tuna Salad with Olive Oil", "1 serving", 370),
    ("Brown Rice & Mixed Vegetables", "1 serving", 420),
    ("Protein Shake with Banana", "1 shake", 290),
    ("Zucchini Noodles & Pesto", "1 serving", 350),
    ("Chia Pudding & Mixed Berries", "1 serving", 300),
    ("Almond Butter on Rye Bread", "2 tbsp + 1 slice", 340),
    ("Steamed Broccoli & Sweet Potato", "1 serving", 360),
    ("Fruit & Nut Mix", "1/4 cup", 280),
    ("Paneer with Bell Peppers", "1 serving", 380),
    ("Hummus & Carrot Sticks", "2 tbsp + 1 cup", 250),
    ("Egg Salad on Whole Wheat", "1 sandwich", 330),
    ("Chicken Caesar Salad", "1 serving", 400),
    ("Apple with Peanut Butter", "1 apple + 2 tbsp", 250),
    ("Veggie Burger on Whole Grain Bun", "1 burger", 380),
    ("Baked Salmon with Asparagus", "200g salmon + 1 cup asparagus", 450),
    ("Sweet Potato & Black Bean Chili", "1 bowl", 370),
    ("Granola with Almond Milk", "1 bowl", 280),
    ("Avocado Smoothie with Almonds", "1 cup", 340),
    ("Rice and Bean Burrito", "1 burrito", 420),
    ("Chickpea Salad with Olive Oil", "1 serving", 330),
    ("Spaghetti with Marinara Sauce", "1 plate", 380),
    ("Mixed Greens Salad with Balsamic", "1 serving", 180)
]

with sqlite3.connect("database.db") as connection:
    cursor = connection.cursor()
    cursor.executemany('''
        insert into exercise (exercise_detail, sets, reps, calorie_burn)
        values (?, ?, ?, ?)
    ''', exercises)
    cursor.executemany('''
        insert into food (food_detail, quantity, calorie_gain)
        values (?, ?, ?)
    ''', foods)

