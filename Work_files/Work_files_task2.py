from  pprint import pprint
def parse_recipes(filename):
    cook_book = {}

    with open(filename, 'r', encoding='utf-8') as file:
        while True:

            dish_name = file.readline().strip()
            if not dish_name:
                break

            num_of_ingredients = int(file.readline().strip())

            ingredients = []

            for _ in range(num_of_ingredients):
                ingredient_data = file.readline().strip().split(' | ')
                ingredient_name = ingredient_data[0]
                quantity = int(ingredient_data[1])
                measure = ingredient_data[2]
                ingredients.append({
                    'ingredient_name': ingredient_name,
                    'quantity': quantity,
                    'measure': measure
                })

            cook_book[dish_name] = ingredients

            file.readline()

    return cook_book

filename = 'recipes.txt'
cook_book = parse_recipes(filename)

