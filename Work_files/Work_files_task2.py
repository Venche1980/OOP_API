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


def get_shop_list_by_dishes(dishes, person_count):
    shop_list = {}

    for dish in dishes:
        if dish in cook_book:
            for ingredient in cook_book[dish]:
                name = ingredient['ingredient_name']
                quantity = ingredient['quantity'] * person_count
                measure = ingredient['measure']

                if name in shop_list:
                    shop_list[name]['quantity'] += quantity
                else:
                    shop_list[name] = {'measure': measure, 'quantity': quantity}

    return shop_list

pprint(get_shop_list_by_dishes(['Запеченный картофель', 'Омлет'], 2))
